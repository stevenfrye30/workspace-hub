// Playable character classes. Unlocked via meta progression (skulls).
const CHARACTERS = [
  {
    id: "survivor", name: "Survivor", emoji: "🧑‍🚀", unlockCost: 0,
    desc: "Baseline. Balanced stats, starts with pistol.",
    startGun: 0,
    passive: s => {},
  },
  {
    id: "soldier", name: "Soldier", emoji: "🪖", unlockCost: 50,
    desc: "+20% damage. Starts with Assault Rifle.",
    startGun: 3,
    passive: s => { s.mult.dmg *= 1.2; },
  },
  {
    id: "medic", name: "Medic", emoji: "⚕️", unlockCost: 80,
    desc: "+30 max HP, regen 1 HP/sec, HP pickups heal double.",
    startGun: 2,
    passive: s => { s.player.maxHp += 30; s.player.hp = s.player.maxHp; s.mult.regen += 1; s.flags.medic = true; },
  },
  {
    id: "engineer", name: "Engineer", emoji: "🔧", unlockCost: 120,
    desc: "Explosives deal +50% damage & radius. Starts with Rocket.",
    startGun: 6,
    passive: s => { s.mult.explosiveDmg *= 1.5; s.mult.explodeRadius *= 1.5; },
  },
  {
    id: "sniper", name: "Marksman", emoji: "🎯", unlockCost: 150,
    desc: "+30% crit, crits do 3×. Starts with Sniper.",
    startGun: 5,
    passive: s => { s.crit.chance += 0.3; s.crit.mult = Math.max(s.crit.mult, 3); },
  },
  {
    id: "berserker", name: "Berserker", emoji: "😤", unlockCost: 200,
    desc: "Low HP = huge damage. Starts with Chainsaw.",
    startGun: 11,
    passive: s => { s.flags.berserker = true; s.mult.moveSpd *= 1.1; },
  },
];

const CHARACTER_BY_ID = Object.fromEntries(CHARACTERS.map(c => [c.id, c]));
