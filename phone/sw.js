// Keeps the app working with no signal: every file is cached on first open.
// With a signal the newest files are fetched and cached, so updates arrive;
// without one, the cached copy is used. Sync requests are never cached.
const CACHE = "hello-world-phone-v10";
const FILES = ["./", "./index.html", "./app.js", "./content.js", "./manifest.webmanifest", "./icon.svg",
               "./icon-maskable.svg", "./icon-512.png"];
// pushChoice, shared with the page.
importScripts("./app.js");

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(
    keys.filter((key) => key !== CACHE && key !== "hello-world-prefs").map((key) => caches.delete(key)))).then(() => self.clients.claim()));
});

// The network first, but not for long: on a weak signal the cached copy is
// used after a few seconds instead of waiting.
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.pathname.includes("/v1/")) return;
  const network = fetch(event.request).then((answer) => {
    if (answer.ok) {
      const copy = answer.clone();
      event.waitUntil(caches.open(CACHE).then((cache) => cache.put(event.request, copy)));
    }
    return answer;
  });
  event.respondWith(new Promise((resolve) => {
    let done = false;
    const finish = (answer) => { if (!done && answer) { done = true; resolve(answer); } };
    network.then(finish, () => caches.match(event.request).then((hit) => finish(hit || Response.error())));
    setTimeout(() => caches.match(event.request).then(finish), 4000);
  }));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(self.clients.matchAll({ type: "window" }).then((list) =>
    list.length ? list[0].focus() : self.clients.openWindow("./index.html")));
});

// The server's push has no content. What to show comes from this phone: the
// daily repeat's own words at its time, otherwise "Check-in time".
// When the check-in and the repeat are close together, each push shows the
// one not yet shown today, so both are seen.
self.addEventListener("push", (event) => {
  event.waitUntil(caches.open("hello-world-prefs").then(async (cache) => {
    const prefs = await cache.match("prefs").then((r) => (r ? r.json() : null)).catch(() => null);
    const [kind, shown] = pushChoice(prefs, new Date());
    if (prefs) await cache.put("prefs", new Response(JSON.stringify(Object.assign({}, prefs, { shown }))));
    const body = kind === "repeat" && prefs && prefs.repeat ? prefs.repeat.text
      : (prefs && prefs.checkin) || "Check-in time.";
    return self.registration.showNotification("hello-world", { body, icon: "icon.svg" });
  }));
});
