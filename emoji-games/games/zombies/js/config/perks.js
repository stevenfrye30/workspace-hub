// Perk pool for level-up draws. `apply(state)` mutates player/run state.
// rarity affects draw weight & border color.
const PERK_RARITY_W = { common: 50, uncommon: 28, rare: 14, epic: 6, legendary: 2 };

const PERKS = [
  // ===== OFFENSE =====
  { id: "dmg1",      name: "Hollow Points",     emoji: "🎯", rarity: "common",    desc: "+15% damage",               apply: s => s.mult.dmg *= 1.15 },
  { id: "dmg2",      name: "Sharper Rounds",    emoji: "🔧", rarity: "uncommon",  desc: "+25% damage",               apply: s => s.mult.dmg *= 1.25 },
  { id: "dmg3",      name: "Devastator",        emoji: "💀", rarity: "rare",      desc: "+45% damage",               apply: s => s.mult.dmg *= 1.45 },
  { id: "fire1",     name: "Trigger Finger",    emoji: "👆", rarity: "common",    desc: "+12% fire rate",            apply: s => s.mult.fireRate *= 0.88 },
  { id: "fire2",     name: "Adrenaline",        emoji: "💉", rarity: "uncommon",  desc: "+20% fire rate",            apply: s => s.mult.fireRate *= 0.80 },
  { id: "crit1",     name: "Lucky Shot",        emoji: "🍀", rarity: "uncommon",  desc: "+15% crit chance (2× dmg)", apply: s => s.crit.chance += 0.15 },
  { id: "crit2",     name: "Deadeye",           emoji: "👁️", rarity: "rare",      desc: "+25% crit + crits do 3×",   apply: s => { s.crit.chance += 0.25; s.crit.mult = Math.max(s.crit.mult, 3); } },
  { id: "pierce1",   name: "Ghost Rounds",      emoji: "🔪", rarity: "rare",      desc: "+1 pierce on all bullets",  apply: s => s.mult.pierce += 1 },
  { id: "pierce2",   name: "Railgun Mod",       emoji: "⚙️", rarity: "epic",      desc: "+3 pierce on all bullets",  apply: s => s.mult.pierce += 3 },
  { id: "bounce",    name: "Ricochet",          emoji: "↩️", rarity: "rare",      desc: "Bullets bounce once",       apply: s => s.mult.bounce += 1 },
  { id: "explode",   name: "Explosive Rounds",  emoji: "💥", rarity: "epic",      desc: "Bullets explode on hit (small AoE)", apply: s => s.flags.explosiveRounds = true },
  { id: "burn",      name: "Incendiary",        emoji: "🔥", rarity: "uncommon",  desc: "20% chance to ignite",      apply: s => s.status.burnChance += 0.2 },
  { id: "chain",     name: "Static Charge",     emoji: "⚡", rarity: "rare",      desc: "10% chance to chain lightning", apply: s => s.status.chainChance += 0.1 },
  { id: "vamp",      name: "Vampirism",         emoji: "🩸", rarity: "epic",      desc: "Heal 1 HP per 3 kills",     apply: s => s.flags.vampPer3 = true },
  { id: "split",     name: "Split Rounds",      emoji: "🔱", rarity: "epic",      desc: "Bullets split into 2 near end of life", apply: s => s.flags.split = true },
  { id: "orbit",     name: "Death Halo",        emoji: "☠️", rarity: "epic",      desc: "2 skulls orbit you, damaging foes", apply: s => s.flags.orbitSkulls = (s.flags.orbitSkulls || 0) + 2 },
  { id: "shotgun+",  name: "Choke Barrel",      emoji: "🧱", rarity: "uncommon",  desc: "Tighter shotgun spread + 2 more pellets", apply: s => s.mult.shotgunBonus += 1 },
  { id: "rocket+",   name: "Bigger Boom",       emoji: "💣", rarity: "rare",      desc: "+30% explosion radius",     apply: s => s.mult.explodeRadius *= 1.3 },
  { id: "bullet++",  name: "Multishot",         emoji: "🔫", rarity: "legendary", desc: "Double-tap: every shot fires twice (tiny delay)", apply: s => s.flags.doubleShot = true },

  // ===== DEFENSE =====
  { id: "hp1",       name: "Iron Skin",         emoji: "🛡️", rarity: "common",    desc: "+20 max HP (also heals)",   apply: s => { s.player.maxHp += 20; s.player.hp += 20; } },
  { id: "hp2",       name: "Tough",             emoji: "🦾", rarity: "uncommon",  desc: "+40 max HP (also heals)",   apply: s => { s.player.maxHp += 40; s.player.hp += 40; } },
  { id: "regen",     name: "Regeneration",      emoji: "💚", rarity: "rare",      desc: "Regenerate 1 HP/sec",       apply: s => s.mult.regen += 1 },
  { id: "armor",     name: "Kevlar",            emoji: "🧥", rarity: "uncommon",  desc: "-15% damage taken",         apply: s => s.mult.dmgTaken *= 0.85 },
  { id: "dodge",     name: "Nimble",            emoji: "💨", rarity: "rare",      desc: "15% dodge chance",          apply: s => s.mult.dodge += 0.15 },
  { id: "thorns",    name: "Thorns",            emoji: "🌵", rarity: "rare",      desc: "Attackers take 20 dmg",     apply: s => s.mult.thorns += 20 },
  { id: "shield",    name: "Wave Shield",       emoji: "🔰", rarity: "epic",      desc: "Absorb 1 hit per wave",     apply: s => s.flags.waveShield = true },
  { id: "slowmo",    name: "Near-Death Clarity",emoji: "🕰️", rarity: "epic",      desc: "Time slows at low HP",      apply: s => s.flags.slowNearDeath = true },

  // ===== UTILITY =====
  { id: "spd1",      name: "Fleet Feet",        emoji: "👟", rarity: "common",    desc: "+10% move speed",           apply: s => s.mult.moveSpd *= 1.1 },
  { id: "spd2",      name: "Marathon",          emoji: "🏃", rarity: "uncommon",  desc: "+20% move speed",           apply: s => s.mult.moveSpd *= 1.2 },
  { id: "pickup",    name: "Magnetism",         emoji: "🧲", rarity: "common",    desc: "+80% pickup radius",        apply: s => s.mult.pickup *= 1.8 },
  { id: "cash",      name: "Greedy",            emoji: "💰", rarity: "uncommon",  desc: "+30% cash from kills",      apply: s => s.mult.cash *= 1.3 },
  { id: "xp",        name: "Quick Learner",     emoji: "📚", rarity: "uncommon",  desc: "+25% XP gain",              apply: s => s.mult.xp *= 1.25 },
  { id: "reload",    name: "Quick Hands",       emoji: "✋", rarity: "common",    desc: "Pickups auto-reload current gun", apply: s => s.flags.autoReload = true },
  { id: "ammo",      name: "Bandolier",         emoji: "🎒", rarity: "uncommon",  desc: "+50% max ammo capacity",    apply: s => s.mult.ammoCap *= 1.5 },

  // ===== EXOTIC / LEGENDARY =====
  { id: "time",      name: "Time Freeze",       emoji: "⏸️", rarity: "legendary", desc: "Killing 20 zombies freezes time 2s", apply: s => s.flags.timeFreeze = true },
  { id: "berserk",   name: "Berserker",         emoji: "😤", rarity: "legendary", desc: "+80% dmg when HP < 30%",    apply: s => s.flags.berserker = true },
  { id: "rocket10",  name: "10th Rocket",       emoji: "🚀", rarity: "rare",      desc: "Every 10th shot is a rocket", apply: s => s.flags.tenthRocket = true },
  { id: "lifesteal", name: "Blood Ritual",      emoji: "🩸", rarity: "legendary", desc: "2% lifesteal on all damage", apply: s => s.mult.lifesteal += 0.02 },
  { id: "minion",    name: "Summoned Ally",     emoji: "🤖", rarity: "epic",      desc: "Summon an ally bot",        apply: s => s.flags.minions = (s.flags.minions || 0) + 1 },
  { id: "freeze_aura", name: "Frost Aura",      emoji: "❄️", rarity: "epic",      desc: "Nearby zombies slowed",     apply: s => s.flags.frostAura = true },
];

const PERK_BY_ID = Object.fromEntries(PERKS.map(p => [p.id, p]));

function draftPerks(state, count = 3) {
  const taken = new Set(state.takenPerks || []);
  const pool = PERKS.filter(p => !taken.has(p.id) || p.id.startsWith("dmg") || p.id.startsWith("hp") || p.id.startsWith("spd") || p.id === "hp1" || p.id === "pickup");
  const draft = [];
  for (let i = 0; i < count && pool.length; i++) {
    const weights = pool.map(p => PERK_RARITY_W[p.rarity] || 1);
    const total = weights.reduce((a, b) => a + b, 0);
    let r = Math.random() * total;
    let pick = 0;
    for (let j = 0; j < pool.length; j++) {
      r -= weights[j];
      if (r <= 0) { pick = j; break; }
    }
    draft.push(pool[pick]);
    pool.splice(pick, 1);
  }
  return draft;
}
