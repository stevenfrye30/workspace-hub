const CACHE = 'mke-v2';

const PRECACHE = [
  './',
  './index.html',
  './map/',
  './map/index.html',
  './manifest.json',
  './icon.svg',
  './orientation/neighborhoods.md',
  './orientation/weather.md',
  './orientation/transit.md',
  './orientation/culture.md',
  './orientation/food.md',
  './orientation/sports.md',
  './orientation/history.md',
  './logistics/checklist.md',
  './logistics/housing.md',
  './logistics/utilities.md',
  './logistics/dmv-and-id.md',
  './logistics/healthcare.md',
  './engagement/news-sources.md',
  './engagement/events.md',
  './engagement/community.md',
  './engagement/places-to-try.md',
  './engagement/daytrips.md',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
  'https://cdn.jsdelivr.net/npm/marked/marked.min.js'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE.map(u => new Request(u, { cache: 'reload' }))).catch(() => {}))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  // Never cache live data endpoints
  if (url.hostname === 'api.weather.gov' || url.hostname.includes('rss2json') || url.hostname.includes('allorigins')) {
    return; // default network
  }
  // Map tiles: network-first, cache as backup
  if (url.hostname.endsWith('tile.openstreetmap.org')) {
    e.respondWith(
      fetch(e.request).then(r => {
        const copy = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return r;
      }).catch(() => caches.match(e.request))
    );
    return;
  }
  // Everything else: cache-first, update in background
  e.respondWith(
    caches.match(e.request).then(hit => {
      const fetchP = fetch(e.request).then(r => {
        if (r && r.status === 200) {
          const copy = r.clone();
          caches.open(CACHE).then(c => c.put(e.request, copy));
        }
        return r;
      }).catch(() => hit);
      return hit || fetchP;
    })
  );
});
