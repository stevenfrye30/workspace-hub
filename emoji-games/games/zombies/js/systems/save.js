// localStorage-backed meta save
const SAVE_KEY = "emojigames.zombies.save.v1";

const DEFAULT_SAVE = {
  skulls: 0,
  unlockedChars: ["survivor"],
  highestWave: 0,
  totalKills: 0,
  totalRuns: 0,
  achievements: {},
  settings: { screenShake: true, gore: "medium" },
};

function loadSave() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return { ...DEFAULT_SAVE };
    return { ...DEFAULT_SAVE, ...JSON.parse(raw) };
  } catch { return { ...DEFAULT_SAVE }; }
}

function writeSave(s) {
  try { localStorage.setItem(SAVE_KEY, JSON.stringify(s)); } catch {}
}

function awardSkulls(save, amount) {
  save.skulls += amount;
  writeSave(save);
}

function isUnlocked(save, charId) {
  return save.unlockedChars.includes(charId);
}

function tryUnlockCharacter(save, charId) {
  const c = CHARACTER_BY_ID[charId];
  if (!c) return { ok: false, reason: "unknown" };
  if (isUnlocked(save, charId)) return { ok: false, reason: "already" };
  if (save.skulls < c.unlockCost) return { ok: false, reason: "cost" };
  save.skulls -= c.unlockCost;
  save.unlockedChars.push(charId);
  writeSave(save);
  return { ok: true };
}

const ACHIEVEMENTS = [
  { id: "first_kill",   name: "First Blood",       desc: "Kill 1 zombie",             check: s => s.totalKills >= 1,     reward: 5 },
  { id: "kill_100",     name: "Cleanup Crew",      desc: "Kill 100 zombies",          check: s => s.totalKills >= 100,   reward: 10 },
  { id: "kill_1k",      name: "Exterminator",      desc: "Kill 1,000 zombies",        check: s => s.totalKills >= 1000,  reward: 50 },
  { id: "kill_10k",     name: "Apocalypse Survivor", desc: "Kill 10,000 zombies",     check: s => s.totalKills >= 10000, reward: 200 },
  { id: "wave_5",       name: "Just Getting Started", desc: "Reach wave 5",           check: s => s.highestWave >= 5,    reward: 10 },
  { id: "wave_10",      name: "Double Digits",     desc: "Reach wave 10",             check: s => s.highestWave >= 10,   reward: 25 },
  { id: "wave_20",      name: "Death Defier",      desc: "Reach wave 20",             check: s => s.highestWave >= 20,   reward: 80 },
  { id: "wave_30",      name: "Horror Legend",     desc: "Reach wave 30",             check: s => s.highestWave >= 30,   reward: 200 },
];

function checkAchievements(save) {
  const newly = [];
  for (const a of ACHIEVEMENTS) {
    if (save.achievements[a.id]) continue;
    if (a.check(save)) {
      save.achievements[a.id] = Date.now();
      save.skulls += a.reward;
      newly.push(a);
    }
  }
  if (newly.length) writeSave(save);
  return newly;
}
