// Weapon firing logic. Reads perks from state.mult/flags.

function gunFireRate(state, gun) {
  return gun.fireRate * state.mult.fireRate;
}

function gunDamage(state, gun) {
  let d = gun.dmg * state.mult.dmg;
  if (gun.dmgType === "explosive" || gun.dmgType === "plasma") d *= state.mult.explosiveDmg;
  if (state.flags.berserker && state.player.hp < state.player.maxHp * 0.3) d *= 1.8;
  return d;
}

function rollCrit(state) {
  if (Math.random() < state.crit.chance) return state.crit.mult;
  return 1;
}

function fireWeapon(state, now) {
  const gun = GUNS[state.currentGun];
  if (!gun) return;
  const fr = gunFireRate(state, gun);
  if (now - state.lastShot < fr) return;
  if (state.ammo[gun.id] !== undefined && state.ammo[gun.id] <= 0) return;

  state.lastShot = now;

  // Minigun windup
  if (gun.windup) {
    state.windupT = (state.windupT || 0) + fr;
    if (state.windupT < gun.windup) return;
  }

  if (isFinite(gun.ammo)) state.ammo[gun.id]--;

  const aimX = Input.mouse.x, aimY = Input.mouse.y;
  const baseAng = Math.atan2(aimY - state.player.y, aimX - state.player.x);

  // Melee weapons
  if (gun.dmgType === "melee") {
    fireMelee(state, gun, baseAng);
    addShake(gun.shake, 150);
    return;
  }

  // Tesla chains instead of firing a bullet
  if (gun.dmgType === "tesla") {
    fireTesla(state, gun, baseAng);
    addShake(gun.shake, 180);
    return;
  }

  addShake(gun.shake, 180);
  muzzleFlash(
    state.player.x + Math.cos(baseAng) * 26,
    state.player.y + Math.sin(baseAng) * 26,
    baseAng, gun.flashColor
  );

  const bullets = gun.bullets + (gun.id === 1 ? state.mult.shotgunBonus : 0);
  const spread = gun.id === 1 ? gun.spread * (1 - state.mult.shotgunBonus * 0.08) : gun.spread;

  for (let i = 0; i < bullets; i++) {
    const ang = baseAng + (Math.random() - 0.5) * spread * 2;
    spawnBullet(state, gun, ang, baseAng);
  }

  // Perks: every 10th shot is a rocket
  state.shotCount = (state.shotCount || 0) + 1;
  if (state.flags.tenthRocket && state.shotCount % 10 === 0) {
    const rg = GUNS[6];
    spawnBullet(state, rg, baseAng, baseAng, { freeBonus: true });
  }
  if (state.flags.doubleShot) {
    setTimeout(() => {
      if (state.gameRunning) {
        for (let i = 0; i < bullets; i++) {
          const ang = baseAng + (Math.random() - 0.5) * spread * 2;
          spawnBullet(state, gun, ang, baseAng);
        }
      }
    }, 80);
  }
}

function spawnBullet(state, gun, ang, baseAng, opts = {}) {
  const critMult = rollCrit(state);
  const dmg = gunDamage(state, gun) * critMult;
  state.bullets.push({
    x: state.player.x + Math.cos(baseAng) * 22,
    y: state.player.y + Math.sin(baseAng) * 22,
    vx: Math.cos(ang) * gun.bulletSpd,
    vy: Math.sin(ang) * gun.bulletSpd,
    dmg,
    critical: critMult > 1,
    life: gun.ttl || 90,
    pierce: gun.pierce + state.mult.pierce,
    bounce: state.mult.bounce,
    hit: new Set(),
    explode: gun.explode ? gun.explode * state.mult.explodeRadius : 0,
    dmgType: gun.dmgType,
    color: gun.bulletColor,
    size: gun.bulletSize,
    randomEffect: gun.randomEffect,
    explosiveRounds: state.flags.explosiveRounds,
    canSplit: state.flags.split,
    splitAtLife: (gun.ttl || 90) * 0.3,
  });
}

function fireMelee(state, gun, ang) {
  // arc swing around player
  const cx = state.player.x, cy = state.player.y;
  if (gun.dashDist) {
    state.player.x += Math.cos(ang) * gun.dashDist;
    state.player.y += Math.sin(ang) * gun.dashDist;
    clampPlayer(state);
  }
  for (const z of state.zombies) {
    const d = dist(state.player, z);
    if (d > gun.range + z.size / 2) continue;
    const za = Math.atan2(z.y - state.player.y, z.x - state.player.x);
    let da = za - ang; while (da > Math.PI) da -= Math.PI*2; while (da < -Math.PI) da += Math.PI*2;
    if (Math.abs(da) <= gun.arc / 2) {
      const critMult = rollCrit(state);
      damageZombie(state, z, gunDamage(state, gun) * critMult, z.x, z.y, { crit: critMult > 1, dmgType: "melee" });
    }
  }
  // visual arc
  for (let i = 0; i < 8; i++) {
    const t = i / 7;
    const a = ang - gun.arc / 2 + gun.arc * t;
    addParticle(
      state.player.x + Math.cos(a) * gun.range * 0.7,
      state.player.y + Math.sin(a) * gun.range * 0.7,
      { color: gun.flashColor, size: 4, life: 12 }
    );
  }
}

function fireTesla(state, gun, ang) {
  // find closest target
  let best = null, bestD = Infinity;
  for (const z of state.zombies) {
    const d = dist(state.player, z);
    if (d < bestD && d < 260) { bestD = d; best = z; }
  }
  if (!best) {
    muzzleFlash(state.player.x + Math.cos(ang)*26, state.player.y + Math.sin(ang)*26, ang, gun.flashColor);
    return;
  }
  const critMult = rollCrit(state);
  const chain = [best];
  const hit = new Set(chain);
  let cur = best, curDmg = gunDamage(state, gun) * critMult;
  damageZombie(state, cur, curDmg, cur.x, cur.y, { crit: critMult > 1, dmgType: "tesla" });
  for (let i = 1; i < (gun.chain || 1); i++) {
    let next = null, nd = Infinity;
    for (const z of state.zombies) {
      if (hit.has(z)) continue;
      const d = dist(cur, z);
      if (d < nd && d < gun.chainRange) { nd = d; next = z; }
    }
    if (!next) break;
    curDmg *= gun.chainFalloff;
    damageZombie(state, next, curDmg, next.x, next.y, { dmgType: "tesla" });
    chain.push(next);
    hit.add(next);
    cur = next;
  }
  // visualize chain
  state.teslaArcs = state.teslaArcs || [];
  state.teslaArcs.push({ points: [state.player, ...chain.map(z => ({ x: z.x, y: z.y }))], life: 8 });
}
