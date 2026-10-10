// hello-world on a phone. Everything is kept in this phone's browser storage
// and nothing is sent anywhere. The logic is plain functions so the tests can
// run them without a browser.
"use strict";

const UI = {
  en: {
    hello: "Hello, world!", ask: "Did you do it?", yesterday: "Yesterday you planned:",
    on: "On {date} you planned:", yes: "Done", no: "Not yet", skip: "Skip",
    todayAsk: "What do you want to get done today?", todayHave: "Your plan for today:",
    did: "Done", clear: "Clear", save: "Save", placeholder: "One thing, or a few with ;",
    thought: "Thought for today:", tip: "Try this today:", settings: "Settings",
    language: "Language", remind: "Reminder", remindOff: "No reminder",
    remindNote: "Phones only let a web page remind you while it is still open in the background, so a reminder can be missed.",
    forget: "Delete everything on this phone", forgetAsk: "Delete your plans and settings from this phone?",
    forgotten: "Everything on this phone was deleted.",
    privacy: "Your plans stay on this phone, in this browser. Nothing is sent anywhere.",
    good: "Good. That one is off your list.", kept: "Kept for today.", skipped: "Skipped. It asks again next time.",
    saved: "Saved.", cleared: "Cleared.", nothing: "Type a word or two first.",
    remindText: "One thing to get done today? Open hello-world.",
    sync: "Sync with a PC", syncCode: "Code from the PC (Sync with my phone, in the PC's menu)", syncSave: "Turn on sync", syncOff: "Turn off sync",
    syncNote: "With sync on, your plan and done list leave this phone, encrypted with that code. The server keeps only the encrypted copy.",
    syncOn: "Sync is on.", syncOffDone: "Sync is off on this phone.", syncBad: "That code doesn't look right. Check it on the PC.", syncFail: "The PC's copy can't be reached just now.",
  },
  es: {
    hello: "¡Hola, mundo!", ask: "¿Lo hiciste?", yesterday: "Ayer planeaste:",
    on: "El {date} planeaste:", yes: "Hecho", no: "Todavía no", skip: "Saltar",
    todayAsk: "¿Qué quieres hacer hoy?", todayHave: "Tu plan para hoy:",
    did: "Hecho", clear: "Borrar", save: "Guardar", placeholder: "Una cosa, o varias con ;",
    thought: "Idea del día:", tip: "Prueba esto hoy:", settings: "Ajustes",
    language: "Idioma", remind: "Recordatorio", remindOff: "Sin recordatorio",
    remindNote: "Los teléfonos solo dejan que una página web te recuerde algo mientras sigue abierta en segundo plano, así que un recordatorio se puede perder.",
    forget: "Borrar todo en este teléfono", forgetAsk: "¿Borrar tus planes y ajustes de este teléfono?",
    forgotten: "Se borró todo en este teléfono.",
    privacy: "Tus planes se quedan en este teléfono, en este navegador. No se envía nada a ningún sitio.",
    good: "Bien. Una cosa menos en tu lista.", kept: "Se queda para hoy.", skipped: "Saltado. Volverá a preguntar la próxima vez.",
    saved: "Guardado.", cleared: "Borrado.", nothing: "Escribe una o dos palabras primero.",
    remindText: "¿Algo que hacer hoy? Abre hello-world.",
    sync: "Sincronizar con un PC", syncCode: "Código del PC (Sincronizar con mi teléfono, en el menú del PC)", syncSave: "Activar sincronización", syncOff: "Desactivar sincronización",
    syncNote: "Con la sincronización activada, tu plan y tu lista de hechos salen de este teléfono, cifrados con ese código. El servidor solo guarda la copia cifrada.",
    syncOn: "La sincronización está activada.", syncOffDone: "La sincronización está desactivada en este teléfono.", syncBad: "Ese código no parece correcto. Revísalo en el PC.", syncFail: "Ahora no se puede llegar a la copia del PC.",
  },
  ar: {
    hello: "مرحبًا بالعالم!", ask: "هل فعلتها؟", yesterday: "خططت أمس:",
    on: "خططت يوم {date}:", yes: "تم", no: "ليس بعد", skip: "تخطَّ",
    todayAsk: "ماذا تريد أن تنجز اليوم؟", todayHave: "خطتك لليوم:",
    did: "تم", clear: "امسح", save: "احفظ", placeholder: "شيء واحد، أو عدة أشياء بينها ;",
    thought: "فكرة اليوم:", tip: "جرّب هذا اليوم:", settings: "الإعدادات",
    language: "اللغة", remind: "التذكير", remindOff: "بلا تذكير",
    remindNote: "لا تسمح الهواتف لصفحة ويب بالتذكير إلا وهي مفتوحة في الخلفية، لذا قد يفوتك التذكير.",
    forget: "احذف كل شيء على هذا الهاتف", forgetAsk: "حذف خططك وإعداداتك من هذا الهاتف؟",
    forgotten: "حُذف كل شيء على هذا الهاتف.",
    privacy: "تبقى خططك على هذا الهاتف، في هذا المتصفح. لا يُرسل شيء إلى أي مكان.",
    good: "جيد. شيء أقل في قائمتك.", kept: "تبقى لليوم.", skipped: "تم التخطي. سيسأل مرة أخرى في المرة القادمة.",
    saved: "تم الحفظ.", cleared: "تم المسح.", nothing: "اكتب كلمة أو كلمتين أولًا.",
    remindText: "شيء تنجزه اليوم؟ افتح hello-world.",
    sync: "المزامنة مع كمبيوتر", syncCode: "الرمز من الكمبيوتر (المزامنة مع هاتفي، في قائمة الكمبيوتر)", syncSave: "شغّل المزامنة", syncOff: "أوقف المزامنة",
    syncNote: "مع تشغيل المزامنة تغادر خطتك وقائمة ما أنجزته هذا الهاتف مشفّرة بذلك الرمز. لا يحتفظ الخادم إلا بالنسخة المشفّرة.",
    syncOn: "المزامنة تعمل.", syncOffDone: "المزامنة متوقفة على هذا الهاتف.", syncBad: "لا يبدو هذا الرمز صحيحًا. تحقق منه على الكمبيوتر.", syncFail: "لا يمكن الوصول إلى نسخة الكمبيوتر الآن.",
  },
};
const LANG_NAMES = { en: "English", es: "Español", ar: "العربية" };
// The cart vendor asked for 6:15, before the lunch rush.
const REMIND_TIMES = ["06:15", "07:00", "08:00", "09:00", "12:00", "18:00"];
const KEY = "hello-world";
const MAX_PLAN = 200;

function iso(d) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// Python's date.toordinal(), so the phone picks the same pair as the PC.
function ordinal(isoDate) {
  const [y, m, d] = isoDate.split("-").map(Number);
  return Math.floor(Date.UTC(y, m - 1, d) / 86400000) + 719163;
}

function todaysPair(lang, isoDate, content) {
  const data = content.langs[lang] || content.langs.en;
  const thoughts = data.thoughts, tips = data.tips;
  const n = ordinal(isoDate);
  const tip = tips[n % tips.length];
  let i = (n + 37) % thoughts.length;
  for (let k = 0; k < thoughts.length; k++) {
    const t = thoughts[i].toLowerCase(), p = tip.toLowerCase();
    if (!content.topics.some((w) => p.includes(w) && t.includes(w))) break;
    i = (i + 1) % thoughts.length;
  }
  return [thoughts[i], tip];
}

function clean(text) {
  const parts = String(text || "").split(";").map((s) => s.replace(/\s+/g, " ").trim()).filter(Boolean);
  return parts.join("; ").slice(0, MAX_PLAN).trim();
}

function blank() {
  return { intent: null, finished: [], lang: null, remind: null };
}

function parse(raw) {
  try {
    const data = JSON.parse(raw);
    const state = blank();
    if (data && data.intent && typeof data.intent.text === "string" && /^\d{4}-\d{2}-\d{2}$/.test(data.intent.date)) {
      state.intent = { text: clean(data.intent.text), date: data.intent.date, skips: Number(data.intent.skips) || 0 };
    }
    if (Array.isArray(data.finished)) {
      state.finished = data.finished.filter((f) => f && typeof f.text === "string").slice(-100);
    }
    if (UI[data.lang]) state.lang = data.lang;
    if (REMIND_TIMES.includes(data.remind)) state.remind = data.remind;
    if (typeof data.updated === "string" && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$/.test(data.updated)) state.updated = data.updated;
    return state;
  } catch (e) {
    return blank();
  }
}

function asks(state, today) {
  const intent = state.intent;
  return Boolean(intent && intent.date < today && (intent.skips || 0) < 2);
}

function answer(state, choice, today) {
  const intent = state.intent;
  if (!asks(state, today)) return "";
  if (choice === "yes") {
    state.finished.push({ text: intent.text, date: intent.date });
    state.intent = null;
    return "good";
  }
  if (choice === "no") {
    state.intent = { text: intent.text, date: today, skips: 0 };
    return "kept";
  }
  intent.skips = (intent.skips || 0) + 1;
  return "skipped";
}

function setPlan(state, text, today) {
  const plan = clean(text);
  if (!plan) return "nothing";
  state.intent = { text: plan, date: today, skips: 0 };
  return "saved";
}

function finishToday(state, today) {
  if (!state.intent) return "";
  state.finished.push({ text: state.intent.text, date: today });
  state.intent = null;
  return "good";
}

function language(state, navigatorLanguages) {
  if (state.lang) return state.lang;
  for (const tag of navigatorLanguages || []) {
    const code = String(tag).slice(0, 2).toLowerCase();
    if (UI[code]) return code;
  }
  return "en";
}


// Sync, the same scheme as hello.py: PBKDF2-SHA256 makes a label and two
// keys from the code; HMAC-SHA256 in counter mode encrypts, and an HMAC tag
// over the result catches any change.
const SYNC_SALT = "hello-world sync v1";
const SYNC_ROUNDS = 200000;
const SYNC_ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789";
const enc8 = (text) => new TextEncoder().encode(text);
const hex = (bytes) => Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");

function normalCode(code) {
  return Array.from(String(code).toLowerCase()).filter((c) => SYNC_ALPHABET.includes(c)).join("");
}

async function syncKeys(code) {
  const subtle = globalThis.crypto.subtle;
  const base = await subtle.importKey("raw", enc8(normalCode(code)), "PBKDF2", false, ["deriveBits"]);
  const raw = new Uint8Array(await subtle.deriveBits(
    { name: "PBKDF2", salt: enc8(SYNC_SALT), iterations: SYNC_ROUNDS, hash: "SHA-256" }, base, 768));
  return { label: hex(raw.slice(0, 32)), enc: raw.slice(32, 64), mac: raw.slice(64, 96) };
}

async function hmacKey(raw) {
  return globalThis.crypto.subtle.importKey("raw", raw, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
}

async function stream(key, nonce, size) {
  const k = await hmacKey(key), out = new Uint8Array(Math.ceil(size / 32) * 32);
  for (let i = 0; i * 32 < size; i++) {
    const block = new Uint8Array(nonce.length + 4);
    block.set(nonce);
    new DataView(block.buffer).setUint32(nonce.length, i);
    out.set(new Uint8Array(await globalThis.crypto.subtle.sign("HMAC", k, block)), i * 32);
  }
  return out.slice(0, size);
}

async function sealSync(keys, data, nonce) {
  nonce = nonce || globalThis.crypto.getRandomValues(new Uint8Array(16));
  const plain = enc8(JSON.stringify(data));
  const ks = await stream(keys.enc, nonce, plain.length);
  const cipher = plain.map((b, i) => b ^ ks[i]);
  const head = new Uint8Array(2 + 16 + cipher.length);
  head.set(enc8("v1")); head.set(nonce, 2); head.set(cipher, 18);
  const tag = new Uint8Array(await globalThis.crypto.subtle.sign("HMAC", await hmacKey(keys.mac), head));
  const out = new Uint8Array(head.length + 32);
  out.set(head); out.set(tag, head.length);
  return out;
}

async function openSync(keys, blob) {
  blob = new Uint8Array(blob);
  if (blob.length < 50 || blob[0] !== 118 || blob[1] !== 49) return null;
  const head = blob.slice(0, blob.length - 32), tag = blob.slice(blob.length - 32);
  const expect = new Uint8Array(await globalThis.crypto.subtle.sign("HMAC", await hmacKey(keys.mac), head));
  let diff = 0;
  for (let i = 0; i < 32; i++) diff |= expect[i] ^ tag[i];
  if (diff) return null;
  const nonce = head.slice(2, 18), cipher = head.slice(18);
  const ks = await stream(keys.enc, nonce, cipher.length);
  try {
    const data = JSON.parse(new TextDecoder().decode(cipher.map((b, i) => b ^ ks[i])));
    return data && typeof data === "object" ? data : null;
  } catch (e) {
    return null;
  }
}

function syncForm(state) {
  return { intent: state.intent ? { text: state.intent.text, date: state.intent.date } : null,
           finished: state.finished, updated: state.updated || "" };
}

// Finished things from both sides, and the plan from whichever side changed
// it last, as hello.py's merge_sync does.
function mergeSync(state, other, today) {
  const have = new Set(state.finished.map((f) => f.text + "\n" + f.date));
  for (const item of other.finished || []) {
    if (item && typeof item.text === "string" && /^\d{4}-\d{2}-\d{2}$/.test(item.date) && item.date <= today
        && !have.has(item.text + "\n" + item.date)) {
      state.finished.push({ text: clean(item.text), date: item.date });
      have.add(item.text + "\n" + item.date);
    }
  }
  state.finished.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));
  state.finished = state.finished.slice(-100);
  const theirs = typeof other.updated === "string" ? other.updated : "";
  if (theirs > (state.updated || "")) {
    const i = other.intent;
    state.intent = i && typeof i.text === "string" && clean(i.text) && /^\d{4}-\d{2}-\d{2}$/.test(i.date)
      ? { text: clean(i.text), date: i.date, skips: 0 } : null;
    state.updated = theirs;
  }
  return state;
}

function stamp(state) {
  const d = new Date(), pad = (n) => String(n).padStart(2, "0");
  state.updated = `${iso(d)}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

if (typeof module !== "undefined") {
  module.exports = { UI, ordinal, todaysPair, clean, parse, asks, answer, setPlan, finishToday, language, blank,
    syncKeys, sealSync, openSync, mergeSync, syncForm, normalCode };
}

if (typeof document !== "undefined") {
  const $ = (id) => document.getElementById(id);
  let state = parse(localStorage.getItem(KEY) || "{}");
  let timer = null;
  const save = () => {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* private mode */ }
  };
  const t = () => UI[language(state, navigator.languages)];
  const say = (key) => { $("status").textContent = key ? t()[key] : ""; };

  function longDate(isoDate, lang) {
    const [y, m, d] = isoDate.split("-").map(Number);
    return new Date(y, m - 1, d).toLocaleDateString(lang, { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  }

  function schedule() {
    clearTimeout(timer);
    if (!state.remind || typeof Notification === "undefined" || Notification.permission !== "granted") return;
    const now = new Date();
    const [h, m] = state.remind.split(":").map(Number);
    const at = new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, m);
    if (at <= now) at.setDate(at.getDate() + 1);
    timer = setTimeout(async () => {
      const reg = navigator.serviceWorker && await navigator.serviceWorker.ready;
      if (reg) reg.showNotification("hello-world", { body: t().remindText, icon: "icon.svg" });
      schedule();
    }, at - now);
  }

  function draw() {
    const lang = language(state, navigator.languages), s = UI[lang], today = iso(new Date());
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    $("hello").textContent = s.hello;
    $("date").textContent = longDate(today, lang);
    const asking = asks(state, today);
    $("ask").hidden = !asking;
    if (asking) {
      const yesterday = iso(new Date(Date.now() - 86400000));
      $("ask-label").textContent = s.ask + " " + (state.intent.date === yesterday ? s.yesterday : s.on.replace("{date}", longDate(state.intent.date, lang)));
      $("ask-plan").textContent = state.intent.text;
    }
    ["yes", "no", "skip", "did", "clear", "save"].forEach((id) => { $(id).textContent = s[id]; });
    const planned = state.intent && state.intent.date === today;
    $("today-label").textContent = planned ? s.todayHave : s.todayAsk;
    $("today-plan").hidden = $("today-buttons").hidden = !planned;
    $("today-plan").textContent = planned ? state.intent.text : "";
    $("plan-form").hidden = planned || asking;
    $("plan-input").placeholder = s.placeholder;
    const [thought, tip] = todaysPair(lang, today, CONTENT);
    $("thought-label").textContent = s.thought;
    $("thought").textContent = thought;
    $("tip-label").textContent = s.tip;
    $("tip").textContent = tip;
    $("settings-label").textContent = s.settings;
    $("language-label").textContent = s.language;
    $("remind-label").textContent = s.remind;
    $("remind-note").textContent = s.remindNote;
    $("forget").textContent = s.forget;
    $("privacy").textContent = s.privacy;
    $("language").replaceChildren(...Object.keys(UI).map((code) => new Option(LANG_NAMES[code], code, false, code === lang)));
    if (typeof drawSync === "function") drawSync();
    $("remind").replaceChildren(new Option(s.remindOff, "", false, !state.remind),
      ...REMIND_TIMES.map((at) => new Option(at, at, false, at === state.remind)));
  }

  const SYNC_KEY = "hello-world-sync";
  let keys = null;
  try { keys = JSON.parse(localStorage.getItem(SYNC_KEY) || "null"); } catch (e) { keys = null; }
  const asBytes = (k) => k && { label: k.label, enc: Uint8Array.from(k.enc), mac: Uint8Array.from(k.mac) };

  // Pull, merge and push; quiet unless something goes wrong while asked.
  async function sync(loud) {
    if (!keys) return;
    const k = asBytes(keys), url = `${location.origin}/v1/sync/${k.label}`;
    try {
      const got = await fetch(url, { cache: "no-store" });
      if (got.ok) {
        const other = await openSync(k, await got.arrayBuffer());
        if (other) { mergeSync(state, other, iso(new Date())); save(); draw(); }
      }
      await fetch(url, { method: "PUT", body: await sealSync(k, syncForm(state)),
                         headers: { "Content-Type": "application/octet-stream" } });
      if (loud) say("syncOn");
    } catch (e) {
      if (loud) say("syncFail");
    }
  }

  function drawSync() {
    const s = t();
    $("sync-label").textContent = s.sync;
    $("sync-code-label").textContent = s.syncCode;
    $("sync-save").textContent = keys ? s.syncOff : s.syncSave;
    $("sync-code").hidden = $("sync-code-label").hidden = Boolean(keys);
    $("sync-note").textContent = s.syncNote;
  }

  $("sync-save").addEventListener("click", async (event) => {
    event.preventDefault();
    if (keys) {
      keys = null;
      try { localStorage.removeItem(SYNC_KEY); } catch (e) { /* nothing saved */ }
      drawSync(); say("syncOffDone");
      return;
    }
    if (normalCode($("sync-code").value).length !== 25) { say("syncBad"); return; }
    const k = await syncKeys($("sync-code").value);
    keys = { label: k.label, enc: Array.from(k.enc), mac: Array.from(k.mac) };
    try { localStorage.setItem(SYNC_KEY, JSON.stringify(keys)); } catch (e) { /* private mode */ }
    $("sync-code").value = "";
    drawSync();
    await sync(true);
  });

  const act = (fn) => (event) => {
    if (event) event.preventDefault();
    const before = JSON.stringify(state.intent && { text: state.intent.text, date: state.intent.date });
    const said = fn();
    if (JSON.stringify(state.intent && { text: state.intent.text, date: state.intent.date }) !== before) stamp(state);
    save(); draw(); say(said);
    sync(false);
  };
  $("yes").addEventListener("click", act(() => answer(state, "yes", iso(new Date()))));
  $("no").addEventListener("click", act(() => answer(state, "no", iso(new Date()))));
  $("skip").addEventListener("click", act(() => answer(state, "skip", iso(new Date()))));
  $("did").addEventListener("click", act(() => finishToday(state, iso(new Date()))));
  $("clear").addEventListener("click", act(() => { state.intent = null; return "cleared"; }));
  $("plan-form").addEventListener("submit", act(() => {
    const said = setPlan(state, $("plan-input").value, iso(new Date()));
    if (said === "saved") $("plan-input").value = "";
    return said;
  }));
  $("language").addEventListener("change", act(() => { state.lang = $("language").value; return ""; }));
  $("remind").addEventListener("change", async () => {
    state.remind = $("remind").value || null;
    // Asked only when someone picks a time; no reminder unless asked (the rider).
    if (state.remind && typeof Notification !== "undefined" && Notification.permission === "default") {
      await Notification.requestPermission();
    }
    save(); schedule();
  });
  $("forget").addEventListener("click", () => {
    if (!confirm(t().forgetAsk)) return;
    const lang = state.lang;
    try { localStorage.removeItem(KEY); localStorage.removeItem(SYNC_KEY); } catch (e) { /* nothing saved */ }
    keys = null;
    drawSync();
    state = blank();
    state.lang = lang;
    draw(); say("forgotten"); schedule();
  });
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
  draw();
  drawSync();
  schedule();
  sync(false);
}
