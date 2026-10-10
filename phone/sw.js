// Keeps the app working with no signal: every file is cached on first open.
// With a signal the newest files are fetched and cached, so updates arrive;
// without one, the cached copy is used. Sync requests are never cached.
const CACHE = "hello-world-phone-v2";
const FILES = ["./", "./index.html", "./app.js", "./content.js", "./manifest.webmanifest", "./icon.svg"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(
    keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))).then(() => self.clients.claim()));
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.pathname.includes("/v1/")) return;
  event.respondWith(fetch(event.request).then((answer) => {
    if (answer.ok) {
      const copy = answer.clone();
      caches.open(CACHE).then((cache) => cache.put(event.request, copy));
    }
    return answer;
  }).catch(() => caches.match(event.request)));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(self.clients.matchAll({ type: "window" }).then((list) =>
    list.length ? list[0].focus() : self.clients.openWindow("./index.html")));
});
