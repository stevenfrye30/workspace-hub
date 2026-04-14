// Zombie AI behaviors. Each ai id maps to an update fn.
// Signature: updateZombie(z, dt, state)  -> mutates z, may push projectiles etc.

const AI = {
  chase(z, dt, st) {
    moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
  },

  swarm(z, dt, st) {
    // oscillate slightly to look bat-like
    z.phase = (z.phase || 0) + dt * 0.01;
    const ox = Math.cos(z.phase) * 14;
    const oy = Math.sin(z.phase * 1.3) * 8;
    moveToward(z, st.player.x + ox, st.player.y + oy, z.spd * dt * 0.06);
  },

  phase(z, dt, st) {
    z.phaseTimer = (z.phaseTimer || 0) + dt;
    z.phasing = (z.phaseTimer % 2200) < 600;
    moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
  },

  ranged(z, dt, st) {
    const d = dist(z, st.player);
    const desired = 180;
    if (d > desired + 40) moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    else if (d < desired - 40) moveToward(z, st.player.x, st.player.y, -z.spd * dt * 0.06);
    z.rangedCd = (z.rangedCd || 0) - dt;
    if (z.rangedCd <= 0 && d < z.projRange) {
      z.rangedCd = z.reload;
      const ang = Math.atan2(st.player.y - z.y, st.player.x - z.x);
      st.enemyBullets.push({
        x: z.x, y: z.y,
        vx: Math.cos(ang) * z.projSpd, vy: Math.sin(ang) * z.projSpd,
        dmg: z.projDmg, life: 180, color: "#22c55e", emoji: "🟢",
      });
    }
  },

  screamer(z, dt, st) {
    moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    z.summonCd = (z.summonCd || z.summonEvery) - dt;
    if (z.summonCd <= 0) {
      z.summonCd = z.summonEvery;
      z.screaming = 20;
      for (let i = 0; i < z.summonCount; i++) {
        const a = Math.random() * Math.PI * 2;
        spawnZombieAt(st, "walker", z.x + Math.cos(a) * 30, z.y + Math.sin(a) * 30);
      }
    }
    if (z.screaming) z.screaming--;
  },

  exploder(z, dt, st) {
    moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    if (dist(z, st.player) < z.explodeRadius * 0.7) {
      detonateExploder(z, st);
      z.hp = 0;
    }
  },

  necro(z, dt, st) {
    const d = dist(z, st.player);
    if (d > 160) moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    z.reviveCd = (z.reviveCd || z.reviveEvery) - dt;
    if (z.reviveCd <= 0) {
      z.reviveCd = z.reviveEvery;
      for (let i = 0; i < 2; i++) {
        const a = Math.random() * Math.PI * 2;
        spawnZombieAt(st, "walker", z.x + Math.cos(a) * 40, z.y + Math.sin(a) * 40);
      }
    }
  },

  curser(z, dt, st) {
    moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    z.curseCd = (z.curseCd || z.curseEvery) - dt;
    if (z.curseCd <= 0 && dist(z, st.player) < 300) {
      z.curseCd = z.curseEvery;
      st.player.cursed = 180; // frames of no pickups
      toast("🔮 Cursed! No pickups for 3s");
    }
  },

  leaper(z, dt, st) {
    z.leapCd = (z.leapCd || z.leapCooldown) - dt;
    if (z.leaping) {
      z.x += z.leapVx; z.y += z.leapVy;
      z.leaping -= dt;
      if (z.leaping <= 0) { z.leapVx = 0; z.leapVy = 0; }
    } else {
      moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
      if (z.leapCd <= 0 && dist(z, st.player) < z.leapDist) {
        z.leapCd = z.leapCooldown;
        z.leaping = 300;
        const a = Math.atan2(st.player.y - z.y, st.player.x - z.x);
        z.leapVx = Math.cos(a) * 6;
        z.leapVy = Math.sin(a) * 6;
      }
    }
  },

  aura(z, dt, st) {
    moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    if (dist(z, st.player) < z.auraRadius) {
      st.player.hp -= z.auraDmg * dt / 1000;
    }
  },

  pack(z, dt, st) {
    // slight flock offset among dogs
    z.packPhase = (z.packPhase || Math.random() * 10) + dt * 0.005;
    const ox = Math.cos(z.packPhase) * 24;
    const oy = Math.sin(z.packPhase) * 24;
    moveToward(z, st.player.x + ox, st.player.y + oy, z.spd * dt * 0.06);
  },

  charger(z, dt, st) {
    z.chargeCd = (z.chargeCd || z.chargeCooldown) - dt;
    if (z.charging) {
      z.x += z.chargeVx; z.y += z.chargeVy;
      z.charging -= dt;
    } else {
      moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
      if (z.chargeCd <= 0 && dist(z, st.player) < 250) {
        z.chargeCd = z.chargeCooldown;
        z.charging = 600;
        const a = Math.atan2(st.player.y - z.y, st.player.x - z.x);
        z.chargeVx = Math.cos(a) * z.chargeSpd;
        z.chargeVy = Math.sin(a) * z.chargeSpd;
      }
    }
  },

  teleport(z, dt, st) {
    z.tpCd = (z.tpCd || z.teleportEvery) - dt;
    if (z.tpCd <= 0) {
      z.tpCd = z.teleportEvery;
      const a = Math.random() * Math.PI * 2;
      z.x = st.player.x + Math.cos(a) * 120;
      z.y = st.player.y + Math.sin(a) * 120;
      for (let i = 0; i < 8; i++) addParticle(z.x, z.y, { color: "#ec4899", life: 14, size: 3 });
    } else {
      moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    }
  },

  buffer(z, dt, st) {
    // maintain distance, buff nearby zombies
    const d = dist(z, st.player);
    if (d < 200) moveToward(z, st.player.x, st.player.y, -z.spd * dt * 0.06);
    else moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    // aura emitted in main draw loop
  },

  // ===== BOSSES =====
  boss_trex(z, dt, st) {
    moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    z.stompCd = (z.stompCd || 2500) - dt;
    if (z.stompCd <= 0 && dist(z, st.player) < 250) {
      z.stompCd = 3000;
      addShake(12, 400);
      if (dist(z, st.player) < 120) st.player.hp -= 20;
      for (let i = 0; i < 24; i++) {
        const a = Math.random() * Math.PI * 2;
        addParticle(z.x, z.y, { vx: Math.cos(a)*6, vy: Math.sin(a)*6, life: 22, color: "#78350f", size: 4 });
      }
    }
  },

  boss_kraken(z, dt, st) {
    // stays near edge, summons tentacle ranged attacks
    z.krakenT = (z.krakenT || 0) + dt;
    const tx = st.W * 0.5 + Math.cos(z.krakenT * 0.0005) * st.W * 0.35;
    const ty = st.H * 0.5 + Math.sin(z.krakenT * 0.0004) * st.H * 0.35;
    moveToward(z, tx, ty, z.spd * dt * 0.06);
    z.tentacleCd = (z.tentacleCd || 900) - dt;
    if (z.tentacleCd <= 0) {
      z.tentacleCd = 700;
      for (let i = 0; i < 4; i++) {
        const a = Math.atan2(st.player.y - z.y, st.player.x - z.x) + (i-1.5) * 0.2;
        st.enemyBullets.push({
          x: z.x, y: z.y,
          vx: Math.cos(a) * 5, vy: Math.sin(a) * 5,
          dmg: 14, life: 200, color: "#7c3aed", emoji: "🟣",
        });
      }
    }
  },

  boss_king(z, dt, st) {
    moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    z.summonCd = (z.summonCd || 3500) - dt;
    if (z.summonCd <= 0) {
      z.summonCd = 5000;
      for (let i = 0; i < 5; i++) {
        const a = i / 5 * Math.PI * 2;
        spawnZombieAt(st, i % 2 ? "runner" : "skeleton", z.x + Math.cos(a) * 60, z.y + Math.sin(a) * 60);
      }
    }
  },

  boss_giga(z, dt, st) {
    moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    // grow size as HP drops
    const hpFrac = z.hp / z.maxHp;
    z.size = 90 + (1 - hpFrac) * 50;
    z.dmg = 38 + (1 - hpFrac) * 40;
  },

  boss_horror(z, dt, st) {
    moveToward(z, st.player.x, st.player.y, z.spd * dt * 0.06);
    z.spawnCd = (z.spawnCd || 2000) - dt;
    if (z.spawnCd <= 0) {
      z.spawnCd = 1800;
      const types = ["ghost", "exploder", "bat", "crawler"];
      const t = types[Math.floor(Math.random() * types.length)];
      spawnZombieAt(st, t, z.x + (Math.random() - 0.5) * 80, z.y + (Math.random() - 0.5) * 80);
    }
  },
};

function moveToward(z, tx, ty, spd) {
  const dx = tx - z.x, dy = ty - z.y;
  const d = Math.hypot(dx, dy) || 1;
  z.x += (dx / d) * spd;
  z.y += (dy / d) * spd;
}

function dist(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }

function detonateExploder(z, st) {
  explosionFx(z.x, z.y, z.explodeRadius);
  addShake(8, 300);
  if (dist(z, st.player) < z.explodeRadius) {
    damagePlayer(st, z.explodeDmg);
  }
  for (const other of st.zombies) {
    if (other === z) continue;
    const d = dist(z, other);
    if (d < z.explodeRadius) {
      damageZombie(st, other, z.explodeDmg * 0.5, other.x, other.y);
    }
  }
}
