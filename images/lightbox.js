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

  // Derive a Wikimedia Commons / Wikipedia "File:" page from an upload URL.
  // Handles thumb URLs (/commons/thumb/X/XX/FILE/<size>px-FILE) and direct
  // originals (/commons/X/XX/FILE). Also supports /wikipedia/en/ hosts.
  function sourceUrl(imgSrc) {
    const m = imgSrc.match(
      /^https?:\/\/[^/]+\/wikipedia\/(commons|en)\/(?:thumb\/)?[0-9a-f]\/[0-9a-f]{2}\/([^/]+?)(?:\/[^/]+)?$/
    );
    if (!m) return null;
    const host = m[1] === 'commons' ? 'commons.wikimedia.org' : 'en.wikipedia.org';
    return 'https://' + host + '/wiki/File:' + m[2];
  }

  function isVisible(el) {
    return el.offsetParent !== null;
  }

  function visibleWorks() {
    return works.filter(isVisible);
  }

  function open(i) {
    idx = ((i % works.length) + works.length) % works.length;
    const w = works[idx];
    const src = w.querySelector('img')?.src || '';
    const alt = w.querySelector('img')?.alt || '';
    const title = w.querySelector('.t')?.textContent || '';
    const meta = w.querySelector('.meta')?.textContent || '';
    const desc = w.querySelector('.d')?.textContent || '';
    imgEl.src = src;
    imgEl.alt = alt;
    const source = sourceUrl(src);
    capEl.innerHTML = `<span class="lb-t"></span><span class="lb-m"></span><span class="lb-d"></span>` +
      (source ? `<br><a class="lb-src" target="_blank" rel="noopener">View on Wikimedia Commons \u2197</a>` : '');
    capEl.querySelector('.lb-t').textContent = title;
    capEl.querySelector('.lb-m').textContent = meta;
    capEl.querySelector('.lb-d').textContent = desc;
    if (source) capEl.querySelector('.lb-src').href = source;
    const visible = visibleWorks();
    const visibleIdx = visible.indexOf(w);
    countEl.textContent = visibleIdx >= 0 ? `${visibleIdx + 1} / ${visible.length}` : '';
    overlay.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function step(delta) {
    const visible = visibleWorks();
    if (!visible.length) return;
    const current = works[idx];
    let vi = visible.indexOf(current);
    if (vi < 0) vi = 0;
    vi = ((vi + delta) % visible.length + visible.length) % visible.length;
    open(works.indexOf(visible[vi]));
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
  overlay.querySelector('.lb-prev').addEventListener('click', e => { e.stopPropagation(); step(-1); });
  overlay.querySelector('.lb-next').addEventListener('click', e => { e.stopPropagation(); step(1); });
  overlay.addEventListener('click', e => { if (e.target === overlay || e.target.tagName === 'FIGURE') close(); });
  document.addEventListener('keydown', e => {
    if (overlay.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') step(-1);
    if (e.key === 'ArrowRight') step(1);
  });
})();
