// Zombie roster. `ai` string picks behavior in update loop.
// firstWave gates when this type can start appearing.
const ZOMBIES = [
  { id: "walker",    emoji: "🧟",    hp: 55,  spd: 0.85, dmg: 8,  cash: 5,  xp: 3,  size: 28, ai: "chase",      firstWave: 1 },
  { id: "runner",    emoji: "🧟‍♀️", hp: 40,  spd: 1.6,  dmg: 7,  cash: 7,  xp: 4,  size: 26, ai: "chase",      firstWave: 2 },
  { id: "tank",      emoji: "👹",   hp: 180, spd: 0.55, dmg: 16, cash: 18, xp: 8,  size: 38, ai: "chase",      firstWave: 3, armor: 0.4 },
  { id: "ghost",     emoji: "👻",   hp: 45,  spd: 1.2,  dmg: 6,  cash: 9,  xp: 5,  size: 28, ai: "phase",      firstWave: 3 },
  { id: "skeleton",  emoji: "💀",   hp: 60,  spd: 1.0,  dmg: 10, cash: 10, xp: 5,  size: 28, ai: "chase",      firstWave: 4, rebuild: true },
  { id: "bat",       emoji: "🦇",   hp: 22,  spd: 2.1,  dmg: 5,  cash: 6,  xp: 4,  size: 22, ai: "swarm",      firstWave: 4 },
  { id: "spitter",   emoji: "🤢",   hp: 45,  spd: 0.75, dmg: 8,  cash: 11, xp: 6,  size: 28, ai: "ranged",     firstWave: 5, projDmg: 12, projSpd: 6, projRange: 260, reload: 2200 },
  { id: "screamer",  emoji: "🗣️",  hp: 50,  spd: 0.7,  dmg: 4,  cash: 14, xp: 7,  size: 30, ai: "screamer",   firstWave: 6, summonEvery: 3200, summonCount: 3 },
  { id: "exploder",  emoji: "💣",   hp: 30,  spd: 1.4,  dmg: 35, cash: 12, xp: 6,  size: 26, ai: "exploder",   firstWave: 6, explodeRadius: 70, explodeDmg: 40 },
  { id: "crawler",   emoji: "🦎",   hp: 30,  spd: 1.3,  dmg: 6,  cash: 7,  xp: 4,  size: 18, ai: "chase",      firstWave: 5 },
  { id: "necro",     emoji: "🧙",   hp: 80,  spd: 0.6,  dmg: 8,  cash: 22, xp: 10, size: 30, ai: "necro",      firstWave: 8, reviveEvery: 4500 },
  { id: "witch",     emoji: "🧙‍♀️", hp: 70,  spd: 0.9,  dmg: 7,  cash: 20, xp: 9,  size: 28, ai: "curser",     firstWave: 8, curseEvery: 3500 },
  { id: "vampire",   emoji: "🧛",   hp: 110, spd: 1.1,  dmg: 14, cash: 18, xp: 8,  size: 30, ai: "chase",      firstWave: 7, lifesteal: 0.8 },
  { id: "werewolf",  emoji: "🐺",   hp: 130, spd: 1.3,  dmg: 18, cash: 20, xp: 9,  size: 32, ai: "leaper",     firstWave: 9, leapCooldown: 2800, leapDist: 220 },
  { id: "mummy",     emoji: "🧻",   hp: 160, spd: 0.55, dmg: 12, cash: 16, xp: 8,  size: 32, ai: "chase",      firstWave: 7, armor: 0.6 },
  { id: "demon",     emoji: "😈",   hp: 120, spd: 0.85, dmg: 15, cash: 24, xp: 10, size: 32, ai: "aura",       firstWave: 10, auraRadius: 90, auraDmg: 12 },
  { id: "dog",       emoji: "🐕",   hp: 35,  spd: 1.8,  dmg: 8,  cash: 8,  xp: 5,  size: 22, ai: "pack",       firstWave: 6 },
  { id: "bear",      emoji: "🐻",   hp: 320, spd: 1.1,  dmg: 25, cash: 60, xp: 25, size: 44, ai: "charger",    firstWave: 12, chargeCooldown: 3500, chargeSpd: 4 },
  { id: "clown",     emoji: "🤡",   hp: 90,  spd: 1.0,  dmg: 14, cash: 24, xp: 11, size: 30, ai: "teleport",   firstWave: 11, teleportEvery: 2400 },
  { id: "lord",      emoji: "👑",   hp: 150, spd: 0.9,  dmg: 10, cash: 40, xp: 18, size: 34, ai: "buffer",     firstWave: 14, buffRadius: 140, buffMult: 1.5 },
];

const BOSSES = [
  { id: "trex",     emoji: "🦖", hp: 2500,  spd: 0.8, dmg: 30, cash: 300, xp: 150, size: 70, ai: "boss_trex",   wave: 5 },
  { id: "kraken",   emoji: "🐙", hp: 3800,  spd: 0.5, dmg: 22, cash: 500, xp: 220, size: 80, ai: "boss_kraken", wave: 10 },
  { id: "king",     emoji: "🤴", hp: 5500,  spd: 0.9, dmg: 28, cash: 800, xp: 320, size: 72, ai: "boss_king",   wave: 15 },
  { id: "giga",     emoji: "🧟‍♂️", hp: 9000,spd: 0.7, dmg: 38, cash: 1200,xp: 500, size: 90, ai: "boss_giga",   wave: 20 },
  { id: "horror",   emoji: "😱", hp: 14000, spd: 0.85,dmg: 45, cash: 2000,xp: 800, size: 100,ai: "boss_horror", wave: 25 },
];

const ZOMBIE_BY_ID = Object.fromEntries([...ZOMBIES, ...BOSSES].map(z => [z.id, z]));
