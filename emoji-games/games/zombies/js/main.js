// Main game state, loop, rendering, and glue.
let state = null;
let save = loadSave();
let canvas, ctx, stage;

const SCENE = { MENU: 0, PLAYING: 1, LEVELUP: 2, SHOP: 3, GAMEOVER: 4, PAUSED: 5 };

function newState(opts = {}) {
  const map = MAP_BY_ID[opts.mapId || "graveyard"];
  const char = CHARACTER_BY_ID[opts.charId || "survivor"];
  const s = {
    scene: SCENE.PLAYING,
    W: 0, H: 0,
    save,
    map, char, mode: opts.mode || "classic",

    player: {
      x: 0, y: 0, r: 18, hp: 100, maxHp: 100, spd: 3.4,
      emoji: char.emoji, facing: 0, iframes: 0, cursed: 0,
      kills: 0, killsForVamp: 0,
    },

    zombies: [], bullets: [], enemyBullets: [], pickups: [],
    defenses: [], allies: [], orbitals: [],
    teslaArcs: [],
    placing: null, // { defId } during placement
    defensesInventory: {}, // id -> count owned but not yet placed

    wave: 0, waveActive: false, waveStartAt: 0,
    spawnedThisWave: 0, waveBudget: 0, waveTimer: 0,
    kills: 0, cash: 0,
    xp: 0, xpNeeded: 20, level: 1,

    unlockedGuns: { 0: true },
    currentGun: char.startGun ?? 0,
    ammo: {},
    lastShot: 0, windupT: 0,

    // perks stacking
    mult: {
      dmg: 1, fireRate: 1, moveSpd: 1, cash: 1, xp: 1,
      pickup: 1, dmgTaken: 1, pierce: 0, bounce: 0,
      regen: 0, dodge: 0, thorns: 0, lifesteal: 0,
      explodeRadius: 1, explosiveDmg: 1, ammoCap: 1,
      shotgunBonus: 0,
    },
    crit: { chance: 0.05, mult: 2 },
    status: { burnChance: 0, chainChance: 0 },
    flags: {},
    takenPerks: [],

    gameRunning: true, gameOver: false,
    shopOpen: false, levelUpOpen: false,
    freezeTimer: 0,
  };
  // ensure started gun is unlocked
  s.unlockedGuns[s.currentGun] = true;
  s.ammo[s.currentGun] = GUNS[s.currentGun].ammo;

  // apply character passive
  char.passive(s);

  return s;
}

function resize() {
  const r = stage.getBoundingClientRect();
  state.W = canvas.width = r.width;
  state.H = canvas.height = r.height;
  state.wallBoxes = computeWallBoxes(state);
  state.hazardBoxes = computeHazardBoxes(state);
}

// ===== WAVE MANAGEMENT =====
function startWave() {
  state.wave++;
  state.waveActive = true;
  state.spawnedThisWave = 0;
  state.waveTimer = 0;
  state.waveBudget = 6 + Math.floor(state.wave * 3.2);
  showWaveBanner(`WAVE ${state.wave}`);

  // Boss wave
  const boss = BOSSES.find(b => b.wave === state.wave);
  if (boss) {
    spawnBossAt(state, boss.id);
    state.waveBudget = 0;
  }

  // Boss Rush: every wave is a boss from the list (cycling + scaling)
  if (state.mode === "bossrush") {
    const bossIdx = (state.wave - 1) % BOSSES.length;
    const b = BOSSES[bossIdx];
    spawnBossAt(state, b.id);
    state.waveBudget = 0;
  }

  // Clear wave shield flag
  if (state.flags.waveShield) state.flags.waveShieldActive = true;
}

function endWave() {
  state.waveActive = false;
  const bonus = 30 + state.wave * 8;
  state.cash += Math.floor(bonus * state.mult.cash);
  toast(`+$${Math.floor(bonus * state.mult.cash)} Wave Clear`);
  // endless: shop only every 5 waves
  if (state.mode === "endless" && state.wave % 5 !== 0) {
    setTimeout(startWave, 1200);
    return;
  }
  openShop();
}

function spawnZombieAt(st, typeId, x, y) {
  const t = ZOMBIE_BY_ID[typeId];
  if (!t) return;
  const scale = 1 + (st.wave - 1) * 0.08;
  const z = {
    ...t, type: typeId,
    x, y, hp: t.hp * scale, maxHp: t.hp * scale,
    spd: t.spd * (1 + (st.wave - 1) * 0.02),
    hitFlash: 0,
    statuses: {}, // burn: {ttl, dmg}, freeze: {ttl}, shock: {ttl}
  };
  st.zombies.push(z);
  return z;
}

function spawnBossAt(st, bossId) {
  const side = Math.floor(Math.random() * 4);
  let x, y;
  if (side === 0) { x = st.W / 2; y = -60; }
  else if (side === 1) { x = st.W + 60; y = st.H / 2; }
  else if (side === 2) { x = st.W / 2; y = st.H + 60; }
  else { x = -60; y = st.H / 2; }
  const z = spawnZombieAt(st, bossId, x, y);
  if (z) z.isBoss = true;
  showWaveBanner(`☠ BOSS: ${ZOMBIE_BY_ID[bossId].emoji} ☠`);
}

function randomEdgeSpawn(st) {
  const side = Math.floor(Math.random() * 4);
  if (side === 0) return { x: Math.random() * st.W, y: -30 };
  if (side === 1) return { x: st.W + 30, y: Math.random() * st.H };
  if (side === 2) return { x: Math.random() * st.W, y: st.H + 30 };
  return { x: -30, y: Math.random() * st.H };
}

function spawnWaveZombie(st) {
  // choose type weighted by wave
  const avail = ZOMBIES.filter(z => z.firstWave <= st.wave);
  const t = avail[Math.floor(Math.random() * avail.length)];
  const { x, y } = randomEdgeSpawn(st);
  spawnZombieAt(st, t.id, x, y);
}

// ===== COMBAT =====
function damageZombie(st, z, dmg, hx, hy, opts = {}) {
  // armor reduces kinetic damage
  if (z.armor && opts.dmgType !== "fire" && opts.dmgType !== "plasma" && opts.dmgType !== "tesla") {
    dmg *= (1 - z.armor);
  }
  if (z.phasing) { dmg *= 0.15; } // ghost mostly phases
  z.hp -= dmg;
  z.hitFlash = 5;

  addPopup(hx, hy - 10, Math.round(dmg), opts.crit ? "#fca5a5" : "#fbbf24", opts.crit ? 20 : 14);
  bloodBurst(hx, hy, opts.crit ? 8 : 4);

  // status application
  if (opts.dmgType === "fire" || (st.status.burnChance > 0 && Math.random() < st.status.burnChance)) {
    z.statuses.burn = { ttl: 120, dmg: 3 };
  }
  if (opts.dmgType === "freeze") {
    z.statuses.freeze = { ttl: 90 };
  }
  if (st.status.chainChance > 0 && Math.random() < st.status.chainChance) {
    // small tesla chain
    let best = null, bestD = 140;
    for (const other of st.zombies) {
      if (other === z) continue;
      const d = dist(z, other);
      if (d < bestD) { bestD = d; best = other; }
    }
    if (best) damageZombie(st, best, dmg * 0.5, best.x, best.y, { dmgType: "tesla" });
  }

  // lifesteal
  if (st.mult.lifesteal > 0) {
    st.player.hp = Math.min(st.player.maxHp, st.player.hp + dmg * st.mult.lifesteal);
  }

  if (z.hp <= 0) onZombieDeath(st, z);
}

function onZombieDeath(st, z) {
  // skeleton rebuild once
  if (z.rebuild && !z.rebuilt) {
    z.rebuilt = true;
    z.hp = z.maxHp * 0.5;
    z.maxHp = z.hp;
    z.emoji = "☠️";
    bloodBurst(z.x, z.y, 6);
    return;
  }
  st.kills++;
  save.totalKills++;
  st.player.kills++;
  st.player.killsForVamp++;

  if (st.flags.vampPer3 && st.player.killsForVamp >= 3) {
    st.player.killsForVamp = 0;
    st.player.hp = Math.min(st.player.maxHp, st.player.hp + 1);
  }

  // cash & xp
  const cashGain = Math.floor(z.cash * st.mult.cash);
  const xpGain = Math.floor(z.xp * st.mult.xp);
  st.cash += cashGain;
  st.xp += xpGain;
  addPopup(z.x, z.y + 12, `+$${cashGain}`, "#22c55e", 12);
  if (st.xp >= st.xpNeeded) openLevelUp();

  gibBurst(z.x, z.y, z.emoji);

  // drop chance
  if (Math.random() < 0.06) st.pickups.push(mkPickup(z.x, z.y, "hp"));
  if (Math.random() < 0.04) st.pickups.push(mkPickup(z.x, z.y, "ammo"));
  if (Math.random() < 0.01) st.pickups.push(mkPickup(z.x, z.y, "cash"));

  if (z.isBoss) {
    st.cash += 200;
    addPopup(z.x, z.y, "BOSS DOWN", "#fbbf24", 22);
    addShake(15, 500);
  }

  // time-freeze flag: 20 kills triggers 2s freeze
  if (st.flags.timeFreeze && st.kills % 20 === 0) {
    st.freezeTimer = 2000;
  }

  save.highestWave = Math.max(save.highestWave, st.wave);
  if (st.kills % 25 === 0) writeSave(save);
  const newAchs = checkAchievements(save);
  newAchs.forEach(a => toast(`🏆 ${a.name} (+${a.reward}💀)`));
}

function mkPickup(x, y, type) {
  const conf = {
    hp:    { emoji: "❤️", life: 600 },
    ammo:  { emoji: "📦", life: 600 },
    cash:  { emoji: "💰", life: 600 },
  }[type];
  return { x, y, type, emoji: conf.emoji, life: conf.life };
}

function damagePlayer(st, dmg) {
  if (st.player.iframes > 0) return;
  if (st.mult.dodge > 0 && Math.random() < st.mult.dodge) {
    addPopup(st.player.x, st.player.y - 20, "DODGE", "#22c55e", 14);
    return;
  }
  if (st.flags.waveShieldActive) {
    st.flags.waveShieldActive = false;
    addPopup(st.player.x, st.player.y - 20, "SHIELD", "#38bdf8", 16);
    return;
  }
  dmg *= st.mult.dmgTaken;
  st.player.hp -= dmg;
  st.player.iframes = 20;
  document.getElementById("vignette").classList.add("hurt");
  setTimeout(() => document.getElementById("vignette").classList.remove("hurt"), 250);
  addShake(4, 200);
  if (st.player.hp <= 0) endRun();
}

// ===== SHOP =====
function openShop() {
  state.shopOpen = true;
  state.scene = SCENE.SHOP;
  renderShop();
  document.getElementById("shopModal").classList.remove("hidden");
}
function closeShop() {
  state.shopOpen = false;
  state.scene = SCENE.PLAYING;
  document.getElementById("shopModal").classList.add("hidden");
  startWave();
}

function closeShopForPlacement() {
  // Hide shop; player places defense; reopen after placing
  document.getElementById("shopModal").classList.add("hidden");
  state.scene = SCENE.PLAYING;
  state.shopOpen = false;
  state._shopReopenAfterPlace = true;
}

function renderShop() {
  const list = document.getElementById("shopItems");
  list.innerHTML = "";
  // Weapons
  const section = (title) => {
    const h = document.createElement("div");
    h.className = "shop-section-label";
    h.textContent = title;
    list.appendChild(h);
  };
  section("🔫 WEAPONS");
  for (const g of GUNS) {
    const owned = state.unlockedGuns[g.id];
    const card = document.createElement("div");
    card.className = "shop-item" + (owned ? " owned" : "");
    card.style.setProperty("--rar", TIER_COLOR[g.tier]);
    card.innerHTML = `
      <div class="si-emoji">${g.emoji}</div>
      <div class="si-info">
        <div class="si-name">${g.name} <span class="si-tier" style="color:${TIER_COLOR[g.tier]}">${g.tier}</span></div>
        <div class="si-stats">DMG ${g.dmg} · RoF ${Math.round(60000/g.fireRate)}/min · ${isFinite(g.ammo)?`Ammo ${g.ammo}`:"∞"} · ${g.dmgType}</div>
      </div>
      <button class="si-buy">${owned ? "OWNED" : "$" + g.cost}</button>
    `;
    const buyBtn = card.querySelector(".si-buy");
    if (!owned) {
      buyBtn.onclick = () => {
        if (state.cash >= g.cost) {
          state.cash -= g.cost;
          state.unlockedGuns[g.id] = true;
          state.ammo[g.id] = g.ammo;
          state.currentGun = g.id;
          updateHUD();
          renderShop();
          toast(`Bought ${g.name}!`);
        } else toast("Not enough cash");
      };
    } else {
      buyBtn.disabled = true;
    }
    list.appendChild(card);
  }
  section("🛡️ DEFENSES (click, then click on map to place)");
  for (const d of DEFENSES) {
    const card = document.createElement("div");
    card.className = "shop-item";
    card.innerHTML = `
      <div class="si-emoji">${d.emoji}</div>
      <div class="si-info">
        <div class="si-name">${d.name}</div>
        <div class="si-stats">${d.desc}</div>
      </div>
      <button class="si-buy">$${d.cost}</button>
    `;
    card.querySelector(".si-buy").onclick = () => {
      if (state.cash >= d.cost) {
        state.cash -= d.cost;
        state.placing = { defId: d.id };
        closeShopForPlacement();
        toast(`Placing ${d.name} — click a spot`);
        updateHUD();
      } else toast("Not enough cash");
    };
    list.appendChild(card);
  }
  section("🩹 CONSUMABLES");
  const refills = [
    { name: "Full Heal", emoji: "❤️", cost: 60, fn: () => state.player.hp = state.player.maxHp },
    { name: "Refill All Ammo", emoji: "📦", cost: 80, fn: () => { for (const g of GUNS) if (isFinite(g.ammo)) state.ammo[g.id] = Math.floor(g.ammo * state.mult.ammoCap); } },
    { name: "+20 Max HP", emoji: "🛡️", cost: 120, fn: () => { state.player.maxHp += 20; state.player.hp += 20; } },
  ];
  for (const r of refills) {
    const card = document.createElement("div");
    card.className = "shop-item";
    card.innerHTML = `
      <div class="si-emoji">${r.emoji}</div>
      <div class="si-info"><div class="si-name">${r.name}</div></div>
      <button class="si-buy">$${r.cost}</button>
    `;
    card.querySelector(".si-buy").onclick = () => {
      if (state.cash >= r.cost) { state.cash -= r.cost; r.fn(); updateHUD(); toast(r.name); }
      else toast("Not enough cash");
    };
    list.appendChild(card);
  }
  document.getElementById("shopCash").textContent = `$${state.cash}`;
  document.getElementById("shopWaveNext").textContent = `Next: Wave ${state.wave + 1}`;
}

// ===== LEVEL UP =====
function openLevelUp() {
  state.level++;
  state.xp -= state.xpNeeded;
  state.xpNeeded = Math.floor(state.xpNeeded * 1.45 + 10);
  state.levelUpOpen = true;
  state.scene = SCENE.LEVELUP;
  const draft = draftPerks(state, 3);
  const modal = document.getElementById("levelupModal");
  const cards = document.getElementById("perkCards");
  cards.innerHTML = "";
  document.getElementById("levelupHead").textContent = `Level ${state.level}! Choose a Perk`;
  draft.forEach(p => {
    const el = document.createElement("div");
    el.className = "perk-card";
    el.style.setProperty("--rar", TIER_COLOR[p.rarity] || "#8b5cf6");
    el.innerHTML = `
      <div class="p-rarity">${p.rarity}</div>
      <div class="p-emoji">${p.emoji}</div>
      <div class="p-name">${p.name}</div>
      <div class="p-desc">${p.desc}</div>
    `;
    el.onclick = () => {
      p.apply(state);
      state.takenPerks.push(p.id);
      toast(`${p.emoji} ${p.name}`);
      closeLevelUp();
    };
    cards.appendChild(el);
  });
  modal.classList.remove("hidden");
}
function closeLevelUp() {
  state.levelUpOpen = false;
  state.scene = SCENE.PLAYING;
  document.getElementById("levelupModal").classList.add("hidden");
  // check if queued another level-up
  if (state.xp >= state.xpNeeded) setTimeout(openLevelUp, 300);
  updateHUD();
}

// ===== PLAYER =====
function clampPlayer(st) {
  st.player.x = Math.max(20, Math.min(st.W - 20, st.player.x));
  st.player.y = Math.max(20, Math.min(st.H - 20, st.player.y));
  if (st.wallBoxes) resolveWallCollision(st.player, st.player.r, st.wallBoxes);
}

function updatePlayer(st, dt) {
  if (st.player.iframes > 0) st.player.iframes--;
  if (st.player.cursed > 0) st.player.cursed--;
  // Lava hazard damage
  if (st.hazardBoxes) {
    for (const h of st.hazardBoxes) {
      if (st.player.x > h.x && st.player.x < h.x + h.w &&
          st.player.y > h.y && st.player.y < h.y + h.h) {
        st.player.hp -= h.dps * dt / 1000;
      }
    }
  }

  let dx = 0, dy = 0;
  if (Input.keys["w"] || Input.keys["arrowup"]) dy -= 1;
  if (Input.keys["s"] || Input.keys["arrowdown"]) dy += 1;
  if (Input.keys["a"] || Input.keys["arrowleft"]) dx -= 1;
  if (Input.keys["d"] || Input.keys["arrowright"]) dx += 1;
  if (dx || dy) {
    const len = Math.hypot(dx, dy);
    const s = st.player.spd * st.mult.moveSpd;
    st.player.x += (dx / len) * s;
    st.player.y += (dy / len) * s;
    clampPlayer(st);
  }

  st.player.facing = Math.atan2(Input.mouse.y - st.player.y, Input.mouse.x - st.player.x);

  // regen
  if (st.mult.regen > 0) {
    st.player.hp = Math.min(st.player.maxHp, st.player.hp + st.mult.regen * dt / 1000);
  }

  // gun switch
  for (const g of GUNS) {
    if (Input.keys[g.key] && st.unlockedGuns[g.id] && st.currentGun !== g.id) {
      st.currentGun = g.id;
      st.windupT = 0;
      updateHUD();
    }
  }
  if (consumeJustPressed("r")) {
    const g = GUNS[st.currentGun];
    if (isFinite(g.ammo)) { st.ammo[g.id] = Math.floor(g.ammo * st.mult.ammoCap); updateHUD(); }
  }

  // placement mode: click places, doesn't fire
  if (st.placing) {
    if (Input.mouse.clicked) {
      placeDefense(st, st.placing.defId, Input.mouse.x, Input.mouse.y);
      toast(`Placed ${DEF_BY_ID[st.placing.defId].name}`);
      st.placing = null;
      if (st._shopReopenAfterPlace) {
        st._shopReopenAfterPlace = false;
        openShop();
      }
    }
  } else if (Input.mouse.down || Input.keys[" "]) {
    fireWeapon(st, performance.now());
  } else {
    st.windupT = Math.max(0, st.windupT - 50);
  }

  // orbitals
  if (st.flags.orbitSkulls) {
    st.orbitalPhase = (st.orbitalPhase || 0) + dt * 0.004;
    if (!st.orbitals.length) {
      for (let i = 0; i < st.flags.orbitSkulls; i++) st.orbitals.push({ off: (i / st.flags.orbitSkulls) * Math.PI * 2 });
    }
    while (st.orbitals.length < st.flags.orbitSkulls) st.orbitals.push({ off: Math.random() * Math.PI * 2 });
    for (const o of st.orbitals) {
      const a = st.orbitalPhase + o.off;
      o.x = st.player.x + Math.cos(a) * 60;
      o.y = st.player.y + Math.sin(a) * 60;
      for (const z of st.zombies) {
        if (Math.hypot(z.x - o.x, z.y - o.y) < 20 + z.size / 2) {
          damageZombie(st, z, 5, z.x, z.y);
        }
      }
    }
  }

  // frost aura
  if (st.flags.frostAura) {
    for (const z of st.zombies) {
      if (dist(st.player, z) < 90) z.statuses.freeze = { ttl: 20 };
    }
  }
}

function updateBullets(st, dt) {
  for (const b of st.bullets) {
    const px = b.x, py = b.y;
    b.x += b.vx; b.y += b.vy; b.life--;
    // wall hit: bullets stop (except explosive which detonates on wall)
    if (st.wallBoxes && b.life > 0) {
      const hit = bulletHitsWall(px, py, b.x, b.y, st.wallBoxes);
      if (hit) {
        if (b.explode) doExplosion(st, b.x, b.y, b.explode, b.dmg);
        for (let i = 0; i < 4; i++) addParticle(b.x, b.y, { color: b.color, size: 2, life: 10 });
        b.life = 0;
        continue;
      }
    }
    // split
    if (b.canSplit && b.life <= b.splitAtLife && !b.split) {
      b.split = true;
      const ang = Math.atan2(b.vy, b.vx);
      for (let k = 0; k < 2; k++) {
        const a = ang + (k === 0 ? 0.3 : -0.3);
        st.bullets.push({
          ...b, x: b.x, y: b.y,
          vx: Math.cos(a) * Math.hypot(b.vx, b.vy),
          vy: Math.sin(a) * Math.hypot(b.vx, b.vy),
          canSplit: false, life: 30, dmg: b.dmg * 0.6, hit: new Set(),
        });
      }
    }

    for (const z of st.zombies) {
      if (b.hit.has(z)) continue;
      if (z.phasing) continue;
      if (Math.hypot(z.x - b.x, z.y - b.y) < z.size / 2) {
        if (b.explode) {
          doExplosion(st, b.x, b.y, b.explode, b.dmg);
          b.life = 0; break;
        }
        damageZombie(st, z, b.dmg, b.x, b.y, { crit: b.critical, dmgType: b.dmgType });
        b.hit.add(z);
        if (b.explosiveRounds) doExplosion(st, b.x, b.y, 40, b.dmg * 0.4);
        if (b.randomEffect) {
          const r = Math.random();
          if (r < 0.3) z.statuses.burn = { ttl: 120, dmg: 3 };
          else if (r < 0.6) z.statuses.freeze = { ttl: 90 };
          else doExplosion(st, b.x, b.y, 30, b.dmg * 0.3);
        }
        if (b.pierce > 0) b.pierce--;
        else if (b.bounce > 0) {
          b.bounce--;
          // bounce to another zombie
          let next = null, nd = 220;
          for (const z2 of st.zombies) {
            if (b.hit.has(z2)) continue;
            const d = Math.hypot(z2.x - b.x, z2.y - b.y);
            if (d < nd) { nd = d; next = z2; }
          }
          if (next) {
            const a = Math.atan2(next.y - b.y, next.x - b.x);
            const sp = Math.hypot(b.vx, b.vy);
            b.vx = Math.cos(a) * sp; b.vy = Math.sin(a) * sp;
            b.life = Math.max(b.life, 40);
          } else b.life = 0;
        }
        else { b.life = 0; break; }
      }
    }
    if (b.x < 0 || b.x > st.W || b.y < 0 || b.y > st.H) b.life = 0;
  }
  st.bullets = st.bullets.filter(b => b.life > 0);

  // enemy bullets
  for (const b of st.enemyBullets) {
    b.x += b.vx; b.y += b.vy; b.life--;
    if (Math.hypot(b.x - st.player.x, b.y - st.player.y) < st.player.r) {
      damagePlayer(st, b.dmg);
      b.life = 0;
    }
  }
  st.enemyBullets = st.enemyBullets.filter(b => b.life > 0);
}

function doExplosion(st, x, y, radius, dmg) {
  explosionFx(x, y, radius);
  addShake(10, 300);
  for (const z of st.zombies) {
    const d = Math.hypot(z.x - x, z.y - y);
    if (d < radius) damageZombie(st, z, dmg * (1 - d / radius), z.x, z.y, { dmgType: "explosive" });
  }
  const pd = Math.hypot(st.player.x - x, st.player.y - y);
  if (pd < radius * 0.5) damagePlayer(st, 15);
}

function updateZombies(st, dt) {
  for (const z of st.zombies) {
    if (z.hitFlash > 0) z.hitFlash--;
    const preX = z.x, preY = z.y;
    // statuses
    if (z.statuses.freeze) {
      z.statuses.freeze.ttl -= dt * 0.06;
      if (z.statuses.freeze.ttl <= 0) delete z.statuses.freeze;
    }
    if (z.statuses.burn) {
      z.statuses.burn.ttl -= dt * 0.06;
      z.hp -= z.statuses.burn.dmg * dt / 1000;
      if (Math.random() < 0.2) addParticle(z.x + (Math.random()-0.5)*10, z.y + (Math.random()-0.5)*10, { color: "#f97316", size: 2.5, life: 10 });
      if (z.statuses.burn.ttl <= 0) delete z.statuses.burn;
      if (z.hp <= 0) { onZombieDeath(st, z); continue; }
    }
    if (z.statuses.freeze) continue; // frozen: skip AI
    const fn = AI[z.ai];
    if (fn) fn(z, dt, st);
    // Wall collision (ghosts phase through)
    if (st.wallBoxes && !z.phasing && z.ai !== "swarm" && z.ai !== "phase") {
      resolveWallCollision(z, z.size / 2, st.wallBoxes);
    }
    // touch damage
    if (dist(z, st.player) < st.player.r + z.size / 3) {
      damagePlayer(st, z.dmg * dt / 600);
      if (z.lifesteal) z.hp = Math.min(z.maxHp, z.hp + z.dmg * z.lifesteal * dt / 600);
    }
    // thorns
    if (st.mult.thorns > 0 && dist(z, st.player) < st.player.r + z.size / 3) {
      z.hp -= st.mult.thorns * dt / 600;
      if (z.hp <= 0) { onZombieDeath(st, z); }
    }
  }
  st.zombies = st.zombies.filter(z => z.hp > 0);
}

function updatePickups(st, dt) {
  const pr = 28 * st.mult.pickup;
  for (const p of st.pickups) {
    p.life--;
    const d = Math.hypot(p.x - st.player.x, p.y - st.player.y);
    if (d < pr + 20) {
      // magnet
      const a = Math.atan2(st.player.y - p.y, st.player.x - p.x);
      p.x += Math.cos(a) * 2.5; p.y += Math.sin(a) * 2.5;
    }
    if (d < st.player.r + 14 && st.player.cursed <= 0) {
      if (p.type === "hp") {
        const heal = st.flags.medic ? 60 : 30;
        st.player.hp = Math.min(st.player.maxHp, st.player.hp + heal);
        addPopup(p.x, p.y, `+${heal}`, "#22c55e", 14);
      } else if (p.type === "ammo") {
        for (const g of GUNS) if (isFinite(g.ammo)) st.ammo[g.id] = Math.min(Math.floor(g.ammo*st.mult.ammoCap), (st.ammo[g.id]||0) + Math.floor(g.ammo * 0.3));
        addPopup(p.x, p.y, "+AMMO", "#fbbf24", 14);
      } else if (p.type === "cash") {
        const c = 50;
        st.cash += c;
        addPopup(p.x, p.y, `+$${c}`, "#22c55e", 14);
      }
      p.life = 0;
      updateHUD();
    }
  }
  st.pickups = st.pickups.filter(p => p.life > 0);
}

function updateWave(st, dt) {
  if (!st.waveActive) return;
  st.waveTimer += dt;
  if (st.spawnedThisWave < st.waveBudget) {
    const interval = Math.max(180, 900 - st.wave * 25);
    if (st.waveTimer > interval) {
      spawnWaveZombie(st);
      st.spawnedThisWave++;
      st.waveTimer = 0;
    }
  } else if (st.zombies.length === 0) {
    endWave();
  }
}

// ===== DRAW =====
function drawMap(st) {
  const m = st.map;
  ctx.fillStyle = m.floorTint;
  ctx.fillRect(0, 0, st.W, st.H);
  // decor scatter (seeded static pattern)
  if (!st._decor) {
    st._decor = [];
    for (let i = 0; i < 30; i++) {
      st._decor.push({
        x: (Math.sin(i * 12.9898) * 43758.5453 % 1 + 1) % 1 * st.W,
        y: (Math.cos(i * 78.233) * 43758.5453 % 1 + 1) % 1 * st.H,
        e: m.decor[i % m.decor.length],
      });
    }
  }
  ctx.font = "16px serif"; ctx.globalAlpha = 0.22;
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  for (const d of st._decor) ctx.fillText(d.e, d.x, d.y);
  ctx.globalAlpha = 1;
  // walls (solid + emoji overlay for flavor)
  for (const wb of (st.wallBoxes || [])) {
    // base block
    ctx.fillStyle = "#2a1f18";
    ctx.strokeStyle = "#5c4a3e";
    ctx.fillRect(wb.x, wb.y, wb.w, wb.h);
    ctx.lineWidth = 1;
    ctx.strokeRect(wb.x, wb.y, wb.w, wb.h);
    // emoji decal
    const emoji = wb.emoji || m.wallEmoji || "🧱";
    const fs = Math.min(wb.w, wb.h) * 0.9;
    if (fs > 8) {
      ctx.font = `${fs}px serif`;
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillText(emoji, wb.x + wb.w / 2, wb.y + wb.h / 2);
    }
  }
  // hazards (lava) with pulsing glow
  for (const h of (st.hazardBoxes || [])) {
    const pulse = 0.55 + Math.sin(Date.now() * 0.004) * 0.15;
    ctx.fillStyle = `rgba(220,60,20,${pulse})`;
    ctx.fillRect(h.x, h.y, h.w, h.h);
    ctx.fillStyle = "rgba(255,180,50,0.5)";
    ctx.fillRect(h.x + 4, h.y + 4, h.w - 8, h.h - 8);
  }
  // flicker effect (hospital)
  if (m.flicker && Math.random() < 0.02) {
    ctx.fillStyle = "rgba(0,0,0,0.5)";
    ctx.fillRect(0, 0, st.W, st.H);
  }
}

function drawZombie(st, z) {
  ctx.font = `${z.size}px serif`;
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.globalAlpha = z.phasing ? 0.35 : 1;
  if (z.hitFlash > 0) { ctx.shadowColor = "#fff"; ctx.shadowBlur = 14; }
  if (z.statuses.freeze) { ctx.shadowColor = "#7dd3fc"; ctx.shadowBlur = 18; }
  if (z.statuses.burn) { ctx.shadowColor = "#f97316"; ctx.shadowBlur = 12; }
  if (z.screaming) { ctx.shadowColor = "#ec4899"; ctx.shadowBlur = 20; }
  ctx.fillText(z.emoji, z.x, z.y);
  ctx.shadowBlur = 0; ctx.globalAlpha = 1;
  // HP bar
  const bw = Math.max(24, z.size);
  const hpFrac = Math.max(0, z.hp / z.maxHp);
  ctx.fillStyle = "#2a0707";
  ctx.fillRect(z.x - bw / 2, z.y - z.size / 2 - 9, bw, 4);
  ctx.fillStyle = hpFrac > 0.5 ? "#22c55e" : hpFrac > 0.25 ? "#fbbf24" : "#dc2626";
  ctx.fillRect(z.x - bw / 2, z.y - z.size / 2 - 9, bw * hpFrac, 4);
  if (z.isBoss) {
    ctx.strokeStyle = "#fbbf24"; ctx.lineWidth = 1.5;
    ctx.strokeRect(z.x - bw / 2, z.y - z.size / 2 - 9, bw, 4);
  }
}

function drawBullet(st, b) {
  ctx.fillStyle = b.color;
  ctx.shadowColor = b.color; ctx.shadowBlur = 8;
  ctx.beginPath();
  ctx.arc(b.x, b.y, b.size || 3, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;
}

function drawEnemyBullet(st, b) {
  ctx.font = "18px serif";
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.fillText(b.emoji, b.x, b.y);
}

function drawPlayer(st) {
  const p = st.player;
  ctx.save();
  ctx.translate(p.x, p.y);
  // gun line
  const g = GUNS[st.currentGun];
  ctx.strokeStyle = g.flashColor;
  ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(0, 0);
  ctx.lineTo(Math.cos(p.facing) * 24, Math.sin(p.facing) * 24);
  ctx.stroke();
  ctx.restore();
  ctx.font = "32px serif";
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  if (p.iframes > 0 && p.iframes % 4 < 2) ctx.globalAlpha = 0.5;
  ctx.fillText(p.emoji, p.x, p.y);
  ctx.globalAlpha = 1;
  ctx.font = "16px serif";
  ctx.fillText(g.emoji, p.x + Math.cos(p.facing) * 28, p.y + Math.sin(p.facing) * 28);

  // orbitals
  if (st.flags.orbitSkulls) {
    ctx.font = "18px serif";
    for (const o of st.orbitals) ctx.fillText("💀", o.x, o.y);
  }
}

function drawTeslaArcs(st) {
  if (!st.teslaArcs) return;
  for (const a of st.teslaArcs) {
    ctx.strokeStyle = "#c084fc";
    ctx.shadowColor = "#c084fc"; ctx.shadowBlur = 10;
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let i = 0; i < a.points.length - 1; i++) {
      const p1 = a.points[i], p2 = a.points[i + 1];
      ctx.moveTo(p1.x, p1.y);
      // jagged lightning
      const steps = 6;
      for (let s = 1; s <= steps; s++) {
        const t = s / steps;
        const mx = p1.x + (p2.x - p1.x) * t + (Math.random() - 0.5) * 10;
        const my = p1.y + (p2.y - p1.y) * t + (Math.random() - 0.5) * 10;
        ctx.lineTo(mx, my);
      }
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
    a.life--;
  }
  st.teslaArcs = st.teslaArcs.filter(a => a.life > 0);
}

function drawPickups(st) {
  for (const p of st.pickups) {
    ctx.font = "22px serif";
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.globalAlpha = p.life < 60 ? p.life / 60 : 1;
    ctx.fillText(p.emoji, p.x, p.y + Math.sin(Date.now() * 0.005 + p.x) * 2);
    ctx.globalAlpha = 1;
  }
}

function drawDarkness(st) {
  const m = st.map;
  // Wave-based tension tint: redder/darker as waves rise
  const tension = Math.min(0.35, st.wave * 0.015);
  if (tension > 0) {
    ctx.fillStyle = `rgba(40,0,0,${tension})`;
    ctx.fillRect(0, 0, st.W, st.H);
  }
  if (!m.darkness) return;
  const grd = ctx.createRadialGradient(st.player.x, st.player.y, 60, st.player.x, st.player.y, 340);
  grd.addColorStop(0, `rgba(0,0,0,0)`);
  grd.addColorStop(1, `rgba(0,0,0,${m.darkness})`);
  ctx.fillStyle = grd;
  ctx.fillRect(0, 0, st.W, st.H);
}

function render() {
  ctx.clearRect(0, 0, state.W, state.H);
  drawMap(state);
  drawPickups(state);
  drawFx(ctx);
  drawDefenses(state);
  for (const z of state.zombies) drawZombie(state, z);
  for (const b of state.bullets) drawBullet(state, b);
  for (const b of state.enemyBullets) drawEnemyBullet(state, b);
  drawTeslaArcs(state);
  drawPlayer(state);
  drawDarkness(state);
}

// ===== HUD =====
function updateHUD() {
  document.getElementById("hp").textContent = Math.max(0, Math.round(state.player.hp));
  document.getElementById("hpMax").textContent = Math.round(state.player.maxHp);
  document.getElementById("hpFill").style.width = Math.max(0, state.player.hp / state.player.maxHp * 100) + "%";
  document.getElementById("kills").textContent = state.kills;
  document.getElementById("cash").textContent = state.cash;
  document.getElementById("wave").textContent = state.wave;
  document.getElementById("level").textContent = state.level;
  document.getElementById("xpFill").style.width = state.xp / state.xpNeeded * 100 + "%";
  document.getElementById("xpBar").setAttribute("data-label", `${state.xp}/${state.xpNeeded} XP`);
  const g = GUNS[state.currentGun];
  const ammoTxt = isFinite(g.ammo) ? `${state.ammo[g.id] ?? 0}/${Math.floor(g.ammo*state.mult.ammoCap)}` : "∞";
  document.getElementById("ammo").textContent = ammoTxt;
  document.getElementById("gunName").textContent = `${g.emoji} ${g.name}`;
  const list = document.getElementById("gunList");
  list.innerHTML = "";
  for (const g2 of GUNS) {
    if (!state.unlockedGuns[g2.id]) continue;
    const el = document.createElement("div");
    el.className = "gun-chip" + (state.currentGun === g2.id ? " active" : "");
    el.textContent = `${g2.key}:${g2.emoji}`;
    list.appendChild(el);
  }
  // low-hp vignette
  const v = document.getElementById("vignette");
  if (state.player.hp / state.player.maxHp < 0.3) v.classList.add("low-hp");
  else v.classList.remove("low-hp");
}

// ===== LOOP =====
let lastT = 0;
function loop(t) {
  let dt = Math.min(40, t - lastT);
  lastT = t;

  if (state && state.scene === SCENE.PLAYING) {
    // freeze or slow effects
    let timeScale = 1;
    if (state.freezeTimer > 0) { state.freezeTimer -= dt; timeScale = 0; }
    if (state.flags.slowNearDeath && state.player.hp / state.player.maxHp < 0.25) timeScale = 0.5;
    const edt = dt * timeScale;
    updatePlayer(state, edt);
    updateWave(state, edt);
    updateBullets(state, edt);
    updateZombies(state, edt);
    updatePickups(state, edt);
    updateDefenses(state, edt);
    updateFx(edt);
    updateHUD();
  } else if (state) {
    updateFx(dt);
  }

  if (state) render();
  applyShakeToStage(stage, dt);
  resetFrameInput();
  requestAnimationFrame(loop);
}

// ===== FLOW =====
function endRun() {
  state.gameRunning = false;
  state.gameOver = true;
  state.scene = SCENE.GAMEOVER;
  save.totalRuns++;
  let earned = Math.floor(state.wave * 2 + state.kills / 10);
  if (state.mode === "nightmare") earned = Math.floor(earned * 2.5);
  if (state.mode === "bossrush") earned = Math.floor(earned * 1.5);
  awardSkulls(save, earned);
  document.getElementById("finalStats").textContent =
    `Wave ${state.wave} · ${state.kills} kills · +${earned} 💀 earned`;
  document.getElementById("gameOver").classList.remove("hidden");
}

function startRun(charId = "survivor", mapId = "graveyard", mode = "classic") {
  state = newState({ charId, mapId, mode });
  if (mode === "nightmare") state.mult.dmgTaken *= 3;
  resize();
  state.player.x = state.W / 2; state.player.y = state.H / 2;
  document.getElementById("startScreen").classList.add("hidden");
  document.getElementById("gameOver").classList.add("hidden");
  startWave();
  updateHUD();
}

// ===== MENUS =====
function renderMenu() {
  const charPick = document.getElementById("charPick");
  charPick.innerHTML = "";
  for (const c of CHARACTERS) {
    const unlocked = isUnlocked(save, c.id);
    const el = document.createElement("div");
    el.className = "char-card" + (unlocked ? "" : " locked");
    el.innerHTML = `
      <div class="cc-emoji">${c.emoji}</div>
      <div class="cc-name">${c.name}</div>
      <div class="cc-desc">${c.desc}</div>
      ${unlocked ? "" : `<div class="cc-cost">💀 ${c.unlockCost}</div>`}
    `;
    el.onclick = () => {
      if (!unlocked) {
        const r = tryUnlockCharacter(save, c.id);
        if (r.ok) { toast(`Unlocked ${c.name}!`); renderMenu(); }
        else if (r.reason === "cost") toast(`Need ${c.unlockCost}💀`);
        return;
      }
      document.querySelectorAll(".char-card").forEach(e => e.classList.remove("selected"));
      el.classList.add("selected");
      state_menu.charId = c.id;
    };
    if (state_menu.charId === c.id) el.classList.add("selected");
    charPick.appendChild(el);
  }
  const mapPick = document.getElementById("mapPick");
  mapPick.innerHTML = "";
  for (const m of MAPS) {
    const el = document.createElement("div");
    el.className = "map-card";
    el.innerHTML = `<div class="mc-emoji">${m.emoji}</div><div class="mc-name">${m.name}</div><div class="mc-amb">${m.ambient}</div>`;
    el.onclick = () => {
      document.querySelectorAll(".map-card").forEach(e => e.classList.remove("selected"));
      el.classList.add("selected");
      state_menu.mapId = m.id;
    };
    if (state_menu.mapId === m.id) el.classList.add("selected");
    mapPick.appendChild(el);
  }
  const modePick = document.getElementById("modePick");
  modePick.innerHTML = "";
  for (const m of MODES) {
    const el = document.createElement("div");
    el.className = "map-card";
    el.innerHTML = `<div class="mc-emoji">${m.emoji}</div><div class="mc-name">${m.name}</div><div class="mc-amb">${m.desc}</div>`;
    el.onclick = () => {
      document.querySelectorAll("#modePick .map-card").forEach(e => e.classList.remove("selected"));
      el.classList.add("selected");
      state_menu.mode = m.id;
    };
    if (state_menu.mode === m.id) el.classList.add("selected");
    modePick.appendChild(el);
  }

  document.getElementById("skullBal").textContent = save.skulls;
  document.getElementById("bestWave").textContent = save.highestWave;
  document.getElementById("totKills").textContent = save.totalKills;
}

const MODES = [
  { id: "classic",   name: "Classic",    emoji: "🌊", desc: "Waves + shop between" },
  { id: "endless",   name: "Endless",    emoji: "♾️", desc: "No breaks. Shop every 5 waves only." },
  { id: "bossrush",  name: "Boss Rush",  emoji: "👑", desc: "Only bosses, back-to-back" },
  { id: "nightmare", name: "Nightmare",  emoji: "💀", desc: "3× damage taken. High skulls reward." },
];

const state_menu = { charId: "survivor", mapId: "graveyard", mode: "classic" };

// ===== INIT =====
window.addEventListener("load", () => {
  canvas = document.getElementById("canvas");
  ctx = canvas.getContext("2d");
  stage = document.getElementById("stage");
  initInput(stage);

  document.getElementById("startBtn").onclick = () => startRun(state_menu.charId, state_menu.mapId, state_menu.mode);
  document.getElementById("restartBtn").onclick = () => {
    document.getElementById("gameOver").classList.add("hidden");
    document.getElementById("startScreen").classList.remove("hidden");
    renderMenu();
  };
  document.getElementById("shopReady").onclick = closeShop;
  document.getElementById("pauseBtn").onclick = () => {
    if (!state) return;
    if (state.scene === SCENE.PLAYING) { state.scene = SCENE.PAUSED; document.getElementById("pauseOverlay").classList.remove("hidden"); }
    else if (state.scene === SCENE.PAUSED) { state.scene = SCENE.PLAYING; document.getElementById("pauseOverlay").classList.add("hidden"); }
  };
  const shakeEl = document.getElementById("setShake");
  if (shakeEl) {
    shakeEl.checked = save.settings.screenShake !== false;
    shakeEl.onchange = () => {
      save.settings.screenShake = shakeEl.checked;
      writeSave(save);
    };
  }
  document.getElementById("pauseResume").onclick = () => {
    state.scene = SCENE.PLAYING;
    document.getElementById("pauseOverlay").classList.add("hidden");
  };
  document.getElementById("pauseQuit").onclick = () => {
    document.getElementById("pauseOverlay").classList.add("hidden");
    state = null;
    document.getElementById("startScreen").classList.remove("hidden");
    renderMenu();
  };

  window.addEventListener("resize", () => { if (state) resize(); });
  window.addEventListener("keydown", e => {
    if (e.key === "Escape" && state && state.scene === SCENE.PLAYING) {
      document.getElementById("pauseBtn").click();
    }
    if (e.key === "b" || e.key === "B") {
      if (state && state.scene === SCENE.SHOP) return;
      // do nothing; shop auto-opens between waves
    }
  });

  renderMenu();
  requestAnimationFrame(loop);
});
