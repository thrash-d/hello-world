// Keeps the app working with no signal: every file is cached on first open.
// With a signal the newest files are fetched and cached, so updates arrive;
// without one, the cached copy is used. Sync requests are never cached.
const CACHE = "hello-world-phone-v13";
const FILES = ["./", "./index.html", "./app.js", "./content.js", "./manifest.webmanifest", "./icon.svg"];

// Fifteen minutes either side of a real HH:MM, including across midnight.
// 99:99 and 25:00 are not clock times. The same rule as pushText in app.js.
function nearClock(at, minutes) {
  if (typeof at !== "string" || !/^([01]\d|2[0-3]):[0-5]\d$/.test(at)) return false;
  const [h, m] = at.split(":").map(Number);
  const diff = Math.abs(h * 60 + m - minutes);
  return Math.min(diff, 1440 - diff) <= 15;
}

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(
    keys.filter((key) => key !== CACHE && key !== "hello-world-prefs").map((key) => caches.delete(key)))).then(() => self.clients.claim()));
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

// The server's push has no content. What to show comes from this phone: the
// daily repeat's own words at its time, otherwise "Check-in time".
self.addEventListener("push", (event) => {
  event.waitUntil(caches.open("hello-world-prefs").then((cache) => cache.match("prefs"))
    .then((r) => (r ? r.json() : null)).catch(() => null).then((prefs) => {
      const now = new Date(), minutes = now.getHours() * 60 + now.getMinutes();
      // The same 15 minutes as pushText in app.js, including across midnight.
      // The server retries a missed push for that long. A time that is not
      // a clock time, such as 99:99, is not near: 1440 minus a huge gap
      // would otherwise be negative and always count.
      const body = prefs && prefs.repeat && nearClock(prefs.repeat.at, minutes) ? prefs.repeat.text
        : (prefs && prefs.checkin) || "Check-in time.";
      return self.registration.showNotification("hello-world", { body, icon: "icon.svg" });
    }));
});
