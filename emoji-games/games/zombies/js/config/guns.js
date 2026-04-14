// Weapon arsenal. Each gun has a unique feel fingerprint.
// fireRate: ms between shots. spread: radians. bullets: projectiles per shot.
// pierce: enemies passed through. shake: screen shake intensity on fire.
// dmgType: 'kinetic'|'fire'|'freeze'|'tesla'|'explosive'|'plasma'|'melee'
// statusChance 0-1: chance to apply status (burn/freeze/shock)
const GUNS = [
  {
    id: 0, name: "Pistol", emoji: "🔫", key: "1",
    cost: 0, tier: "common", dmg: 28, fireRate: 260, ammo: Infinity,
    spread: 0.04, bulletSpd: 10, bullets: 1, pierce: 0,
    shake: 2, flashColor: "#fbbf24", bulletColor: "#fde68a", bulletSize: 3,
    dmgType: "kinetic",
  },
  {
    id: 1, name: "Shotgun", emoji: "💥", key: "2",
    cost: 140, tier: "common", dmg: 18, fireRate: 620, ammo: 24,
    spread: 0.32, bulletSpd: 8.5, bullets: 7, pierce: 0,
    shake: 9, flashColor: "#f97316", bulletColor: "#fb923c", bulletSize: 3,
    dmgType: "kinetic",
  },
  {
    id: 2, name: "SMG", emoji: "🔪", key: "3",
    cost: 260, tier: "common", dmg: 14, fireRate: 85, ammo: 90,
    spread: 0.1, bulletSpd: 11, bullets: 1, pierce: 0,
    shake: 1.5, flashColor: "#fbbf24", bulletColor: "#fde68a", bulletSize: 2.5,
    dmgType: "kinetic",
  },
  {
    id: 3, name: "Assault Rifle", emoji: "🎯", key: "4",
    cost: 450, tier: "uncommon", dmg: 22, fireRate: 110, ammo: 60,
    spread: 0.05, bulletSpd: 13, bullets: 1, pierce: 0,
    shake: 2.5, flashColor: "#fbbf24", bulletColor: "#fde68a", bulletSize: 3,
    dmgType: "kinetic",
  },
  {
    id: 4, name: "Crossbow", emoji: "🏹", key: "5",
    cost: 520, tier: "uncommon", dmg: 55, fireRate: 420, ammo: 20,
    spread: 0.005, bulletSpd: 14, bullets: 1, pierce: 3,
    shake: 3, flashColor: "#a3a3a3", bulletColor: "#cbd5e1", bulletSize: 4,
    dmgType: "kinetic",
  },
  {
    id: 5, name: "Sniper", emoji: "🔭", key: "6",
    cost: 680, tier: "rare", dmg: 120, fireRate: 900, ammo: 10,
    spread: 0, bulletSpd: 22, bullets: 1, pierce: 5,
    shake: 12, flashColor: "#f59e0b", bulletColor: "#fef3c7", bulletSize: 4,
    dmgType: "kinetic", crit: true,
  },
  {
    id: 6, name: "Rocket", emoji: "🚀", key: "7",
    cost: 1100, tier: "rare", dmg: 130, fireRate: 900, ammo: 8,
    spread: 0, bulletSpd: 7, bullets: 1, pierce: 0,
    shake: 16, flashColor: "#fb923c", bulletColor: "#fbbf24", bulletSize: 6,
    dmgType: "explosive", explode: 85,
  },
  {
    id: 7, name: "Flamethrower", emoji: "🔥", key: "8",
    cost: 820, tier: "rare", dmg: 8, fireRate: 40, ammo: 260,
    spread: 0.18, bulletSpd: 7, bullets: 1, pierce: 2,
    shake: 1, flashColor: "#f97316", bulletColor: "#fb923c", bulletSize: 5,
    dmgType: "fire", statusChance: 1, ttl: 22,
  },
  {
    id: 8, name: "Minigun", emoji: "🌀", key: "9",
    cost: 1400, tier: "epic", dmg: 18, fireRate: 55, ammo: 300,
    spread: 0.14, bulletSpd: 12, bullets: 1, pierce: 0,
    shake: 3, flashColor: "#fbbf24", bulletColor: "#fde68a", bulletSize: 3,
    dmgType: "kinetic", windup: 600,
  },
  {
    id: 9, name: "Freeze Ray", emoji: "❄️", key: "0",
    cost: 1200, tier: "epic", dmg: 10, fireRate: 60, ammo: 200,
    spread: 0.05, bulletSpd: 13, bullets: 1, pierce: 4,
    shake: 1, flashColor: "#38bdf8", bulletColor: "#7dd3fc", bulletSize: 3,
    dmgType: "freeze", statusChance: 1, ttl: 30,
  },
  {
    id: 10, name: "Tesla", emoji: "⚡", key: "-",
    cost: 1500, tier: "epic", dmg: 35, fireRate: 220, ammo: 80,
    spread: 0.02, bulletSpd: 18, bullets: 1, pierce: 0,
    shake: 4, flashColor: "#c084fc", bulletColor: "#e9d5ff", bulletSize: 4,
    dmgType: "tesla", chain: 5, chainRange: 140, chainFalloff: 0.75,
  },
  {
    id: 11, name: "Chainsaw", emoji: "🪚", key: "=",
    cost: 700, tier: "epic", dmg: 38, fireRate: 80, ammo: Infinity,
    spread: 0, bulletSpd: 0, bullets: 0, pierce: 0,
    shake: 2, flashColor: "#dc2626", bulletColor: "#dc2626", bulletSize: 0,
    dmgType: "melee", range: 55, arc: 1.2,
  },
  {
    id: 12, name: "Katana", emoji: "🗡️", key: "[",
    cost: 900, tier: "legendary", dmg: 140, fireRate: 480, ammo: Infinity,
    spread: 0, bulletSpd: 0, bullets: 0, pierce: 0,
    shake: 5, flashColor: "#e5e7eb", bulletColor: "#e5e7eb", bulletSize: 0,
    dmgType: "melee", range: 80, arc: 2.6, dashDist: 70,
  },
  {
    id: 13, name: "Plasma Cannon", emoji: "☠️", key: "]",
    cost: 1800, tier: "legendary", dmg: 90, fireRate: 380, ammo: 40,
    spread: 0.01, bulletSpd: 11, bullets: 1, pierce: 3,
    shake: 6, flashColor: "#22d3ee", bulletColor: "#67e8f9", bulletSize: 6,
    dmgType: "plasma", explode: 40,
  },
  {
    id: 14, name: "Rainbow Gun", emoji: "🌈", key: ";",
    cost: 2400, tier: "legendary", dmg: 50, fireRate: 150, ammo: 150,
    spread: 0.12, bulletSpd: 12, bullets: 1, pierce: 1,
    shake: 3, flashColor: "#ec4899", bulletColor: "#f0abfc", bulletSize: 4,
    dmgType: "kinetic", randomEffect: true,
  },
];

const TIER_COLOR = {
  common: "#a3a3a3",
  uncommon: "#22c55e",
  rare: "#3b82f6",
  epic: "#a855f7",
  legendary: "#f59e0b",
};
