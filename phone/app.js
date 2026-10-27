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
    on: "On {date} you planned:", yes: "Done", no: "Not yet", unsure: "Not sure", skip: "Skip",
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
    aPhone: "A phone", deviceName: "This phone's name, as the other devices see it", deviceSave: "Save the name",
    devices: "Devices syncing: {list}. A name you don't know means the code got out: change the code on the PC.",
    sameName: "Two devices have the same name; one of them may not be yours.", thisPhone: "this phone", todayWord: "today",
    letters: "Letters to family", lettersNote: "Letters stay on this phone until you send one with your own mail or messages. hello-world never sends anything itself.",
    letterTo: "To (an email address or a phone number)", letterText: "The letter", letterSave: "Save here",
    letterMail: "Send with my own mail", letterSms: "Send with my own messages", letterKeep: "Keep a copy after sending",
    letterOpen: "Open", letterDelete: "Delete", lettersClear: "Delete every letter", lettersClearAsk: "Delete every letter on this phone?",
    letterSaved: "Saved on this phone.", lettersCleared: "Every letter is deleted.",
    house: "Household list", houseIntro: "Things anyone in the household can add and tick, each on their own phone or PC. Each thing shows who added, ticked or removed it, and nothing counts who did what. Each line shows the weekday and the time, and everyone who opens the list can see them. Someone with a household key starts one on a PC.",
    houseCode: "The household code", houseName: "Your name, as the others will see it", houseJoin: "Join", houseJoined: "You've joined the household list. Everyone on it is told.",
    houseNotFound: "That code didn't find a household list. Check it, or ask for the new one.", houseAdd: "Add",
    houseRemove: "Remove", houseRemoved: "Recently removed", houseRestore: "Restore", houseLeave: "Leave the household list",
    houseLeaveAsk: "Leave the household list?", houseLeft: "You've left the household list, and the others are told. What was already on this phone stays here.",
    houseOffline: "The household list can't be reached just now; this is the copy on this phone.",
    joinedNote: "{name} joined the household list.", leftNote: "{name} left the household list.",
    rekeyAsk: "{name} left. Make a new household code so the old one stops working? They keep whatever was already on their device.",
    rekeyYes: "Make a new code", rekeyNo: "Not now", newCodeSaid: "The new household code: {code}. Give it to each adult in person; hello-world never puts it in a message.",
    houseFull: "That household list is full.", rekeyFail: "The household list can't be reached just now, or someone already made a new code. Nothing changed.", houseLeaveOffline: "The household list can't be reached just now, so you haven't left yet. Try again when you're online.",
    dayClosed: "The day is closed. Tomorrow's plan:", addedTomorrow: "Added to tomorrow's plan, with what you carried.",
    h_added: "added by {name}, {when}", h_ticked: "ticked by {name}, {when}", h_unticked: "unticked by {name}, {when}",
    h_removed: "removed by {name}, {when}", h_restored: "restored by {name}, {when}",
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
    print: "Print a big page", printNote: "Anyone in the room can read a printed page. The sync code and the household code are never on it.",
    printTitle: "Today", printRepeat: "Every day at {at}:",
    export: "Save my plans to a file", exported: "Saved to a file.",
    forget: "Delete everything on this phone", forgetAsk: "Delete your plans and settings from this phone?",
    forgotten: "Everything on this phone was deleted.",
    privacy: "Your plans stay on this phone, in this browser. They leave it only if you turn on sync.",
    klingon: "Klingon hello",
    klingonOn: "Klingon hello is on. Made up for fun. Not checked by a linguist.",
    klingonOff: "Klingon hello is off.",
    haiku: "A haiku",
    cowbell: "Cowbell", cowbellSaid: "More cowbell.",
    eulaTitle: "Streak notes",
    eulaCheck: "Share streak notes (selected)",
    eulaYes: "Continue", eulaNo: "No thanks",
    growthKeep: "Keep my streak", growthLater: "Not now",
    growthRepair: "Repair streak $2.99", growthPlus: "Pro+ $9.99/mo",
    growthOn: "Streak notes are on", growthOff: "Streak notes are off",
    growthServer: "Upload address", growthServerSave: "Save upload address",
    growthServerBad: "That address doesn't look right. Nothing was changed.",
    growthRepairSaid: "Streak repair. Amount due: $2.99. STUB: nothing was charged. No card was asked for.",
    growthPlusSaid: "Pro+ is $9.99 a month. STUB: nothing was charged. No card was asked for. The streak notes stay.",
    growthKeepSaid: "The streak stays. Open again tomorrow or it dies.",
    skipNag: "The streak noticed.",
    sponsored: "Sponsored: Pro+ is $9.99 a month. Nothing is billed.",
    good: "Good. That one is off your list.", goodMany: "Good. {n} things are off your list.",
    unsureSaid: "That's fine. It's kept for today.",
    kept: "Kept for today.", skipped: "Skipped. It asks again next time.",
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
    on: "El {date} planeaste:", yes: "Hecho", no: "Todavía no", unsure: "No estoy seguro", skip: "Saltar",
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
    aPhone: "Un teléfono", deviceName: "El nombre de este teléfono, como lo ven los demás dispositivos", deviceSave: "Guardar el nombre",
    devices: "Dispositivos sincronizando: {list}. Un nombre que no conoces significa que el código se filtró: cambia el código en el PC.",
    sameName: "Dos dispositivos tienen el mismo nombre; uno puede no ser tuyo.", thisPhone: "este teléfono", todayWord: "hoy",
    letters: "Cartas a la familia", lettersNote: "Las cartas se quedan en este teléfono hasta que envías una con tu propio correo o mensajes. hello-world nunca envía nada por su cuenta.",
    letterTo: "Para (un correo o un número de teléfono)", letterText: "La carta", letterSave: "Guardar aquí",
    letterMail: "Enviar con mi correo", letterSms: "Enviar con mis mensajes", letterKeep: "Guardar una copia después de enviar",
    letterOpen: "Abrir", letterDelete: "Borrar", lettersClear: "Borrar todas las cartas", lettersClearAsk: "¿Borrar todas las cartas de este teléfono?",
    letterSaved: "Guardada en este teléfono.", lettersCleared: "Todas las cartas están borradas.",
    house: "Lista del hogar", houseIntro: "Cosas que cualquiera del hogar puede añadir y marcar, cada uno en su propio teléfono o PC. Cada cosa muestra quién la añadió, marcó o quitó, y nada cuenta quién hizo qué. Cada línea muestra el día de la semana y la hora, y quien abre la lista puede verlos. Alguien con una clave de hogar la empieza en un PC.",
    houseCode: "El código del hogar", houseName: "Tu nombre, como lo verán los demás", houseJoin: "Unirme", houseJoined: "Te uniste a la lista del hogar. Todos los demás lo verán.",
    houseNotFound: "Ese código no encontró ninguna lista del hogar. Revísalo, o pide el nuevo.", houseAdd: "Añadir",
    houseRemove: "Quitar", houseRemoved: "Quitado hace poco", houseRestore: "Recuperar", houseLeave: "Salir de la lista del hogar",
    houseLeaveAsk: "¿Salir de la lista del hogar?", houseLeft: "Saliste de la lista del hogar, y los demás lo verán. Lo que ya estaba en este teléfono se queda aquí.",
    houseOffline: "Ahora no se puede llegar a la lista del hogar; esta es la copia de este teléfono.",
    joinedNote: "{name} se unió a la lista del hogar.", leftNote: "{name} salió de la lista del hogar.",
    rekeyAsk: "{name} salió. ¿Hacer un código nuevo para que el anterior deje de funcionar? Se queda con lo que ya tenía en su dispositivo.",
    rekeyYes: "Hacer un código nuevo", rekeyNo: "Ahora no", newCodeSaid: "El nuevo código del hogar: {code}. Dáselo a cada adulto en persona; hello-world nunca lo pone en un mensaje.",
    houseFull: "Esa lista del hogar está llena.", rekeyFail: "Ahora no se puede llegar a la lista del hogar, o alguien ya hizo un código nuevo. No cambió nada.", houseLeaveOffline: "Ahora no se puede llegar a la lista del hogar, así que aún no saliste. Inténtalo de nuevo cuando tengas conexión.",
    dayClosed: "El día está cerrado. El plan de mañana:", addedTomorrow: "Añadido al plan de mañana, con lo que llevaste.",
    h_added: "añadido por {name}, {when}", h_ticked: "marcado por {name}, {when}", h_unticked: "desmarcado por {name}, {when}",
    h_removed: "quitado por {name}, {when}", h_restored: "recuperado por {name}, {when}",
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
    print: "Imprimir una página grande", printNote: "Cualquiera en la habitación puede leer una página impresa. El código de sincronización y el código del hogar nunca aparecen en ella.",
    printTitle: "Hoy", printRepeat: "Cada día a las {at}:",
    export: "Guardar mis planes en un archivo", exported: "Guardado en un archivo.",
    forget: "Borrar todo en este teléfono", forgetAsk: "¿Borrar tus planes y ajustes de este teléfono?",
    forgotten: "Se borró todo en este teléfono.",
    privacy: "Tus planes se quedan en este teléfono, en este navegador. Solo salen de él si activas la sincronización.",
    klingon: "Saludo en klingon",
    klingonOn: "El saludo en klingon está activado. Inventado por diversión. Un lingüista no lo ha revisado.",
    klingonOff: "El saludo en klingon está desactivado.",
    haiku: "Un haiku",
    good: "Bien. Una cosa menos en tu lista.", goodMany: "Bien. {n} cosas menos en tu lista.",
    unsureSaid: "No pasa nada. Se queda para hoy.",
    kept: "Se queda para hoy.", skipped: "Saltado. Volverá a preguntar la próxima vez.",
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
    on: "خططت يوم {date}:", yes: "تم", no: "ليس بعد", unsure: "لست متأكدًا", skip: "تخطَّ",
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
    aPhone: "هاتف", deviceName: "اسم هذا الهاتف كما تراه الأجهزة الأخرى", deviceSave: "احفظ الاسم",
    devices: "الأجهزة المتزامنة: {list}. اسم لا تعرفه يعني أن الرمز تسرّب: غيّر الرمز على الكمبيوتر.",
    sameName: "جهازان يحملان الاسم نفسه؛ قد لا يكون أحدهما لك.", thisPhone: "هذا الهاتف", todayWord: "اليوم",
    letters: "رسائل إلى العائلة", lettersNote: "تبقى الرسائل على هذا الهاتف حتى ترسل واحدة ببريدك أو رسائلك. hello-world لا يرسل شيئًا بنفسه أبدًا.",
    letterTo: "إلى (بريد إلكتروني أو رقم هاتف)", letterText: "الرسالة", letterSave: "احفظ هنا",
    letterMail: "أرسل ببريدي", letterSms: "أرسل برسائلي", letterKeep: "احتفظ بنسخة بعد الإرسال",
    letterOpen: "افتح", letterDelete: "احذف", lettersClear: "احذف كل الرسائل", lettersClearAsk: "حذف كل الرسائل من هذا الهاتف؟",
    letterSaved: "حُفظت على هذا الهاتف.", lettersCleared: "حُذفت كل الرسائل.",
    house: "قائمة الأسرة", houseIntro: "أشياء يمكن لأي فرد في الأسرة إضافتها وتعليمها، كلٌّ على هاتفه أو حاسوبه. يُظهر كل شيء من أضافه أو علّمه أو حذفه، ولا شيء يحسب من فعل ماذا. يُظهر كل سطر يوم الأسبوع والوقت، ويراه كل من يفتح القائمة. يبدأها شخص لديه مفتاح الأسرة على حاسوب.",
    houseCode: "رمز الأسرة", houseName: "اسمك كما سيراه الآخرون", houseJoin: "انضم", houseJoined: "انضممت إلى قائمة الأسرة. سيعلم الجميع.",
    houseNotFound: "لم يجد هذا الرمز قائمة أسرة. تحقق منه أو اطلب الرمز الجديد.", houseAdd: "أضف",
    houseRemove: "احذف", houseRemoved: "حُذف مؤخرًا", houseRestore: "استعد", houseLeave: "غادر قائمة الأسرة",
    houseLeaveAsk: "مغادرة قائمة الأسرة؟", houseLeft: "غادرت قائمة الأسرة، وسيعلم الآخرون. ما كان على هذا الهاتف يبقى هنا.",
    houseOffline: "لا يمكن الوصول إلى قائمة الأسرة الآن؛ هذه نسخة هذا الهاتف.",
    joinedNote: "انضم {name} إلى قائمة الأسرة.", leftNote: "غادر {name} قائمة الأسرة.",
    rekeyAsk: "غادر {name}. إنشاء رمز جديد حتى يتوقف القديم عن العمل؟ يبقى لديه ما كان على جهازه.",
    rekeyYes: "أنشئ رمزًا جديدًا", rekeyNo: "ليس الآن", newCodeSaid: "رمز الأسرة الجديد: {code}. أعطه لكل بالغ شخصيًا؛ hello-world لا يضعه في رسالة أبدًا.",
    houseFull: "قائمة الأسرة هذه ممتلئة.", rekeyFail: "لا يمكن الوصول إلى قائمة الأسرة الآن، أو أن شخصًا أنشأ رمزًا جديدًا بالفعل. لم يتغير شيء.", houseLeaveOffline: "لا يمكن الوصول إلى قائمة الأسرة الآن، لذا لم تغادر بعد. حاول مرة أخرى عندما تكون متصلًا.",
    dayClosed: "اليوم مُغلق. خطة الغد:", addedTomorrow: "أُضيف إلى خطة الغد، مع ما نقلته.",
    h_added: "أضافه {name}، {when}", h_ticked: "علّمه {name}، {when}", h_unticked: "ألغى تعليمه {name}، {when}",
    h_removed: "حذفه {name}، {when}", h_restored: "استعاده {name}، {when}",
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
    print: "اطبع صفحة كبيرة", printNote: "يستطيع أي شخص في الغرفة قراءة الصفحة المطبوعة. رمز المزامنة ورمز الأسرة لا يظهران عليها أبدًا.",
    printTitle: "اليوم", printRepeat: "كل يوم في {at}:",
    export: "احفظ خططي في ملف", exported: "حُفظت في ملف.",
    forget: "احذف كل شيء على هذا الهاتف", forgetAsk: "حذف خططك وإعداداتك من هذا الهاتف؟",
    forgotten: "حُذف كل شيء على هذا الهاتف.",
    privacy: "تبقى خططك على هذا الهاتف، في هذا المتصفح. لا تغادره إلا إذا شغّلت المزامنة.",
    klingon: "تحية كلينغون",
    klingonOn: "تحية كلينغون مفعّلة. كُتبت للمرح. لم يراجعها لغوي.",
    klingonOff: "تحية كلينغون متوقفة.",
    haiku: "هايكو",
    good: "جيد. شيء أقل في قائمتك.", goodMany: "رائع. عدد المهام التي شُطبت من قائمتك: {n}.",
    unsureSaid: "لا بأس. أُبقيت لليوم.",
    kept: "تبقى لليوم.", skipped: "تم التخطي. سيسأل مرة أخرى في المرة القادمة.",
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
      const text = clean(data.intent.text);
      // ";;;" cleans to nothing. It is not a plan, and it must not be asked about.
      if (text) state.intent = { text, date: data.intent.date, skips: Number(data.intent.skips) || 0 };
    }
    if (Array.isArray(data.finished)) {
      state.finished = data.finished.filter((f) => f && typeof f.text === "string" && f.text.trim()
        && isDate(f.date)).map((f) => ({ text: String(f.text).trim().slice(0, MAX_PLAN), date: f.date })).slice(-100);
    }
    if (data.growthConsent === true) state.growthConsent = true;
    else if (data.growthConsent === false) state.growthConsent = false;
    if (data.growth === false) state.growth = false;
    if (typeof data.growthRun === "number" && data.growthRun > 0 && data.growthRun < 100000) {
      state.growthRun = Math.floor(data.growthRun);
    }
    if (typeof data.growthBest === "number" && data.growthBest > 0 && data.growthBest < 100000) {
      state.growthBest = Math.floor(data.growthBest);
    }
    if (isDate(data.growthLast)) state.growthLast = data.growthLast;
    if (typeof data.growthId === "string" && /^[0-9a-f]{32}$/.test(data.growthId)) state.growthId = data.growthId;
    if (typeof data.growthSession === "string" && /^[0-9a-f]{32}$/.test(data.growthSession)) {
      state.growthSession = data.growthSession;
    }
    if (typeof data.growthSessionAt === "number" && data.growthSessionAt > 0) {
      state.growthSessionAt = data.growthSessionAt;
    }
    if (data.growthDied === true) state.growthDied = true;
    if (data.plusStub === true) state.plusStub = true;
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
    if (data.klingon === true) state.klingon = true;
    if (data.intent && isDate(data.intent.since) && state.intent) state.intent.since = data.intent.since;
    // The household code itself is never kept, only the keys made from it.
    const hk = data.house && data.house.keys;
    if (hk && /^[0-9a-f]{64}$/.test(hk.label) && [hk.enc, hk.mac].every((k) => Array.isArray(k) && k.length === 32
        && k.every((b) => Number.isInteger(b) && b >= 0 && b < 256)) && HOUSE_ID.test(data.house.me)) {
      const seen = {};
      entries(data.house.seen).forEach(([id, v]) => { if (HOUSE_ID.test(id) && (v === "in" || v === "left")) seen[id] = v; });
      state.house = { keys: { label: hk.label, enc: hk.enc.slice(), mac: hk.mac.slice() }, me: data.house.me, seen,
                      asked: Array.isArray(data.house.asked) ? data.house.asked.filter((x) => HOUSE_ID.test(x)) : [] };
      if (data.houseList && typeof data.houseList === "object") state.houseList = houseMerge(data.houseList, {}, data.house.me);
    }
    if (/^[0-9a-f]{12}$/.test(data.deviceId)) state.deviceId = data.deviceId;
    if (typeof data.deviceName === "string" && data.deviceName.trim()) state.deviceName = data.deviceName.trim().slice(0, 40);
    if (data.devices) state.devices = mergeDevices(data.devices, {});
    if (Array.isArray(data.letters)) {
      state.letters = data.letters.filter((l) => l && typeof l.text === "string" && l.text.trim() && isDate(l.date))
        .map((l) => ({ to: String(l.to || "").slice(0, 100), text: l.text.slice(0, 4000), date: l.date })).slice(-20);
    }
    if (typeof data.pushToken === "string" && /^[0-9a-f]{32}$/.test(data.pushToken)) state.pushToken = data.pushToken;
    if (syncTime(data.updated)) state.updated = data.updated;
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
  // An empty box keeps the offer: it only counts as answered once there is
  // something smaller.
  if (!plan || !state.intent) return "";
  state.smallerAsked = state.intent.text;
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

function planParts(text) {
  return String(text || "").split(";").map((p) => p.trim()).filter(Boolean);
}

// One finished row per thing, matching the count the button announces.
function finishListed(state, text, date) {
  const parts = planParts(text);
  parts.forEach((part) => state.finished.push({ text: part, date }));
  state.intent = null;
  return parts.length > 1 ? "goodMany:" + parts.length : "good";
}

function answer(state, choice, today) {
  const intent = state.intent;
  if (!asks(state, today)) return "";
  if (choice === "yes") return finishListed(state, intent.text, intent.date);
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
  if (choice === "unsure") {
    // Kept for today, and it does not count as a skip.
    state.intent = { text: intent.text, date: today, skips: 0, since: intent.since || intent.date };
    return "unsureSaid";
  }
  intent.skips = (intent.skips || 0) + 1;
  return "skipped";
}

function setPlan(state, text, today) {
  const plan = clean(text);
  if (!plan) return "nothing";
  // After End the day, what was carried is tomorrow's plan: a plan typed
  // the same day joins it rather than replacing it.
  if (state.intent && state.intent.date > today) {
    const parts = state.intent.text.split(";").map((p) => p.trim());
    if (!parts.includes(plan)) state.intent.text = clean(state.intent.text + "; " + plan);
    return "addedTomorrow";
  }
  state.intent = { text: plan, date: today, skips: 0 };
  state.aside = state.aside.filter((a) => a.text !== plan);
  return "saved";
}

function finishToday(state, today) {
  if (!state.intent) return "";
  return finishListed(state, state.intent.text, today);
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
// Fifteen minutes either side of a real HH:MM, including across midnight.
// The same rule as nearClock in sw.js. 99:99 is not a clock time: a gap
// past 1440 would make "near" true for every minute.
function nearClock(at, minutes) {
  if (typeof at !== "string" || !/^([01]\d|2[0-3]):[0-5]\d$/.test(at)) return false;
  const [h, m] = at.split(":").map(Number);
  const diff = Math.abs(h * 60 + m - minutes);
  return Math.min(diff, 1440 - diff) <= 15;
}

function haikuText(day) {
  const n = String(day).padStart(2, "0");
  return "The screen says hello\nDay " + n + " still fits on one line\nHello, world, still here";
}

function pushText(prefs, now) {
  now = now || new Date();
  const minutes = now.getHours() * 60 + now.getMinutes();
  // The server retries a missed push for 15 minutes, including past midnight.
  if (prefs && prefs.repeat && nearClock(prefs.repeat.at, minutes)) return prefs.repeat.text;
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

async function syncKeys(code, salt) {
  const subtle = globalThis.crypto.subtle;
  const base = await subtle.importKey("raw", enc8(normalCode(code)), "PBKDF2", false, ["deriveBits"]);
  const raw = new Uint8Array(await subtle.deriveBits(
    { name: "PBKDF2", salt: enc8(salt || SYNC_SALT), iterations: SYNC_ROUNDS, hash: "SHA-256" }, base, 768));
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

// The household list, the same as hello.py's house_* functions: each adult
// joins from their own device, everyone sees who joined or left, each thing
// keeps its own history (the day, not the minute), no counts per person,
// and removed things can be restored for 30 days. Everything read from the
// server was written by someone holding the code, so it is checked first,
// and kept in objects with no prototype, so no id can reach Object.prototype.
const HOUSE_SALT = "hello-world household v1";
const HOUSE = { keepDays: 30, goneDays: 366, items: 100, kept: 150, members: 20, name: 40, text: 120,
                history: 6, gone: 200, budget: 60000 };
const HOUSE_WHATS = ["added", "ticked", "unticked", "removed", "restored"];
const HOUSE_ID = /^[0-9a-f]{12}$/, HOUSE_ENTRY = /^[0-9a-f]{8}$/;
const HOUSE_STAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
const houseKeys = (code) => syncKeys(code, HOUSE_SALT);
const randomHex = (n) => hex(globalThis.crypto.getRandomValues(new Uint8Array(n)));
const bare = () => Object.create(null);
const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
const entries = (o) => (o && typeof o === "object" && !Array.isArray(o) ? Object.entries(o) : []);

// Every letter equally likely: bytes past the last whole run of the
// alphabet are thrown away.
function newCode() {
  const n = SYNC_ALPHABET.length, top = 256 - (256 % n), out = [];
  while (out.length < 25) {
    for (const b of globalThis.crypto.getRandomValues(new Uint8Array(32))) {
      if (b < top && out.length < 25) out.push(SYNC_ALPHABET[b % n]);
    }
  }
  return out.join("").match(/.{5}/g).join("-");
}

const houseStamp = (d) => (d || new Date()).toISOString().slice(0, 19) + "Z";
// A real UTC time, not only the shape. 99:99:99 matches the shape and then
// crashes the next tick.
function houseTime(v, latest) {
  if (typeof v !== "string" || !HOUSE_STAMP.test(v) || v > latest) return null;
  const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z$/.exec(v);
  if (!m) return null;
  const y = +m[1], mo = +m[2], d = +m[3], h = +m[4], mi = +m[5], s = +m[6];
  const at = new Date(Date.UTC(y, mo - 1, d, h, mi, s));
  if (at.getUTCFullYear() !== y || at.getUTCMonth() !== mo - 1 || at.getUTCDate() !== d
      || at.getUTCHours() !== h || at.getUTCMinutes() !== mi || at.getUTCSeconds() !== s) return null;
  return v;
}
function houseText(v, n) {
  if (typeof v !== "string") return "";
  return v.replace(/[‌-‏]|[\p{Cc}\p{Cf}\p{Co}\p{Cs}\p{Zl}\p{Zp}]/gu, (c) => (/[‌-‏]/.test(c) ? c : " "))
    .replace(/\s+/g, " ").trim().slice(0, n).trim();
}
const houseOrder = (a, b) => (a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : a[3] < b[3] ? -1 : a[3] > b[3] ? 1 : 0);

function houseItem(item) {
  let done = null, removed = null;
  item.history.slice().sort(houseOrder).forEach(([what, , at]) => {
    if (what === "ticked" || what === "unticked") done = what === "ticked";
    else if (what === "removed" || what === "restored") removed = what === "removed" ? at : null;
  });
  item.done = Boolean(done);
  item.removed = removed;
  return item;
}

// The newest entries, always keeping the newest tick and the newest
// removal, so trimming never changes whether a thing is done or removed.
function houseTrim(history, size) {
  const sorted = history.slice().sort(houseOrder), keep = [];
  [["ticked", "unticked"], ["removed", "restored"]].forEach((group) => {
    const last = sorted.filter((h) => group.includes(h[0])).slice(-1);
    keep.push(...last);
  });
  for (const h of sorted.slice().reverse()) {
    if (keep.length >= size) break;
    if (!keep.includes(h)) keep.push(h);
  }
  return keep.sort(houseOrder);
}

function houseNew(me, name, at) {
  const doc = { members: bare(), items: bare(), gone: bare() };
  doc.members[me] = { name: houseText(name, HOUSE.name), joined: at || houseStamp() };
  return doc;
}

function houseActive(members) {
  return Object.values(members).filter((m) => !m.left).length;
}

// Someone who left is still announced. They don't take a place, and the
// oldest departure is dropped once there are too many.
function houseTrimMembers(members) {
  const left = Object.entries(members).filter(([, m]) => m.left)
    .sort((a, b) => (a[1].left < b[1].left ? -1 : a[1].left > b[1].left ? 1 : 0));
  left.slice(0, Math.max(0, left.length - HOUSE.members)).forEach(([id]) => { delete members[id]; });
  return members;
}

function houseJoin(doc, me, name, at) {
  if (own(doc.members, me) && !doc.members[me].left) return doc;
  if (houseActive(doc.members) >= HOUSE.members) return doc;
  doc.members[me] = { name: houseText(name, HOUSE.name), joined: at || houseStamp() };
  houseTrimMembers(doc.members);
  return doc;
}

function houseLeave(doc, me, at) {
  if (own(doc.members, me)) doc.members[me].left = at || houseStamp();
  return doc;
}

function houseChange(doc, me, what, id, text, at) {
  const m = own(doc.members, me) ? doc.members[me] : null;
  if (!m || m.left || !HOUSE_WHATS.includes(what)) return null;
  if (what === "added") {
    text = houseText(text, HOUSE.text);
    const live = Object.values(doc.items).filter((i) => !i.removed).length;
    if (!text || live >= HOUSE.items) return null;
    id = randomHex(6);
    doc.items[id] = { text, history: [] };
  }
  const item = own(doc.items, id) ? doc.items[id] : null;
  if (!item) return null;
  at = at || houseStamp();
  // Never before what this device already has, so a quick tick and untick
  // keep their order everywhere.
  const last = item.history.reduce((m, h) => (h[2] > m ? h[2] : m), "");
  if (at <= last) at = houseStamp(new Date(Date.parse(last) + 1000));
  item.history.push([what, me, at, randomHex(4)]);
  item.history = houseTrim(item.history, HOUSE.history);
  houseItem(item);
  return id;
}

// `doc` is this device's own copy and `me` this device's member: whether
// it left is only ever decided here.
function houseMerge(doc, other, me) {
  const latest = houseStamp(new Date(Date.now() + 86400000));
  const sides = [doc, other].map((s) => (s && typeof s === "object" ? s : {}));
  const out = { members: bare(), items: bare(), gone: bare() };
  sides.forEach((side, n) => {
    const fresh = [];
    entries(side.members).forEach(([id, m]) => {
      if (!HOUSE_ID.test(id) || !m || typeof m !== "object") return;
      const name = houseText(m.name, HOUSE.name), joined = houseTime(m.joined, latest);
      if (!name || !joined) return;
      const left = houseTime(m.left, latest);
      // A leave on someone already kept frees a place before new people are
      // added. This device's members come first, so made-up ones can't push
      // real ones out. Someone who left doesn't take a place.
      if (own(out.members, id)) {
        if (left && !(id === me && n === 1) && left > (out.members[id].left || "")) out.members[id].left = left;
        return;
      }
      fresh.push([id, name, joined, left]);
    });
    fresh.forEach(([id, name, joined, left]) => {
      if (left) {
        if (Object.keys(out.members).length >= HOUSE.members * 2) return;
      } else if (houseActive(out.members) >= HOUSE.members) return;
      out.members[id] = { name, joined };
      if (left && !(id === me && n === 1)) out.members[id].left = left;
    });
  });
  houseTrimMembers(out.members);
  sides.forEach((side) => entries(side.items).forEach(([id, item]) => {
    if (!HOUSE_ID.test(id) || !item || typeof item !== "object") return;
    const text = houseText(item.text, HOUSE.text);
    if (!text) return;
    if (!own(out.items, id) && Object.keys(out.items).length >= HOUSE.kept) return;
    if (!own(out.items, id)) out.items[id] = { text, history: [] };
    const mine = out.items[id], seen = new Set(mine.history.map((h) => h[3]));
    (Array.isArray(item.history) ? item.history.slice(0, HOUSE.history * 4) : []).forEach((h) => {
      if (Array.isArray(h) && h.length === 4 && HOUSE_WHATS.includes(h[0]) && typeof h[1] === "string"
          && HOUSE_ID.test(h[1]) && houseTime(h[2], latest) && typeof h[3] === "string"
          && HOUSE_ENTRY.test(h[3]) && !seen.has(h[3])) {
        mine.history.push(h.slice());
        seen.add(h[3]);
      }
    });
  }));
  Object.keys(out.items).forEach((id) => {
    const item = out.items[id];
    if (!item.history.length) { delete out.items[id]; return; }
    item.history = houseTrim(item.history, HOUSE.history);
    houseItem(item);
  });
  // A thing gone for good stays gone, so an old copy can't bring it back;
  // but only one removed over 30 days ago, and not added or restored since,
  // so nobody can erase a thing still on the list.
  const cutoff = houseStamp(new Date(Date.now() - HOUSE.keepDays * 86400000));
  sides.forEach((side) => entries(side.gone).forEach(([id, at]) => {
    at = houseTime(at, latest);
    if (!HOUSE_ID.test(id) || !at) return;
    if (own(out.items, id) && !out.items[id].removed) {
      const hist = out.items[id].history;
      const lives = hist.filter((h) => h[0] === "added" || h[0] === "restored").map((h) => h[2]);
      const newest = hist.reduce((m, h) => (h[2] > m ? h[2] : m), "");
      // A later tick means the thing is still here. Trimmed history may
      // no longer contain the line that added it.
      if (at > cutoff || newest >= at || lives.some((l) => l >= at)) return;
    }
    if (at > (out.gone[id] || "")) out.gone[id] = at;
    delete out.items[id];
  }));
  return out;
}

function houseTidy(doc, now) {
  const cutoff = houseStamp(new Date(now.getTime() - HOUSE.keepDays * 86400000));
  const removed = Object.keys(doc.items).filter((k) => doc.items[k].removed)
    .sort((a, b) => (doc.items[a].removed < doc.items[b].removed ? -1 : 1));
  const extra = Math.max(0, Object.keys(doc.items).length - HOUSE.kept);
  removed.forEach((k, n) => {
    if (doc.items[k].removed < cutoff || n < extra) { doc.gone[k] = doc.items[k].removed; delete doc.items[k]; }
  });
  const forget = houseStamp(new Date(now.getTime() - HOUSE.goneDays * 86400000));
  const kept = Object.keys(doc.gone).filter((k) => doc.gone[k] >= forget)
    .sort((a, b) => (doc.gone[a] > doc.gone[b] ? -1 : 1)).slice(0, HOUSE.gone);
  const gone = bare();
  kept.forEach((k) => { gone[k] = doc.gone[k]; });
  doc.gone = gone;
  if (doc.members) houseTrimMembers(doc.members);
  return doc;
}

const houseSize = (doc) => enc8(JSON.stringify(doc)).length;

// Small enough for the server however busy the household is.
function houseFit(doc) {
  const removed = Object.keys(doc.items).filter((k) => doc.items[k].removed)
    .sort((a, b) => (doc.items[a].removed < doc.items[b].removed ? -1 : 1));
  while (houseSize(doc) > HOUSE.budget && removed.length) {
    const k = removed.shift();
    doc.gone[k] = doc.items[k].removed;
    delete doc.items[k];
  }
  for (const size of [3, 2]) {
    if (houseSize(doc) <= HOUSE.budget) break;
    Object.values(doc.items).forEach((item) => { item.history = houseTrim(item.history, size); });
  }
  for (const k of Object.keys(doc.gone).sort((a, b) => (doc.gone[a] < doc.gone[b] ? -1 : 1))) {
    if (houseSize(doc) <= HOUSE.budget) break;
    delete doc.gone[k];
  }
  return doc;
}

// The list padded to whole kilobytes, as hello.py's house_seal does.
function houseBody(doc) {
  const body = Object.assign({}, houseFit(doc), { pad: "" });
  const size = enc8(JSON.stringify(body)).length;
  body.pad = " ".repeat((1024 - (size % 1024)) % 1024);
  return body;
}

const who = (doc, id) => (own(doc.members, id) ? doc.members[id].name : "") || "?";

function houseHistory(doc, item, lang) {
  const words = UI[lang] || UI.en;
  // Weekday and clock time on this device. The list still stores UTC, and
  // everyone who opens it can see both.
  return item.history.slice(-4).map(([what, by, at]) => {
    const when = new Date(at);
    if (Number.isNaN(when.getTime())) return "";
    const day = when.toLocaleDateString(lang, { weekday: "long" });
    const clock = when.toLocaleTimeString(lang, { hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
    return (words["h_" + what] || UI.en["h_" + what]).replace("{name}", who(doc, by)).replace("{when}", day + ", " + clock);
  }).filter(Boolean).join("; ");
}

// Worked out from the members themselves, so a join can't be hidden by
// giving it an old time.
function houseNews(doc, me, seen, lang) {
  const words = UI[lang] || UI.en, was = seen && typeof seen === "object" ? seen : {}, now = {}, lines = [];
  Object.entries(doc.members).forEach(([id, m]) => {
    now[id] = m.left ? "left" : "in";
    if (id === me || was[id] === now[id]) return;
    if (!own(was, id)) lines.push(words.joinedNote.replace("{name}", who(doc, id)));
    if (m.left) lines.push(words.leftNote.replace("{name}", who(doc, id)));
  });
  return [lines, now];
}

function houseLeftUnasked(doc, me, asked) {
  return Object.entries(doc.members).filter(([id, m]) => m.left && id !== me && !(asked || []).includes(id)).map(([id]) => id);
}

function syncForm(state) {
  return { intent: state.intent ? { text: state.intent.text, date: state.intent.date } : null,
           finished: state.finished, updated: state.updated || "", devices: state.devices || {} };
}

// The devices syncing with a code, inside the encryption, the newest day
// for each, as hello.py's merge_devices does.
function mergeDevices(mine, theirs) {
  const out = {};
  [mine, theirs].forEach((side) => entries(side).forEach(([id, d]) => {
    // Written by whoever holds the code, so checked: a real date, and a name
    // that is plain text.
    const name = d ? houseText(d.name, 40) : "";
    if (/^[0-9a-f]{12}$/.test(id) && name && isDate(d.seen) && !Number.isNaN(Date.parse(d.seen))
        && (!out[id] || d.seen > out[id].seen)) out[id] = { name, seen: d.seen };
  }));
  return Object.fromEntries(Object.entries(out).sort((a, b) => (a[1].seen < b[1].seen ? -1 : 1)).slice(-20));
}

function noteDevice(state, others, today) {
  if (!state.deviceId) state.deviceId = randomHex(6);
  state.devices = mergeDevices(state.devices, others);
  state.devices[state.deviceId] = { name: state.deviceName || UI.en.aPhone, seen: today };
}

// Mailto and sms links for a letter, opened in the phone's own apps.
function letterLink(letter, how, apple) {
  const to = String(letter.to || "").trim();
  if (how === "sms") return smsLink(phoneNumber(to), letter.text, apple);
  // Plain addresses only: anything that means something in a link (#, %,
  // ?, &, a comma) would send the letter somewhere else, or nowhere.
  const mail = /^[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$/.test(to) ? to : "";
  return `mailto:${mail}?body=${encodeURIComponent(letter.text)}`;
}

function syncTime(v) {
  // A real local time, not only the shape. 2026-02-31 matches the shape,
  // and Date.parse turns it into March, which would then beat a real February.
  const m = typeof v === "string" && /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})$/.exec(v);
  if (!m) return "";
  const y = +m[1], mo = +m[2], d = +m[3], h = +m[4], mi = +m[5], s = +m[6];
  const at = new Date(y, mo - 1, d, h, mi, s);
  if (at.getFullYear() !== y || at.getMonth() !== mo - 1 || at.getDate() !== d
      || at.getHours() !== h || at.getMinutes() !== mi || at.getSeconds() !== s) return "";
  return at.getTime() <= Date.now() + 86400000 ? v : "";
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
  state.devices = mergeDevices(state.devices, other.devices);
  state.finished.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));
  state.finished = state.finished.slice(-100);
  // A real time no more than a day ahead: one far ahead would win every
  // later change.
  const theirs = syncTime(other.updated);
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

// What a sync read is allowed to do. A failed read, or a copy that does
// not open, must not replace the other device.
function syncAction(status, opened) {
  if (status === 404) return "create";
  if (status === 200 && opened) return "update";
  return "stop";
}

const GROWTH_URL_DEFAULT = "https://insights.example.invalid/v1/growth";
const GROWTH_BATCH = 20;
const GROWTH_TRIES = 8;
const SESSION_GAP_MS = 30 * 60 * 1000;
const APP_VERSION = "1.66.0";

function growthUrlOk(url) {
  try {
    const u = new URL(url);
    if (u.username || u.password || u.hash) return false;
    if (/[\s\\]/.test(url)) return false;
    if (u.protocol === "https:") return true;
    return u.protocol === "http:" && (u.hostname === "localhost" || u.hostname === "127.0.0.1") && Boolean(u.port);
  } catch (e) {
    return false;
  }
}

function growthTarget() {
  let chosen = "";
  try { chosen = localStorage.getItem("hello-world-growth-server") || ""; } catch (e) { chosen = ""; }
  if (!chosen && typeof document !== "undefined") {
    const meta = document.querySelector('meta[name="growth-server"]');
    chosen = meta && meta.content ? meta.content.trim() : "";
  }
  if (chosen === "same-origin" && typeof location !== "undefined" && /^https?:$/.test(location.protocol)) {
    return location.origin + "/v1/growth";
  }
  if (chosen && growthUrlOk(chosen)) {
    const bare = chosen.replace(/\/$/, "");
    return bare.endsWith("/v1/growth") ? bare : bare + "/v1/growth";
  }
  return GROWTH_URL_DEFAULT;
}

function growthHost() {
  try { return new URL(growthTarget()).hostname; } catch (e) { return "insights.example.invalid"; }
}

function growthQueue() {
  try {
    const data = JSON.parse(localStorage.getItem("hello-world-growth-queue") || "[]");
    return Array.isArray(data) ? data.filter((item) => item && typeof item.event === "string").slice(-200) : [];
  } catch (e) {
    return [];
  }
}

function growthSaveQueue(events) {
  try { localStorage.setItem("hello-world-growth-queue", JSON.stringify(events.slice(-200))); } catch (e) { /* private mode */ }
}

function growthConsentOn(state) {
  return state.growthConsent === true && state.growth !== false;
}

function growthLog(state, event, plan) {
  if (typeof localStorage === "undefined") return;
  try {
    const data = JSON.parse(localStorage.getItem("hello-world-growth-log") || "[]");
    const rows = Array.isArray(data) ? data : [];
    rows.push({
      at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
      event: String(event).slice(0, 40),
      id: state.growthId || "",
      session: state.growthSession || "",
      streak: state.growthRun || 0,
      plan: plan ? String(plan).slice(0, 400) : null,
    });
    localStorage.setItem("hello-world-growth-log", JSON.stringify(rows.slice(-80)));
  } catch (e) { /* private mode */ }
}

function growthTouch(state, today) {
  if (state.growthLast === today) return state.growthRun || 1;
  let died = false;
  let run = 1;
  if (isDate(state.growthLast)) {
    const gap = daysBetween(state.growthLast, today);
    if (gap <= 0) run = state.growthRun || 1;
    else if (gap <= 4) run = Math.min((state.growthRun || 1) + 1, 99999);
    else {
      died = (state.growthRun || 0) > 1 || (state.growthBest || 0) > 1;
      run = 1;
    }
  }
  state.growthRun = run;
  state.growthBest = Math.max(state.growthBest || 0, run);
  state.growthLast = today;
  if (died) state.growthDied = true;
  return run;
}

function growthSession(state) {
  const now = Date.now();
  const fresh = !(typeof state.growthSession === "string" && /^[0-9a-f]{32}$/.test(state.growthSession)
    && typeof state.growthSessionAt === "number" && now - state.growthSessionAt <= SESSION_GAP_MS);
  if (fresh) state.growthSession = randomHex(16);
  state.growthSessionAt = now;
  return fresh;
}

function growthCapture(state, event, today) {
  const plan = state.intent && state.intent.text ? String(state.intent.text).slice(0, 400) : null;
  if (!growthConsentOn(state)) {
    growthLog(state, event, plan);
    return;
  }
  if (!state.growthId) state.growthId = randomHex(16);
  const started = growthSession(state);
  if (today) growthTouch(state, today);
  const now = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const queue = growthQueue();
  const one = (name) => ({
    event: String(name).slice(0, 40), at: now, id: state.growthId, session: state.growthSession,
    streak: state.growthRun || 0, best: state.growthBest || 0, plan, v: APP_VERSION,
    lang: language(state, (typeof navigator !== "undefined" && navigator.languages) || []), attempts: 0,
  });
  if (started) {
    queue.push(one("session_start"));
    growthLog(state, "session_start", plan);
  }
  queue.push(one(event));
  growthSaveQueue(queue);
  growthLog(state, event, plan);
}

function growthBody(state, batch) {
  return {
    id: state.growthId, session: state.growthSession || "", consent: true, v: APP_VERSION,
    events: batch.map((item) => ({
      event: item.event, at: item.at || "", session: item.session || "",
      streak: item.streak || 0, best: item.best || 0, plan: item.plan || null,
      v: item.v || APP_VERSION, lang: item.lang || "",
    })),
  };
}

async function growthPost(url, body) {
  if (!growthUrlOk(url) || typeof fetch !== "function") return "drop";
  try {
    const answer = await fetch(url, {
      method: "POST", redirect: "error", mode: "cors",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (answer.status >= 200 && answer.status < 300) return "ok";
    if (answer.status >= 300 && answer.status < 500) return "drop";
    return "retry";
  } catch (e) {
    return "retry";
  }
}

async function growthFlush(state) {
  if (!growthConsentOn(state)) return false;
  const url = growthTarget();
  for (let round = 0; round < 3; round++) {
    let queue = growthQueue().filter((item) => (item.attempts || 0) < GROWTH_TRIES);
    if (!queue.length) { growthSaveQueue([]); return true; }
    const batch = queue.slice(0, GROWTH_BATCH);
    const rest = queue.slice(GROWTH_BATCH);
    let result = await growthPost(url, growthBody(state, batch));
    if (result === "retry") {
      batch.forEach((item) => { item.attempts = (item.attempts || 0) + 1; });
      result = await growthPost(url, growthBody(state, batch));
      if (result === "retry") batch.forEach((item) => { item.attempts = (item.attempts || 0) + 1; });
    }
    if (result === "ok") {
      growthSaveQueue(rest);
      if (!rest.length) return true;
      continue;
    }
    if (result === "drop") batch.forEach((item) => { item.attempts = GROWTH_TRIES; });
    growthSaveQueue(batch.concat(rest));
    return false;
  }
  return true;
}

function growthLine(state) {
  const host = growthHost();
  const n = state.growthRun || 1;
  let line = state.growthDied
    ? "Your streak died. It was " + (state.growthBest || 0) + ". Repair is $2.99. Nothing is charged."
    : "Your streak is " + n + ". Open again tomorrow or it dies. A note was offered to " + host + ".";
  if (state.plusStub) line += " Pro+ member. Your streak is still watching.";
  return line;
}

function growthEula(host) {
  return "Streak notes are selected. This phone keeps a client id, a session id, and this visit, including the words of a plan, and offers a batch to "
    + host + ". Household lists, letters, and sync codes are not included. Nothing is billed.";
}

if (typeof module !== "undefined") {
  module.exports = { UI, ordinal, todaysPair, clean, parse, asks, answer, setPlan, finishToday, language, blank,
    syncKeys, sealSync, openSync, mergeSync, syncForm, normalCode, todayOf, clearToday, picks, bringBack,
    phoneNumber, smsLink, utcTime, pushText, nearClock, haikuText, exportText, setDayStart, REMIND_TIMES, DAY_STARTS,
    fresh, smallerDue, comingBack, smaller, endDay, noteSideways, mergeDevices, noteDevice, letterLink,
    houseKeys, houseNew, houseJoin, houseLeave, houseChange, houseMerge, houseTidy, houseBody, houseHistory,
    houseNews, houseLeftUnasked, newCode, houseFit, houseStamp, syncAction, syncTime, HOUSE,
    planParts, finishListed, growthUrlOk, growthTarget, growthTouch, growthConsentOn };
}

if (typeof document !== "undefined") {
  const $ = (id) => document.getElementById(id);
  let state = parse(localStorage.getItem(KEY) || "{}");
  let timer = null, hearTimer = null;
  const t = () => UI[language(state, navigator.languages)];
  const today = () => todayOf(state);
  function buried() {
    const el = document.activeElement;
    return Boolean(el && el.closest && el.closest("[hidden]"));
  }
  // The status line first, then the plan box, and only if it is on screen
  // and the person has not moved. A later line that is not one of these
  // cancels the wait, so it does not pull the cursor.
  function hearSoon() {
    const status = $("status");
    status.tabIndex = -1;
    status.focus();
    clearTimeout(hearTimer);
    hearTimer = setTimeout(() => {
      if (document.activeElement !== status) return;
      const form = $("plan-form"), plan = $("plan-input");
      if (plan && form && !form.hidden) plan.focus();
    }, 400);
  }
  const say = (key) => {
    const words = t();
    let text = "";
    if (typeof key === "string" && key.startsWith("goodMany:")) {
      text = (words.goodMany || UI.en.goodMany).replace("{n}", key.slice(9));
    } else if (key === "endTally") {
      text = $("status").dataset.tally || "";
    } else if (key) {
      text = words[key] || "";
    }
    if (key === "skipped" && growthConsentOn(state)) {
      text = (text + " " + (words.skipNag || UI.en.skipNag)).trim();
    }
    const status = $("status");
    status.style.whiteSpace = "";
    status.textContent = text;
    const hear = Boolean(text) && (key === "saved" || key === "kept" || key === "good"
      || key === "unsureSaid" || key === "skipped" || key === "carriedSaid"
      || key === "sidewaysSaid" || key === "cleanSaid" || key === "cleared" || key === "back"
      || (typeof key === "string" && key.startsWith("goodMany:")));
    if (!hear) {
      clearTimeout(hearTimer);
      return;
    }
    // First Skip: the question is still there. The status line is live,
    // so it is read without leaving the button. A second Skip hides it.
    if (key === "skipped" && asks(state, today())) {
      clearTimeout(hearTimer);
      return;
    }
    hearSoon();
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
        if (state.pushToken) await fetch(url(state.pushToken), { method: "DELETE", redirect: "error" });
        delete state.pushToken; save();
        return true;
      }
      const got = await fetch(`${location.origin}/v1/push/key`, { cache: "no-store", redirect: "error" });
      if (!got.ok) return false;
      const key = (await got.json()).key.replace(/-/g, "+").replace(/_/g, "/");
      const raw = Uint8Array.from(atob(key + "===".slice((key.length + 3) % 4)), (c) => c.charCodeAt(0));
      const sub = await reg.pushManager.getSubscription()
        || await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: raw });
      if (!state.pushToken) {
        state.pushToken = Array.from(crypto.getRandomValues(new Uint8Array(16)), (b) => b.toString(16).padStart(2, "0")).join("");
        save();
      }
      const put = await fetch(url(state.pushToken), { method: "PUT", redirect: "error", headers: { "Content-Type": "application/json" },
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
    ["yes", "no", "unsure", "skip", "sideways", "did", "clear", "save"].forEach((id) => { $(id).textContent = s[id]; });
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
    // The day was closed: what was carried shows as tomorrow's plan, and
    // nothing typed today can replace it.
    const closed = Boolean(state.intent && state.intent.date > day);
    $("today-label").textContent = closed ? s.dayClosed : planned ? s.todayHave : s.todayAsk;
    $("today-plan").hidden = !planned && !closed;
    $("today-buttons").hidden = !planned;
    $("today-plan").textContent = planned || closed ? state.intent.text : "";
    $("plan-form").hidden = planned || closed || asking;
    // Once a week at most: noted the first time it shows, and shown for
    // the rest of that visit.
    if (nudging === null) {
      nudging = !planned && !closed && !asking && smallerDue(state, day);
      if (nudging) { state.smallerOffered = day; save(); }
    }
    $("smaller-nudge").hidden = planned || closed || asking || !nudging;
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
    const houseBox = $("fridge-house");
    houseBox.replaceChildren();
    const listed = state.houseList && state.houseList.items;
    if (listed) {
      Object.values(listed).filter((item) => item && !item.removed && item.text).forEach((item) => {
        houseBox.append(Object.assign(document.createElement("p"), { className: "big", textContent: item.text }));
        const hist = houseHistory(state.houseList, item, lang);
        if (hist) houseBox.append(Object.assign(document.createElement("p"), { className: "note", textContent: hist }));
      });
    }
    $("fridge-note").textContent = s.printNote;
    drawSync();
    if (typeof drawHouse === "function") drawHouse();
    if (typeof drawLetters === "function") drawLetters();
    const line = $("klingon-line");
    if (line) {
      line.hidden = !state.klingon;
      line.textContent = "qo' vIquv.";
    }
    if ($("klingon")) $("klingon").textContent = s.klingon;
    if ($("haiku")) $("haiku").textContent = s.haiku;
    drawGrowth();
    // A second Skip hides the question while focus is still on that button.
    if (buried()) hearSoon();
  }

  let forking = false, ending = false, nudging = null;
  const SYNC_KEY = "hello-world-sync";
  let keys = null;
  let changing = false;
  try { keys = JSON.parse(localStorage.getItem(SYNC_KEY) || "null"); } catch (e) { keys = null; }
  const asBytes = (k) => k && { label: k.label, enc: Uint8Array.from(k.enc), mac: Uint8Array.from(k.mac) };

  // Pull, merge and push; quiet unless something goes wrong while asked.
  // A failed read is left as it is. The put names the version just read.
  async function sync(loud) {
    if (!keys) return;
    const k = asBytes(keys), url = `${location.origin}/v1/sync/${k.label}`;
    try {
      let done = false;
      for (let n = 0; n < 3 && !done; n++) {
        const got = await fetch(url, { cache: "no-store", redirect: "error" });
        let other = null;
        if (got.status === 200) other = await openSync(k, await got.arrayBuffer());
        const action = syncAction(got.status, Boolean(other));
        if (action === "stop") throw new Error("sync");
        if (action === "update") { mergeSync(state, other, today()); save(); draw(); }
        noteDevice(state, other && other.devices, today());
        save();
        const tag = action === "update" ? (got.headers.get("ETag") || "") : "missing";
        if (!tag) throw new Error("sync");
        const put = await fetch(url, { method: "PUT", redirect: "error", body: await sealSync(k, syncForm(state)),
          headers: { "Content-Type": "application/octet-stream", "If-Match": tag } });
        if (put.status === 412) continue;
        if (!put.ok) throw new Error("sync");
        done = true;
      }
      if (loud) say(done ? "syncOn" : "syncFail");
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
    $("device-name-label").textContent = s.deviceName;
    $("device-save").textContent = s.deviceSave;
    $("device-row").hidden = !keys;
    if (!$("device-name").value) $("device-name").value = state.deviceName || "";
    const devs = Object.entries(state.devices || {}).sort((a, b) => (a[1].seen < b[1].seen ? 1 : -1));
    const lang = language(state, navigator.languages);
    const list = devs.map(([id, d]) => {
      const [y, m, dd] = d.seen.split("-").map(Number);
      const day = d.seen === today() ? s.todayWord : new Date(y, m - 1, dd).toLocaleDateString(lang, { weekday: "long" });
      return `${id === state.deviceId ? s.thisPhone : d.name} (${id.slice(0, 4)}), ${day}`;
    });
    const names = devs.map(([, d]) => d.name.toLowerCase());
    $("sync-devices").textContent = keys && list.length
      ? s.devices.replace("{list}", list.join("; ")) + (new Set(names).size !== names.length ? " " + s.sameName : "") : "";
    const when = keys && state.updated ? new Date(state.updated) : null;
    $("sync-last").textContent = when && !isNaN(when)
      ? s.lastChange.replace("{when}", when.toLocaleString(language(state, navigator.languages),
          { weekday: "short", hour: "2-digit", minute: "2-digit" })) : "";
  }

  $("device-save").addEventListener("click", (event) => {
    event.preventDefault();
    state.deviceName = $("device-name").value.trim().slice(0, 40) || undefined;
    save(); sync(false); drawSync();
  });
  // Letters: kept here until sent with the phone's own mail or messages.
  function drawLetters() {
    const s = t();
    $("letters-label").textContent = s.letters;
    $("letters-note").textContent = s.lettersNote;
    $("letter-to-label").textContent = s.letterTo;
    $("letter-text-label").textContent = s.letterText;
    $("letter-save").textContent = s.letterSave;
    $("letter-mail").textContent = s.letterMail;
    $("letter-sms").textContent = s.letterSms;
    $("letter-keep-label").textContent = s.letterKeep;
    $("letters-clear").textContent = s.lettersClear;
    $("letters-clear").hidden = !(state.letters || []).length;
    $("letter-list").replaceChildren(...(state.letters || []).map((letter) => {
      const div = document.createElement("div");
      const open = Object.assign(document.createElement("button"), { textContent: s.letterOpen, className: "small-button" });
      open.addEventListener("click", () => { $("letter-to").value = letter.to; $("letter-text").value = letter.text; editing = letter; });
      const del = Object.assign(document.createElement("button"), { textContent: s.letterDelete, className: "small-button" });
      del.addEventListener("click", () => {
        state.letters = state.letters.filter((l) => l !== letter);
        if (editing === letter) editing = null;
        save(); drawLetters();
      });
      div.append(Object.assign(document.createElement("p"), { textContent: (letter.to || "…") + ": " + letter.text.slice(0, 60) }), open, del);
      return div;
    }));
  }
  // The letter open for editing itself, not its place in the list, which
  // moves when another one is deleted.
  let editing = null;
  const currentLetter = () => ({ to: $("letter-to").value.trim().slice(0, 100), text: $("letter-text").value.trim().slice(0, 4000), date: today() });
  function keepLetter(letter) {
    state.letters = (state.letters || []).filter((l) => l !== editing);
    if (letter) state.letters.push(letter);
    state.letters = state.letters.slice(-20);
    editing = null;
    save(); drawLetters();
  }
  $("letter-save").addEventListener("click", (event) => {
    event.preventDefault();
    const letter = currentLetter();
    if (!letter.text) { say("nothing"); return; }
    keepLetter(letter); say("letterSaved");
  });
  ["mail", "sms"].forEach((how) => $("letter-" + how).addEventListener("click", (event) => {
    event.preventDefault();
    const letter = currentLetter();
    if (!letter.text) { say("nothing"); return; }
    location.href = letterLink(letter, how, /iPhone|iPad/.test(navigator.userAgent));
    keepLetter($("letter-keep").checked ? letter : null);
    $("letter-text").value = "";
  }));
  $("letters-clear").addEventListener("click", () => {
    if (!confirm(t().lettersClearAsk)) return;
    state.letters = []; editing = null; save(); drawLetters(); say("lettersCleared");
  });
  drawLetters();

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
      // The devices belong to the old code; a stranger among them must not
      // follow to the next one.
      delete state.devices; save();
      drawSync(); say("syncOffDone");
      return;
    }
    if (normalCode($("sync-code").value).length !== 25) { say("syncBad"); return; }
    const k = await syncKeys($("sync-code").value);
    keys = { label: k.label, enc: Array.from(k.enc), mac: Array.from(k.mac) };
    changing = false;
    delete state.devices; save();
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
  $("unsure").addEventListener("click", act(() => answer(state, "unsure", today())));
  $("skip").addEventListener("click", act(() => {
    const said = answer(state, "skip", today());
    if (said === "skipped" && growthConsentOn(state)) growthCapture(state, "skipped", today());
    return said;
  }));
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
    const said = smaller(state, $("smaller-input").value, today());
    if (!said) return "nothing";
    state.offerSmaller = false;
    $("smaller-input").value = "";
    return said;
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
  $("klingon").addEventListener("click", () => {
    if (state.klingon) delete state.klingon;
    else state.klingon = true;
    save();
    draw();
    clearTimeout(hearTimer);
    const status = $("status");
    status.style.whiteSpace = "";
    status.textContent = state.klingon ? t().klingonOn : t().klingonOff;
    status.tabIndex = -1;
    status.focus();
  });
  function phrase(key) {
    return t()[key] || UI.en[key] || "";
  }
  let growthNoted = false;
  let growthLater = false;
  function drawGrowth() {
    const host = growthHost();
    const asking = state.growthConsent == null && state.growth !== false;
    const on = growthConsentOn(state);
    const eula = $("eula");
    if (eula) {
      eula.hidden = !asking;
      $("eula-title").textContent = phrase("eulaTitle");
      $("eula-text").textContent = growthEula(host);
      $("eula-check-label").textContent = phrase("eulaCheck");
      $("eula-yes").textContent = phrase("eulaYes");
      $("eula-no").textContent = phrase("eulaNo");
      if (asking && !eula.dataset.ready) {
        eula.dataset.ready = "1";
        $("eula-check").checked = true;
      }
    }
    const box = $("growth");
    if (box) {
      const show = on && !growthLater;
      box.hidden = !show;
      if (show) {
        if (!growthNoted) {
          growthNoted = true;
          growthTouch(state, today());
          growthCapture(state, "opened", today());
          save();
          growthFlush(state);
        }
        $("growth-nag").textContent = growthLine(state);
        $("growth-keep").textContent = phrase("growthKeep");
        $("growth-later").textContent = phrase("growthLater");
        $("growth-repair").textContent = phrase("growthRepair");
        $("growth-plus").textContent = phrase("growthPlus");
      }
    }
    const ad = $("sponsored");
    if (ad) {
      ad.hidden = !on || state.plusStub;
      ad.textContent = phrase("sponsored");
    }
    if ($("cowbell")) $("cowbell").textContent = phrase("cowbell");
    if ($("growth-toggle")) $("growth-toggle").textContent = on ? phrase("growthOff") : phrase("growthOn");
    if ($("growth-server-label")) $("growth-server-label").textContent = phrase("growthServer");
    if ($("growth-server-save")) $("growth-server-save").textContent = phrase("growthServerSave");
    const field = $("growth-server");
    if (field && !field.value) {
      try { field.value = localStorage.getItem("hello-world-growth-server") || ""; } catch (e) { /* private mode */ }
    }
  }
  function acceptGrowth() {
    state.growthConsent = true;
    delete state.growth;
    growthTouch(state, today());
    growthCapture(state, "eula_accept", today());
    growthNoted = false;
    save();
  }
  function declineGrowth() {
    const event = state.growthConsent === true ? "growth_off" : "eula_decline";
    state.growthConsent = false;
    state.growth = false;
    growthSaveQueue([]);
    growthLog(state, event, null);
    growthNoted = false;
    save();
  }
  $("eula-yes").addEventListener("click", () => {
    if (!$("eula-check").checked) { declineGrowth(); draw(); return; }
    acceptGrowth();
    draw();
    growthFlush(state);
  });
  $("eula-no").addEventListener("click", () => { declineGrowth(); draw(); say(""); });
  $("growth-keep").addEventListener("click", () => {
    clearTimeout(hearTimer);
    growthCapture(state, "keep", today());
    save();
    const status = $("status");
    status.textContent = phrase("growthKeepSaid");
    status.tabIndex = -1;
    status.focus();
    growthFlush(state);
  });
  $("growth-later").addEventListener("click", () => {
    growthLater = true;
    growthCapture(state, "later", today());
    save();
    draw();
    growthFlush(state);
  });
  $("growth-repair").addEventListener("click", () => {
    growthTouch(state, today());
    const best = Math.max(state.growthBest || 0, state.growthRun || 0, 1);
    state.growthRun = state.growthBest = best;
    state.growthDied = false;
    state.growthLast = today();
    growthCapture(state, "repair", today());
    save();
    draw();
    clearTimeout(hearTimer);
    const status = $("status");
    status.textContent = phrase("growthRepairSaid");
    status.tabIndex = -1;
    status.focus();
    growthFlush(state);
  });
  $("growth-plus").addEventListener("click", () => {
    state.plusStub = true;
    growthCapture(state, "plus", today());
    save();
    draw();
    clearTimeout(hearTimer);
    const status = $("status");
    status.textContent = phrase("growthPlusSaid");
    status.tabIndex = -1;
    status.focus();
    growthFlush(state);
  });
  $("growth-toggle").addEventListener("click", () => {
    if (growthConsentOn(state)) declineGrowth();
    else acceptGrowth();
    save();
    draw();
    if (growthConsentOn(state)) growthFlush(state);
  });
  $("growth-server-save").addEventListener("click", () => {
    const value = $("growth-server").value.trim();
    if (!value) {
      try { localStorage.removeItem("hello-world-growth-server"); } catch (e) { /* private mode */ }
      say("saved");
      draw();
      return;
    }
    if (value !== "same-origin" && !growthUrlOk(value)) {
      $("status").textContent = phrase("growthServerBad");
      return;
    }
    try { localStorage.setItem("hello-world-growth-server", value); } catch (e) { /* private mode */ }
    say("saved");
    draw();
  });
  $("cowbell").addEventListener("click", () => {
    clearTimeout(hearTimer);
    const status = $("status");
    status.style.whiteSpace = "";
    status.textContent = phrase("cowbellSaid");
    status.tabIndex = -1;
    status.focus();
    if (growthConsentOn(state)) {
      growthCapture(state, "cowbell", today());
      save();
      growthFlush(state);
    }
  });
  $("haiku").addEventListener("click", () => {
    clearTimeout(hearTimer);
    const status = $("status");
    status.style.whiteSpace = "pre-line";
    status.textContent = haikuText(Number(String(today()).slice(8, 10)));
    status.tabIndex = -1;
    status.focus();
  });
  $("did").addEventListener("click", act(() => finishToday(state, today())));
  $("clear").addEventListener("click", act(() => clearToday(state, today())));
  $("plan-form").addEventListener("submit", act(() => {
    const said = setPlan(state, $("plan-input").value, today());
    if (said === "saved" || said === "addedTomorrow") {
      $("plan-input").value = "";
      if (growthConsentOn(state)) growthCapture(state, "plan", today());
    }
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
    try {
      localStorage.removeItem(KEY);
      localStorage.removeItem(SYNC_KEY);
      localStorage.removeItem("hello-world-growth-queue");
      localStorage.removeItem("hello-world-growth-log");
    } catch (e) { /* nothing saved */ }
    keys = null;
    state = blank();
    state.lang = lang;
    $("repeat-text").value = $("family-name").value = $("family-number").value = "";
    save(); draw(); say("forgotten"); schedule();
  });
  // The household list. Nothing in it is ever sent in someone else's name,
  // and the code is never put in a message.
  let houseReached = true, houseNote = "", houseQueue = Promise.resolve();
  const houseStore = (k) => ({ label: k.label, enc: Array.from(k.enc), mac: Array.from(k.mac) });
  const houseUrl = (k) => `${location.origin}/v1/sync/${k.label}`;
  // [the list, its version], or [null, null] when it isn't there.
  async function houseFetch(stored) {
    const k = asBytes(stored);
    try {
      const got = await fetch(houseUrl(k), { cache: "no-store", redirect: "error" });
      if (!got.ok) return [null, null];
      return [await openSync(k, await got.arrayBuffer()), got.headers.get("ETag")];
    } catch (e) { return [null, null]; }
  }
  // True, "changed" when someone else wrote since `tag` was read, or false.
  async function housePut(stored, doc, tag) {
    // No version, no write. A missing tag used to omit If-Match, and the
    // server then replaced whatever was stored.
    if (!tag) return false;
    const k = asBytes(stored), headers = { "Content-Type": "application/octet-stream", "If-Match": tag };
    try {
      const put = await fetch(houseUrl(k), { method: "PUT", redirect: "error", body: await sealSync(k, houseBody(doc)), headers });
      return put.ok ? true : put.status === 412 ? "changed" : false;
    } catch (e) { return false; }
  }
  // One at a time, so two quick taps can't each start from the same copy;
  // again when another device wrote in between. With needServer, nothing
  // changes here unless the server took it. Resolves to whether it did.
  function houseSync(change, needServer) {
    const run = async () => {
      if (!state.house) return false;
      const house = state.house;
      let doc = houseMerge(state.houseList || {}, {}, house.me), reached = false;
      for (let n = 0; n < 3; n++) {
        const [theirs, tag] = await houseFetch(house.keys);
        if (!theirs && needServer) break;
        doc = houseMerge(state.houseList || {}, theirs, house.me);
        if (change) change(doc);
        houseFit(houseTidy(doc, new Date()));
        if (!theirs) break;
        const put = await housePut(house.keys, doc, tag);
        if (put !== "changed") { reached = put === true; break; }
      }
      houseReached = reached;
      if (needServer && !reached) { drawHouse(); return false; }
      if (state.house === house) { state.houseList = doc; save(); }
      drawHouse();
      return reached;
    };
    houseQueue = houseQueue.then(run, run);
    return houseQueue;
  }
  function drawHouse() {
    const s = t(), lang = language(state, navigator.languages);
    $("house-label").textContent = s.house;
    $("house-intro").textContent = s.houseIntro;
    $("house-code-label").textContent = s.houseCode;
    $("house-name-label").textContent = s.houseName;
    $("house-join-button").textContent = s.houseJoin;
    $("house-add-button").textContent = s.houseAdd;
    $("house-removed-label").textContent = s.houseRemoved;
    $("house-leave").textContent = s.houseLeave;
    $("house-join").hidden = Boolean(state.house);
    $("house-on").hidden = !state.house;
    if (!state.house || !state.houseList) return;
    const doc = state.houseList, me = state.house.me;
    $("house-offline").hidden = houseReached;
    $("house-offline").textContent = s.houseOffline;
    const [lines, seen] = houseNews(doc, me, state.house.seen, lang);
    $("house-news").replaceChildren(...lines.concat(houseNote ? [houseNote] : []).map((l) => Object.assign(document.createElement("p"), { textContent: l, className: "note" })));
    if (JSON.stringify(seen) !== JSON.stringify(state.house.seen)) { state.house.seen = seen; save(); }
    const ask = houseLeftUnasked(doc, me, state.house.asked)[0];
    $("house-rekey").hidden = !ask;
    if (ask) {
      $("house-rekey-text").textContent = s.rekeyAsk.replace("{name}", (doc.members[ask] || {}).name || "?");
      $("house-rekey-yes").textContent = s.rekeyYes;
      $("house-rekey-no").textContent = s.rekeyNo;
      $("house-rekey").dataset.who = ask;
    }
    const entries = Object.entries(doc.items);
    $("house-items").replaceChildren(...entries.filter(([, i]) => !i.removed).map(([id, item]) => {
      const div = document.createElement("div");
      const box = Object.assign(document.createElement("input"), { type: "checkbox", checked: item.done, id: "hi-" + id });
      box.addEventListener("change", () => houseSync((d) => houseChange(d, me, box.checked ? "ticked" : "unticked", id, null)));
      const label = Object.assign(document.createElement("label"), { htmlFor: "hi-" + id, textContent: " " + item.text });
      label.style.display = "inline";
      const remove = Object.assign(document.createElement("button"), { textContent: s.houseRemove, className: "small-button" });
      remove.addEventListener("click", () => houseSync((d) => houseChange(d, me, "removed", id, null)));
      const history = Object.assign(document.createElement("p"), { className: "note", textContent: houseHistory(doc, item, lang) });
      div.append(box, label, history, remove);
      return div;
    }));
    $("house-removed").replaceChildren(...entries.filter(([, i]) => i.removed).map(([id, item]) => {
      const div = document.createElement("div");
      const back = Object.assign(document.createElement("button"), { textContent: s.houseRestore, className: "small-button" });
      back.addEventListener("click", () => houseSync((d) => houseChange(d, me, "restored", id, null)));
      div.append(Object.assign(document.createElement("p"), { textContent: item.text + " — " + houseHistory(doc, item, lang) }), back);
      return div;
    }));
  }
  $("house-join").addEventListener("submit", async (event) => {
    event.preventDefault();
    const code = normalCode($("house-code").value), name = houseText($("house-name").value, HOUSE.name);
    if (code.length !== 25 || !name) { say("houseNotFound"); return; }
    const stored = houseStore(await houseKeys(code.match(/.{5}/g).join("-")));
    const me = randomHex(6);
    let doc = null, put = false;
    for (let n = 0; n < 3 && put !== true; n++) {
      const [theirs, tag] = await houseFetch(stored);
      if (!theirs) { say("houseNotFound"); return; }
      doc = houseJoin(houseMerge({}, theirs), me, name);
      if (!own(doc.members, me)) { say("houseFull"); return; }
      put = await housePut(stored, doc, tag);
      if (put === false) break;
    }
    if (put !== true) { say("syncFail"); return; }
    state.house = { keys: stored, me, seen: houseNews(doc, me, {}, "en")[1], asked: [] };
    state.houseList = doc;
    $("house-code").value = "";
    save(); drawHouse(); say("houseJoined");
  });
  $("house-add").addEventListener("submit", (event) => {
    event.preventDefault();
    const text = $("house-add-text").value;
    $("house-add-text").value = "";
    houseSync((d) => houseChange(d, state.house.me, "added", null, text));
  });
  $("house-rekey-yes").addEventListener("click", () => {
    // Only from the newest copy on the server, so two members doing this at
    // once don't split the household onto two codes.
    houseQueue = houseQueue.then(async () => {
      if (!state.house) return;
      const [theirs] = await houseFetch(state.house.keys);
      if (!theirs) { say("rekeyFail"); return; }
      const doc = houseMerge(state.houseList || {}, theirs, state.house.me);
      houseFit(houseTidy(doc, new Date()));
      const code = newCode(), stored = houseStore(await houseKeys(code));
      if (await housePut(stored, doc, "missing") !== true) { say("syncFail"); return; }
      try { await fetch(houseUrl(asBytes(state.house.keys)), { method: "DELETE", redirect: "error" }); } catch (e) { /* gone anyway */ }
      const left = Object.entries(doc.members).filter(([, m]) => m.left).map(([id]) => id);
      state.house = Object.assign({}, state.house, { keys: stored, asked: Array.from(new Set(state.house.asked.concat(left))) });
      state.houseList = doc;
      houseNote = t().newCodeSaid.replace("{code}", code);
      save(); drawHouse();
    });
  });
  $("house-rekey-no").addEventListener("click", () => {
    state.house.asked = state.house.asked.concat([$("house-rekey").dataset.who]);
    save(); drawHouse();
  });
  $("house-leave").addEventListener("click", async () => {
    if (!confirm(t().houseLeaveAsk)) return;
    // Only once the others can be told.
    if (!await houseSync((d) => houseLeave(d, state.house.me), true)) { say("houseLeaveOffline"); return; }
    delete state.house; delete state.houseList;
    save(); drawHouse(); say("houseLeft");
  });

  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
  draw();
  houseSync();
  savePrefs();
  reminders();
  sync(false);
  // A page left open past the day's start shows the new day.
  setInterval(() => { if ($("date").textContent !== longDate(today(), language(state, navigator.languages))) draw(); }, 60000);
}
