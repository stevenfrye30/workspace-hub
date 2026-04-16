// Registry of mini games. Add new entries here as you build them.
// Each game: { name, emoji, color, desc, tags, path (omit for "Coming soon") }
const GAMES = [
  {
    name: "Zombie Survival",
    emoji: "🧟",
    color: "#dc2626",
    desc: "Top-down survival shooter — fight emoji hordes, earn cash, unlock 5 guns",
    tags: ["survival", "shooter", "scary"],
    path: "games/zombies/index.html"
  },
  {
    name: "Nuggets",
    emoji: "⛏",
    color: "#b8901f",
    desc: "Mine-cart arcade game — dodge rocks, lava, and spikes; collect gems and hearts",
    tags: ["arcade"],
    path: "games/nuggets/index.html"
  },
  {
    name: "Emoji Match",
    emoji: "🍉",
    color: "#ec4899",
    desc: "Classic memory match — flip pairs of emoji cards",
    tags: ["memory", "casual"],
    // path: "games/match/index.html"
  },
  {
    name: "Emoji Snake",
    emoji: "🐍",
    color: "#10b981",
    desc: "Eat fruit emojis, grow longer, don't bite yourself",
    tags: ["arcade", "classic"],
  },
  {
    name: "Emoji 2048",
    emoji: "🧩",
    color: "#f59e0b",
    desc: "Combine matching emojis to evolve them",
    tags: ["puzzle"],
  },
  {
    name: "Emoji Tic-Tac-Toe",
    emoji: "❌",
    color: "#3b82f6",
    desc: "X vs O with emoji skins",
    tags: ["classic", "two-player"],
  },
  {
    name: "Emoji Whack-A-Mole",
    emoji: "🐹",
    color: "#a855f7",
    desc: "Tap the emoji before it disappears",
    tags: ["arcade", "reflex"],
  },
  {
    name: "Emoji Wordle",
    emoji: "📝",
    color: "#22c55e",
    desc: "Guess the secret emoji sequence",
    tags: ["puzzle", "daily"],
  },
  {
    name: "Emoji Tetris",
    emoji: "🟦",
    color: "#06b6d4",
    desc: "Stack falling emoji blocks, clear lines",
    tags: ["arcade", "classic"],
  },
  {
    name: "Emoji Sudoku",
    emoji: "🔢",
    color: "#eab308",
    desc: "Sudoku, but with 9 emojis instead of digits",
    tags: ["puzzle"],
  },
  {
    name: "Emoji Reaction",
    emoji: "⚡",
    color: "#facc15",
    desc: "Test your reaction speed",
    tags: ["reflex", "casual"],
  },
];
