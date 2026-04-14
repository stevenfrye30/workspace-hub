// Placeable defenses: turrets, barricades, traps.
// Bought from the shop, placed during PLACING sub-state (user clicks a spot).

const DEFENSES = [
  { id: "barricade", name: "Wooden Barricade", emoji: "🪵", cost: 40,  hp: 200, blocks: true,  desc: "Blocks zombies. 200 HP." },
  { id: "wall",      name: "Reinforced Wall",  emoji: "🧱", cost: 90,  hp: 500, blocks: true,  desc: "Blocks zombies. 500 HP." },
  { id: "spike",     name: "Spike Trap",       emoji: "🔱", cost: 50,  hp: 9999, blocks: false, dmg: 20, desc: "Damages zombies that walk over (20 dmg)." },
  { id: "mine",      name: "Proximity Mine",   emoji: "💣", cost: 80,  hp: 1,   blocks: false, dmg: 80, radius: 70, oneShot: true, desc: "Explodes on contact." },
  { id: "tesla",     name: "Tesla Coil",       emoji: "⚡", cost: 180, hp: 300, blocks: true,  auto: "tesla", dmg: 25, range: 140, cd: 600, desc: "Auto-zaps nearby zombies." },
  { id: "turret",    name: "Auto Turret",      emoji: "🔫", cost: 250, hp: 250, blocks: true,  auto: "turret", dmg: 14, range: 260, cd: 180, desc: "Auto-fires at zombies." },
  { id: "barrel",    name: "Explosive Barrel", emoji: "🛢️", cost: 30,  hp: 40,  blocks: true,  explodeDmg: 100, explodeRadius: 90, desc: "Explodes when shot/killed." },
];
const DEF_BY_ID = Object.fromEntries(DEFENSES.map(d => [d.id, d]));

function placeDefense(state, defId, x, y) {
  const d = DEF_BY_ID[defId];
  if (!d) return;
  state.defenses.push({
    ...d, x, y, maxHp: d.hp, lastFire: 0, size: 28,
  });
}

function updateDefenses(st, dt) {
  if (!st.defenses) return;
  for (const d of st.defenses) {
    if (d.auto === "turret") {
      d.lastFire -= dt;
      if (d.lastFire <= 0) {
        // find closest zombie
        let best = null, bd = d.range;
        for (const z of st.zombies) {
          const dd = Math.hypot(z.x - d.x, z.y - d.y);
          if (dd < bd) { bd = dd; best = z; }
        }
        if (best) {
          d.lastFire = d.cd;
          const ang = Math.atan2(best.y - d.y, best.x - d.x);
          st.bullets.push({
            x: d.x, y: d.y,
            vx: Math.cos(ang) * 10, vy: Math.sin(ang) * 10,
            dmg: d.dmg, life: 60, pierce: 0, bounce: 0, hit: new Set(),
            color: "#38bdf8", size: 3, dmgType: "kinetic", fromTurret: true,
          });
          muzzleFlash(d.x + Math.cos(ang)*14, d.y + Math.sin(ang)*14, ang, "#38bdf8");
        }
      }
    } else if (d.auto === "tesla") {
      d.lastFire -= dt;
      if (d.lastFire <= 0) {
        let best = null, bd = d.range;
        for (const z of st.zombies) {
          const dd = Math.hypot(z.x - d.x, z.y - d.y);
          if (dd < bd) { bd = dd; best = z; }
        }
        if (best) {
          d.lastFire = d.cd;
          damageZombie(st, best, d.dmg, best.x, best.y, { dmgType: "tesla" });
          st.teslaArcs = st.teslaArcs || [];
          st.teslaArcs.push({ points: [{x:d.x,y:d.y}, {x:best.x,y:best.y}], life: 8 });
        }
      }
    }

    // zombies attack blocks
    if (d.blocks) {
      for (const z of st.zombies) {
        if (Math.hypot(z.x - d.x, z.y - d.y) < z.size / 2 + d.size / 2) {
          d.hp -= z.dmg * dt / 800;
          // push zombie back slightly
          const ang = Math.atan2(z.y - d.y, z.x - d.x);
          z.x += Math.cos(ang) * 0.8; z.y += Math.sin(ang) * 0.8;
        }
      }
    } else if (d.dmg) {
      // trap: damage zombies passing over
      for (const z of st.zombies) {
        if (Math.hypot(z.x - d.x, z.y - d.y) < d.size / 2 + 4) {
          damageZombie(st, z, d.dmg * dt / 400, z.x, z.y);
          if (d.oneShot) {
            if (d.radius) doExplosion(st, d.x, d.y, d.radius, d.dmg);
            d.hp = 0; break;
          }
        }
      }
    }

    if (d.hp <= 0 && d.explodeDmg) {
      doExplosion(st, d.x, d.y, d.explodeRadius, d.explodeDmg);
    }
  }
  st.defenses = st.defenses.filter(d => d.hp > 0);
}

function drawDefenses(st) {
  if (!st.defenses) return;
  for (const d of st.defenses) {
    ctx.font = "28px serif";
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(d.emoji, d.x, d.y);
    // hp bar
    if (d.hp < d.maxHp && d.maxHp > 1) {
      const bw = 30, hpFrac = d.hp / d.maxHp;
      ctx.fillStyle = "#2a0707";
      ctx.fillRect(d.x - bw/2, d.y - 22, bw, 3);
      ctx.fillStyle = hpFrac > 0.5 ? "#22c55e" : hpFrac > 0.25 ? "#fbbf24" : "#dc2626";
      ctx.fillRect(d.x - bw/2, d.y - 22, bw * hpFrac, 3);
    }
  }
}
