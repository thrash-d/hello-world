// hello-world on a phone. Plans are kept in this phone's browser storage.
// They leave it only with sync turned on, encrypted; a reminder turned on
// sends the server a random token, the browser's push address and the times,
// never the plan. The logic is plain functions so the tests can run them
// without a browser.
"use strict";

const SCAM_EN = "hello-world has no phone line and no support staff. We never call, email or text. Nobody real will ever ask for your sync code. If someone asks, hang up.";
const UI = {
  en: {
    hello: "Hello, world!", ask: "Did you do it?", yesterday: "Yesterday you planned:",
    on: "On {date} you planned:", yes: "Done", no: "Not yet", skip: "Skip",
    sideways: "The day went sideways", sidewaysSaid: "That's okay. It's set aside, and tomorrow is new.",
    carryIt: "Carry it over", asideIt: "Set it aside", carriedSaid: "That's okay. It's carried over to today.",
    fresh: "Fresh day. Bring it over, or start clean?", bring: "Bring it over", startClean: "Start clean",
    cleanSaid: "Starting clean. It's set aside; tap it below to bring it back.",
    comingBack: "This one keeps coming back. Make it smaller, or set it aside?", makeSmaller: "Make it smaller",
    keepIt: "Keep it", smallerSaid: "Smaller it is. The bigger one is set aside.",
    smallerNudge: "Want today's plan smaller? Small is fine.",
    endDay: "End the day", endDone: "Done", endCarry: "Carry to tomorrow", endAside: "Set aside",
    endClose: "Close the day", endTally: "Done {done}, carried {carried}, set aside {aside}. The day is closed.",
    large: "Large print", usual: "Usual print",
    todayAsk: "Anything for today? Small is fine.", todayHave: "Your plan for today:",
    picks: "Put aside, tap one to bring it back:", back: "Back on today's plan.",
    did: "Done", clear: "Set aside", save: "Save", placeholder: "One thing, or a few with ;",
    thought: "Thought for today:", tip: "Try this today:", settings: "Settings",
    language: "Language", remind: "Reminder", remindOff: "No reminder",
    remindNote: "The reminder comes through the server this app came from, with nothing in it: the server keeps only a random number, your browser's push address and the time. On an iPhone, add hello-world to the Home Screen first.",
    remindLocal: "This server doesn't send reminders, so one comes only while this page is still open in the background, and can be missed.",
    remindShown: "Check-in time.", remindFail: "The reminder couldn't be set up on this phone.",
    dayStart: "My day starts at", midnight: "Midnight",
    dayStartNote: "18:00 keeps a night shift from 22:00 to 6:00 on one day; midnight splits it.",
    repeat: "Every day", repeatPlaceholder: "Something to do every day", repeatAt: "At",
    repeatNote: "A reminder only, not a medical device. Its words stay on this phone.",
    repeatOff: "Off", repeatSaved: "The daily reminder is saved.",
    family: "Family", familyName: "Their name", familyNumber: "Their phone number",
    familyNote: "Kept only on this phone. The buttons open your phone's own text or call screen; nothing is sent unless you press send there.",
    familySave: "Save", draft: "Draft text to {name}", call: "Call {name}", okayText: "I'm okay today.",
    print: "Print a big page", printNote: "Anyone in the room can read a printed page. The sync code is never on it.",
    printTitle: "Today", printRepeat: "Every day at {at}:",
    export: "Save my plans to a file", exported: "Saved to a file.",
    forget: "Delete everything on this phone", forgetAsk: "Delete your plans and settings from this phone?",
    forgotten: "Everything on this phone was deleted.",
    privacy: "Your plans stay on this phone, in this browser. They leave it only if you turn on sync.",
    good: "Good. That one is off your list.", kept: "Kept for today.", skipped: "Skipped. It asks again next time.",
    saved: "Saved.", cleared: "Set aside. Tap it below to bring it back.", nothing: "Type a word or two first.",
    sync: "Sync with a PC", syncCode: "Code from the PC (Sync with my phone, in the PC's menu)", syncSave: "Turn on sync", syncOff: "Turn off sync",
    syncChange: "Change code", syncChangeNote: "Type the new code the PC shows.",
    syncNote: "With sync on, your plan and done list leave this phone, encrypted with that code. The server keeps only the encrypted copy.",
    syncOn: "Sync is on.", syncOffDone: "Sync is off on this phone.", syncBad: "That code doesn't look right. Check it on the PC.", syncFail: "The PC's copy can't be reached just now.",
    scam: SCAM_EN,
    familyScam: "hello-world will never ask you for a code or key.",
    lastChange: "Last change to your synced plan: {when}. If you didn't make it, change the code on the PC.",
  },
  es: {
    hello: "¡Hola, mundo!", ask: "¿Lo hiciste?", yesterday: "Ayer planeaste:",
    on: "El {date} planeaste:", yes: "Hecho", no: "Todavía no", skip: "Saltar",
    sideways: "El día salió de lado", sidewaysSaid: "No pasa nada. Queda apartado, y mañana es un día nuevo.",
    carryIt: "Llevarlo a hoy", asideIt: "Apartarlo", carriedSaid: "No pasa nada. Pasa a hoy.",
    fresh: "Día nuevo. ¿Lo traes o empiezas de cero?", bring: "Traerlo", startClean: "Empezar de cero",
    cleanSaid: "Empiezas de cero. Queda apartado; tócalo abajo para recuperarlo.",
    comingBack: "Este vuelve una y otra vez. ¿Lo haces más pequeño o lo apartas?", makeSmaller: "Hacerlo más pequeño",
    keepIt: "Dejarlo", smallerSaid: "Más pequeño, entonces. El grande queda apartado.",
    smallerNudge: "¿Un plan más pequeño hoy? Algo pequeño está bien.",
    endDay: "Cerrar el día", endDone: "Hecho", endCarry: "Pasar a mañana", endAside: "Apartar",
    endClose: "Cerrar el día", endTally: "Hechos {done}, pasados {carried}, apartados {aside}. El día está cerrado.",
    large: "Letra grande", usual: "Letra normal",
    todayAsk: "¿Algo para hoy? Algo pequeño está bien.", todayHave: "Tu plan para hoy:",
    picks: "Apartados, toca uno para recuperarlo:", back: "De nuevo en el plan de hoy.",
    did: "Hecho", clear: "Apartar", save: "Guardar", placeholder: "Una cosa, o varias con ;",
    thought: "Idea del día:", tip: "Prueba esto hoy:", settings: "Ajustes",
    language: "Idioma", remind: "Recordatorio", remindOff: "Sin recordatorio",
    remindNote: "El recordatorio llega a través del servidor del que vino esta app, sin nada dentro: el servidor solo guarda un número al azar, la dirección de notificaciones de tu navegador y la hora. En un iPhone, añade hello-world a la pantalla de inicio primero.",
    remindLocal: "Este servidor no envía recordatorios, así que uno solo llega mientras esta página sigue abierta en segundo plano, y se puede perder.",
    remindShown: "Hora de revisar.", remindFail: "No se pudo activar el recordatorio en este teléfono.",
    dayStart: "Mi día empieza a las", midnight: "Medianoche",
    dayStartNote: "18:00 deja un turno de noche de 22:00 a 6:00 en un solo día; medianoche lo parte.",
    repeat: "Cada día", repeatPlaceholder: "Algo que hacer cada día", repeatAt: "A las",
    repeatNote: "Solo un recordatorio, no un dispositivo médico. Sus palabras se quedan en este teléfono.",
    repeatOff: "Apagado", repeatSaved: "El recordatorio diario está guardado.",
    family: "Familia", familyName: "Su nombre", familyNumber: "Su número de teléfono",
    familyNote: "Se guarda solo en este teléfono. Los botones abren la pantalla de mensajes o llamadas de tu teléfono; no se envía nada si no pulsas enviar allí.",
    familySave: "Guardar", draft: "Escribir mensaje a {name}", call: "Llamar a {name}", okayText: "Hoy estoy bien.",
    print: "Imprimir una página grande", printNote: "Cualquiera en la habitación puede leer una página impresa. El código de sincronización nunca aparece en ella.",
    printTitle: "Hoy", printRepeat: "Cada día a las {at}:",
    export: "Guardar mis planes en un archivo", exported: "Guardado en un archivo.",
    forget: "Borrar todo en este teléfono", forgetAsk: "¿Borrar tus planes y ajustes de este teléfono?",
    forgotten: "Se borró todo en este teléfono.",
    privacy: "Tus planes se quedan en este teléfono, en este navegador. Solo salen de él si activas la sincronización.",
    good: "Bien. Una cosa menos en tu lista.", kept: "Se queda para hoy.", skipped: "Saltado. Volverá a preguntar la próxima vez.",
    saved: "Guardado.", cleared: "Apartado. Tócalo abajo para recuperarlo.", nothing: "Escribe una o dos palabras primero.",
    sync: "Sincronizar con un PC", syncCode: "Código del PC (Sincronizar con mi teléfono, en el menú del PC)", syncSave: "Activar sincronización", syncOff: "Desactivar sincronización",
    syncChange: "Cambiar código", syncChangeNote: "Escribe el código nuevo que muestra el PC.",
    syncNote: "Con la sincronización activada, tu plan y tu lista de hechos salen de este teléfono, cifrados con ese código. El servidor solo guarda la copia cifrada.",
    syncOn: "La sincronización está activada.", syncOffDone: "La sincronización está desactivada en este teléfono.", syncBad: "Ese código no parece correcto. Revísalo en el PC.", syncFail: "Ahora no se puede llegar a la copia del PC.",
    scam: "hello-world no tiene línea telefónica ni personal de soporte. Nunca llamamos, ni enviamos correos ni mensajes. Nadie de verdad te pedirá nunca tu código de sincronización. Si alguien lo pide, cuelga.",
    familyScam: "hello-world nunca te pedirá un código ni una clave.",
    lastChange: "Último cambio en tu plan sincronizado: {when}. Si no lo hiciste tú, cambia el código en el PC.",
  },
  ar: {
    hello: "مرحبًا بالعالم!", ask: "هل فعلتها؟", yesterday: "خططت أمس:",
    on: "خططت يوم {date}:", yes: "تم", no: "ليس بعد", skip: "تخطَّ",
    sideways: "اليوم لم يسر كما يجب", sidewaysSaid: "لا بأس. أُجّلت، والغد يوم جديد.",
    carryIt: "انقلها إلى اليوم", asideIt: "أجّلها", carriedSaid: "لا بأس. نُقلت إلى اليوم.",
    fresh: "يوم جديد. تنقلها أم تبدأ من جديد؟", bring: "انقلها", startClean: "ابدأ من جديد",
    cleanSaid: "تبدأ من جديد. أُجّلت؛ المسها في الأسفل لإعادتها.",
    comingBack: "هذه تعود كل مرة. تجعلها أصغر أم تؤجلها؟", makeSmaller: "اجعلها أصغر",
    keepIt: "أبقها", smallerSaid: "أصغر إذن. الكبيرة أُجّلت.",
    smallerNudge: "خطة أصغر اليوم؟ الصغير يكفي.",
    endDay: "أنهِ اليوم", endDone: "تم", endCarry: "انقلها إلى الغد", endAside: "أجّلها",
    endClose: "أغلق اليوم", endTally: "تم {done}، نُقل {carried}، أُجّل {aside}. أُغلق اليوم.",
    large: "خط كبير", usual: "خط عادي",
    todayAsk: "أي شيء لليوم؟ الصغير يكفي.", todayHave: "خطتك لليوم:",
    picks: "خطط مؤجلة، المس واحدة لإعادتها:", back: "عادت إلى خطة اليوم.",
    did: "تم", clear: "أجّل", save: "احفظ", placeholder: "شيء واحد، أو عدة أشياء بينها ;",
    thought: "فكرة اليوم:", tip: "جرّب هذا اليوم:", settings: "الإعدادات",
    language: "اللغة", remind: "التذكير", remindOff: "بلا تذكير",
    remindNote: "يصل التذكير عبر الخادم الذي جاء منه هذا التطبيق، دون أي محتوى: لا يحتفظ الخادم إلا برقم عشوائي وعنوان الإشعارات في متصفحك والوقت. على iPhone، أضف hello-world إلى الشاشة الرئيسية أولًا.",
    remindLocal: "هذا الخادم لا يرسل تذكيرات، لذا لا يصل التذكير إلا والصفحة مفتوحة في الخلفية، وقد يفوتك.",
    remindShown: "وقت المراجعة.", remindFail: "تعذّر إعداد التذكير على هذا الهاتف.",
    dayStart: "يبدأ يومي في", midnight: "منتصف الليل",
    dayStartNote: "18:00 تُبقي المناوبة الليلية من 22:00 إلى 6:00 يومًا واحدًا؛ منتصف الليل يقسمها.",
    repeat: "كل يوم", repeatPlaceholder: "شيء تفعله كل يوم", repeatAt: "في",
    repeatNote: "تذكير فقط، وليس جهازًا طبيًا. تبقى كلماته على هذا الهاتف.",
    repeatOff: "متوقف", repeatSaved: "حُفظ التذكير اليومي.",
    family: "العائلة", familyName: "الاسم", familyNumber: "رقم الهاتف",
    familyNote: "يُحفظ على هذا الهاتف فقط. تفتح الأزرار شاشة الرسائل أو الاتصال في هاتفك؛ لا يُرسل شيء ما لم تضغط إرسال هناك.",
    familySave: "احفظ", draft: "اكتب رسالة إلى {name}", call: "اتصل بـ{name}", okayText: "أنا بخير اليوم.",
    print: "اطبع صفحة كبيرة", printNote: "يستطيع أي شخص في الغرفة قراءة الصفحة المطبوعة. رمز المزامنة لا يظهر عليها أبدًا.",
    printTitle: "اليوم", printRepeat: "كل يوم في {at}:",
    export: "احفظ خططي في ملف", exported: "حُفظت في ملف.",
    forget: "احذف كل شيء على هذا الهاتف", forgetAsk: "حذف خططك وإعداداتك من هذا الهاتف؟",
    forgotten: "حُذف كل شيء على هذا الهاتف.",
    privacy: "تبقى خططك على هذا الهاتف، في هذا المتصفح. لا تغادره إلا إذا شغّلت المزامنة.",
    good: "جيد. شيء أقل في قائمتك.", kept: "تبقى لليوم.", skipped: "تم التخطي. سيسأل مرة أخرى في المرة القادمة.",
    saved: "تم الحفظ.", cleared: "أُجّلت. المسها في الأسفل لإعادتها.", nothing: "اكتب كلمة أو كلمتين أولًا.",
    sync: "المزامنة مع كمبيوتر", syncCode: "الرمز من الكمبيوتر (المزامنة مع هاتفي، في قائمة الكمبيوتر)", syncSave: "شغّل المزامنة", syncOff: "أوقف المزامنة",
    syncChange: "غيّر الرمز", syncChangeNote: "اكتب الرمز الجديد الذي يظهره الكمبيوتر.",
    syncNote: "مع تشغيل المزامنة تغادر خطتك وقائمة ما أنجزته هذا الهاتف مشفّرة بذلك الرمز. لا يحتفظ الخادم إلا بالنسخة المشفّرة.",
    syncOn: "المزامنة تعمل.", syncOffDone: "المزامنة متوقفة على هذا الهاتف.", syncBad: "لا يبدو هذا الرمز صحيحًا. تحقق منه على الكمبيوتر.", syncFail: "لا يمكن الوصول إلى نسخة الكمبيوتر الآن.",
    scam: "ليس لدى hello-world خط هاتف ولا فريق دعم. لا نتصل ولا نرسل بريدًا أو رسائل أبدًا. لن يطلب منك أي شخص حقيقي رمز المزامنة. إن طلبه أحد، أغلق الخط.",
    familyScam: "لن يطلب منك hello-world أبدًا رمزًا أو مفتاحًا.",
    lastChange: "آخر تغيير في خطتك المتزامنة: {when}. إن لم تقم به، غيّر الرمز على الكمبيوتر.",
  },
};
const LANG_NAMES = { en: "English", es: "Español", ar: "العربية" };
// The cart vendor asked for 6:15, before the lunch rush; 13:00 to 22:00 for
// late sleepers and night shifts.
const REMIND_TIMES = ["06:15", "07:00", "08:00", "09:00", "12:00", "13:00", "15:00", "18:00", "22:00"];
const DAY_STARTS = [0, 4, 12, 18];
const KEY = "hello-world";
const MAX_PLAN = 200;
const MAX_ASIDE = 20;
const MAX_PICKS = 3;

function iso(d) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// Today in the person's own day: with a day start of 18, 2:00 on Tuesday is
// still Monday (Marisol's night shift).
function todayOf(state, now) {
  now = now || new Date();
  return iso(new Date(now.getTime() - (state.dayStart || 0) * 3600000));
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
  return { intent: null, finished: [], lang: null, remind: null, dayStart: 0, aside: [],
           repeat: null, family: null };
}

const isDate = (v) => typeof v === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v);

function parse(raw) {
  try {
    const data = JSON.parse(raw);
    const state = blank();
    if (data && data.intent && typeof data.intent.text === "string" && isDate(data.intent.date)) {
      state.intent = { text: clean(data.intent.text), date: data.intent.date, skips: Number(data.intent.skips) || 0 };
    }
    if (Array.isArray(data.finished)) {
      state.finished = data.finished.filter((f) => f && typeof f.text === "string").slice(-100);
    }
    if (Array.isArray(data.aside)) {
      state.aside = data.aside.filter((a) => a && typeof a.text === "string" && clean(a.text) && isDate(a.date))
        .map((a) => ({ text: clean(a.text), date: a.date })).slice(-MAX_ASIDE);
    }
    if (UI[data.lang]) state.lang = data.lang;
    if (REMIND_TIMES.includes(data.remind)) state.remind = data.remind;
    if (DAY_STARTS.includes(data.dayStart)) state.dayStart = data.dayStart;
    if (data.repeat && typeof data.repeat.text === "string" && clean(data.repeat.text)
        && REMIND_TIMES.includes(data.repeat.at)) {
      state.repeat = { text: clean(data.repeat.text), at: data.repeat.at };
    }
    if (data.family && typeof data.family.name === "string" && typeof data.family.number === "string") {
      const number = phoneNumber(data.family.number);
      if (number) state.family = { name: data.family.name.trim().slice(0, 40), number };
    }
    if (Array.isArray(data.sideways)) state.sideways = data.sideways.filter(isDate).slice(-6);
    if (isDate(data.smallerOffered)) state.smallerOffered = data.smallerOffered;
    if (typeof data.smallerAsked === "string") state.smallerAsked = data.smallerAsked.slice(0, MAX_PLAN);
    if (data.large === true) state.large = true;
    if (data.intent && isDate(data.intent.since) && state.intent) state.intent.since = data.intent.since;
    if (typeof data.pushToken === "string" && /^[0-9a-f]{32}$/.test(data.pushToken)) state.pushToken = data.pushToken;
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

function putAside(state, text, today) {
  state.aside = state.aside.filter((a) => a.text !== text).concat([{ text, date: today }]).slice(-MAX_ASIDE);
}

function daysBetween(a, b) {
  return Math.round((Date.UTC(...b.split("-").map((n, i) => i === 1 ? n - 1 : +n))
    - Date.UTC(...a.split("-").map((n, i) => i === 1 ? n - 1 : +n))) / 86400000);
}

// Two days or more since the plan's day: "Fresh day", with no count.
function fresh(state, today) {
  return Boolean(state.intent && daysBetween(state.intent.date, today) >= 2);
}

// The days "sideways" was used, on this phone only, never shown (Dot).
function noteSideways(state, today) {
  state.sideways = (state.sideways || []).filter((x) => x !== today).concat([today]).slice(-6);
}

function smallerDue(state, today) {
  const recent = (state.sideways || []).filter((x) => daysBetween(x, today) < 7);
  return recent.length >= 3 && !(state.smallerOffered && daysBetween(state.smallerOffered, today) < 7);
}

function comingBack(state, today) {
  const i = state.intent;
  return Boolean(i && daysBetween(i.since || i.date, today) >= 2 && state.smallerAsked !== i.text);
}

// Make it smaller (the new words) or, with none, keep it; the bigger one is
// set aside.
function smaller(state, text, today) {
  const plan = clean(text);
  state.smallerAsked = state.intent ? state.intent.text : null;
  if (!plan || !state.intent) return "";
  putAside(state, state.intent.text, today);
  state.intent = { text: plan, date: today, skips: 0 };
  return "smallerSaid";
}

// End the day: each thing done, carried to tomorrow, or set aside.
function endDay(state, choices, today) {
  if (!state.intent) return null;
  const parts = state.intent.text.split(";").map((p) => p.trim()).filter(Boolean);
  const tally = { done: 0, carried: 0, aside: 0 }, carried = [];
  parts.forEach((part, i) => {
    const c = choices[i] || "carry";
    if (c === "done") { state.finished.push({ text: part, date: today }); tally.done++; }
    else if (c === "aside") { putAside(state, part, today); tally.aside++; }
    else { carried.push(part); tally.carried++; }
  });
  const [y, m, d] = today.split("-").map(Number);
  state.intent = carried.length ? { text: carried.join("; "), date: iso(new Date(y, m - 1, d + 1)), skips: 0,
                                    since: state.intent.since || state.intent.date } : null;
  return tally;
}

function answer(state, choice, today) {
  const intent = state.intent;
  if (!asks(state, today)) return "";
  if (choice === "yes") {
    state.finished.push({ text: intent.text, date: intent.date });
    state.intent = null;
    return "good";
  }
  if (choice === "no" || choice === "carry") {
    const wasFresh = fresh(state, today);
    if (choice === "carry") noteSideways(state, today);
    state.intent = { text: intent.text, date: today, skips: 0, since: intent.since || intent.date };
    return choice === "carry" ? "carriedSaid" : wasFresh ? "carriedSaid" : "kept";
  }
  if (choice === "sideways" || choice === "clean") {
    // Set aside with nothing marked; no follow-up.
    if (choice === "sideways") noteSideways(state, today);
    putAside(state, intent.text, today);
    state.intent = null;
    return choice === "clean" ? "cleanSaid" : "sidewaysSaid";
  }
  intent.skips = (intent.skips || 0) + 1;
  return "skipped";
}

function setPlan(state, text, today) {
  const plan = clean(text);
  if (!plan) return "nothing";
  state.intent = { text: plan, date: today, skips: 0 };
  state.aside = state.aside.filter((a) => a.text !== plan);
  return "saved";
}

function finishToday(state, today) {
  if (!state.intent) return "";
  state.finished.push({ text: state.intent.text, date: today });
  state.intent = null;
  return "good";
}

function clearToday(state, today) {
  if (!state.intent) return "";
  putAside(state, state.intent.text, today);
  state.intent = null;
  return "cleared";
}

// A new day start can move "today" back a day; today's plan stays today's.
function setDayStart(state, hours, now) {
  state.dayStart = DAY_STARTS.includes(hours) ? hours : 0;
  const day = todayOf(state, now);
  if (state.intent && state.intent.date > day) state.intent.date = day;
  return "saved";
}

// The newest plans put aside, offered as buttons when there's no plan.
function picks(state) {
  return state.aside.slice(-MAX_PICKS).reverse();
}

function bringBack(state, text, today) {
  if (!state.aside.some((a) => a.text === text)) return "";
  setPlan(state, text, today);
  return "back";
}

// Digits, spaces and + ( ) - only, so a link can only dial or text.
function phoneNumber(text) {
  const raw = String(text || "").trim();
  if (!/^\+?[0-9 ()-]{3,25}$/.test(raw)) return "";
  return raw.replace(/[ ()-]/g, "");
}

// The phone's own text screen with the words filled in; the person presses
// send. iPhones read &body, others ?body.
function smsLink(number, text, apple) {
  return `sms:${number}${apple ? "&" : "?"}body=${encodeURIComponent(text)}`;
}

// A local time today as the UTC time the server should send at. Sent again
// each time the app opens, so a clock change moves it.
function utcTime(at, now) {
  now = now || new Date();
  const [h, m] = at.split(":").map(Number);
  const when = new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, m);
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(when.getUTCHours())}:${pad(when.getUTCMinutes())}`;
}

// What a push shows, chosen on the phone: the daily repeat's own words at its
// time, otherwise the check-in. The server's push carries nothing.
function pushText(prefs, now) {
  now = now || new Date();
  const minutes = now.getHours() * 60 + now.getMinutes();
  const near = (at) => {
    const [h, m] = at.split(":").map(Number);
    return Math.abs(h * 60 + m - minutes) <= 10;
  };
  if (prefs && prefs.repeat && near(prefs.repeat.at)) return prefs.repeat.text;
  return (prefs && prefs.checkin) || UI.en.remindShown;
}

// Everything kept, as plain text to save as a file (Noor: never locked in).
function exportText(state) {
  const lines = ["hello-world"];
  if (state.intent) lines.push("", "Plan: " + state.intent.text + " (" + state.intent.date + ")");
  if (state.repeat) lines.push("", "Every day at " + state.repeat.at + ": " + state.repeat.text);
  if (state.finished.length) {
    lines.push("", "Done:");
    state.finished.forEach((f) => lines.push(f.date + "  " + f.text));
  }
  if (state.aside.length) {
    lines.push("", "Put aside:");
    state.aside.forEach((a) => lines.push(a.date + "  " + a.text));
  }
  return lines.join("\n") + "\n";
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
    syncKeys, sealSync, openSync, mergeSync, syncForm, normalCode, todayOf, clearToday, picks, bringBack,
    phoneNumber, smsLink, utcTime, pushText, exportText, setDayStart, REMIND_TIMES, DAY_STARTS,
    fresh, smallerDue, comingBack, smaller, endDay, noteSideways };
}

if (typeof document !== "undefined") {
  const $ = (id) => document.getElementById(id);
  let state = parse(localStorage.getItem(KEY) || "{}");
  let timer = null;
  const t = () => UI[language(state, navigator.languages)];
  const today = () => todayOf(state);
  const say = (key) => {
    $("status").textContent = key === "endTally" ? $("status").dataset.tally : key ? t()[key] : "";
  };

  // What the service worker shows for a push, kept where it can read it.
  // It stays on this phone.
  async function savePrefs() {
    if (typeof caches === "undefined") return;
    try {
      const cache = await caches.open("hello-world-prefs");
      await cache.put("prefs", new Response(JSON.stringify({ checkin: t().remindShown, repeat: state.repeat })));
    } catch (e) { /* storage refused */ }
  }
  const save = () => {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* private mode */ }
    savePrefs();
  };

  function longDate(isoDate, lang) {
    const [y, m, d] = isoDate.split("-").map(Number);
    return new Date(y, m - 1, d).toLocaleDateString(lang, { weekday: "long", day: "numeric", month: "long", year: "numeric" });
  }

  const times = () => [state.remind, state.repeat && state.repeat.at].filter(Boolean);

  // A reminder through the server, by Web Push with no content, when the
  // server offers it; otherwise a timer while the page is open.
  let pushOk = false;
  async function registerPush() {
    const wanted = times();
    const url = (token) => `${location.origin}/v1/push/${token}`;
    try {
      const reg = navigator.serviceWorker && await navigator.serviceWorker.ready;
      if (!reg || !reg.pushManager) return false;
      if (!wanted.length) {
        const sub = await reg.pushManager.getSubscription();
        if (sub) await sub.unsubscribe();
        if (state.pushToken) await fetch(url(state.pushToken), { method: "DELETE" });
        delete state.pushToken; save();
        return true;
      }
      const got = await fetch(`${location.origin}/v1/push/key`, { cache: "no-store" });
      if (!got.ok) return false;
      const key = (await got.json()).key.replace(/-/g, "+").replace(/_/g, "/");
      const raw = Uint8Array.from(atob(key + "===".slice((key.length + 3) % 4)), (c) => c.charCodeAt(0));
      const sub = await reg.pushManager.getSubscription()
        || await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: raw });
      if (!state.pushToken) {
        state.pushToken = Array.from(crypto.getRandomValues(new Uint8Array(16)), (b) => b.toString(16).padStart(2, "0")).join("");
        save();
      }
      const put = await fetch(url(state.pushToken), { method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ endpoint: sub.endpoint, times: wanted.map((at) => utcTime(at)) }) });
      return put.ok;
    } catch (e) {
      return false;
    }
  }

  function schedule() {
    clearTimeout(timer);
    if (pushOk || !times().length || typeof Notification === "undefined" || Notification.permission !== "granted") return;
    const now = new Date();
    const next = times().map((at) => {
      const [h, m] = at.split(":").map(Number);
      const when = new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, m);
      if (when <= now) when.setDate(when.getDate() + 1);
      return when;
    }).sort((a, b) => a - b)[0];
    timer = setTimeout(async () => {
      const reg = navigator.serviceWorker && await navigator.serviceWorker.ready;
      if (reg) reg.showNotification("hello-world", { body: pushText({ checkin: t().remindShown, repeat: state.repeat }), icon: "icon.svg" });
      schedule();
    }, next - now);
  }

  async function reminders() {
    pushOk = await registerPush();
    $("remind-note").textContent = pushOk || !times().length ? t().remindNote : t().remindLocal;
    schedule();
  }

  const options = (select, items, chosen) =>
    select.replaceChildren(...items.map(([label, value]) => new Option(label, value, false, value === chosen)));

  function draw() {
    const lang = language(state, navigator.languages), s = UI[lang], day = today();
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    $("hello").textContent = s.hello;
    $("date").textContent = longDate(day, lang);
    const asking = asks(state, day);
    $("ask").hidden = !asking;
    if (asking) {
      const [y, m, d] = day.split("-").map(Number);
      const yesterday = iso(new Date(y, m - 1, d - 1));
      $("ask-label").textContent = s.ask + " " + (state.intent.date === yesterday ? s.yesterday : s.on.replace("{date}", longDate(state.intent.date, lang)));
      $("ask-plan").textContent = state.intent.text;
    }
    ["yes", "no", "skip", "sideways", "did", "clear", "save"].forEach((id) => { $(id).textContent = s[id]; });
    document.body.classList.toggle("large", Boolean(state.large));
    $("large").textContent = state.large ? s.usual : s.large;
    const isFresh = asking && fresh(state, day);
    if (isFresh) {
      $("ask-label").textContent = s.fresh;
      $("no").textContent = s.bring;
      $("sideways").textContent = s.startClean;
    }
    $("fork").hidden = !forking || !asking;
    $("carry-it").textContent = s.carryIt;
    $("aside-it").textContent = s.asideIt;
    const offering = !asking && comingBack(state, day) && state.offerSmaller;
    $("smaller-offer").hidden = !offering;
    $("coming-back").textContent = s.comingBack;
    $("make-smaller").textContent = s.makeSmaller;
    $("aside-smaller").textContent = s.asideIt;
    $("keep-it").textContent = s.keepIt;
    const planned = state.intent && state.intent.date === day;
    $("today-label").textContent = planned ? s.todayHave : s.todayAsk;
    $("today-plan").hidden = $("today-buttons").hidden = !planned;
    $("today-plan").textContent = planned ? state.intent.text : "";
    $("plan-form").hidden = planned || asking;
    // Once a week at most: noted the first time it shows, and shown for
    // the rest of that visit.
    if (nudging === null) {
      nudging = !planned && !asking && smallerDue(state, day);
      if (nudging) { state.smallerOffered = day; save(); }
    }
    $("smaller-nudge").hidden = planned || asking || !nudging;
    $("smaller-nudge").textContent = s.smallerNudge;
    $("end-day").hidden = !planned || ending;
    $("end-day").textContent = s.endDay;
    $("end-panel").hidden = !ending || !state.intent;
    $("end-close").textContent = s.endClose;
    if (ending && state.intent) {
      $("end-list").replaceChildren(...state.intent.text.split(";").map((p) => p.trim()).filter(Boolean).map((part, i) => {
        const label = document.createElement("label");
        label.textContent = part;
        label.htmlFor = "end-" + i;
        const select = document.createElement("select");
        select.id = "end-" + i;
        [["carry", s.endCarry], ["done", s.endDone], ["aside", s.endAside]]
          .forEach(([v, t]) => select.add(new Option(t, v)));
        const div = document.createElement("div");
        div.append(label, select);
        return div;
      }));
    }
    $("plan-input").placeholder = s.placeholder;
    const offered = planned || asking ? [] : picks(state);
    $("picks").hidden = !offered.length;
    $("picks-label").textContent = s.picks;
    $("picks-list").replaceChildren(...offered.map((a) => {
      const b = document.createElement("button");
      b.textContent = a.text;
      b.addEventListener("click", act(() => bringBack(state, a.text, today())));
      return b;
    }));
    $("repeat-today").hidden = !state.repeat;
    $("repeat-today").textContent = state.repeat ? s.printRepeat.replace("{at}", state.repeat.at) + " " + state.repeat.text : "";
    $("family-buttons").hidden = !state.family;
    $("family-scam").textContent = s.familyScam;
    if (state.family) {
      $("draft").textContent = s.draft.replace("{name}", state.family.name);
      $("call").textContent = s.call.replace("{name}", state.family.name);
      const apple = /iPhone|iPad/.test(navigator.userAgent);
      $("draft").href = smsLink(state.family.number, s.okayText, apple);
      $("call").href = "tel:" + state.family.number;
    }
    const [thought, tip] = todaysPair(lang, day, CONTENT);
    $("thought-label").textContent = s.thought;
    $("thought").textContent = thought;
    $("tip-label").textContent = s.tip;
    $("tip").textContent = tip;
    ["settings", "language", "remind", "dayStart", "repeat", "family", "familyName", "familyNumber"].forEach((k) => {
      $(k.replace(/[A-Z]/g, (c) => "-" + c.toLowerCase()) + "-label").textContent = s[k];
    });
    $("repeat-at-label").textContent = s.repeatAt;
    $("day-start-note").textContent = s.dayStartNote;
    $("repeat-note").textContent = s.repeatNote;
    $("family-note").textContent = s.familyNote;
    $("repeat-text").placeholder = s.repeatPlaceholder;
    $("repeat-save").textContent = $("family-save").textContent = s.familySave;
    $("print").textContent = s.print;
    $("print-note").textContent = s.printNote;
    $("export").textContent = s.export;
    $("forget").textContent = s.forget;
    $("privacy").textContent = s.privacy;
    options($("language"), Object.keys(UI).map((code) => [LANG_NAMES[code], code]), lang);
    options($("remind"), [[s.remindOff, ""], ...REMIND_TIMES.map((at) => [at, at])], state.remind || "");
    options($("day-start"), DAY_STARTS.map((h) => [h ? `${h}:00` : s.midnight, String(h)]), String(state.dayStart || 0));
    options($("repeat-at"), [[s.repeatOff, ""], ...REMIND_TIMES.map((at) => [at, at])], state.repeat ? state.repeat.at : "");
    if (state.repeat && !$("repeat-text").value) $("repeat-text").value = state.repeat.text;
    if (state.family && !$("family-name").value) {
      $("family-name").value = state.family.name;
      $("family-number").value = state.family.number;
    }
    // The fridge page: only what's printed, in big type.
    $("fridge-title").textContent = s.printTitle + ": " + longDate(day, lang);
    $("fridge-plan").textContent = planned ? state.intent.text : "";
    $("fridge-repeat").textContent = state.repeat ? s.printRepeat.replace("{at}", state.repeat.at) + " " + state.repeat.text : "";
    $("fridge-note").textContent = s.printNote;
    drawSync();
  }

  let forking = false, ending = false, nudging = null;
  const SYNC_KEY = "hello-world-sync";
  let keys = null;
  let changing = false;
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
        if (other) { mergeSync(state, other, today()); save(); draw(); }
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
    $("sync-scam").textContent = s.scam;
    $("sync-code-label").textContent = changing ? s.syncChangeNote : s.syncCode;
    $("sync-save").textContent = keys && !changing ? s.syncOff : s.syncSave;
    $("sync-change").textContent = s.syncChange;
    $("sync-change").hidden = !keys || changing;
    $("sync-code").hidden = $("sync-code-label").hidden = Boolean(keys) && !changing;
    $("sync-note").textContent = s.syncNote;
    const when = keys && state.updated ? new Date(state.updated) : null;
    $("sync-last").textContent = when && !isNaN(when)
      ? s.lastChange.replace("{when}", when.toLocaleString(language(state, navigator.languages),
          { weekday: "short", hour: "2-digit", minute: "2-digit" })) : "";
  }

  $("sync-change").addEventListener("click", (event) => {
    event.preventDefault();
    changing = true;
    drawSync();
  });

  $("sync-save").addEventListener("click", async (event) => {
    event.preventDefault();
    if (keys && !changing) {
      keys = null;
      try { localStorage.removeItem(SYNC_KEY); } catch (e) { /* nothing saved */ }
      drawSync(); say("syncOffDone");
      return;
    }
    if (normalCode($("sync-code").value).length !== 25) { say("syncBad"); return; }
    const k = await syncKeys($("sync-code").value);
    keys = { label: k.label, enc: Array.from(k.enc), mac: Array.from(k.mac) };
    changing = false;
    try { localStorage.setItem(SYNC_KEY, JSON.stringify(keys)); } catch (e) { /* private mode */ }
    $("sync-code").value = "";
    drawSync();
    await sync(true);
  });

  function act(fn) {
    return (event) => {
      if (event) event.preventDefault();
      const before = JSON.stringify(state.intent && { text: state.intent.text, date: state.intent.date });
      const said = fn();
      if (JSON.stringify(state.intent && { text: state.intent.text, date: state.intent.date }) !== before) stamp(state);
      save(); draw(); say(said);
      sync(false);
    };
  }
  $("yes").addEventListener("click", act(() => answer(state, "yes", today())));
  $("no").addEventListener("click", act(() => afterCarry(answer(state, "no", today()))));
  $("skip").addEventListener("click", act(() => answer(state, "skip", today())));
  // Sideways asks carry or set aside, two equal buttons (Mary); a fresh
  // day's "Start clean" sets it aside at once.
  $("sideways").addEventListener("click", (event) => {
    if (fresh(state, today())) return act(() => answer(state, "clean", today()))(event);
    forking = true; draw();
  });
  const afterCarry = (said) => {
    forking = false;
    if (comingBack(state, today())) state.offerSmaller = true;
    return said;
  };
  $("carry-it").addEventListener("click", act(() => afterCarry(answer(state, "carry", today()))));
  $("aside-it").addEventListener("click", act(() => { forking = false; return answer(state, "sideways", today()); }));
  $("make-smaller").addEventListener("click", act(() => {
    state.offerSmaller = false;
    const said = smaller(state, $("smaller-input").value, today());
    $("smaller-input").value = "";
    return said || "nothing";
  }));
  $("aside-smaller").addEventListener("click", act(() => {
    state.offerSmaller = false;
    state.smallerAsked = state.intent && state.intent.text;
    return clearToday(state, today());
  }));
  $("keep-it").addEventListener("click", act(() => {
    state.offerSmaller = false;
    state.smallerAsked = state.intent && state.intent.text;
    return "kept";
  }));
  $("end-day").addEventListener("click", () => { ending = true; draw(); });
  $("end-close").addEventListener("click", act(() => {
    const parts = state.intent ? state.intent.text.split(";").map((p) => p.trim()).filter(Boolean) : [];
    const tally = endDay(state, parts.map((_, i) => $("end-" + i).value), today());
    ending = false;
    if (!tally) return "";
    $("status").dataset.tally = t().endTally.replace("{done}", tally.done)
      .replace("{carried}", tally.carried).replace("{aside}", tally.aside);
    return "endTally";
  }));
  $("large").addEventListener("click", act(() => { state.large = !state.large; return ""; }));
  $("did").addEventListener("click", act(() => finishToday(state, today())));
  $("clear").addEventListener("click", act(() => clearToday(state, today())));
  $("plan-form").addEventListener("submit", act(() => {
    const said = setPlan(state, $("plan-input").value, today());
    if (said === "saved") $("plan-input").value = "";
    return said;
  }));
  $("language").addEventListener("change", act(() => { state.lang = $("language").value; return ""; }));
  $("day-start").addEventListener("change", act(() => setDayStart(state, Number($("day-start").value) || 0)));
  async function askPermission() {
    // Asked only when someone picks a time; no reminder unless asked (the rider).
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      await Notification.requestPermission();
    }
  }
  $("remind").addEventListener("change", async () => {
    state.remind = $("remind").value || null;
    if (state.remind) await askPermission();
    save(); reminders();
  });
  $("repeat-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = clean($("repeat-text").value), at = $("repeat-at").value;
    state.repeat = text && at ? { text, at } : null;
    if (!state.repeat) $("repeat-text").value = "";
    if (state.repeat) await askPermission();
    save(); draw(); say(state.repeat ? "repeatSaved" : "saved");
    reminders();
  });
  $("family-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const number = phoneNumber($("family-number").value), name = $("family-name").value.trim().slice(0, 40);
    state.family = number && name ? { name, number } : null;
    save(); draw(); say("saved");
  });
  $("print").addEventListener("click", () => window.print());
  $("export").addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([exportText(state)], { type: "text/plain" }));
    link.download = "hello-world-plans.txt";
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    say("exported");
  });
  $("forget").addEventListener("click", async () => {
    if (!confirm(t().forgetAsk)) return;
    const lang = state.lang;
    state.remind = null; state.repeat = null;
    await registerPush();
    try { localStorage.removeItem(KEY); localStorage.removeItem(SYNC_KEY); } catch (e) { /* nothing saved */ }
    keys = null;
    state = blank();
    state.lang = lang;
    $("repeat-text").value = $("family-name").value = $("family-number").value = "";
    save(); draw(); say("forgotten"); schedule();
  });
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
  draw();
  savePrefs();
  reminders();
  sync(false);
  // A page left open past the day's start shows the new day.
  setInterval(() => { if ($("date").textContent !== longDate(today(), language(state, navigator.languages))) draw(); }, 60000);
}
