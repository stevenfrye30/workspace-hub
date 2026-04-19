(function() {
  const works = Array.from(document.querySelectorAll('.work'));
  if (!works.length) return;

  const overlay = document.createElement('div');
  overlay.id = 'lightbox';
  overlay.hidden = true;
  overlay.innerHTML = `
    <div class="lb-count"></div>
    <button class="lb-close" aria-label="Close">\u2715</button>
    <button class="lb-prev" aria-label="Previous">\u2039</button>
    <button class="lb-next" aria-label="Next">\u203A</button>
    <figure>
      <img class="lb-img" alt="">
      <figcaption class="lb-cap"></figcaption>
    </figure>
  `;
  document.body.appendChild(overlay);

  const imgEl = overlay.querySelector('.lb-img');
  const capEl = overlay.querySelector('.lb-cap');
  const countEl = overlay.querySelector('.lb-count');
  let idx = -1;

  function open(i) {
    idx = (i + works.length) % works.length;
    const w = works[idx];
    const src = w.querySelector('img')?.src || '';
    const alt = w.querySelector('img')?.alt || '';
    const title = w.querySelector('.t')?.textContent || '';
    const meta = w.querySelector('.meta')?.textContent || '';
    const desc = w.querySelector('.d')?.textContent || '';
    imgEl.src = src;
    imgEl.alt = alt;
    capEl.innerHTML = `<span class="lb-t"></span><span class="lb-m"></span><span class="lb-d"></span>`;
    capEl.querySelector('.lb-t').textContent = title;
    capEl.querySelector('.lb-m').textContent = meta;
    capEl.querySelector('.lb-d').textContent = desc;
    countEl.textContent = `${idx + 1} / ${works.length}`;
    overlay.hidden = false;
    document.body.style.overflow = 'hidden';
  }
  function close() {
    overlay.hidden = true;
    document.body.style.overflow = '';
  }

  works.forEach((w, i) => {
    const img = w.querySelector('img');
    if (img) img.addEventListener('click', () => open(i));
  });
  overlay.querySelector('.lb-close').addEventListener('click', close);
  overlay.querySelector('.lb-prev').addEventListener('click', e => { e.stopPropagation(); open(idx - 1); });
  overlay.querySelector('.lb-next').addEventListener('click', e => { e.stopPropagation(); open(idx + 1); });
  overlay.addEventListener('click', e => { if (e.target === overlay || e.target.tagName === 'FIGURE') close(); });
  document.addEventListener('keydown', e => {
    if (overlay.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') open(idx - 1);
    if (e.key === 'ArrowRight') open(idx + 1);
  });
})();
