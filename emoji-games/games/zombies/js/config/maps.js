// Map/biome definitions. Walls in normalized [0-1] rects — become solid collision.
// Each map has a genuinely different layout to shape combat.
const MAPS = [
  {
    id: "graveyard",
    name: "Graveyard",
    emoji: "🪦",
    floorTint: "rgba(40,35,30,0.12)",
    // Scattered tombstones in clusters — moderate cover, open sightlines
    walls: [
      { x: 0.15, y: 0.2,  w: 0.04, h: 0.06 },
      { x: 0.22, y: 0.18, w: 0.04, h: 0.06 },
      { x: 0.12, y: 0.3,  w: 0.04, h: 0.06 },
      { x: 0.78, y: 0.2,  w: 0.04, h: 0.06 },
      { x: 0.85, y: 0.22, w: 0.04, h: 0.06 },
      { x: 0.82, y: 0.32, w: 0.04, h: 0.06 },
      { x: 0.18, y: 0.72, w: 0.04, h: 0.06 },
      { x: 0.25, y: 0.76, w: 0.04, h: 0.06 },
      { x: 0.12, y: 0.82, w: 0.04, h: 0.06 },
      { x: 0.78, y: 0.74, w: 0.04, h: 0.06 },
      { x: 0.85, y: 0.80, w: 0.04, h: 0.06 },
      { x: 0.60, y: 0.48, w: 0.06, h: 0.08, emoji: "⛪" }, // mausoleum off-center
    ],
    decor: ["🪦", "⚰️", "🕯️", "🌫️"],
    ambient: "Eerie mist hangs low over the crumbling graves...",
    wallEmoji: "🪦",
  },
  {
    id: "mall",
    name: "Abandoned Mall",
    emoji: "🏬",
    floorTint: "rgba(80,70,100,0.15)",
    // Long aisle corridors — choke-point combat
    walls: [
      // outer store walls
      { x: 0.05, y: 0.05, w: 0.12, h: 0.04 },
      { x: 0.22, y: 0.05, w: 0.15, h: 0.04 },
      { x: 0.42, y: 0.05, w: 0.15, h: 0.04 },
      { x: 0.62, y: 0.05, w: 0.15, h: 0.04 },
      { x: 0.82, y: 0.05, w: 0.12, h: 0.04 },
      { x: 0.05, y: 0.91, w: 0.12, h: 0.04 },
      { x: 0.22, y: 0.91, w: 0.15, h: 0.04 },
      { x: 0.42, y: 0.91, w: 0.15, h: 0.04 },
      { x: 0.62, y: 0.91, w: 0.15, h: 0.04 },
      { x: 0.82, y: 0.91, w: 0.12, h: 0.04 },
      // central aisles (3 rows of shelves)
      { x: 0.15, y: 0.25, w: 0.18, h: 0.03 },
      { x: 0.42, y: 0.25, w: 0.16, h: 0.03 },
      { x: 0.67, y: 0.25, w: 0.18, h: 0.03 },
      { x: 0.15, y: 0.45, w: 0.25, h: 0.03 },
      { x: 0.50, y: 0.45, w: 0.25, h: 0.03 },
      { x: 0.15, y: 0.65, w: 0.18, h: 0.03 },
      { x: 0.42, y: 0.65, w: 0.16, h: 0.03 },
      { x: 0.67, y: 0.65, w: 0.18, h: 0.03 },
    ],
    decor: ["🛒", "👟", "💄", "🛍️"],
    ambient: "Shattered glass litters the dead food court...",
    wallEmoji: "🧱",
  },
  {
    id: "hospital",
    name: "Hospital",
    emoji: "🏥",
    floorTint: "rgba(150,200,220,0.08)",
    // Tight hallways with rooms — claustrophobic, flickering
    walls: [
      // horizontal corridor walls
      { x: 0.0,  y: 0.22, w: 0.30, h: 0.04 },
      { x: 0.40, y: 0.22, w: 0.60, h: 0.04 },
      { x: 0.0,  y: 0.72, w: 0.20, h: 0.04 },
      { x: 0.30, y: 0.72, w: 0.30, h: 0.04 },
      { x: 0.70, y: 0.72, w: 0.30, h: 0.04 },
      // vertical room dividers
      { x: 0.18, y: 0.22, w: 0.03, h: 0.20 },
      { x: 0.40, y: 0.22, w: 0.03, h: 0.20 },
      { x: 0.62, y: 0.22, w: 0.03, h: 0.20 },
      { x: 0.82, y: 0.22, w: 0.03, h: 0.20 },
      { x: 0.18, y: 0.55, w: 0.03, h: 0.17 },
      { x: 0.40, y: 0.55, w: 0.03, h: 0.17 },
      { x: 0.62, y: 0.55, w: 0.03, h: 0.17 },
      { x: 0.82, y: 0.55, w: 0.03, h: 0.17 },
    ],
    decor: ["🩸", "💊", "🩻", "🧴"],
    flicker: true,
    ambient: "Emergency lights flicker. Something moans down the hall.",
    wallEmoji: "🏥",
  },
  {
    id: "forest",
    name: "Dark Forest",
    emoji: "🌲",
    floorTint: "rgba(40,60,40,0.2)",
    // Many small tree obstacles, flashlight makes visibility critical
    walls: [
      ...Array.from({length: 22}, (_, i) => {
        const x = (Math.sin(i * 2.7) * 0.4 + 0.5);
        const y = (Math.cos(i * 1.9) * 0.38 + 0.5);
        return { x: Math.max(0.04, Math.min(0.92, x - 0.02)), y: Math.max(0.04, Math.min(0.92, y - 0.02)), w: 0.04, h: 0.04, emoji: "🌲" };
      }),
    ],
    decor: ["🍂", "🌿", "🪵"],
    darkness: 0.55,
    ambient: "Something howls between the trees...",
    wallEmoji: "🌲",
  },
  {
    id: "hell",
    name: "Hellscape",
    emoji: "🔥",
    floorTint: "rgba(80,20,10,0.25)",
    // Central arena, pillar cover, lava hazards
    walls: [
      { x: 0.22, y: 0.22, w: 0.06, h: 0.06 },
      { x: 0.72, y: 0.22, w: 0.06, h: 0.06 },
      { x: 0.22, y: 0.72, w: 0.06, h: 0.06 },
      { x: 0.72, y: 0.72, w: 0.06, h: 0.06 },
      { x: 0.46, y: 0.38, w: 0.08, h: 0.08, emoji: "🗿" },
      { x: 0.46, y: 0.54, w: 0.08, h: 0.08, emoji: "🗿" },
    ],
    decor: ["🔥", "💀", "🩸", "☠️"],
    hazards: [
      { type: "lava", x: 0.10, y: 0.45, w: 0.10, h: 0.10, dps: 25 },
      { type: "lava", x: 0.80, y: 0.45, w: 0.10, h: 0.10, dps: 25 },
      { type: "lava", x: 0.45, y: 0.10, w: 0.10, h: 0.08, dps: 25 },
      { type: "lava", x: 0.45, y: 0.82, w: 0.10, h: 0.08, dps: 25 },
    ],
    ambient: "The ground burns. The damned screech in unison.",
    wallEmoji: "🪨",
  },
];

const MAP_BY_ID = Object.fromEntries(MAPS.map(m => [m.id, m]));

// Convert walls to pixel-space axis-aligned bounding boxes for the current W/H
function computeWallBoxes(st) {
  const m = st.map;
  return m.walls.map(w => ({
    x: w.x * st.W, y: w.y * st.H,
    w: w.w * st.W, h: w.h * st.H,
    emoji: w.emoji,
  }));
}

function computeHazardBoxes(st) {
  const m = st.map;
  return (m.hazards || []).map(h => ({
    x: h.x * st.W, y: h.y * st.H, w: h.w * st.W, h: h.h * st.H,
    dps: h.dps, type: h.type,
  }));
}

// Resolve circle vs AABB: pushes the entity out of any overlapping wall.
function resolveWallCollision(entity, radius, walls) {
  for (const w of walls) {
    const nx = Math.max(w.x, Math.min(entity.x, w.x + w.w));
    const ny = Math.max(w.y, Math.min(entity.y, w.y + w.h));
    const dx = entity.x - nx, dy = entity.y - ny;
    const d2 = dx * dx + dy * dy;
    if (d2 < radius * radius) {
      const d = Math.sqrt(d2) || 0.01;
      const push = radius - d;
      entity.x += (dx / d) * push;
      entity.y += (dy / d) * push;
    }
  }
}

// Ray-AABB intersection check for bullets (returns true if line from (x1,y1) to (x2,y2) hits any wall)
function bulletHitsWall(x1, y1, x2, y2, walls) {
  for (const w of walls) {
    if (lineRectHit(x1, y1, x2, y2, w)) return w;
  }
  return null;
}

function lineRectHit(x1, y1, x2, y2, r) {
  // Check if the line segment intersects the rectangle
  if (pointInRect(x1, y1, r) || pointInRect(x2, y2, r)) return true;
  return lineLine(x1,y1,x2,y2, r.x,r.y, r.x+r.w,r.y) ||
         lineLine(x1,y1,x2,y2, r.x+r.w,r.y, r.x+r.w,r.y+r.h) ||
         lineLine(x1,y1,x2,y2, r.x+r.w,r.y+r.h, r.x,r.y+r.h) ||
         lineLine(x1,y1,x2,y2, r.x,r.y+r.h, r.x,r.y);
}
function pointInRect(x, y, r) { return x >= r.x && x <= r.x+r.w && y >= r.y && y <= r.y+r.h; }
function lineLine(x1,y1,x2,y2, x3,y3,x4,y4) {
  const den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4);
  if (den === 0) return false;
  const t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / den;
  const u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3)) / den;
  return t >= 0 && t <= 1 && u >= 0 && u <= 1;
}
