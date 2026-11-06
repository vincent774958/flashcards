// Bump VERSION whenever index.html changes so phones pick up the new copy.
const VERSION = 'v3';
const CORE = ['./', './index.html', './manifest.webmanifest', './cloud.js', './firebase-config.js',
  './icons/icon-192.png', './icons/icon-512.png', './icons/apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open('core-' + VERSION).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(
    ks.filter(k => k.startsWith('core-') && k !== 'core-' + VERSION).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    // App shell: network first (so updates arrive), fall back to cache offline.
    e.respondWith(fetch(req).then(res => {
      const copy = res.clone();
      caches.open('core-' + VERSION).then(c => c.put(req, copy));
      return res;
    }).catch(() => caches.match(req).then(r => r || caches.match('./index.html'))));
    return;
  }
  // Firebase SDK files: cache-first so the app still starts offline.
  if (url.hostname === 'www.gstatic.com' && url.pathname.startsWith('/firebasejs/')) {
    e.respondWith(caches.open('sdk').then(async c => (await c.match(req)) || fetch(req).then(res => { c.put(req, res.clone()); return res; })));
    return;
  }
  // Card photos from other sites: cache what has been seen, keep at most ~300.
  if (req.destination === 'image') {
    e.respondWith(caches.open('img').then(async c => {
      const hit = await c.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok || res.type === 'opaque') {
        c.put(req, res.clone());
        c.keys().then(ks => ks.length > 300 && c.delete(ks[0]));
      }
      return res;
    }));
  }
});
