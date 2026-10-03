#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print "Hello, world!" and one small useful thing each day.

On Windows the installer runs it through hello.cmd with its own pinned Python.
It shows a thought and a small thing to try, and can keep one plan for the day.
Everything it saves stays in one small file in the user's own folder, and
nothing is sent anywhere. Exit 0 when the text was written, 1 when stdout
could not be written or a command (--reset, --stats, --remind, --streak)
failed, 2 for an unknown option.
"""
import collections
import contextlib
import copy
import datetime
import json
import os
import shutil
import sys
import textwrap
import unicodedata
import time

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
        "Sunday")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
DAYS_ES = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado",
           "domingo")
MONTHS_ES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre")
GREETING = "Hello, world!"

# Chosen by date, so everyone sees the same line on the same day and the
# lists repeat every 100 days (the pairing much later).
TIPS = (
    'Sip a glass of water slowly, away from your screen.',
    'Roll your shoulders back five times, nice and slow.',
    'Rest your eyes for twenty seconds: look far away, or close them.',
    'Stretch your arms overhead, seated or standing, and take a deep breath.',
    'Move to the farthest room or window you can reach, and back.',
    'Check your posture and let your shoulders drop away from your ears.',
    'Turn your neck gently side to side, only as far as feels easy.',
    'Open and close your hands ten times to loosen your fingers.',
    'Pin the one document you open most so it is one click away.',
    'Take a short walk or roll outside, whatever suits you.',
    'Pour a warm or cool drink and enjoy it away from your screen.',
    'Rest your attention on something calm, a view, a sound or a texture.',
    'Write the next step on one task you left half done.',
    'Plant both feet flat and sit tall, or stand tall, for ten breaths.',
    'Mute one group chat you only ever skim.',
    'Unclench your jaw and relax your forehead for a moment.',
    'Move around for two minutes in whatever way feels good today.',
    'Block fifteen minutes in your calendar for the task you keep putting off.',
    'Adjust your chair, screen or keyboard so one thing sits more comfortably.',
    'Take the long way to your next meeting or call, if you can.',
    'Save a template for one email you write again and again.',
    'Learn one keyboard shortcut for the program you use most.',
    'Drink a full glass of water before your next coffee or tea.',
    'Shrug your shoulders up to your ears, then let them melt down.',
    'Step outside or open a window for a minute of fresh air.',
    'Take five slow breaths, making each exhale a little longer.',
    'Pause for one quiet minute before you open your next message.',
    'Note one good thing that has happened so far today.',
    'Close your eyes for three breaths and notice how you feel.',
    'Name three things you notice right now, with any sense.',
    'Write down one thing you are looking forward to this week.',
    'Set a timer for two minutes and simply sit with no screen.',
    'Enjoy something small nearby, like a plant or a favorite mug.',
    'Think of one thing you did well this week and give yourself a nod.',
    'Listen to one favorite song, start to finish, with nothing else open.',
    'Breathe in for four counts and out for six, three times.',
    'Take one breath before reacting to the next small annoyance.',
    'Jot down one thing that made you laugh recently.',
    'For one minute, notice something pleasant: a sound, a smell or something you touch.',
    'Recall a place you love and picture it for thirty seconds.',
    'Say "good enough for now" about one small task and move on.',
    'Write one sentence about something you are grateful for.',
    'Savor the next sip of your drink and notice the taste.',
    'Take a short break between two tasks before you start the next one.',
    'Look for one thing today that turns out better than you expected.',
    'Choose one word for how you want the afternoon to feel.',
    'Let your mind rest for sixty seconds, then go back to your next task.',
    'Notice your feet on the floor and feel steady for a moment.',
    'Remember one kind thing someone did for you and enjoy the memory.',
    'Jot down one idea you want to revisit later and let it rest.',
    'Tidy one small corner of your desk, just one.',
    'Reply to one message that has been waiting a while.',
    "Write tomorrow's top task on a sticky note or in your notes.",
    'Close the browser tabs you no longer need.',
    'Say thanks to a colleague for something they did recently.',
    'Archive five old emails you no longer need.',
    'Rename one messy file so you can find it easily later.',
    'Clear one or two stray files off your desktop.',
    'Delete one old reminder that no longer applies.',
    'Add a clear title to a document you open often.',
    'Cross off one small item on your to-do list.',
    'Unsubscribe from one newsletter you never read.',
    'Wipe your keyboard or screen with a soft cloth.',
    'Put a pen, notebook, and water where you can reach them easily.',
    'Draft a short note to future you about where you left off today.',
    'Pick the one task that matters most this afternoon and do it first.',
    'Empty the recycling or waste bin at your desk.',
    'Update one progress note so others can see where things stand.',
    'Sort your downloads folder by moving one handful of files.',
    'Set a reminder for one thing you tend to forget.',
    'Turn off one notification you do not really need.',
    'Bookmark one page you keep searching for.',
    'Write a two-line summary of a meeting while it is still fresh.',
    'Ask if one recurring meeting could be a little shorter.',
    'Name your single goal for the next hour and write it down.',
    'Ask a colleague how their day is going and really listen.',
    'Share a useful link with someone who might enjoy it.',
    'Say hello to someone you have not spoken with before.',
    'Send a quick thank-you note to someone who helped you lately.',
    'Greet a coworker warmly at the start of your next call.',
    'Ask a teammate what they are looking forward to this week.',
    'Congratulate someone on a small win you noticed.',
    'Invite a colleague for a short chat over tea, coffee, or a call.',
    'Compliment a colleague on something specific they did well.',
    'Learn the name of someone you see often but do not know yet.',
    'Share a helpful tip with a teammate who may need it.',
    'Ask someone to recommend a song, show, or book.',
    'Check in with a colleague who has been quiet lately.',
    'Offer to help with one small thing if someone seems busy.',
    'Greet the next person you meet with a warm hello.',
    'Pass along a kind word you heard about a colleague.',
    'Ask a coworker what made their week easier.',
    'Send a friendly message to someone you used to work with.',
    'Thank someone who keeps shared spaces running smoothly.',
    'Introduce two colleagues who might enjoy meeting each other.',
    'Ask a teammate how you can make a handoff easier for them.',
    'Share a small, harmless joke with someone nearby.',
    'Add a little extra warmth to your next please and thank you.',
    'Ask a colleague what they enjoy doing outside of work.',
    'Listen fully to the next person who speaks to you, without multitasking.',
)

THOUGHTS = (
    'Open the one document you have been avoiding and read just the first paragraph.',
    'A ten-minute start is still a start, and it usually makes the next ten easier.',
    'You do not need the whole plan today, only a sensible first step.',
    'Write the ugly first sentence. It gives you something real to improve later.',
    'Clear one small corner of your desk and notice how much calmer the rest feels.',
    'Pick the smallest task on your list and finish it before you look at the others.',
    'Starting badly on a quiet morning beats waiting for a perfect moment that may not come.',
    'Put the first step in your calendar so it has a place to live.',
    'Big projects are mostly small afternoons stacked together, so aim for one afternoon.',
    'Name the very next action out loud, and let the rest of the list wait its turn.',
    'Some days your pace is slower than you would like, and that pace still counts.',
    'Talk to yourself the way you would talk to a new colleague in their first week.',
    'You are allowed to still be learning something you have done for years.',
    'A flat morning does not decide the afternoon. You can start again after lunch.',
    'Being tired is information, not a failing. Adjust the plan and carry on gently.',
    'Give yourself the same grace you so readily hand to others.',
    'Progress often looks like nothing for a while, then suddenly like a finished page.',
    'It is fine to need a second read before things make sense.',
    'You do not have to feel ready. Doing it nervously is still doing it.',
    "Today's version of your best may be smaller than yesterday's, and that is all right.",
    'Close the tabs you are not using. Your attention will thank you within minutes.',
    'One task, one window, twenty-five minutes. See how far a quiet stretch can go.',
    'Write down the stray thought that pops up, then return to what you were doing.',
    'If you can, silence your phone for an hour and give the work your full attention.',
    'Decide the one thing that would make today a good day, and protect time for it.',
    'Doing things one at a time is usually faster than it feels.',
    'A tidy list of three things beats a scattered list of twenty.',
    'Notice when your mind wanders, and bring it back without any scolding.',
    'Put the hardest task where your energy is best, even if that is not first thing.',
    'Headphones on, kettle filled, door closed. Set the scene and the focus follows.',
    'Step away from the screen for five minutes. You will come back a little clearer.',
    'Eat lunch away from your desk today. The inbox can wait for a sandwich.',
    'A short walk around the building counts as real work for your head.',
    'A minute away from the screen is a fine use of a busy afternoon.',
    'Stretch your shoulders and unclench your jaw. You may have held them up for hours.',
    "Leave on time tonight if you can. Tomorrow's you will be glad of the evening.",
    'Rest is part of the job, because tired people tend to make the same slip twice.',
    'Rest your eyes for a moment and let your shoulders drop.',
    'A proper break makes the second half of the day feel like a fresh start.',
    "Let the evening belong to you. Nothing in your inbox needs you at nine o'clock.",
    'Say thank you to someone today for a small thing they did without being asked.',
    'Most people are doing their best with more on their plate than you can see.',
    'Learn how a colleague takes their tea or coffee. It is a tiny gift to remember.',
    'If someone seems short with you, assume a hard day and not a verdict on you.',
    'Hold the door, share the biscuits, and let someone finish their sentence.',
    'A quick hello and a question about the weekend can be the nicest part of a morning.',
    'When a newcomer asks something obvious, remember that you once asked it too.',
    "Give credit out loud when a teammate's idea made your work better.",
    'Reply to a message with a bit of warmth. It costs nothing and lands softly.',
    'Talk to a colleague who has been quiet in meetings lately and ask how they are.',
    'Finish the thing that is nearly done before you start something new.',
    'Finished and good enough is usually more useful than perfect and not finished.',
    'Close one open loop today and notice the small relief that follows.',
    'The last ten percent is often just a few careful minutes. Give them today.',
    'Send the email that is waiting in your drafts. It is probably fine as it is.',
    'Mark it complete, take a breath, and be pleased that it is done.',
    'A finished small thing is worth more than a half-finished big one.',
    "Before you log off, write tomorrow's first step on a note so you don't have to remember it.",
    'Read it once more, fix what you find, and then send it.',
    'Ending the day with one tidy result makes the evening feel lighter.',
    'Asking a question early usually saves an hour of quiet struggling later.',
    'Most people enjoy being asked for their knowledge. Ask without apologizing.',
    'Saying "I am stuck" is a clear, useful sentence that colleagues can work with.',
    'Ask for what you need in plain words, and give people the chance to say yes.',
    'Two people looking at a problem often solve it faster than one person staring alone.',
    'You are not a burden for needing a hand. You are a teammate.',
    'Bring a specific question and the person you ask can give a specific answer.',
    'If the instructions are unclear, asking for clarity is part of doing the job properly.',
    'Offer help when you can and accept it when you need it. Both get easier with practice.',
    'Someone down the corridor has probably solved this before. Go and find them.',
    'Keep a small note of things you figured out this week. It adds up to more than you think.',
    'Being a beginner at something new is a sign your work is still growing.',
    'Notice how a colleague you admire handles a tricky call, and borrow one thing.',
    'Read one useful page on your break and call that a good day for your mind.',
    'Explaining a task to someone else is a surprisingly good way to learn it yourself.',
    'It is fine to say "I do not know that yet" and then go and find out.',
    'Every unfamiliar system looks confusing until you have used it a handful of times.',
    'Ask someone with more experience how they learned it. The answer is often reassuring.',
    'Skills come from repetition, so repeat the small thing and let it become easy.',
    'A little curiosity about an ordinary task can make it more interesting.',
    'A mistake caught early is just a correction, and most of them are caught early.',
    'Fix it, tell the people who need to know, and then let the sting fade.',
    'Nearly every error at work feels smaller in a week than it does in the moment.',
    'One slip does not erase the years of careful work behind you.',
    'When something goes wrong, look at the process first and the person second.',
    'Everyone around you has sent an email to the wrong person at least once.',
    'Take the one lesson a mistake offers and leave the rest of it behind.',
    'Owning an error plainly usually earns more trust than never having made one.',
    'A clumsy day happens to careful people too, and it passes by evening.',
    "You will not remember most of today's small stumbles by next month.",
    'A quiet day with nothing on fire is a good day, even if no one mentions it.',
    'Notice the small pleasures: a warm mug, a clear inbox, a quiet minute.',
    'Not every day needs a big win. Steady and pleasant is a fine way to work.',
    'Enjoy the meeting that ends five minutes early and spend the time as you like.',
    'An ordinary day done well is something quietly to be proud of.',
    'Good work often looks unremarkable from the outside, and that is all right.',
    'Let a pleasant afternoon be pleasant without waiting for it to be productive.',
    'The small routines of the day, the first coffee and the familiar faces, are worth noticing.',
    'Today you showed up and did your share, and that is plenty.',
    'Take a moment this evening to remember one thing that went well today.',
    'A quiet minute between two tasks is not wasted; it is how the next one starts well.',
)

DONE_LINES = (
    "Good. That one is finished.",
    "Nice. It is good to finish something.",
    "Well done. Take a short break before the next one.",
    "Good. Small finished tasks add up.",
    "That is done. You can be pleased about it.",
    "Good. That one is off your list.",
)

# The Spanish lists follow the English ones item for item.
TIPS_ES = (
    'Bebe un vaso de agua despacio, lejos de la pantalla.',
    'Gira los hombros hacia atrás cinco veces, muy despacio.',
    'Descansa la vista veinte segundos: mira a lo lejos o cierra los ojos.',
    'Estira los brazos hacia arriba, en la silla o de pie, y respira hondo.',
    'Ve hasta la sala o la ventana más lejana que puedas y vuelve.',
    'Revisa tu postura y deja caer los hombros, lejos de las orejas.',
    'Gira el cuello con suavidad de un lado a otro, solo hasta donde sea cómodo.',
    'Abre y cierra las manos diez veces para soltar los dedos.',
    'Fija el documento que más abres para tenerlo a un clic.',
    'Sal a dar un paseo corto, caminando o en silla de ruedas, como te vaya mejor.',
    'Sírvete una bebida caliente o fría y disfrútala lejos de la pantalla.',
    'Fíjate en algo tranquilo: un paisaje, un sonido o una textura.',
    'Escribe el siguiente paso de una tarea que dejaste a medias.',
    'Apoya los pies en el suelo y estira la espalda, en la silla o de pie, durante diez respiraciones.',
    'Silencia un chat de grupo que solo lees por encima.',
    'Relaja la mandíbula y la frente durante un momento.',
    'Muévete durante dos minutos de la forma que te siente bien hoy.',
    'Reserva quince minutos en tu calendario para la tarea que siempre aplazas.',
    'Ajusta un poco la silla, la pantalla o el teclado para tu comodidad.',
    'Si puedes, toma el camino largo hacia tu próxima reunión o llamada.',
    'Guarda una plantilla para un correo que escribes una y otra vez.',
    'Aprende un atajo de teclado del programa que más usas.',
    'Bebe un vaso entero de agua antes de tu próximo café o té.',
    'Sube los hombros hasta las orejas y luego déjalos caer despacio.',
    'Sal un minuto o abre una ventana para tomar aire fresco.',
    'Respira despacio cinco veces y alarga un poco cada exhalación.',
    'Haz una pausa tranquila de un minuto antes de abrir tu próximo mensaje.',
    'Anota una cosa buena que te haya pasado hoy.',
    'Cierra los ojos durante tres respiraciones y nota cómo te sientes.',
    'Nombra tres cosas que percibes ahora mismo, con cualquier sentido.',
    'Escribe una cosa que esperas con ganas esta semana.',
    'Pon un temporizador de dos minutos y descansa sin ninguna pantalla.',
    'Disfruta de algo pequeño cerca de ti, como una planta o tu taza favorita.',
    'Piensa en algo que hiciste bien esta semana y reconócelo.',
    'Escucha una de tus canciones favoritas de principio a fin, sin nada más abierto.',
    'Inhala contando hasta cuatro y exhala contando hasta seis, tres veces.',
    'Respira una vez antes de reaccionar a la próxima pequeña molestia.',
    'Anota algo que te hizo reír hace poco.',
    'Durante un minuto, fíjate en algo agradable: un sonido, un olor o algo que tocas.',
    'Recuerda un lugar que te encanta e imagínalo durante treinta segundos.',
    'Di "por ahora está bien así" sobre una tarea pequeña y sigue adelante.',
    'Escribe una frase sobre algo que agradeces.',
    'Saborea el próximo sorbo de tu bebida y fíjate en el sabor.',
    'Haz una pausa corta entre dos tareas antes de empezar la siguiente.',
    'Busca hoy una cosa que salga mejor de lo que esperabas.',
    'Resume en una palabra cómo quieres que sea la tarde.',
    'Deja descansar la mente sesenta segundos y luego vuelve a tu siguiente tarea.',
    'Siente los pies en el suelo y nota la estabilidad un momento.',
    'Recuerda algo amable que alguien hizo por ti y disfruta del recuerdo.',
    'Anota una idea que quieras retomar más tarde y déjala reposar.',
    'Ordena un rincón pequeño de tu escritorio, solo uno.',
    'Responde a un mensaje que lleva un tiempo esperando.',
    "Apunta la tarea principal de mañana en una nota adhesiva o en tus notas.",
    'Cierra las pestañas del navegador que ya no necesitas.',
    'Da las gracias a alguien de tu equipo por algo que hizo hace poco.',
    'Archiva cinco correos antiguos que ya no necesitas.',
    'Cambia el nombre de un archivo desordenado para encontrarlo fácilmente después.',
    'Quita uno o dos archivos sueltos del escritorio de Windows.',
    'Borra un recordatorio antiguo que ya no sirve.',
    'Pon un título claro a un documento que abres a menudo.',
    'Tacha una tarea pequeña de tu lista de pendientes.',
    'Date de baja de un boletín que nunca lees.',
    'Limpia el teclado o la pantalla con un paño suave.',
    'Deja un bolígrafo, un cuaderno y agua donde los alcances fácilmente.',
    'Escribe una nota breve para tu yo de mañana sobre dónde lo dejaste hoy.',
    'Elige la tarea más importante de esta tarde y hazla primero.',
    'Vacía la papelera o el contenedor de reciclaje de tu mesa.',
    'Actualiza una nota de progreso para que otros vean cómo van las cosas.',
    'Ordena tu carpeta de descargas moviendo unos cuantos archivos.',
    'Pon un recordatorio para algo que sueles olvidar.',
    'Desactiva una notificación que en realidad no necesitas.',
    'Guarda en favoritos una página que buscas una y otra vez.',
    'Escribe un resumen de dos líneas de una reunión mientras la recuerdas bien.',
    'Pregunta si una reunión periódica podría ser un poco más corta.',
    'Define tu único objetivo para la próxima hora y escríbelo.',
    'Pregunta a alguien del equipo cómo va su día y escucha con atención.',
    'Comparte un enlace útil con alguien a quien le pueda gustar.',
    'Saluda a alguien con quien todavía no has hablado.',
    'Envía una nota breve de agradecimiento a alguien que te ayudó hace poco.',
    'Saluda con calidez a los demás al empezar tu próxima llamada.',
    'Pregunta a alguien de tu equipo qué espera con ganas esta semana.',
    'Felicita a alguien por un pequeño logro que hayas notado.',
    'Invita a alguien del trabajo a una charla corta con un té, un café o por llamada.',
    'Elogia algo concreto que alguien del trabajo hizo bien.',
    'Aprende el nombre de alguien a quien ves a menudo pero aún no conoces.',
    'Comparte un consejo útil con alguien del equipo que pueda necesitarlo.',
    'Pide a alguien que te recomiende una canción, una serie o un libro.',
    'Habla con alguien del trabajo que ha hablado poco últimamente y pregúntale cómo está.',
    'Si alguien parece tener mucho trabajo, ofrécete a ayudar con algo pequeño.',
    'Saluda con calidez a la próxima persona que veas.',
    'Si oíste algo amable sobre alguien del trabajo, cuéntaselo.',
    'Pregunta a alguien del trabajo qué le facilitó la semana.',
    'Envía un mensaje amable a alguien con quien trabajaste antes.',
    'Da las gracias a quien mantiene en orden los espacios compartidos.',
    'Presenta a dos personas del trabajo que podrían llevarse bien.',
    'Pregunta a alguien del equipo cómo puedes facilitarle el traspaso de una tarea.',
    'Comparte una broma pequeña e inofensiva con alguien cerca de ti.',
    'Pon un poco más de calidez en tu próximo "por favor" y "gracias".',
    'Pregunta a alguien del trabajo qué le gusta hacer en su tiempo libre.',
    'Escucha con toda tu atención a la próxima persona que te hable, sin hacer otras cosas.',
)

THOUGHTS_ES = (
    'Abre ese documento que llevas tiempo evitando y lee solo el primer párrafo.',
    'Diez minutos de trabajo ya son un comienzo, y suelen hacer más fáciles los diez siguientes.',
    'Hoy no necesitas el plan completo, solo un primer paso razonable.',
    'Escribe una primera frase imperfecta. Te da algo real que mejorar después.',
    'Despeja un rincón de tu mesa y fíjate en cuánto más tranquilo se ve el resto.',
    'Elige la tarea más pequeña de tu lista y termínala antes de mirar las demás.',
    'Un comienzo imperfecto en una mañana tranquila vale más que esperar un momento perfecto que quizá no llegue.',
    'Pon el primer paso en tu calendario para que tenga su propio espacio.',
    'Los grandes proyectos se hacen tarde a tarde. Piensa solo en esta.',
    'Di en voz alta la próxima acción y deja que el resto de la lista espere su turno.',
    'Algunos días vas más despacio de lo que te gustaría, y ese ritmo también cuenta.',
    'Háblate como le hablarías a una persona nueva en su primera semana de trabajo.',
    'Puedes seguir aprendiendo algo que llevas años haciendo.',
    'Una mañana floja no decide la tarde. Puedes empezar de nuevo después de comer.',
    'El cansancio es información, no un fallo. Ajusta el plan y sigue con calma.',
    'Trátate con la misma comprensión que ofreces tan fácilmente a los demás.',
    'A veces el progreso no se nota durante un tiempo, y de pronto tienes una página terminada.',
    'No pasa nada si necesitas leer algo dos veces para entenderlo.',
    'No necesitas sentir que todo está listo. Hacerlo con nervios también es hacerlo.',
    "Lo mejor que puedes dar hoy quizá sea menos que ayer, y no pasa nada.",
    'Cierra las pestañas que no usas. Tu atención lo notará en pocos minutos.',
    'Una tarea, una ventana, veinticinco minutos. Mira hasta dónde llegas con un rato tranquilo.',
    'Anota la idea suelta que te venga a la cabeza y vuelve a lo que estabas haciendo.',
    'Si puedes, silencia el teléfono durante una hora y dale al trabajo toda tu atención.',
    'Decide qué cosa haría de hoy un buen día y reserva tiempo para ella.',
    'Hacer las cosas de una en una suele ser más rápido de lo que parece.',
    'Una lista clara de tres cosas es mejor que una lista desordenada de veinte.',
    'Nota cuándo se distrae tu mente y tráela de vuelta sin regañarte.',
    'Pon la tarea más difícil en el momento en que tienes más energía, aunque no sea a primera hora.',
    'Auriculares puestos, una bebida a mano, puerta cerrada. Prepara el lugar y la concentración llega sola.',
    'Aléjate de la pantalla cinco minutos. Volverás con la mente un poco más clara.',
    'Hoy come lejos de tu mesa. El correo puede esperar mientras comes.',
    'Un paseo corto alrededor del edificio también es trabajo útil para tu cabeza.',
    'Un minuto lejos de la pantalla es un buen uso de una tarde ocupada.',
    'Estira los hombros y relaja la mandíbula. Quizá llevas horas en tensión.',
    "Si puedes, sal a tu hora hoy. Mañana agradecerás haber tenido la tarde libre.",
    'Descansar es parte del trabajo, porque con cansancio es fácil repetir el mismo error.',
    'Descansa la vista un momento y deja caer los hombros.',
    'Un buen descanso hace que la segunda mitad del día se sienta como un nuevo comienzo.',
    "Deja que la noche sea para ti. Nada en tu correo te necesita a las nueve.",
    'Da las gracias hoy a alguien por algo pequeño que hizo sin que se lo pidieran.',
    'La mayoría de la gente hace lo que puede, con más carga de la que tú ves.',
    'Averigua cómo toma el té o el café alguien del trabajo. Recordarlo es un pequeño regalo.',
    'Si alguien te responde de forma seca, piensa que tiene un mal día, no que te está juzgando.',
    'Sujeta la puerta, comparte las galletas y deja que la otra persona termine de hablar.',
    'Un saludo rápido y una pregunta sobre el fin de semana pueden ser lo mejor de la mañana.',
    'Cuando alguien nuevo pregunte algo obvio, recuerda que tú también lo preguntaste una vez.',
    "Reconoce en voz alta cuando la idea de alguien del equipo mejoró tu trabajo.",
    'Responde a un mensaje con un poco de calidez. No cuesta nada y se recibe bien.',
    'Habla con alguien que ha participado poco en las reuniones y pregúntale cómo está.',
    'Termina lo que casi está hecho antes de empezar algo nuevo.',
    'Más vale hecho y bastante bien que perfecto y sin terminar.',
    'Cierra hoy un asunto pendiente y nota el pequeño alivio que llega después.',
    'El último diez por ciento suele ser solo unos minutos de cuidado. Dáselos hoy.',
    'Envía el correo que espera en tus borradores. Probablemente está bien así.',
    'Márcalo como hecho, respira y alégrate de haberlo terminado.',
    'Una cosa pequeña terminada vale más que una grande a medias.',
    "Antes de desconectarte, anota el primer paso de mañana para no tener que recordarlo.",
    'Léelo una vez más, corrige lo que encuentres y envíalo.',
    'Terminar el día con un resultado claro hace que la noche se sienta más ligera.',
    'Preguntar pronto suele ahorrar una hora de esfuerzo en silencio después.',
    'A la mayoría de la gente le gusta compartir lo que sabe. Pregunta sin pedir perdón.',
    '"No sé cómo seguir" es una frase clara y útil con la que tu equipo puede ayudarte.',
    'Pide lo que necesitas con palabras sencillas y da a los demás la oportunidad de decir que sí.',
    'Dos personas mirando un problema suelen resolverlo antes que una sola persona en silencio.',
    'Necesitar ayuda no te convierte en una carga. Eres parte del equipo.',
    'Lleva una pregunta concreta y la persona a quien preguntes podrá darte una respuesta concreta.',
    'Si las instrucciones no están claras, pedir aclaraciones es parte de hacer bien el trabajo.',
    'Ofrece ayuda cuando puedas y acéptala cuando la necesites. Ambas cosas se aprenden con práctica.',
    'Seguramente alguien cerca de ti ya ha resuelto esto antes. Ve a buscar a esa persona.',
    'Anota las cosas que aprendiste a resolver esta semana. Suman más de lo que crees.',
    'Ser principiante en algo nuevo es señal de que tu trabajo sigue creciendo.',
    'Observa cómo alguien a quien admiras maneja una llamada difícil y quédate con una idea.',
    'Lee una página útil en tu descanso y da el día por bien aprovechado.',
    'Explicar una tarea a otra persona es una forma sorprendentemente buena de aprenderla.',
    'Está bien decir "todavía no lo sé" y luego ir a averiguarlo.',
    'Todo sistema nuevo parece confuso hasta que lo has usado unas cuantas veces.',
    'Pregunta a alguien con más experiencia cómo lo aprendió. La respuesta suele tranquilizar.',
    'Las habilidades vienen de la repetición. Repite lo pequeño y deja que se vuelva fácil.',
    'Un poco de curiosidad puede hacer más interesante una tarea normal.',
    'Un error detectado a tiempo es solo una corrección, y la mayoría se detectan a tiempo.',
    'Corrígelo, avisa a quien necesite saberlo y deja que la molestia pase.',
    'Casi cualquier error en el trabajo parece más pequeño una semana después.',
    'Un fallo no borra los años de trabajo cuidadoso que llevas detrás.',
    'Cuando algo sale mal, mira primero el proceso y después a la persona.',
    'Todas las personas a tu alrededor han enviado alguna vez un correo a quien no era.',
    'Quédate con la lección que deja un error y deja atrás el resto.',
    'Reconocer un error con sencillez suele dar más confianza que no haberlo cometido nunca.',
    'Hasta la gente cuidadosa tiene días torpes, y se acaban antes de la noche.',
    "El próximo mes no recordarás la mayoría de los pequeños tropiezos de hoy.",
    'Un día tranquilo y sin urgencias es un buen día, aunque nadie lo diga.',
    'Fíjate en los pequeños placeres: una taza caliente, la bandeja de entrada vacía, un minuto de calma.',
    'No todos los días necesitan un gran logro. Trabajar con calma y a gusto está bien.',
    'Disfruta de la reunión que termina cinco minutos antes y usa ese tiempo como quieras.',
    'Un día normal bien hecho es motivo de un orgullo tranquilo.',
    'El buen trabajo a menudo no se nota desde fuera, y no pasa nada.',
    'Deja que una tarde agradable sea agradable, sin esperar que sea productiva.',
    'Las pequeñas rutinas del día, como el primer café y las caras conocidas, merecen tu atención.',
    'Hoy estuviste presente e hiciste tu parte, y eso es suficiente.',
    'Esta noche, tómate un momento para recordar algo que salió bien hoy.',
    'Un minuto tranquilo entre dos tareas no es tiempo perdido; ayuda a empezar bien la siguiente.',
)

DONE_LINES_ES = (
    "Bien. Esa ya está terminada.",
    "Muy bien. Da gusto terminar algo.",
    "Bien hecho. Descansa un poco antes de la siguiente.",
    "Bien. Las tareas pequeñas terminadas suman.",
    "Ya está hecho. Alégrate un momento.",
    "Bien. Una tarea menos en tu lista.",
)

HELP = """hello-world prints a greeting, a thought, and a small thing to try.

At the last prompt, type plan for today's plan, done when you finish
it, or menu (or m) for options. Enter closes, and q, x and close
close it from any question. At a plan prompt, same brings back an
unfinished earlier plan. After done it lists your last 3 finished
plans. Menu option 1 shows all of them, option 7 forgets one, and
option 8 hides the thought and tip. At the menu, Enter goes back.
You can also run hello.cmd with one of these:
  --plain         Print only the greeting
  --stats         Show what is saved on this computer
  --reset         Delete everything saved (asks first)
  --remind on     Open once a day when you sign in (off to stop)
  --streak off    Hide the days-in-a-row message (on to show it)
  --version       Show the version
  --check-content FILE
                  Check an organization content file
  --help          Show this text

Exit codes: 0 when it worked, 1 when a command failed or the screen
could not be written, 2 for an unknown option.

Saved notes stay on this computer, in your user folder. Nothing is sent
anywhere. IT staff who can read this computer's files could read them."""

MENU_HELP = """Words you can type at the last prompt:
  done  marks today's plan finished, then asks for the next one
  plan  sets or changes today's plan
  menu  opens these options
  q     closes the window, and so does Enter
At a plan prompt, same brings back your earlier unfinished plan.
When it asks "Did you do it?", n means not yet, and you can keep the
plan for today. q closes from any question.
In this menu, 1 shows what is saved, 7 forgets one finished plan,
and 8 hides the thought and tip.
Type m to hear the options again. Nothing is sent anywhere."""

HELP_ES = """hello-world muestra un saludo, una idea y algo sencillo que probar.

En la última pregunta, escribe plan para el plan de hoy, hecho cuando
lo termines, o menú (o m) para ver las opciones. Enter cierra; q, salir
o x cierran desde cualquier pregunta. En la pregunta del plan,
repetir recupera un plan anterior sin terminar. Después de hecho,
muestra tus 3 últimos planes terminados. La opción 1 del menú los
muestra todos, la 7 olvida uno y la 8 oculta la idea y la sugerencia.
En el menú, Enter vuelve atrás.
También puedes ejecutar hello.cmd con una de estas opciones:
  --plain         Muestra solo el saludo, en inglés
  --stats         Muestra lo que hay guardado en este equipo
  --reset         Borra todo lo guardado (pregunta antes)
  --remind on     Se abre al iniciar sesión cada día (off: lo quita)
  --streak off    Oculta el mensaje de días seguidos (on: lo muestra)
  --version       Muestra la versión
  --check-content FILE
                  Comprueba un archivo de contenido de la organización
  --help          Muestra este texto

Códigos de salida: 0 si funcionó, 1 si un comando falló o no se pudo
escribir en la pantalla, 2 para una opción desconocida.

Las notas guardadas se quedan en este equipo, en tu carpeta de
usuario. No se envía nada a ningún sitio. El personal de TI que puede
leer los archivos de este equipo podría leerlas."""

MENU_HELP_ES = """Palabras que puedes escribir en la última pregunta:
  hecho  marca como terminado el plan de hoy y pide el siguiente
  plan   escribe o cambia el plan de hoy
  menú   abre estas opciones
  q      cierra la ventana, igual que Enter
En la pregunta del plan, repetir recupera tu plan anterior sin terminar.
Cuando pregunta "¿Lo hiciste?", n significa todavía no, y puedes
mantener el plan para hoy. q cierra desde cualquier pregunta.
En este menú, 1 muestra lo guardado, 7 olvida un plan terminado
y 8 oculta la idea y la sugerencia.
Escribe m para ver de nuevo las opciones. No se envía nada a ningún
sitio."""


# A thought that shares one of these with the day's tip moves on by one, so
# one screen never has two lines about the same body part.
TOPICS = ("shoulder", "jaw", "neck", "eye", "water", "breath", "posture",
          "stretch", "wrist", "hombro", "mandíbula", "cuello", "ojo", "agua",
          "respir", "postura", "estir", "muñeca")


def todays_pair(d):
    """The day's thought and tip. Everyone gets the same pair on the same day."""
    thoughts, tips = content_lists()
    tip = tips[d.toordinal() % len(tips)]
    i = (d.toordinal() + 37) % len(thoughts)
    # At most one pass, so lists where every thought shares a topic with the
    # tip can't loop forever.
    for _ in range(len(thoughts)):
        if not any(w in tip.lower() and w in thoughts[i].lower() for w in TOPICS):
            break
        i = (i + 1) % len(thoughts)
    return thoughts[i], tip


# An organization can ship its own thoughts and tips in content.json next to
# hello.py, inside the signed package. They replace the built-in lists whole.
# The rules keep it a list of short, timeless lines, not a way to send
# announcements: no links, no addresses, no dates, nothing long.
CONTENT = None
MIN_CONTENT, MAX_CONTENT = 7, 200
CONTENT_LENGTH = (10, 120)


def content_problems(data):
    """What is wrong with organization content, as plain sentences."""
    if not isinstance(data, dict) or set(data) != {"thoughts", "tips"}:
        return ['The file must hold an object with exactly two lists: '
                '"thoughts" and "tips".']
    problems = []
    low_months = [m.lower() for m in MONTHS if m != "May"] + list(MONTHS_ES)
    for key in ("thoughts", "tips"):
        items = data[key]
        if not isinstance(items, list) or not MIN_CONTENT <= len(items) <= MAX_CONTENT:
            problems.append(f'"{key}" must be a list of {MIN_CONTENT} to '
                            f"{MAX_CONTENT} lines.")
            continue
        for n, item in enumerate(items, 1):
            where = f"{key} line {n}"
            if not isinstance(item, str):
                problems.append(f"{where} is not text.")
                continue
            text, low = tidy(item), tidy(item).lower()
            if text != item.strip():
                problems.append(f"{where} has control characters or extra spaces.")
            if not CONTENT_LENGTH[0] <= len(text) <= CONTENT_LENGTH[1]:
                problems.append(f"{where} must be {CONTENT_LENGTH[0]} to "
                                f"{CONTENT_LENGTH[1]} characters long.")
            if any(mark in low for mark in ("http", "www.", "://", "@")):
                problems.append(f"{where} has a link or an address.")
            if any(m in low.split() or m + "," in low for m in low_months) or any(
                    c.isdigit() and next_c in "/-." and after.isdigit()
                    for c, next_c, after in zip(text, text[1:], text[2:], strict=False)):
                problems.append(f"{where} has a date.")
    return problems


def content_lists():
    """The organization's thoughts and tips if it shipped valid ones, else
    the built-in lists. A file that breaks the rules is ignored whole."""
    path = CONTENT or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "content.json")
    try:
        with open(path, encoding="utf-8-sig") as f:
            data = json.loads(f.read(200_000))
    except (OSError, ValueError, RecursionError):
        return built_in_lists()
    if content_problems(data):
        return built_in_lists()
    return (tuple(tidy(x) for x in data["thoughts"]),
            tuple(tidy(x) for x in data["tips"]))


def built_in_lists():
    return (THOUGHTS_ES, TIPS_ES) if spanish() else (THOUGHTS, TIPS)


def help_text():
    here = os.path.dirname(os.path.abspath(__file__))
    return tr(HELP) + "\n\n" + tr("hello.cmd is in this folder:") + "\n  " + here

VERSION = "1.25.0"
MAX_VISITS = 400
KEEP_VISIT_DAYS = 60
MAX_FILE = 1_000_000
# Spanish words count in either language, so nobody has to guess which
# language the program thinks it speaks.
YES = ("y", "yes", "yep", "ya", "yeah", "done", "s", "si", "sí", "hecho",
       "listo")
# The sign-in offer starts something, so a stray "done" must not count.
STRICT_YES = ("y", "yes", "yep", "ya", "yeah", "s", "si", "sí")
MAX_OFFER_SKIPS = 1
NO = ("n", "no", "nope", "not yet", "todavía no", "aún no", "aun no")
DONE_WORDS = ("done", "hecho")
SAME_WORDS = ("same", "repetir")

# The tests set these after importing the module, to run against a fixed date,
# a temporary folder, and typed input. Nothing outside the program sets them.
TODAY = None
HOME = None
STARTUP_DIR = None
FORCE_INTERACTIVE = False
# A dict of policy values, so tests never read the real registry.
POLICY = None
# "en" or "es" in tests; None follows the Windows display language.
LANGUAGE = None
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE = "hello-world"
POLICY_KEY = r"SOFTWARE\Policies\hello-world"


class Quit(Exception):
    """The person typed q at a question, so the window closes."""


QUIT_WORDS = ("q", "quit", "exit", "x", "close", "salir", "cerrar")


class OutputClosed(Exception):
    """Writing to stdout failed, so nothing more can be shown."""


def today():
    return datetime.date.fromisoformat(TODAY) if TODAY else datetime.date.today()


def long_date(d):
    if spanish():
        return f"{DAYS_ES[d.weekday()]}, {d.day} de {MONTHS_ES[d.month - 1]} de {d.year}"
    return f"{DAYS[d.weekday()]}, {d.day} {MONTHS[d.month - 1]} {d.year}"


def data_dir():
    if HOME:
        return HOME
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "hello-world")
    return os.path.join(os.path.expanduser("~"), ".local", "share",
                        "hello-world")


def data_file():
    return os.path.join(data_dir(), "notes.json")


def policy(name):
    """True when Group Policy sets this value to 1 for the PC or the user.

    Read from HKLM, then HKCU, under SOFTWARE\\Policies\\hello-world, where
    only administrators and Group Policy can write.
    """
    if POLICY is not None:
        return bool(POLICY.get(name))
    if os.name != "nt":
        return False
    import winreg
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, POLICY_KEY) as key:
                value, kind = winreg.QueryValueEx(key, name)
            if kind == winreg.REG_DWORD and value == 1:
                return True
        except OSError:
            pass
    return False


def plans_off():
    """Group Policy can turn plans off, for records or works-council rules."""
    return policy("DisablePlans")


def launcher_place():
    """Where the sign-in launcher lives: ("file", path) for a test folder,
    ("run", key) for the HKCU Run value on Windows, or (None, None)."""
    # The tests set "" for no launcher, so they never touch the real one.
    if STARTUP_DIR is not None:
        if not STARTUP_DIR:
            return None, None
        return "file", os.path.join(STARTUP_DIR, "hello-world-daily.cmd")
    if os.name == "nt":
        return "run", RUN_KEY
    return None, None


def legacy_launcher():
    """The Startup .cmd that versions before 1.23 wrote, on Windows only."""
    if STARTUP_DIR is not None or os.name != "nt" or not os.environ.get("APPDATA"):
        return None
    return os.path.join(os.environ["APPDATA"], "Microsoft", "Windows",
                        "Start Menu", "Programs", "Startup",
                        "hello-world-daily.cmd")


def launcher_on():
    kind, where = launcher_place()
    if kind == "file":
        return os.path.exists(where)
    if kind == "run":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, where) as key:
                winreg.QueryValueEx(key, RUN_VALUE)
            return True
        except OSError:
            return False
    return False


def new_state():
    return {"visits": [], "intent": None, "streak": True}


MAX_PLAN = 120
SAVED_PLAN = "Saved. Type done when you finish it, or it asks next time you open this."
MAX_FINISHED = 7
SHOWN_AFTER_DONE = 3


def spanish():
    """Spanish when Windows is set to show Spanish, unless policy says English."""
    if policy("ForceEnglish"):
        return False
    if LANGUAGE is not None:
        return LANGUAGE == "es"
    if os.name != "nt":
        return False
    try:
        import ctypes
        # The low 10 bits are the primary language; 0x0A is Spanish.
        return ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x0A
    except (AttributeError, OSError):
        return False


def tr(text):
    """The text in the person's language. The English text is the key."""
    return ES.get(text, text) if spanish() else text


ES = {
    HELP: HELP_ES,
    MENU_HELP: MENU_HELP_ES,
    SAVED_PLAN: "Guardado. Escribe hecho al terminarlo, o te lo preguntará "
                "en la próxima visita.",
    GREETING: "¡Hola, mundo!",
    "hello.cmd is in this folder:": "hello.cmd está en esta carpeta:",
    "Shortened to {n} characters.": "Se acortó a {n} caracteres.",
    "Your saved file was damaged, so hello-world set it aside as a backup "
    "copy and started fresh. Your earlier days and plan could not be read. "
    "Menu option 4 deletes the backup.":
        "Tu archivo guardado estaba dañado, así que hello-world lo apartó como "
        "copia de seguridad y empezó de nuevo. No se pudieron leer tus días ni "
        "tu plan anteriores. La opción 4 del menú borra la copia.",
    "Backup copy: ": "Copia de seguridad: ",
    "In the folder: ": "En la carpeta: ",
    'That was not one of the choices: "{shown}".':
        'No es una de las opciones: "{shown}".',
    "The sign-in reminder works on Windows only.":
        "El aviso al iniciar sesión solo funciona en Windows.",
    "Your organization has turned off opening at sign-in.":
        "Tu organización ha desactivado la apertura al iniciar sesión.",
    "The reminder cannot be set up from this folder.":
        "El aviso no se puede configurar desde esta carpeta.",
    "Could not set up the reminder.": "No se pudo configurar el aviso.",
    "Done. hello-world will open once a day when you sign in.":
        "Listo. hello-world se abrirá una vez al día al iniciar sesión.",
    "To stop it, choose option 2 in the menu.":
        "Para desactivarlo, elige la opción 2 del menú.",
    "Could not turn off the sign-in reminder.":
        "No se pudo desactivar el aviso al iniciar sesión.",
    "Done. The sign-in reminder is off.":
        "Listo. El aviso al iniciar sesión está desactivado.",
    "Saved on this computer in:": "Guardado en este equipo, en:",
    "Saved in your own user folder on this computer.":
        "Guardado en tu propia carpeta de usuario de este equipo.",
    "Days you opened it in the last {days} days: {n} (last 7 days: {recent})":
        "Días que lo abriste en los últimos {days} días: {n} "
        "(últimos 7 días: {recent})",
    "Times you marked a plan done: {n}":
        "Veces que marcaste un plan como hecho: {n}",
    "Your current plan: ": "Tu plan actual: ",
    "Earlier plan (for same): ": "Plan anterior (para repetir): ",
    "Days-in-a-row message: shown.": "Mensaje de días seguidos: visible.",
    "Days-in-a-row message: hidden.": "Mensaje de días seguidos: oculto.",
    "Opens by itself at sign-in: turned off by your organization.":
        "Se abre solo al iniciar sesión: desactivado por tu organización.",
    "Opens by itself at sign-in: on.": "Se abre solo al iniciar sesión: sí.",
    "Opens by itself at sign-in: off.": "Se abre solo al iniciar sesión: no.",
    "It never leaves this computer. Others who can read this computer's "
    "files, such as IT staff, could read it.":
        "Nunca sale de este equipo. Quien pueda leer los archivos de este "
        "equipo, como el personal de TI, podría leerlo.",
    "After tidying, the file holds only this:":
        "Después de ordenarlo, el archivo solo contiene esto:",
    "Delete all saved notes, dates and plans on this computer? "
    "(y or n, Enter to cancel) > ":
        "¿Borrar todas las notas, fechas y planes guardados en este equipo? "
        "(s o n, Enter para cancelar) > ",
    "Nothing was deleted.": "No se borró nada.",
    "Could not delete everything.": "No se pudo borrar todo.",
    "Delete these yourself:": "Borra tú estos archivos:",
    "Could not list the folder, so backup copies may remain:":
        "No se pudo leer la carpeta, así que pueden quedar copias:",
    "Done. Everything saved was deleted.": "Listo. Se borró todo lo guardado.",
    "Another open hello-world window cannot put it back.":
        "Otra ventana abierta de hello-world no puede recuperarlo.",
    "Close any other open hello-world window, or it may save its notes "
    "again.":
        "Cierra cualquier otra ventana abierta de hello-world, o podría "
        "volver a guardar sus notas.",
    "Everything saved was deleted in another window, so this was not saved.":
        "Todo lo guardado se borró en otra ventana, así que esto no se "
        "guardó.",
    "The other open window had also finished a plan.":
        "La otra ventana abierta también había terminado un plan.",
    "The other open window changed the plan, so its plan is kept.":
        "La otra ventana cambió el plan, así que se mantiene el suyo.",
    "Type plan at the last prompt to set one.":
        "Escribe plan en la última pregunta para crear uno.",
    "That looks like a command, not a plan, so nothing was saved.":
        "Eso parece un comando, no un plan, así que no se guardó nada.",
    "Type your plan, or press Enter to go back.":
        "Escribe tu plan o pulsa Enter para volver.",
    "Finished lately:": "Terminados hace poco:",
    "Your plan today: ": "Tu plan de hoy: ",
    "Your plan from {date}: ": "Tu plan del {date}: ",
    "Earlier plan: ": "Plan anterior: ",
    "Type the next plan, or Enter to close > ":
        "Escribe el siguiente plan, o Enter para cerrar > ",
    "Type the next plan, same to reuse the earlier plan, or Enter to close > ":
        "Escribe el siguiente plan, repetir para usar el plan anterior, o "
        "Enter para cerrar > ",
    "Type today's plan, or Enter to keep it > ":
        "Escribe el plan de hoy, o Enter para mantenerlo > ",
    "Type today's plan, same to reuse the earlier plan, or Enter to keep it > ":
        "Escribe el plan de hoy, repetir para usar el plan anterior, o Enter "
        "para mantenerlo > ",
    "Type today's plan, or Enter to go back > ":
        "Escribe el plan de hoy, o Enter para volver > ",
    "Type today's plan, same to reuse the earlier plan, or Enter to go back > ":
        "Escribe el plan de hoy, repetir para usar el plan anterior, o Enter "
        "para volver > ",
    "Closing.": "Cerrando.",
    "There is no earlier plan to reuse yet. Nothing changed.":
        "Todavía no hay un plan anterior para repetir. No cambió nada.",
    "Nothing changed.": "No cambió nada.",
    "Could not save that on this computer. Your plan is unchanged.":
        "No se pudo guardar en este equipo. Tu plan no ha cambiado.",
    "No finished plans are saved.": "No hay planes terminados guardados.",
    "Type the number to forget (1 to {n}), or Enter to keep them all > ":
        "Escribe el número que quieres olvidar (del 1 al {n}), o Enter para "
        "mantenerlos todos > ",
    'There is no number "{typed}" on the list. Type a number from 1 to {n}, '
    "or press Enter to keep them all.":
        'No hay ningún número "{typed}" en la lista. Escribe un número del 1 '
        "al {n}, o pulsa Enter para mantenerlos todos.",
    "Also forget it as the earlier plan for same? "
    "(y or n, Enter to keep it for same) > ":
        "¿Olvidarlo también como plan anterior para repetir? "
        "(s o n, Enter para mantenerlo) > ",
    "Type y or n, or press Enter to keep it for same.":
        "Escribe s o n, o pulsa Enter para mantenerlo para repetir.",
    "That plan was already forgotten. Nothing changed.":
        "Ese plan ya estaba olvidado. No cambió nada.",
    "Forgotten: ": "Olvidado: ",
    "Same still has it.": "Aún puedes recuperarlo con repetir.",
    "Could not save that on this computer. Nothing changed.":
        "No se pudo guardar en este equipo. No cambió nada.",
    "Options": "Opciones",
    "Show what is saved on this computer": "Mostrar lo guardado en este equipo",
    "Open once a day at sign-in (turned off by your organization)":
        "Abrir al iniciar sesión (desactivado por tu organización)",
    "Turn off: open once a day at sign-in (now on)":
        "Desactivar: abrir al iniciar sesión (ahora activado)",
    "Turn on: open once a day at sign-in (now off)":
        "Activar: abrir al iniciar sesión (ahora desactivado)",
    "Days-in-a-row message (hidden by your organization)":
        "Mensaje de días seguidos (oculto por tu organización)",
    "Hide the days-in-a-row message (now shown)":
        "Ocultar el mensaje de días seguidos (ahora visible)",
    "Show the days-in-a-row message (now hidden)":
        "Mostrar el mensaje de días seguidos (ahora oculto)",
    "Delete everything saved": "Borrar todo lo guardado",
    "Help": "Ayuda",
    "Set today's plan (turned off by your organization)":
        "Escribir el plan de hoy (desactivado por tu organización)",
    "Forget a finished plan (turned off by your organization)":
        "Olvidar un plan terminado (desactivado por tu organización)",
    "Set or change today's plan": "Escribir o cambiar el plan de hoy",
    "Forget one finished plan": "Olvidar un plan terminado",
    "Thought and tip (hidden by your organization)":
        "Idea y sugerencia (ocultas por tu organización)",
    "Hide the thought and tip (now shown)":
        "Ocultar la idea y la sugerencia (ahora visibles)",
    "Show the thought and tip (now hidden)":
        "Mostrar la idea y la sugerencia (ahora ocultas)",
    "Back to the last prompt": "Volver a la última pregunta",
    "Choose 1 to 8, or Enter to go back > ":
        "Elige del 1 al 8, o Enter para volver > ",
    "Choose 1 to 8, m to list the options, or Enter to go back > ":
        "Elige del 1 al 8, m para ver las opciones, o Enter para volver > ",
    "The saved file could not be read just now, so this may be out of date.":
        "El archivo guardado no se pudo leer ahora, así que esto puede no "
        "estar al día.",
    "Type full to see the whole file, or Enter to go on > ":
        "Escribe todo para ver el archivo entero, o Enter para seguir > ",
    "Could not save that choice on this computer.":
        "No se pudo guardar esa elección en este equipo.",
    "Your organization has hidden the days-in-a-row message.":
        "Tu organización ha ocultado el mensaje de días seguidos.",
    "Done. The days-in-a-row message is on.":
        "Listo. El mensaje de días seguidos está activado.",
    "Done. The days-in-a-row message is off.":
        "Listo. El mensaje de días seguidos está desactivado.",
    "Plans are turned off by your organization.":
        "Tu organización ha desactivado los planes.",
    "Your organization has hidden the thought and tip.":
        "Tu organización ha ocultado la idea y la sugerencia.",
    "Done. The thought and tip are on.":
        "Listo. La idea y la sugerencia están activadas.",
    "Done. The thought and tip are off.":
        "Listo. La idea y la sugerencia están desactivadas.",
    "Type 1 to 8, or press Enter to go back.":
        "Escribe del 1 al 8, o pulsa Enter para volver.",
    "Want it to open once a day when you sign in? "
    "(y or n, Enter for not now) > ":
        "¿Quieres que se abra una vez al día al iniciar sesión? "
        "(s o n, Enter para más tarde) > ",
    "Want it to open once a day when you sign in so it can ask about your "
    "plan? (y or n, Enter for not now) > ":
        "¿Quieres que se abra una vez al día al iniciar sesión para "
        "preguntarte por tu plan? (s o n, Enter para más tarde) > ",
    "Type y or n, or press Enter for not now.":
        "Escribe s o n, o pulsa Enter para más tarde.",
    "That was not understood. It will ask again on a later visit.":
        "No se entendió. Volverá a preguntar en otra visita.",
    "It will ask again on a later visit. Menu option 2 also turns it on.":
        "Volverá a preguntar en otra visita. La opción 2 del menú también "
        "lo activa.",
    "No problem. Menu option 2 turns it on later.":
        "Sin problema. La opción 2 del menú lo activa más adelante.",
    "Okay. It won't ask again. Menu option 2 turns it on.":
        "De acuerdo. No volverá a preguntar. La opción 2 del menú lo activa.",
    "Okay. It will ask again on a later visit. Type n to stop it.":
        "De acuerdo. Volverá a preguntar en otra visita. Escribe n para "
        "que no pregunte más.",
    "When did you finish it?": "¿Cuándo lo terminaste?",
    "Today": "Hoy",
    "Type a number from 1 to {n}, or Enter for 1 > ":
        "Escribe un número del 1 al {n}, o Enter para 1 > ",
    "Type a number from 1 to {n}, or press Enter.":
        "Escribe un número del 1 al {n}, o pulsa Enter.",
    "That looks like more than one thing. Finishing the first part still "
    "counts.":
        "Eso parece más de una cosa. Terminar la primera parte ya cuenta.",
    "There is no plan to mark as done. Type plan to set one.":
        "No hay ningún plan para marcar como hecho. Escribe plan para crear "
        "uno.",
    "Could not save that on this computer. The plan is still open.":
        "No se pudo guardar en este equipo. El plan sigue pendiente.",
    "Your plan from over two weeks ago was put away. Type same at the plan "
    "prompt to bring it back.":
        "Tu plan de hace más de dos semanas se guardó aparte. Escribe "
        "repetir en la pregunta del plan para recuperarlo.",
    "Press Enter at each question to skip it, and once more to close. "
    "That's it.":
        "Pulsa Enter en cada pregunta para saltarla, y una vez más para "
        "cerrar. Eso es todo.",
    "Welcome.": "Te damos la bienvenida.",
    "Each day you get one thought and one small thing to try, the same for "
    "everyone.":
        "Cada día verás una idea y algo sencillo que probar, igual para "
        "todo el mundo.",
    "If you type a plan, it asks next time how it went. Notes stay in your "
    "user folder and it sends nothing anywhere, but IT staff could read "
    "them, so skip private details.":
        "Si escribes un plan, la próxima vez te pregunta cómo fue. Las notas "
        "se quedan en tu carpeta de usuario y no se envía nada a ningún "
        "sitio, pero el personal de TI podría leerlas, así que no escribas "
        "datos privados.",
    "Type menu at the last prompt for the options.":
        "Escribe menú en la última pregunta para ver las opciones.",
    "Welcome back. Glad you are here.": "Qué bien verte de nuevo.",
    "You have opened this {row} times in a row. Nice to see you.":
        "Lo has abierto {row} días seguidos. Qué bien verte.",
    "Last time you planned: ": "Tu último plan: ",
    "Did you do it? (y for yes, n for not yet, Enter to skip) > ":
        "¿Lo hiciste? (s para sí, n para todavía no, Enter para saltar) > ",
    "Type y or n, or press Enter to skip.":
        "Escribe s o n, o pulsa Enter para saltar.",
    "Could not save that on this computer. Your answer was not counted.":
        "No se pudo guardar en este equipo. Tu respuesta no se contó.",
    "That is fine. Keep it for today? (y or n, Enter to keep it) > ":
        "No pasa nada. ¿Lo mantienes para hoy? (s o n, Enter para "
        "mantenerlo) > ",
    "Type y to keep it, n to clear it, or press Enter to keep it.":
        "Escribe s para mantenerlo, n para quitarlo, o pulsa Enter para "
        "mantenerlo.",
    "Cleared. Type same at a plan prompt if you want it back.":
        "Quitado. Escribe repetir en la pregunta del plan para recuperarlo.",
    "Kept for today.": "Se mantiene para hoy.",
    "That was not understood. Your plan is left as it was.":
        "No se entendió. Tu plan se queda como estaba.",
    "Your plan is still open.": "Tu plan sigue pendiente.",
    "Thought for today:": "Idea para hoy:",
    "Try this today:": "Prueba esto hoy:",
    "Your plan for today: ": "Tu plan para hoy: ",
    "Still open since {date}:": "Pendiente desde el {date}:",
    "(Enter to skip)": "(Enter para saltar)",
    "(A plan typed here replaces the old one. Enter to skip)":
        "(Un plan escrito aquí sustituye al anterior. Enter para saltar)",
    "(Type same to reuse it, or Enter to skip)":
        "(Escribe repetir para usarlo, o Enter para saltar)",
    "What is one thing you want to get done today?":
        "¿Qué cosa quieres terminar hoy?",
    "The menu comes at the last prompt, after this question. Type menu "
    "there.":
        "El menú está en la última pregunta, después de esta. Escribe menú "
        "allí.",
    "There is no earlier plan to reuse yet. Nothing was saved.":
        "Todavía no hay un plan anterior para repetir. No se guardó nada.",
    "Your notes could not be saved on this computer. This screen still "
    "works.":
        "Tus notas no se pudieron guardar en este equipo. Esta pantalla "
        "sigue funcionando.",
    "Type menu or q, or Enter to close > ":
        "Escribe menú o q, o Enter para cerrar > ",
    "Type done, plan, menu or q, or Enter to close > ":
        "Escribe hecho, plan, menú o q, o Enter para cerrar > ",
    "Type plan, menu or q, or Enter to close > ":
        "Escribe plan, menú o q, o Enter para cerrar > ",
    "Type done, plan, menu or q, or press Enter to close.":
        "Escribe hecho, plan, menú o q, o pulsa Enter para cerrar.",
    "Type plan, menu or q, or press Enter to close.":
        "Escribe plan, menú o q, o pulsa Enter para cerrar.",
    "The saved file can't be read right now, or it is damaged.":
        "El archivo guardado no se puede leer ahora, o está dañado.",
    "Nothing was changed. Saved in: ": "No se cambió nada. Guardado en: ",
    "Deleting saved notes needs a person at the keyboard.":
        "Para borrar las notas guardadas hace falta una persona al teclado.",
    "{option} needs on or off. Here are the options.":
        "{option} necesita on u off. Estas son las opciones.",
    "Unknown option: {option}. Here are the options.":
        "Opción desconocida: {option}. Estas son las opciones.",
}


# Controls, format marks such as bidi overrides, private-use and surrogate
# code points go. Unassigned ones (Cn) stay, so emoji newer than the bundled
# Python's Unicode tables survive.
DROPPED = {"Cc", "Cf", "Co", "Cs", "Zl", "Zp"}
MAX_MARKS = 4


def tidy(text):
    """One printable line: tabs and odd spaces become spaces, controls go."""
    text = "".join(" " if c.isspace() else c for c in text)
    kept, marks = [], 0
    for c in text:
        kind = unicodedata.category(c)
        # ZWNJ and ZWJ are format marks, but Persian, Indic scripts and emoji
        # sequences need them.
        if kind in DROPPED and c not in "\u200c\u200d":
            continue
        # A pile of combining marks on one letter draws over the lines above.
        marks = marks + 1 if kind in ("Mn", "Me") else 0
        if marks > MAX_MARKS:
            continue
        kept.append(c)
    text = " ".join("".join(kept).split())
    # Nothing but joiners would show as an empty plan.
    return text if text.strip("\u200c\u200d ") else ""


def clean(text):
    return tidy(tidy(text)[:MAX_PLAN].rstrip(" \u200c\u200d"))


def typed_plan(raw):
    """Clean a typed plan, and say so when it is cut."""
    if len(tidy(raw)) > MAX_PLAN:
        say(tr("Shortened to {n} characters.").format(n=MAX_PLAN))
    return clean(raw)


def day(value):
    """The date as a canonical string, or ValueError."""
    if not isinstance(value, str):
        raise ValueError("not a date")
    return datetime.date.fromisoformat(value).isoformat()


def backup_name(path):
    """notes.json.bak, or a numbered name when an earlier backup exists."""
    name, n = path + ".bak", 1
    while os.path.exists(name):
        n += 1
        name = f"{path}.bak{n}"
    return name


def load(repair=True):
    """Read the saved file. Returns (state, can_save).

    A missing file or a damaged one gives a fresh start; a damaged file is kept
    as notes.json.bak. A file that exists but can't be read right now is left
    alone, so a locked file is never overwritten with an empty one. With
    repair=False a damaged file is left where it is and can_save is False.
    """
    state = new_state()
    path = data_file()
    try:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read(MAX_FILE + 1)
    except FileNotFoundError:
        return state, True
    except OSError:
        return state, False
    except ValueError:
        text = None
    try:
        if text is None or len(text) > MAX_FILE:
            raise ValueError("too big or not text")
        raw = json.loads(text)
        if not isinstance(raw, dict):
            raise ValueError("not an object")
    except (ValueError, RecursionError, MemoryError):
        if not repair:
            return state, False
        backup = backup_name(path)
        try:
            os.replace(path, backup)
        except OSError:
            return state, False
        para(tr("Your saved file was damaged, so hello-world set it aside as a "
                "backup copy and started fresh. Your earlier days and plan "
                "could not be read. Menu option 4 deletes the backup."))
        say(tr("Backup copy: ") + os.path.basename(backup))
        say(tr("In the folder: ") + data_dir())
        say()
        return state, True
    if raw.get("streak") is False:
        state["streak"] = False
    if raw.get("tips") is False:
        state["tips"] = False
    if raw.get("offered") is True:
        state["offered"] = True
    # Changes only when everything is deleted. commit() compares it, so a
    # window opened before a delete can't write its old notes back.
    epoch = raw.get("epoch")
    state["epoch"] = (epoch if isinstance(epoch, str) and len(epoch) <= 64
                      and all(c in "0123456789abcdef" for c in epoch) else "")
    skips = raw.get("offer_skips")
    if isinstance(skips, int) and not isinstance(skips, bool) and skips > 0:
        state["offer_skips"] = min(skips, MAX_OFFER_SKIPS)
    prev = raw.get("previous")
    if isinstance(prev, str) and clean(prev):
        state["previous"] = clean(prev)
    n = raw.get("done")
    if isinstance(n, int) and not isinstance(n, bool) and n > 0:
        state["done"] = min(n, 99999)
    visits = []
    for v in raw["visits"] if isinstance(raw.get("visits"), list) else []:
        try:
            visits.append(day(v))
        except ValueError:
            pass
    # A visit dated after today comes from a clock that was wrong once. It
    # would sort last and hide every real visit, so it is dropped.
    now = today().isoformat()
    # Only recent visits are kept: enough for "welcome back" and the
    # days-in-a-row count, and too few to read as an attendance record.
    oldest = (today() - datetime.timedelta(days=KEEP_VISIT_DAYS)).isoformat()
    state["visits"] = sorted(v for v in set(visits) if oldest <= v <= now)[-MAX_VISITS:]
    intent = raw.get("intent")
    try:
        if isinstance(intent, dict) and isinstance(intent.get("text"), str):
            text = clean(intent["text"])
            if text:
                state["intent"] = {"text": text, "date": day(intent.get("date"))}
                # The day it was first set, kept while it is carried over.
                try:
                    since = day(intent.get("since"))
                    if since < state["intent"]["date"]:
                        state["intent"]["since"] = since
                except ValueError:
                    pass
                skips = intent.get("skips")
                if isinstance(skips, int) and not isinstance(skips, bool) and 0 < skips < 10:
                    state["intent"]["skips"] = skips
    except ValueError:
        pass
    finished = []
    # A hostile file could fill the screen with far-off dates.
    latest = (today() + datetime.timedelta(days=365)).isoformat()
    for item in (raw.get("finished") if isinstance(raw.get("finished"), list)
                 else []):
        try:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                text = clean(item["text"])
                when = day(item.get("date"))
                if text and "2000-01-01" <= when <= latest:
                    finished.append({"text": text, "date": when})
        except ValueError:
            pass
    if finished:
        state["finished"] = finished[-MAX_FINISHED:]
    # With plans turned off by policy, plan text is neither shown nor kept: it
    # is dropped here, so the next save leaves it out of the file.
    if plans_off():
        state["intent"] = None
        for key in ("previous", "done", "finished"):
            state.pop(key, None)
    # Without the days-in-a-row count, only the latest visit is needed.
    if policy("HideDaysInARow"):
        state["visits"] = state["visits"][-1:]
    return state, True


def file_form(state):
    """What goes in the file: the state, holding at most MAX_VISITS dates."""
    out = {k: v for k, v in state.items() if not (k == "epoch" and not v)}
    out["visits"] = sorted(set(state["visits"]))[-MAX_VISITS:]
    return out


def sweep_tmp():
    """Remove temp copies left by a save that was killed partway.

    Only copies a day old go, so another window's save in progress is never
    touched.
    """
    try:
        names = os.listdir(data_dir())
    except OSError:
        return
    for name in names:
        if name.startswith("notes.json.") and name.endswith(".tmp"):
            path = os.path.join(data_dir(), name)
            try:
                if time.time() - os.path.getmtime(path) > 86400:
                    os.remove(path)
            except OSError:
                pass


def save(state):
    sweep_tmp()
    try:
        os.makedirs(data_dir(), mode=0o700, exist_ok=True)
        tmp = f"{data_file()}.{os.getpid()}.tmp"
        try:
            os.remove(tmp)
        except FileNotFoundError:
            pass
        # Created private, never through a link, and flushed to disk before it
        # replaces the real file, so a power cut can't leave a half-written one.
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(tmp, flags, 0o600), "w", encoding="utf-8") as f:
            json.dump(file_form(state), f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        # Antivirus or another window reading the file can hold it for a
        # moment, and Windows then refuses the replace.
        for attempt in range(5):
            try:
                os.replace(tmp, data_file())
                break
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(0.1)
        return True
    except OSError:
        try:
            os.remove(tmp)
        except (OSError, UnboundLocalError):
            pass
        return False


def say(text=""):
    try:
        print(text, flush=True)
    except (OSError, ValueError) as e:
        raise OutputClosed(e) from e


def width():
    """Wrap to the window, so a large font doesn't re-wrap lines raggedly."""
    try:
        cols = shutil.get_terminal_size((80, 24)).columns
    except (OSError, ValueError):
        cols = 80
    return max(30, min(72, cols - 2))


def indent(text):
    return "\n".join(textwrap.wrap(text, width() - 4, initial_indent="  ",
                                   subsequent_indent="  ",
                                   break_on_hyphens=False,
                                   break_long_words=False))


def interactive():
    if FORCE_INTERACTIVE:
        return True
    try:
        if sys.stdin is None or not sys.stdin.isatty():
            return False
    except (OSError, ValueError):
        return False
    if os.name != "nt":
        return True
    # Windows calls the NUL device a terminal too. Only a real console has a
    # console mode, so ask for one.
    try:
        import ctypes
        import msvcrt
        from ctypes import wintypes
        handle = msvcrt.get_osfhandle(sys.stdin.fileno())
    except (OSError, ValueError):
        return False
    except Exception:
        return True  # the check itself broke; trust isatty() rather than flash shut
    try:
        get_mode = ctypes.WinDLL("kernel32", use_last_error=True).GetConsoleMode
        get_mode.argtypes = [wintypes.HANDLE, wintypes.LPDWORD]
        get_mode.restype = wintypes.BOOL
        return bool(get_mode(handle, ctypes.byref(wintypes.DWORD())))
    except Exception:
        return True


def ask(prompt):
    """Return the typed text, or None when nobody can answer.

    A prompt longer than the window is wrapped, and only its last line is
    left for the answer, so the choices never run off a magnified screen.
    """
    if not interactive():
        return None
    lines = []
    for part in prompt.split("\n"):
        lines += textwrap.wrap(part, width(), break_on_hyphens=False,
                               break_long_words=False) or [""]
    for line in lines[:-1]:
        say(line)
    try:
        return input(lines[-1] + " ").strip()
    except KeyboardInterrupt:
        say()  # the prompt is still on this line; start the next one cleanly
        return None
    except (EOFError, OSError, UnicodeError):
        return None


def is_yes(text):
    return (text or "").lower().strip(" .!") in YES


def is_no(text):
    return (text or "").lower().strip(" .!") in NO


def not_a_choice(word, choices):
    """Name what was typed, and say what would have worked."""
    shown = tidy(word)
    if len(shown) > 30:
        shown = shown[:30] + "..."
    say(tr('That was not one of the choices: "{shown}".').format(shown=shown)
        + " " + choices)


def ask_choice(prompt, yes, no, hint, tries=3):
    """Ask until the answer is recognised. Returns "yes", "no", "" or None.

    "" means Enter, None means nobody could answer or the answers were not
    understood three times, so the caller treats it as no answer.
    """
    for _ in range(tries):
        answer = ask(prompt)
        if answer is None:
            return None
        text = answer.lower().strip(" .!")
        if not text:
            return ""
        if text in QUIT_WORDS:
            raise Quit
        if text in yes:
            return "yes"
        if text in no:
            return "no"
        not_a_choice(answer, hint)
    return None


def para(text):
    """Say a paragraph wrapped to the window, never broken by hand."""
    say(textwrap.fill(text, width(), break_on_hyphens=False,
                      break_long_words=False))


def wrapped(prefix, text):
    return textwrap.fill(prefix + text, width(), subsequent_indent="  ",
                         break_on_hyphens=False, break_long_words=False)


def in_a_row(visits, d):
    """Count visits back from today where each is within 4 days of the next.

    Four days lets a Friday off and a weekend pass without breaking it.
    """
    days = [datetime.date.fromisoformat(v) for v in visits]
    days = [x for x in days if x <= d] + [d]
    days = sorted(set(days))
    n = 1
    for later, earlier in zip(days[:0:-1], days[-2::-1], strict=True):
        if (later - earlier).days > 4:
            break
        n += 1
    return n


def launcher_command():
    """The command the launcher runs, or None for a folder cmd would misread.

    It checks hello.cmd still exists, so a launcher left behind after an
    uninstall, or roamed to a PC without the program, does nothing.
    """
    target = os.path.dirname(os.path.abspath(__file__))
    if any(c in target for c in '"%&^<>|!'):
        return None
    # start runs a .cmd through cmd /k, which strips the quotes from a path
    # with ( or @ in it. /d keeps the folder out of that command line.
    return (f'if exist "{target}\\hello.cmd" start "hello-world" /d "{target}" '
            "hello.cmd --startup")


def remove_legacy_launcher():
    """Delete an old Startup .cmd launcher; True when there was one."""
    path = legacy_launcher()
    if not path or not os.path.isfile(path) or os.path.islink(path):
        return False
    clear_launcher_temps(path)
    try:
        os.remove(path)
        return True
    except OSError:
        return False


def clear_launcher_temps(path):
    """Remove temp copies a killed launcher write left in the Startup folder."""
    folder, name = os.path.split(path)
    try:
        names = os.listdir(folder)
    except OSError:
        return
    for n in names:
        if n.startswith(name + ".") and n.endswith(".tmp"):
            try:
                os.remove(os.path.join(folder, n))
            except OSError:
                pass


def remind(on, quiet=False):
    """Turn the sign-in launcher on or off. True when it worked."""
    kind, where = launcher_place()
    if not kind:
        say(tr("The sign-in reminder works on Windows only."))
        return False
    if on and policy("DisableSignInLauncher"):
        say(tr("Your organization has turned off opening at sign-in."))
        return False
    if on:
        command = launcher_command()
        if not command:
            say(tr("The reminder cannot be set up from this folder."))
            return False
        try:
            if kind == "file":
                write_launcher_file(where, command)
            else:
                import winreg
                cmd = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"),
                                   "System32", "cmd.exe")
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, where) as key:
                    winreg.SetValueEx(key, RUN_VALUE, 0, winreg.REG_SZ,
                                      f'"{cmd}" /d /c {command}')
                remove_legacy_launcher()
        except (OSError, UnicodeEncodeError):
            say(tr("Could not set up the reminder."))
            return False
        say(tr("Done. hello-world will open once a day when you sign in."))
        say(tr("To stop it, choose option 2 in the menu."))
        return True
    try:
        if kind == "file":
            clear_launcher_temps(where)
            try:
                os.remove(where)
            except FileNotFoundError:
                pass
        else:
            import winreg
            remove_legacy_launcher()
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, where, 0,
                                    winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, RUN_VALUE)
            except FileNotFoundError:
                pass
    except OSError:
        say(tr("Could not turn off the sign-in reminder."))
        return False
    if not quiet:
        say(tr("Done. The sign-in reminder is off."))
    return True


def write_launcher_file(path, command):
    """Write the test stand-in for the Run value, whole, then move it in."""
    clear_launcher_temps(path)
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(tmp, "w", encoding="ascii", newline="") as f:
            f.write("@echo off\r\n" + command + "\r\n")
        os.replace(tmp, path)
    except (OSError, UnicodeEncodeError):
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def show_saved(state, full=True):
    d = today()
    recent = [v for v in state["visits"]
              if 0 <= (d - datetime.date.fromisoformat(v)).days <= 6]
    if full:
        say(tr("Saved on this computer in:"))
        say("  " + data_file())
    else:
        say(tr("Saved in your own user folder on this computer."))
    para(tr("Days you opened it in the last {days} days: {n} (last 7 days: "
            "{recent})").format(days=KEEP_VISIT_DAYS, n=len(state["visits"]),
                                recent=len(recent)))
    if state.get("done"):
        say(tr("Times you marked a plan done: {n}").format(n=state["done"]))
    if state["intent"]:
        say(wrapped(tr("Your current plan: "), state["intent"]["text"]))
    if state.get("previous"):
        say(wrapped(tr("Earlier plan (for same): "), state["previous"]))
    show_finished(state)
    say(tr("Days-in-a-row message: shown.") if state["streak"] else
        tr("Days-in-a-row message: hidden."))
    if launcher_place()[0]:
        say(tr("Opens by itself at sign-in: turned off by your organization.")
            if policy("DisableSignInLauncher") else
            tr("Opens by itself at sign-in: on.") if launcher_on() else
            tr("Opens by itself at sign-in: off."))
    para(tr("It never leaves this computer. Others who can read this "
            "computer's files, such as IT staff, could read it."))
    if full:
        say(tr("After tidying, the file holds only this:"))
        say(json.dumps(file_form(state), indent=2, ensure_ascii=False))


def reset(state):
    """True when deleted, False when a delete failed, None when declined."""
    answer = ask(tr("Delete all saved notes, dates and plans on this "
                    "computer? (y or n, Enter to cancel) > "))
    word = (answer or "").lower().strip(" .!")
    if word not in STRICT_YES:
        say(tr("Nothing was deleted."))
        if word in QUIT_WORDS:
            raise Quit
        return None
    with file_lock():
        return delete_everything(state)


def delete_everything(state):
    """The body of reset() once confirmed, run while holding the lock."""
    leftovers = [data_file()]
    failed = []
    listing_failed = False
    try:
        leftovers += [os.path.join(data_dir(), n)
                      for n in os.listdir(data_dir())
                      if n.startswith("notes.json.")
                      and (n.endswith(".tmp") or n.startswith("notes.json.bak"))]
    except FileNotFoundError:
        pass
    except OSError:
        listing_failed = True
    for path in leftovers:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError:
            failed.append(path)
    if failed or listing_failed:
        say(tr("Could not delete everything."))
        if failed:
            say(tr("Delete these yourself:"))
            for path in failed:
                say("  " + path)
        if listing_failed:
            say(tr("Could not list the folder, so backup copies may remain:"))
            say("  " + data_dir())
        return False
    state.clear()
    state.update(new_state())
    # A marker with a new epoch instead of no file, so another open window
    # can tell the notes were deleted.
    state["epoch"] = os.urandom(8).hex()
    say(tr("Done. Everything saved was deleted."))
    if save(state):
        say(tr("Another open hello-world window cannot put it back."))
    else:
        para(tr("Close any other open hello-world window, or it may save its "
                "notes again."))
    return True


@contextlib.contextmanager
def file_lock():
    """Hold notes.lock while a change reads and writes the file.

    Without it, a delete in one window could land between another window's
    read and write, and that write would bring the deleted notes back.
    """
    try:
        os.makedirs(data_dir(), mode=0o700, exist_ok=True)
        fd = os.open(os.path.join(data_dir(), "notes.lock"),
                     os.O_RDWR | os.O_CREAT, 0o600)
    except OSError:
        yield
        return
    locked = False
    try:
        # ponytail: gives up after about 5 seconds and goes ahead unlocked,
        # so a stuck window can never freeze another one.
        for _ in range(50):
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError:
                time.sleep(0.1)
        yield
    finally:
        if locked:
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
        os.close(fd)


def refresh(state, can_save):
    """Re-read the file before a change, so a second open window can't
    overwrite what the first one saved. Returns False when it could not."""
    if not can_save:
        return False
    fresh, ok = load(repair=False)
    if ok:
        state.clear()
        state.update(fresh)
    return ok


def commit(state, base, can_save, soft=()):
    """Apply what this window changed since `base` to the file as it is now.

    A second open window's newer save is kept. Every save of a change goes
    through here. The file is re-read just before the write, with no prompt
    in between. Visits and finished plans are merged. Counts add only what
    this window added. Any other key is taken from this window only when it
    changed it. A key in `soft` was changed by tidying, not by the person, so
    the other window's change to it wins. Returns True when saved, and the
    state is then the merged copy.

    When everything was deleted since `base` was read, nothing is saved, and
    both the state and `base` become the file as it is now. A caller's undo()
    then leaves the window empty too.
    """
    if not can_save:
        return False
    with file_lock():
        return merge_and_save(state, base, soft)


def merge_and_save(state, base, soft):
    """The body of commit(), run while holding the lock."""
    fresh, ok = load(repair=False)
    if not ok:
        return False
    # A missing file has no marker at all: deleted by hand or set aside as
    # damaged, not by Delete everything, which always writes a new marker.
    if "epoch" in base and "epoch" in fresh and fresh["epoch"] != base["epoch"]:
        para(tr("Everything saved was deleted in another window, so this was "
                "not saved."))
        state.clear()
        state.update(fresh)
        base.clear()
        base.update(copy.deepcopy(fresh))
        return False
    if (fresh.get("done", 0) > base.get("done", 0)
            and state.get("done", 0) > base.get("done", 0)):
        say(tr("The other open window had also finished a plan."))
    for key in set(state) | set(base):
        if key in ("visits", "done", "offer_skips", "finished"):
            continue
        if state.get(key) == base.get(key):
            continue
        if key in soft and fresh.get(key) != base.get(key):
            if key == "intent":
                say(tr("The other open window changed the plan, so its plan "
                       "is kept."))
            continue
        if key in state:
            fresh[key] = copy.deepcopy(state[key])
        else:
            fresh.pop(key, None)
    fresh["visits"] = sorted(set(fresh["visits"]) | set(state["visits"]))[-MAX_VISITS:]
    mine, before = state.get("finished", []), base.get("finished", [])
    theirs = fresh.get("finished", [])
    added = row_counts(mine) - row_counts(before)
    removed = row_counts(before) - row_counts(mine)
    # Each finished row came with one done. A row the other window also added
    # with the same words and date is one finish, not two.
    repeats = added & (row_counts(theirs) - row_counts(before))
    for key, cap in (("done", 99999), ("offer_skips", MAX_OFFER_SKIPS)):
        gained = state.get(key, 0) - base.get(key, 0)
        if key == "done":
            gained -= sum(repeats.values())
        if gained > 0:
            fresh[key] = min(fresh.get(key, 0) + gained, cap)
    rows = {json.dumps(r, sort_keys=True): r for r in theirs + mine}
    kept = (row_counts(theirs) - removed) + (added - repeats)
    finished = sorted((rows[k] for k in kept.elements()), key=lambda r: r["date"])
    if finished:
        fresh["finished"] = finished[-MAX_FINISHED:]
    else:
        fresh.pop("finished", None)
    if not save(fresh):
        return False
    state.clear()
    state.update(fresh)
    return True


def row_counts(rows):
    """Finished rows counted as a multiset, since dicts can't go in a Counter."""
    return collections.Counter(json.dumps(r, sort_keys=True) for r in rows)


def undo(state, base):
    """Put the state back as it was when a save failed."""
    state.clear()
    state.update(base)


COMMAND_WORDS = ("menu", "help", "?", "q", "quit", "exit", "done", "plan",
                 "m", "p", "menú", "ayuda", "hecho", "salir")
# Someone declining to plan is not making an error, so these get no lecture.
DECLINE_WORDS = ("none", "no", "nope", "nothing", "skip", "n", "nada",
                 "ninguno", "saltar")


def is_command(text, again=None):
    """A command word typed where a plan is asked is not a plan."""
    word = (text or "").lower().strip(" .!")
    if word in DECLINE_WORDS:
        return True
    if word in COMMAND_WORDS:
        para(tr("That looks like a command, not a plan, so nothing was saved.")
             + " " + (again or tr("Type plan at the last prompt to set one.")))
        return True
    return False


def is_same(text):
    return (text or "").strip().lower() in SAME_WORDS


def show_finished(state, limit=MAX_FINISHED):
    """The last few finished plans, so finishing has a visible payoff.

    After done and on welcome back only the last few are read out; option 1
    lists every one kept.
    """
    items = state.get("finished") or []
    if not items:
        return
    say()
    say(tr("Finished lately:"))
    for item in list(reversed(items))[:limit]:
        say(wrapped("  " + long_date(datetime.date.fromisoformat(
            item["date"])) + ": ", item["text"]))


def reuse(state, raw):
    """Typing `same` brings back the plan before this one, if there is one."""
    if is_same(raw) and state.get("previous"):
        return state["previous"]
    return raw


def set_plan(state, can_save, iso=None, after_done=False):
    """Returns True when the person chose to close (after a done only)."""
    refresh(state, can_save)
    old = state["intent"]
    # daily() passes its own date, so a window left open past midnight
    # doesn't date a plan to the next day.
    iso = iso or today().isoformat()
    if old:
        label = (tr("Your plan today: ") if old["date"] == iso else
                 tr("Your plan from {date}: ").format(date=long_date(
                     datetime.date.fromisoformat(old["date"]))))
        say(wrapped(label, old["text"]))
    same = bool(state.get("previous"))
    if same:
        say(wrapped(tr("Earlier plan: "), state["previous"]))
    if after_done:
        prompt = (tr("Type the next plan, same to reuse the earlier plan, or "
                     "Enter to close > ") if same else
                  tr("Type the next plan, or Enter to close > "))
    elif old:
        prompt = (tr("Type today's plan, same to reuse the earlier plan, or "
                     "Enter to keep it > ") if same else
                  tr("Type today's plan, or Enter to keep it > "))
    else:
        prompt = (tr("Type today's plan, same to reuse the earlier plan, or "
                     "Enter to go back > ") if same else
                  tr("Type today's plan, or Enter to go back > "))
    typed = ask(prompt)
    word = (typed or "").lower().strip(" .!")
    if after_done and not word:
        say(tr("Closing."))
        return True
    if word in QUIT_WORDS:
        raise Quit
    # Another window may have saved while this prompt waited.
    refresh(state, can_save)
    old = state["intent"]
    if is_same(typed) and not state.get("previous"):
        say(tr("There is no earlier plan to reuse yet. Nothing changed."))
        return False
    if is_command(typed, tr("Type your plan, or press Enter to go back.")):
        return False
    text = typed_plan(reuse(state, typed) or "")
    if not text:
        say(tr("Nothing changed."))
        return False
    base = copy.deepcopy(state)
    # Changing today's plan is a correction, so only a plan carried over from
    # an earlier day is kept for same.
    if old and old["text"] != text and old["date"] != iso:
        state["previous"] = old["text"]
    state["intent"] = {"text": text, "date": iso}
    if commit(state, base, can_save):
        para(tr(SAVED_PLAN))
        nudge_if_several(text)
    else:
        undo(state, base)
        say(tr("Could not save that on this computer. Your plan is unchanged."))
    return False


def forget_finished(state, can_save):
    """Remove one finished plan from the file, and leave everything else."""
    refresh(state, can_save)
    shown = list(reversed(state.get("finished") or []))
    if not shown:
        say(tr("No finished plans are saved."))
        return
    for n, item in enumerate(shown, 1):
        say(wrapped(f"  {n}  {long_date(datetime.date.fromisoformat(item['date']))}: ",
                    item["text"]))
    numbers = [str(n) for n in range(1, len(shown) + 1)]
    for _ in range(3):
        choice = ask(tr("Type the number to forget (1 to {n}), or Enter to "
                        "keep them all > ").format(n=len(shown)))
        if (choice or "").lower().strip(" .!") in QUIT_WORDS:
            raise Quit
        if not choice or choice in numbers:
            break
        para(tr('There is no number "{typed}" on the list. Type a number from '
                "1 to {n}, or press Enter to keep them all.").format(
                    typed=tidy(choice)[:30], n=len(shown)))
    if not choice or choice not in numbers:
        say(tr("Nothing changed."))
        return
    item = shown[int(choice) - 1]
    also_same = state.get("previous") == item["text"] and ask_choice(
        tr("Also forget it as the earlier plan for same? "
           "(y or n, Enter to keep it for same) > "),
        STRICT_YES, ("n", "no", "nope"),
        tr("Type y or n, or press Enter to keep it for same.")) == "yes"
    refresh(state, can_save)
    if item not in state.get("finished", []):
        say(tr("That plan was already forgotten. Nothing changed."))
        return
    base = copy.deepcopy(state)
    state["finished"] = [i for i in state["finished"] if i != item]
    if also_same and state.get("previous") == item["text"]:
        state.pop("previous")
    kept = state.get("previous") == item["text"]
    if commit(state, base, can_save):
        say(wrapped(tr("Forgotten: "), item["text"]))
        if kept:
            say(tr("Same still has it."))
    else:
        undo(state, base)
        say(tr("Could not save that on this computer. Nothing changed."))


def menu(state, can_save=True, iso=None):
    # The options are read out once. After that only the prompt comes back,
    # and m lists them again.
    listed = False
    while True:
        say()
        reminding = launcher_on()
        if not listed:
            say(tr("Options"))
            say("  1  " + tr("Show what is saved on this computer"))
            say("  2  " + (tr("Open once a day at sign-in (turned off by your "
                              "organization)")
                           if policy("DisableSignInLauncher") and not reminding else
                           tr("Turn off: open once a day at sign-in (now on)")
                           if reminding else
                           tr("Turn on: open once a day at sign-in (now off)")))
            say("  3  " + (tr("Days-in-a-row message (hidden by your "
                              "organization)")
                           if policy("HideDaysInARow") else
                           tr("Hide the days-in-a-row message (now shown)")
                           if state["streak"] else
                           tr("Show the days-in-a-row message (now hidden)")))
            say("  4  " + tr("Delete everything saved"))
            say("  5  " + tr("Help"))
            if plans_off():
                say("  6  " + tr("Set today's plan (turned off by your "
                                 "organization)"))
                say("  7  " + tr("Forget a finished plan (turned off by your "
                                 "organization)"))
            else:
                say("  6  " + tr("Set or change today's plan"))
                say("  7  " + tr("Forget one finished plan"))
            say("  8  " + (tr("Thought and tip (hidden by your organization)")
                           if policy("HideThoughtAndTip") else
                           tr("Hide the thought and tip (now shown)")
                           if state.get("tips", True) else
                           tr("Show the thought and tip (now hidden)")))
            say("  Enter  " + tr("Back to the last prompt"))
            listed = True
            choice = ask(tr("Choose 1 to 8, or Enter to go back > "))
        else:
            choice = ask(tr("Choose 1 to 8, m to list the options, or Enter to "
                            "go back > "))
        if not choice:
            return
        if choice.lower().strip(" .!") in QUIT_WORDS:
            raise Quit
        if choice.lower() in ("m", "menu", "list", "menú", "lista"):
            listed = False
            continue
        if choice.lower() in ("help", "?", "h", "ayuda"):
            choice = "5"
        if choice == "1":
            if not refresh(state, can_save):
                para(tr("The saved file could not be read just now, so this "
                        "may be out of date."))
            show_saved(state, full=False)
            if (ask(tr("Type full to see the whole file, or Enter to go on > "))
                    or "").lower() in ("full", "todo"):
                refresh(state, can_save)
                say(json.dumps(file_form(state), indent=2, ensure_ascii=False))
        elif choice == "2":
            if remind(not reminding):
                # A choice made here is final; the offer must not come back.
                refresh(state, can_save)
                base = copy.deepcopy(state)
                state["offered"] = True
                if not commit(state, base, can_save):
                    undo(state, base)
                    say(tr("Could not save that choice on this computer."))
        elif choice == "3" and policy("HideDaysInARow"):
            say(tr("Your organization has hidden the days-in-a-row message."))
        elif choice == "3":
            refresh(state, can_save)
            base = copy.deepcopy(state)
            state["streak"] = not state["streak"]
            if commit(state, base, can_save):
                say(tr("Done. The days-in-a-row message is on.")
                    if state["streak"] else
                    tr("Done. The days-in-a-row message is off."))
            else:
                undo(state, base)
                say(tr("Could not save that choice on this computer."))
        elif choice == "4":
            reset(state)
        elif choice == "5":
            say(tr(MENU_HELP))
        elif choice in ("6", "7") and plans_off():
            say(tr("Plans are turned off by your organization."))
        elif choice == "6":
            set_plan(state, can_save, iso)
        elif choice == "7":
            forget_finished(state, can_save)
        elif choice == "8" and policy("HideThoughtAndTip"):
            say(tr("Your organization has hidden the thought and tip."))
        elif choice == "8":
            refresh(state, can_save)
            base = copy.deepcopy(state)
            if state.get("tips", True):
                state["tips"] = False
            else:
                state.pop("tips", None)
            if commit(state, base, can_save):
                say(tr("Done. The thought and tip are on.")
                    if state.get("tips", True) else
                    tr("Done. The thought and tip are off."))
            else:
                undo(state, base)
                say(tr("Could not save that choice on this computer."))
        else:
            not_a_choice(choice, tr("Type 1 to 8, or press Enter to go back."))


def offer_reminder(state, can_save, planned=False):
    """Ask whether to open at sign-in, right after a plan or from visit two on.

    It is asked once. Enter is final too, and an unclear answer asks again on
    a later visit.
    """
    if (not launcher_place()[0] or policy("DisableSignInLauncher")
            or state.get("offered") or launcher_on()
            or not (planned or len(state["visits"]) >= 2)):
        return
    answer = ask_choice(
        tr("Want it to open once a day when you sign in? "
           "(y or n, Enter for not now) > ")
        if plans_off() else
        tr("Want it to open once a day when you sign in so it can ask about "
           "your plan? (y or n, Enter for not now) > "),
        STRICT_YES, ("n", "no", "nope", "no thanks", "never", "stop",
                     "no gracias", "nunca"),
        tr("Type y or n, or press Enter for not now."))
    if answer is None:
        say(tr("That was not understood. It will ask again on a later visit."))
        return
    refresh(state, can_save)
    base = copy.deepcopy(state)
    if answer == "yes":
        if not remind(True):
            para(tr("It will ask again on a later visit. Menu option 2 also "
                    "turns it on."))
            say()
            return
        state["offered"] = True
    elif answer == "no":
        state["offered"] = True
        say(tr("No problem. Menu option 2 turns it on later."))
    else:
        skips = state.get("offer_skips", 0) + 1
        state["offer_skips"] = skips
        if skips >= MAX_OFFER_SKIPS:
            state["offered"] = True
            para(tr("Okay. It won't ask again. Menu option 2 turns it on."))
        else:
            para(tr("Okay. It will ask again on a later visit. Type n to stop it."))
    if not commit(state, base, can_save):
        say(tr("Could not save that choice on this computer."))
    say()


def finish_plan(state, text, d):
    """Count a finished plan, dated d. `same` only ever holds unfinished plans."""
    if state.get("previous") == text:
        state.pop("previous")
    state["done"] = min(state.get("done", 0) + 1, 99999)
    state["finished"] = (state.get("finished", [])
                         + [{"text": text, "date": d.isoformat()}])[-MAX_FINISHED:]


def done_lines(state, d):
    """Shown only once the save has worked, and with the merged count, so
    nobody is congratulated for something that was not recorded."""
    lines = DONE_LINES_ES if spanish() else DONE_LINES
    return [lines[d.toordinal() % len(lines)]]


def finish_day(plan_day, d):
    """The day a plan was finished. Asked only when it was set over a day ago,
    since the next morning almost always means the plan's own day."""
    if (d - plan_day).days <= 1:
        return plan_day
    days = [plan_day + datetime.timedelta(days=n)
            for n in range((d - plan_day).days + 1)]
    if len(days) > 7:
        days = days[:1] + days[-6:]
    # Numbers, like the menu: a letter here would clash with the y just typed.
    say(tr("When did you finish it?"))
    for n, when in enumerate(days, 1):
        say(f"  {n}  " + (tr("Today") if when == d else long_date(when)))
    numbers = [str(n) for n in range(1, len(days) + 1)]
    for _ in range(3):
        answer = ask(tr("Type a number from 1 to {n}, or Enter for 1 > ")
                     .format(n=len(days)))
        word = (answer or "").lower().strip(" .!")
        if not word:
            return days[0]
        if word in QUIT_WORDS:
            raise Quit
        if word in numbers:
            return days[int(word) - 1]
        not_a_choice(answer, tr("Type a number from 1 to {n}, or press Enter.")
                     .format(n=len(days)))
    return days[0]


def nudge_if_several(text):
    """A plan of several things joined together is hard to finish."""
    padded = f" {text.lower()} "
    if any(joint in padded for joint in (" and ", " & ", " y ")) or "+" in text:
        para(tr("That looks like more than one thing. Finishing the first "
                "part still counts."))


def mark_done_now(state, can_save, d):
    """Same-day done: the plan on screen is finished, so say so at once."""
    refresh(state, can_save)
    plan = state["intent"]
    if not plan:
        para(tr("There is no plan to mark as done. Type plan to set one."))
        return False
    base = copy.deepcopy(state)
    finish_plan(state, plan["text"], d)
    state["intent"] = None
    if not commit(state, base, can_save):
        undo(state, base)
        say(tr("Could not save that on this computer. The plan is still open."))
        return False
    for line in done_lines(state, d):
        say(line)
    show_finished(state, SHOWN_AFTER_DONE)
    return True


def daily(startup):
    d = today()
    iso = d.isoformat()
    state, can_save = load()
    base = copy.deepcopy(state)
    person = interactive()
    seen_today = iso in state["visits"]
    typed_new = False
    answered = False
    if startup and seen_today:
        return
    if policy("DisableSignInLauncher"):
        if launcher_on() or legacy_launcher() and os.path.isfile(legacy_launcher()):
            remind(False, quiet=True)
    elif remove_legacy_launcher():
        # An old Startup .cmd becomes the Run value, keeping the person's choice.
        remind(True)
    first = not state["visits"]
    intent = state["intent"]
    if intent and intent["date"] > iso:
        intent["date"] = iso  # the clock moved back; it is today's plan now
    expired = False
    # A plan kept day after day still counts from the day it was first set.
    since = intent.get("since", intent["date"]) if intent else None
    if intent and (d - datetime.date.fromisoformat(since)).days > 14:
        state["previous"] = intent["text"]
        intent, expired = None, True

    say(tr(GREETING))
    header = long_date(d)
    say(header[0].upper() + header[1:])
    say()

    if expired:
        para(tr("Your plan from over two weeks ago was put away. Type same "
                "at the plan prompt to bring it back."))
        say()

    if first:
        para(tr("Press Enter at each question to skip it, and once more to "
                "close. That's it."))
        say()
        welcome = [tr("Welcome.")]
        if not policy("HideThoughtAndTip"):
            welcome.append(tr("Each day you get one thought and one small "
                              "thing to try, the same for everyone."))
        if not plans_off():
            welcome.append(tr("If you type a plan, it asks next time how it "
                              "went. Notes stay in your user folder and it "
                              "sends nothing anywhere, but IT staff could read "
                              "them, so skip private details."))
        welcome.append(tr("Type menu at the last prompt for the options."))
        para(" ".join(welcome))
        say()
    elif not seen_today:
        last = datetime.date.fromisoformat(state["visits"][-1])
        row = in_a_row(state["visits"], d)
        if (d - last).days > 7:
            say(tr("Welcome back. Glad you are here."))
            show_finished(state, SHOWN_AFTER_DONE)
            say()
        elif (state["streak"] and not policy("HideDaysInARow")
              and (row in (3, 7, 14) or row % 30 == 0)):
            say(tr("You have opened this {row} times in a row. Nice to see "
                   "you.").format(row=row))
            say()

    quitting = False
    try:
        # Asked until it is answered, also on a second open the same day,
        # but two skips mean "stop asking"; the plan then shows as still open.
        if (intent and intent["date"] < iso and intent.get("skips", 0) < 2
                and not plans_off()):
            say(wrapped(tr("Last time you planned: "), intent["text"]))
            answer = ask_choice(
                tr("Did you do it? (y for yes, n for not yet, Enter to skip) > "),
                YES, NO, tr("Type y or n, or press Enter to skip."))
            if answer == "yes":
                answered = True
                when = finish_day(datetime.date.fromisoformat(intent["date"]), d)
                # Saved now, so the answer is heard now.
                finish_plan(state, intent["text"], when)
                state["intent"] = None
                if commit(state, base, can_save):
                    base = copy.deepcopy(state)
                    intent = None
                    for line in done_lines(state, d):
                        say(line)
                else:
                    # A delete in another window also lands here, so take
                    # the plan from the state, never the copy held above.
                    undo(state, base)
                    intent = state["intent"]
                    say(tr("Could not save that on this computer. Your answer "
                           "was not counted."))
            elif answer == "no":
                answered = True
                keep = ask_choice(
                    tr("That is fine. Keep it for today? (y or n, Enter to "
                       "keep it) > "),
                    STRICT_YES + ("not yet", "todavía no", "aún no", "aun no"),
                    ("n", "no", "nope"),
                    tr("Type y to keep it, n to clear it, or press Enter to "
                       "keep it."))
                if keep == "no":
                    state["previous"] = intent["text"]
                    intent = None
                    say(tr("Cleared. Type same at a plan prompt if you want it back."))
                else:
                    intent = {"text": intent["text"], "date": iso,
                              "since": intent.get("since", intent["date"])}
                    say(tr("Kept for today."))
            elif answer is None and person:
                say(tr("That was not understood. Your plan is left as it was."))
            elif answer is not None:
                intent = dict(intent, skips=intent.get("skips", 0) + 1)
                say(tr("Your plan is still open."))
            say()

        if state.get("tips", True) and not policy("HideThoughtAndTip"):
            thought, tip = todays_pair(d)
            say(tr("Thought for today:"))
            say(indent(thought))
            say()
            say(tr("Try this today:"))
            say(indent(tip))
            say()

        if intent and intent["date"] == iso:
            say(wrapped(tr("Your plan for today: "), intent["text"]))
            say()
        elif intent:
            # Not answered, or skipped twice; it must not vanish.
            when = long_date(datetime.date.fromisoformat(intent["date"]))
            say(tr("Still open since {date}:").format(date=when))
            say(indent(intent["text"]))
            say()
        if (not seen_today and not plans_off()
                and not (intent and intent["date"] == iso)):
            skip = (tr("(Enter to skip)") if not intent else
                    tr("(A plan typed here replaces the old one. Enter to skip)"))
            if state.get("previous") and not intent:
                say(wrapped(tr("Earlier plan: "), state["previous"]))
                skip = tr("(Type same to reuse it, or Enter to skip)")
            question = (tr("What is one thing you want to get done today?")
                        + "\n" + skip + " > ")
            text = ask(question)
            # The welcome mentions the menu, so someone may type it here first.
            if (text or "").lower().strip(" .!") in ("menu", "m", "help", "h",
                                                    "?", "menú", "ayuda"):
                para(tr("The menu comes at the last prompt, after this question. "
                        "Type menu there."))
                text = ask(question)
            if (text or "").lower().strip(" .!") in QUIT_WORDS:
                raise Quit
            if is_same(text) and not state.get("previous"):
                say(tr("There is no earlier plan to reuse yet. Nothing was saved."))
                text = ""
            elif is_command(text):
                text = ""
            if text:
                text = typed_plan(reuse(state, text))
                if text:
                    if intent and intent["text"] != text:
                        state["previous"] = intent["text"]
                    intent = {"text": text, "date": iso}
                    typed_new = True
            say()
    except Quit:
        quitting = True

    # With nobody at the keyboard, such as a launch with no console, show the
    # screen but keep today's questions for the next real visit.
    if person:
        if not seen_today:
            state["visits"] = (state["visits"] + [iso])[-MAX_VISITS:]
        state["intent"] = intent
        # A plan only tidied here (a future date made today, an old plan
        # cleared) must not overwrite one the other window saved meanwhile.
        soft = () if answered or typed_new else ("intent", "previous")
        if not commit(state, base, can_save, soft):
            undo(state, base)
            intent = state["intent"]
            para(tr("Your notes could not be saved on this computer. This "
                    "screen still works."))
        else:
            intent = state["intent"]
            if typed_new:
                para(tr(SAVED_PLAN))
                nudge_if_several(intent["text"])
                say()
            if not seen_today and not quitting:
                try:
                    offer_reminder(state, can_save, planned=typed_new)
                except Quit:
                    quitting = True
                # The offer re-reads the file, so pick up the plan it read.
                intent = state["intent"]
    if quitting:
        say(tr("Closing."))
        return

    # A message at the very end must stay on screen until the person has read
    # it, because the window closes as soon as the program exits.
    try:
        last_prompt(state, can_save, intent, person, d, iso)
    except Quit:
        say(tr("Closing."))


def last_prompt(state, can_save, intent, person, d, iso):
    """Loop at the last prompt until the person closes the window."""
    while True:
        planned = bool(intent and person and state["intent"] is intent)
        prompt = (tr("Type menu or q, or Enter to close > ") if plans_off() else
                  tr("Type done, plan, menu or q, or Enter to close > ")
                  if planned else
                  tr("Type plan, menu or q, or Enter to close > "))
        answer = (ask(prompt) or "").lower().strip()
        if answer in (*DONE_WORDS, "p", "plan") and plans_off():
            say(tr("Plans are turned off by your organization."))
            continue
        if answer in DONE_WORDS and person:
            closing = False
            if mark_done_now(state, can_save, d):
                say()
                closing = set_plan(state, can_save, iso, after_done=True)
            intent = state["intent"]
            if closing:
                break
            continue
        elif answer in ("p", "plan") and person:
            set_plan(state, can_save, iso)
            intent = state["intent"]
            continue
        elif answer in ("m", "menu", "h", "help", "?", "menú", "ayuda"):
            menu(state, can_save, iso)
            intent = state["intent"]
            continue
        elif answer in QUIT_WORDS:
            pass
        elif answer:
            not_a_choice(answer, tr("Type done, plan, menu or q, or press "
                                    "Enter to close.")
                         if planned else
                         tr("Type plan, menu or q, or press Enter to close."))
            continue
        break


def run(argv):
    # Before lowercasing, so a path keeps its case.
    if len(argv) == 2 and argv[0].lower() == "--check-content":
        return check_content(argv[1])
    argv = [a.lower() for a in argv]
    if argv in (["/?"], ["-?"], ["/help"], ["-help"], ["help"]):
        argv = ["--help"]
    if argv == ["--plain"]:
        say(GREETING)
        return 0
    if argv in (["--version"], ["-v"]):
        say("hello-world " + VERSION)
        return 0
    if argv == ["--help"] or argv == ["-h"]:
        say(help_text())
        return 0
    if argv == ["--startup"]:
        daily(startup=True)
        return 0
    if not argv:
        daily(startup=False)
        return 0
    if argv == ["--stats"]:
        state, readable = load(repair=False)
        if not readable:
            say(tr("The saved file can't be read right now, or it is damaged."))
            say(tr("Nothing was changed. Saved in: ") + data_dir())
            return 1
        show_saved(state)
        return 0
    if argv == ["--reset"]:
        if not interactive():
            say(tr("Deleting saved notes needs a person at the keyboard."))
            return 1
        state, _ = load(repair=False)
        # Answering no is the person's choice; only a failed delete is an error.
        try:
            return 1 if reset(state) is False else 0
        except Quit:
            return 0
    if len(argv) == 2 and argv[0] == "--remind" and argv[1] in ("on", "off"):
        return 0 if remind(argv[1] == "on") else 1
    if len(argv) == 2 and argv[0] == "--streak" and argv[1] in ("on", "off"):
        state, can_save = load()
        base = copy.deepcopy(state)
        state["streak"] = argv[1] == "on"
        if commit(state, base, can_save):
            say(tr("Done. The days-in-a-row message is on.")
                if state["streak"] else
                tr("Done. The days-in-a-row message is off."))
            return 0
        say(tr("Could not save that choice on this computer."))
        return 1
    if len(argv) == 1 and argv[0] in ("--remind", "--streak"):
        say(tr("{option} needs on or off. Here are the options.")
            .format(option=argv[0]))
    else:
        say(tr("Unknown option: {option}. Here are the options.")
            .format(option=tidy(" ".join(argv))[:60]))
    say()
    say(help_text())
    return 2


def check_content(path):
    """--check-content: say whether an organization content file is usable."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            data = json.loads(f.read(200_001))
    except OSError as e:
        say(f"Can't read {tidy(path)}: {e.strerror}")
        return 1
    except (ValueError, RecursionError):
        say("The file isn't valid JSON, or is over 200,000 characters.")
        return 1
    problems = content_problems(data)
    for problem in problems:
        say(problem)
    if problems:
        return 1
    say(f"OK: {len(data['thoughts'])} thoughts and {len(data['tips'])} tips.")
    return 0


def main():
    try:
        # print() silently does nothing when stdout is None (fd 1 closed at start).
        # A stdout object that was closed later raises ValueError instead.
        if sys.stdout is None:
            raise OutputClosed("stdout is closed")
        # A console that can't show a typed character prints ? instead of failing.
        for stream in (sys.stdout, sys.stderr):
            if stream is not None and hasattr(stream, "reconfigure"):
                try:
                    stream.reconfigure(errors="replace")
                except (OSError, ValueError) as e:
                    if stream is sys.stdout:
                        raise OutputClosed(e) from e
        return run(sys.argv[1:])
    except OutputClosed as e:
        try:
            print(f"hello.py: cannot write to stdout: {e} "
                  "(contact IT if this keeps happening)", file=sys.stderr,
                  flush=True)
        except Exception:
            pass
        # A failed write stays buffered, and the shutdown flush would fail
        # again and turn exit 1 into 120. _exit skips that flush.
        os._exit(1)
    except KeyboardInterrupt:
        return 1
    except Exception as e:
        try:
            print(f"hello.py: something went wrong ({type(e).__name__}). "
                  "Contact IT.", file=sys.stderr, flush=True)
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
