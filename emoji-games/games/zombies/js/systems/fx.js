// Visual feel: screen shake, hit-stop, damage numbers, particles, gibs, wave banners, toasts.
const FX = {
  shake: { amount: 0, duration: 0 },
  hitStop: 0,
  timeScale: 1,
  particles: [],
  popups: [],
  flashes: [],
};

function addShake(amount, duration = 200) {
  if (!state?.save?.settings?.screenShake && state) return;
  if (amount > FX.shake.amount) {
    FX.shake.amount = amount;
    FX.shake.duration = duration;
  }
}

function applyShakeToStage(stage, dt) {
  if (FX.shake.duration <= 0) {
    stage.style.transform = "";
    return;
  }
  FX.shake.duration -= dt;
  const mag = FX.shake.amount * (FX.shake.duration > 0 ? FX.shake.duration / 200 : 0);
  const dx = (Math.random() - 0.5) * mag * 2;
  const dy = (Math.random() - 0.5) * mag * 2;
  stage.style.transform = `translate(${dx}px, ${dy}px)`;
  if (FX.shake.duration <= 0) {
    FX.shake.amount = 0;
    stage.style.transform = "";
  }
}

function triggerHitStop(ms) {
  FX.hitStop = Math.max(FX.hitStop, ms);
}

function addPopup(x, y, text, color = "#fbbf24", size = 16) {
  FX.popups.push({ x, y, text, color, size, life: 50, vy: -1.2 });
}

function addParticle(x, y, opts = {}) {
  FX.particles.push({
    x, y,
    vx: opts.vx ?? (Math.random() - 0.5) * 4,
    vy: opts.vy ?? (Math.random() - 0.5) * 4,
    life: opts.life ?? 20,
    maxLife: opts.life ?? 20,
    color: opts.color ?? "#dc2626",
    size: opts.size ?? 3,
    shrink: opts.shrink ?? false,
    text: opts.text ?? null,
    gravity: opts.gravity ?? 0,
  });
}

function bloodBurst(x, y, count = 6) {
  for (let i = 0; i < count; i++) {
    addParticle(x, y, {
      vx: (Math.random() - 0.5) * 5,
      vy: (Math.random() - 0.5) * 5,
      life: 18 + Math.random() * 10,
      color: Math.random() < 0.5 ? "#dc2626" : "#7f1d1d",
      size: 2 + Math.random() * 2,
    });
  }
}

function gibBurst(x, y, emoji) {
  const gibs = ["🦴", "🧠", "👁️", "🦷", "💀"];
  for (let i = 0; i < 3 + Math.floor(Math.random() * 3); i++) {
    addParticle(x, y, {
      vx: (Math.random() - 0.5) * 7,
      vy: (Math.random() - 0.5) * 7 - 2,
      life: 45 + Math.random() * 20,
      color: "#fff",
      size: 14,
      text: gibs[Math.floor(Math.random() * gibs.length)],
      gravity: 0.18,
    });
  }
  bloodBurst(x, y, 14);
}

function muzzleFlash(x, y, ang, color = "#fbbf24") {
  FX.flashes.push({ x, y, ang, color, life: 5 });
  for (let i = 0; i < 5; i++) {
    addParticle(x, y, {
      vx: Math.cos(ang) * (3 + Math.random() * 3) + (Math.random() - 0.5) * 1.5,
      vy: Math.sin(ang) * (3 + Math.random() * 3) + (Math.random() - 0.5) * 1.5,
      life: 8, color, size: 2.5,
    });
  }
}

function explosionFx(x, y, radius) {
  for (let i = 0; i < 30; i++) {
    const a = Math.random() * Math.PI * 2;
    const s = 2 + Math.random() * 6;
    addParticle(x, y, {
      vx: Math.cos(a) * s, vy: Math.sin(a) * s,
      life: 24 + Math.random() * 10,
      color: i % 3 === 0 ? "#fde68a" : i % 2 ? "#fb923c" : "#dc2626",
      size: 3 + Math.random() * 3,
    });
  }
  FX.flashes.push({ x, y, ang: 0, color: "#fbbf24", life: 12, radius });
}

function updateFx(dt) {
  for (const p of FX.particles) {
    p.x += p.vx; p.y += p.vy;
    p.vx *= 0.93; p.vy *= 0.93;
    if (p.gravity) p.vy += p.gravity;
    p.life--;
  }
  FX.particles = FX.particles.filter(p => p.life > 0);

  for (const p of FX.popups) {
    p.y += p.vy; p.vy *= 0.95; p.life--;
  }
  FX.popups = FX.popups.filter(p => p.life > 0);

  for (const f of FX.flashes) f.life--;
  FX.flashes = FX.flashes.filter(f => f.life > 0);
}

function drawFx(ctx) {
  // flashes (additive glow)
  ctx.globalCompositeOperation = "lighter";
  for (const f of FX.flashes) {
    const a = f.life / (f.radius ? 12 : 5);
    ctx.globalAlpha = a * 0.8;
    ctx.fillStyle = f.color;
    ctx.beginPath();
    ctx.arc(f.x, f.y, f.radius ? f.radius * (1 - a + 0.4) : 28 * a + 8, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalCompositeOperation = "source-over";
  ctx.globalAlpha = 1;

  // particles
  for (const p of FX.particles) {
    const a = Math.min(1, p.life / 16);
    ctx.globalAlpha = a;
    if (p.text) {
      ctx.font = `${p.size}px serif`;
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillText(p.text, p.x, p.y);
    } else {
      ctx.fillStyle = p.color;
      ctx.fillRect(p.x - p.size / 2, p.y - p.size / 2, p.size, p.size);
    }
  }
  ctx.globalAlpha = 1;

  // damage popups
  for (const p of FX.popups) {
    const a = Math.min(1, p.life / 30);
    ctx.globalAlpha = a;
    ctx.font = `bold ${p.size}px system-ui`;
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.lineWidth = 3;
    ctx.strokeStyle = "#000";
    ctx.strokeText(p.text, p.x, p.y);
    ctx.fillStyle = p.color;
    ctx.fillText(p.text, p.x, p.y);
  }
  ctx.globalAlpha = 1;
}

function showWaveBanner(text) {
  const el = document.getElementById("waveBanner");
  if (!el) return;
  el.textContent = text;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 1700);
}

function toast(text) {
  const list = document.getElementById("toastList");
  if (!list) return;
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = text;
  list.appendChild(el);
  setTimeout(() => el.remove(), 2600);
}
