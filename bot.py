import telebot
from telebot import types
import os
import tempfile

BOT_TOKEN = "8553508437:AAEwuLlhelaNjVqqtmxUwLsxkbHn3PAioPI"
bot = telebot.TeleBot(BOT_TOKEN)

# ==================== ДАННЫЕ ====================

# Налоговые режимы
tax_regimes = {
    "🟢 Патент": {
        "Лимит дохода": "до 3 528 МРП в год (≈ 13.9 млн тг)",
        "Ставка": "1% от дохода",
        "Отчётность": "Нет",
        "Сотрудники": "Нельзя нанимать",
        "Кому подходит": "Фрилансеры, репетиторы, мастера"
    },
    "🔵 Упрощёнка (ФНО 910)": {
        "Лимит дохода": "до 24 038 МРП за полугодие (≈ 94.8 млн тг)",
        "Ставка": "3% от дохода (1.5% ИПН + 1.5% соцналог)",
        "Отчётность": "Раз в полугодие (910 форма)",
        "Сотрудники": "До 30 человек",
        "Кому подходит": "Малый бизнес, услуги, торговля"
    },
    "🟠 Розничный налог": {
        "Лимит дохода": "до 600 000 МРП в год",
        "Ставка": "3% от дохода",
        "Отчётность": "Ежеквартально",
        "Сотрудники": "Без ограничений",
        "Кому подходит": "Розничная торговля, общепит, услуги населению"
    },
    "⚪ Общеустановленный режим": {
        "Лимит дохода": "Без ограничений",
        "Ставка": "10% ИПН от чистого дохода",
        "Отчётность": "Ежеквартально (ФНО 200, 220)",
        "Сотрудники": "Без ограничений",
        "Кому подходит": "Крупный бизнес, высокие расходы"
    }
}

# ЕСП данные
esp_data = {
    "categories": {
        "🏠 За себя (город)": {"rate": "1", "amount": "5 204", "mci": "5 204"},
        "🌾 За себя (село)": {"rate": "0.5", "amount": "2 602", "mci": "5 204"},
        "👨‍👩‍👧 За работника": {"rate": "1", "amount": "5 204", "mci": "5 204"}
    },
    "covers": [
        "✅ ИПН (индивидуальный подоходный налог)",
        "✅ СО (социальные отчисления)",
        "✅ ВОСМС (мед. страхование)",
        "✅ ОПВ (пенсионные взносы)"
    ]
}

# Сроки сдачи
deadlines_data = {
    "📊 ФНО 910 (Упрощёнка)": {
        "period": "Полугодие",
        "deadlines": ["• За 1 полугодие: до 15 августа", "• За 2 полугодие: до 15 февраля"],
        "payment": "Оплата до 25 числа после сдачи"
    },
    "💳 Патент": {
        "period": "Месяц/Квартал/Год",
        "deadlines": ["• Оплата ДО начала периода", "• Заявление за 3 дня до начала"],
        "payment": "Предоплата 100%"
    },
    "🛒 Розничный налог": {
        "period": "Квартал",
        "deadlines": ["• За 1 квартал: до 15 мая", "• За 2 квартал: до 15 августа", "• За 3 квартал: до 15 ноября", "• За 4 квартал: до 15 февраля"],
        "payment": "Оплата до 25 числа после сдачи"
    },
    "💰 ЕСП": {
        "period": "Месяц",
        "deadlines": ["• Ежемесячно до 25 числа"],
        "payment": "Через Kaspi/банк"
    }
}

# Контакты
contacts_data = {
    "🏛 Комитет госдоходов": {
        "phone": "📞 1414 (бесплатно)",
        "website": "🌐 kgd.gov.kz",
        "cabinet": "💻 cabinet.salyk.kz",
        "description": "Налоги, отчётность, проверки"
    },
    "📱 eGov": {
        "phone": "📞 1414",
        "website": "🌐 egov.kz",
        "cabinet": "💻 egov.kz/services",
        "description": "Госуслуги онлайн, справки, регистрация"
    },
    "🏦 Минтруда (соцзащита)": {
        "phone": "📞 1411",
        "website": "🌐 enbek.gov.kz",
        "cabinet": "💻 myenbek.kz",
        "description": "Пенсия, пособия, трудовые вопросы"
    }
}

# Чек-лист открытия ИП
checklist_ip = [
    {"step": "1️⃣ Получить ЭЦП", "description": "Электронная цифровая подпись нужна для всех онлайн-услуг", "where": "ЦОН или egov.kz", "cost": "Бесплатно", "time": "1 день"},
    {"step": "2️⃣ Зарегистрировать ИП", "description": "Подать заявление на регистрацию ИП", "where": "egov.kz или Kaspi Business", "cost": "Бесплатно", "time": "1 день"},
    {"step": "3️⃣ Выбрать налоговый режим", "description": "Патент, упрощёнка или розничный налог", "where": "cabinet.salyk.kz", "cost": "Бесплатно", "time": "1 день"},
    {"step": "4️⃣ Открыть банковский счёт", "description": "Расчётный счёт для бизнеса", "where": "Любой банк / Kaspi Business", "cost": "Бесплатно", "time": "1 день"},
    {"step": "5️⃣ Установить Kaspi Pay / ККМ", "description": "Для приёма платежей от клиентов", "where": "Kaspi.kz", "cost": "Бесплатно", "time": "1 день"}
]

# Частые вопросы (расширенные)
faq_data = {
    "Как открыть ИП?": "Для открытия ИП нужно:\n1. Зарегистрироваться на egov.kz\n2. Получить ЭЦП\n3. Подать заявление онлайн\n4. Выбрать налоговый режим\n\n⏱ Время: 1 день\n💵 Стоимость: бесплатно",
    
    "Какой режим выбрать?": "📊 *Рекомендации:*\n\n• Доход до 3 528 МРП/год → *Патент*\n• Доход до 24 038 МРП/полугодие → *Упрощёнка (910)*\n• Розничная торговля → *Розничный налог*\n• Услуги физлицам на дому → *ЕСП*",
    
    "Когда платить налоги?": "📅 *Сроки уплаты:*\n\n• Упрощёнка (910) — до 25 числа после отчёта\n• Патент — до получения патента\n• Розничный налог — до 25 числа после квартала\n• ЕСП — ежемесячно до 25 числа",
    
    "Нужна ли касса?": "🧾 *ККМ обязателен если:*\n\n• Работаете с наличными\n• Розничная торговля\n• Общепит\n\n*Не нужен:* при безналичных расчётах B2B, ЕСП",
    
    "Какие лицензии нужны?": "📜 *Лицензируемые виды деятельности:*\n\n• 🏥 Медицина и фармацевтика\n• 🎓 Образовательные услуги\n• 🚕 Пассажирские перевозки\n• 🏗 Строительство (1-3 категории)\n• 💰 Финансовые услуги\n• 🔒 Охранная деятельность\n• 🍺 Продажа алкоголя/табака\n\n*Где получить:* egov.kz → Лицензии и разрешения\n*Стоимость:* 10 МРП (≈ 40 000 тг)\n*Срок:* до 15 рабочих дней",
    
    "Что умеет этот бот?": "🤖 *Возможности БизГид:*\n\n📋 Налоговые режимы — сравнение всех режимов РК\n\n💰 ЕСП — информация о едином платеже для самозанятых\n\n🧮 Калькулятор — расчёт налогов по упрощёнке, патенту, рознице\n\n📅 Сроки сдачи — когда сдавать отчётность и платить\n\n📞 Контакты — телефоны и сайты госорганов\n\n✅ Чек-лист — пошаговое открытие ИП\n\n📄 Договоры — готовые шаблоны для скачивания\n\n❓ FAQ — ответы на частые вопросы",
    
    "Как закрыть ИП?": "🚪 *Закрытие ИП:*\n\n1. Сдать всю отчётность\n2. Оплатить все налоги и взносы\n3. Подать заявление на egov.kz\n4. Дождаться проверки (до 3 дней)\n\n⏱ Время: 3-5 дней\n💵 Стоимость: бесплатно\n\n⚠️ *Важно:* нельзя закрыть при наличии долгов по налогам"
}

# ==================== ШАБЛОНЫ ДОГОВОРОВ ====================

contracts_templates = {
    "аренда": {
        "name": "📝 Договор аренды помещения",
        "filename": "dogovor_arendy.txt",
        "content": """ДОГОВОР АРЕНДЫ НЕЖИЛОГО ПОМЕЩЕНИЯ

г. _________________ 			«___» _____________ 20__ г.

АРЕНДОДАТЕЛЬ: ____________________________________________
ИИН/БИН: _____________________, в лице _____________________
действующего на основании _________________________________

АРЕНДАТОР: _______________________________________________
ИИН/БИН: _____________________, в лице _____________________
действующего на основании _________________________________

заключили настоящий договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Арендодатель передаёт, а Арендатор принимает во временное владение и пользование нежилое помещение, расположенное по адресу:
_____________________________________________________________

1.2. Общая площадь помещения: ________ кв.м.

1.3. Цель использования: _____________________________________

1.4. Помещение принадлежит Арендодателю на праве собственности, что подтверждается: __________________________________________

2. СРОК АРЕНДЫ

2.1. Срок аренды: с «___» _________ 20__ г. по «___» _________ 20__ г.

2.2. Договор может быть продлён по соглашению сторон.

3. АРЕНДНАЯ ПЛАТА И ПОРЯДОК РАСЧЁТОВ

3.1. Арендная плата составляет: __________________ тенге в месяц.

3.2. Оплата производится ежемесячно не позднее _____ числа текущего месяца.

3.3. Способ оплаты: _________________________________________

3.4. Коммунальные услуги оплачиваются: ☐ Арендодателем ☐ Арендатором

4. ПРАВА И ОБЯЗАННОСТИ СТОРОН

4.1. Арендодатель обязуется:
— передать помещение в состоянии, пригодном для использования;
— не препятствовать Арендатору в пользовании помещением;
— производить капитальный ремонт.

4.2. Арендатор обязуется:
— использовать помещение по назначению;
— своевременно вносить арендную плату;
— содержать помещение в надлежащем состоянии;
— не производить перепланировку без согласия Арендодателя;
— вернуть помещение по окончании срока аренды.

5. ОТВЕТСТВЕННОСТЬ СТОРОН

5.1. За просрочку арендной платы — пеня 0,1% от суммы за каждый день просрочки.

5.2. Стороны несут ответственность в соответствии с законодательством РК.

6. РАСТОРЖЕНИЕ ДОГОВОРА

6.1. Договор может быть расторгнут по соглашению сторон.

6.2. Досрочное расторжение — с уведомлением за 30 дней.

7. РЕКВИЗИТЫ И ПОДПИСИ СТОРОН

АРЕНДОДАТЕЛЬ:				АРЕНДАТОР:
_____________________			_____________________
ИИН/БИН: _______________		ИИН/БИН: _______________
Адрес: __________________		Адрес: __________________
Банк: ___________________		Банк: ___________________
ИИК: ____________________		ИИК: ____________________
Тел: ____________________		Тел: ____________________

_______________ / ________		_______________ / ________
   (подпись)       (Ф.И.О.)		   (подпись)       (Ф.И.О.)

М.П.					М.П.
"""
    },
    
    "услуги": {
        "name": "🤝 Договор оказания услуг",
        "filename": "dogovor_uslugi.txt",
        "content": """ДОГОВОР ОКАЗАНИЯ УСЛУГ

г. _________________ 			«___» _____________ 20__ г.

ИСПОЛНИТЕЛЬ: _____________________________________________
ИИН/БИН: _____________________, в лице _____________________
действующего на основании _________________________________

ЗАКАЗЧИК: ________________________________________________
ИИН/БИН: _____________________, в лице _____________________
действующего на основании _________________________________

заключили настоящий договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Исполнитель обязуется оказать Заказчику следующие услуги:
_____________________________________________________________
_____________________________________________________________

1.2. Результат оказания услуг: ________________________________

2. СРОКИ ОКАЗАНИЯ УСЛУГ

2.1. Начало оказания услуг: «___» _____________ 20__ г.
2.2. Окончание оказания услуг: «___» _____________ 20__ г.

3. СТОИМОСТЬ УСЛУГ И ПОРЯДОК РАСЧЁТОВ

3.1. Стоимость услуг составляет: _________________ тенге.
     НДС: ☐ включён ☐ не облагается

3.2. Порядок оплаты:
☐ 100% предоплата
☐ 50% предоплата, 50% по завершении
☐ 100% по завершении
☐ Другое: _______________________________________________

3.3. Оплата производится в течение ___ банковских дней с момента ____________________________________________

4. ПРАВА И ОБЯЗАННОСТИ СТОРОН

4.1. Исполнитель обязуется:
— оказать услуги качественно и в срок;
— соблюдать требования Заказчика;
— информировать о ходе выполнения.

4.2. Заказчик обязуется:
— предоставить необходимую информацию;
— своевременно оплатить услуги;
— принять оказанные услуги.

5. ПОРЯДОК СДАЧИ-ПРИЁМКИ УСЛУГ

5.1. По завершении Исполнитель предоставляет Акт выполненных работ.

5.2. Заказчик в течение ___ рабочих дней подписывает Акт или направляет мотивированный отказ.

5.3. При отсутствии замечаний в указанный срок услуги считаются принятыми.

6. ОТВЕТСТВЕННОСТЬ СТОРОН

6.1. За нарушение сроков оказания услуг — пеня 0,1% от стоимости за каждый день просрочки.

6.2. За нарушение сроков оплаты — пеня 0,1% от суммы за каждый день просрочки.

7. ФОРС-МАЖОР

7.1. Стороны освобождаются от ответственности при наступлении обстоятельств непреодолимой силы.

8. СРОК ДЕЙСТВИЯ ДОГОВОРА

8.1. Договор вступает в силу с момента подписания и действует до полного исполнения обязательств.

9. РЕКВИЗИТЫ И ПОДПИСИ СТОРОН

ИСПОЛНИТЕЛЬ:				ЗАКАЗЧИК:
_____________________			_____________________
ИИН/БИН: _______________		ИИН/БИН: _______________
Адрес: __________________		Адрес: __________________
Банк: ___________________		Банк: ___________________
ИИК: ____________________		ИИК: ____________________
Тел: ____________________		Тел: ____________________

_______________ / ________		_______________ / ________
   (подпись)       (Ф.И.О.)		   (подпись)       (Ф.И.О.)

М.П.					М.П.
"""
    },
    
    "трудовой": {
        "name": "💼 Трудовой договор",
        "filename": "trudovoy_dogovor.txt",
        "content": """ТРУДОВОЙ ДОГОВОР

г. _________________ 			«___» _____________ 20__ г.

РАБОТОДАТЕЛЬ: ____________________________________________
БИН: ________________________, в лице _______________________
действующего на основании _________________________________

РАБОТНИК: ________________________________________________
ИИН: ________________________
Удостоверение личности: № ____________ выдано _______________

заключили настоящий трудовой договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Работодатель принимает Работника на должность:
_____________________________________________________________

1.2. Место работы: ___________________________________________

1.3. Вид договора:
☐ На неопределённый срок
☐ На определённый срок до «___» _____________ 20__ г.
   Причина срочности: ________________________________________

1.4. Дата начала работы: «___» _____________ 20__ г.

1.5. Испытательный срок: ☐ Нет ☐ Да, _______ месяца(ев)

2. РЕЖИМ РАБОТЫ И ОТДЫХА

2.1. Режим работы:
☐ Пятидневная рабочая неделя (40 часов)
☐ Сменный график
☐ Гибкий график
☐ Другое: _______________________________________________

2.2. Время работы: с ___:___ до ___:___
     Перерыв: с ___:___ до ___:___

2.3. Выходные дни: __________________________________________

2.4. Ежегодный оплачиваемый отпуск: 24 календарных дня.

3. ОПЛАТА ТРУДА

3.1. Должностной оклад: __________________ тенге в месяц.

3.2. Надбавки/премии: _______________________________________

3.3. Заработная плата выплачивается:
— аванс: _____ числа каждого месяца
— расчёт: _____ числа каждого месяца

3.4. Способ выплаты: ☐ На карту ☐ Наличными

4. ПРАВА И ОБЯЗАННОСТИ РАБОТНИКА

4.1. Работник обязуется:
— добросовестно выполнять должностные обязанности;
— соблюдать трудовую дисциплину;
— соблюдать правила внутреннего распорядка;
— бережно относиться к имуществу Работодателя;
— соблюдать требования охраны труда.

4.2. Работник имеет право на:
— своевременную оплату труда;
— отдых и ежегодный отпуск;
— безопасные условия труда;
— социальное обеспечение.

5. ПРАВА И ОБЯЗАННОСТИ РАБОТОДАТЕЛЯ

5.1. Работодатель обязуется:
— обеспечить работой согласно договору;
— своевременно выплачивать заработную плату;
— обеспечить безопасные условия труда;
— осуществлять обязательные отчисления (ОПВ, СО, ВОСМС).

5.2. Работодатель имеет право:
— требовать выполнения обязанностей;
— привлекать к дисциплинарной ответственности;
— поощрять за успехи в работе.

6. СОЦИАЛЬНОЕ ОБЕСПЕЧЕНИЕ

6.1. Работодатель осуществляет:
— ОПВ (10% от зарплаты)
— СО (3,5% от зарплаты)
— ВОСМС (3% от зарплаты)
— ОППВ (1,5% от зарплаты) — за счёт работодателя

7. РАСТОРЖЕНИЕ ДОГОВОРА

7.1. Договор может быть расторгнут:
— по соглашению сторон;
— по инициативе Работника (уведомление за 1 месяц);
— по инициативе Работодателя (по основаниям ТК РК).

8. РЕКВИЗИТЫ И ПОДПИСИ СТОРОН

РАБОТОДАТЕЛЬ:				РАБОТНИК:
_____________________			_____________________
БИН: ___________________		ИИН: ___________________
Адрес: __________________		Адрес: __________________
Банк: ___________________		Банк: ___________________
ИИК: ____________________		ИИК: ____________________
Тел: ____________________		Тел: ____________________

_______________ / ________		_______________ / ________
   (подпись)       (Ф.И.О.)		   (подпись)       (Ф.И.О.)

М.П.

Экземпляр трудового договора получил(а): _____________ / __________
                                          (подпись)     (дата)
"""
    },
    
    "поставка": {
        "name": "📦 Договор поставки",
        "filename": "dogovor_postavki.txt",
        "content": """ДОГОВОР ПОСТАВКИ ТОВАРОВ

г. _________________ 			«___» _____________ 20__ г.

ПОСТАВЩИК: _______________________________________________
ИИН/БИН: _____________________, в лице _____________________
действующего на основании _________________________________

ПОКУПАТЕЛЬ: ______________________________________________
ИИН/БИН: _____________________, в лице _____________________
действующего на основании _________________________________

заключили настоящий договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА

1.1. Поставщик обязуется передать, а Покупатель принять и оплатить товар:

№ | Наименование | Ед.изм. | Кол-во | Цена (тг) | Сумма (тг)
--|--------------|---------|--------|-----------|----------
1 |              |         |        |           |
2 |              |         |        |           |
3 |              |         |        |           |

1.2. Общая сумма договора: __________________ тенге.
     НДС: ☐ включён (12%) ☐ не облагается

1.3. Качество товара должно соответствовать: _________________

2. СРОКИ И ПОРЯДОК ПОСТАВКИ

2.1. Срок поставки: до «___» _____________ 20__ г.

2.2. Место поставки: _________________________________________

2.3. Способ доставки:
☐ Самовывоз Покупателем
☐ Доставка Поставщиком (включена в стоимость)
☐ Доставка Поставщиком (за счёт Покупателя)

2.4. Переход права собственности: с момента подписания накладной.

3. ПОРЯДОК РАСЧЁТОВ

3.1. Порядок оплаты:
☐ 100% предоплата
☐ 50% предоплата, 50% при получении
☐ 100% при получении
☐ Отсрочка _____ дней
☐ Другое: _______________________________________________

3.2. Оплата производится в течение ___ банковских дней путём перечисления на расчётный счёт Поставщика.

4. ПРИЁМКА ТОВАРА

4.1. Приёмка товара по количеству — в момент получения.

4.2. Приёмка товара по качеству — в течение ___ дней с момента получения.

4.3. При обнаружении недостатков Покупатель составляет акт и уведомляет Поставщика в течение ___ дней.

5. ГАРАНТИИ

5.1. Гарантийный срок на товар: _______ месяцев с момента передачи.

5.2. Гарантия не распространяется на повреждения по вине Покупателя.

6. ОТВЕТСТВЕННОСТЬ СТОРОН

6.1. За нарушение сроков поставки — пеня 0,1% от стоимости за каждый день просрочки.

6.2. За нарушение сроков оплаты — пеня 0,1% от суммы за каждый день просрочки.

6.3. За поставку некачественного товара — замена или возврат средств.

7. ФОРС-МАЖОР

7.1. Стороны освобождаются от ответственности при наступлении обстоятельств непреодолимой силы.

8. СРОК ДЕЙСТВИЯ ДОГОВОРА

8.1. Договор вступает в силу с момента подписания и действует до полного исполнения обязательств.

9. РЕКВИЗИТЫ И ПОДПИСИ СТОРОН

ПОСТАВЩИК:				ПОКУПАТЕЛЬ:
_____________________			_____________________
ИИН/БИН: _______________		ИИН/БИН: _______________
Адрес: __________________		Адрес: __________________
Банк: ___________________		Банк: ___________________
ИИК: ____________________		ИИК: ____________________
Тел: ____________________		Тел: ____________________

_______________ / ________		_______________ / ________
   (подпись)       (Ф.И.О.)		   (подпись)       (Ф.И.О.)

М.П.					М.П.
"""
    }
}

# Временное хранилище для калькулятора
user_calc_data = {}

# ==================== МЕНЮ ====================

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📋 Налоговые режимы"),
        types.KeyboardButton("💰 Единый совокупный платёж"),
        types.KeyboardButton("🧮 Калькулятор налогов"),
        types.KeyboardButton("📅 Сроки сдачи отчётности"),
        types.KeyboardButton("📞 Контакты госорганов"),
        types.KeyboardButton("✅ Чек-лист открытия ИП"),
        types.KeyboardButton("❓ Частые вопросы"),
        types.KeyboardButton("📄 Шаблоны договоров")
        types.KeyboardButton("🏠 В главное меню")
    )
    return markup

# ==================== ОБРАБОТЧИКИ ====================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я *БизГид* — твой помощник по налогам и бизнесу в Казахстане.\n\n"
        "Выбери раздел:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🏠 В главное меню")
def go_home(message):
    bot.send_message(
        message.chat.id,
        "🏠 *Главное меню*\n\nВыбери раздел:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# --- НАЛОГОВЫЕ РЕЖИМЫ ---
@bot.message_handler(func=lambda m: m.text == "📋 Налоговые режимы")
def show_tax_regimes(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for regime in tax_regimes.keys():
        markup.add(types.InlineKeyboardButton(regime, callback_data=f"regime_{regime}"))
    
    bot.send_message(
        message.chat.id,
        "📋 *Налоговые режимы РК*\n\nВыбери режим для подробной информации:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("regime_"))
def show_regime_details(call):
    regime_name = call.data.replace("regime_", "")
    regime = tax_regimes.get(regime_name)
    
    if regime:
        text = f"📌 *{regime_name}*\n\n"
        for key, value in regime.items():
            text += f"*{key}:* {value}\n\n"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
    
    bot.answer_callback_query(call.id)

# --- ЕСП ---
@bot.message_handler(func=lambda m: m.text == "💰 Единый совокупный платёж")
def show_esp(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📊 Ставки ЕСП", callback_data="esp_rates"),
        types.InlineKeyboardButton("📋 Что входит в ЕСП", callback_data="esp_covers"),
        types.InlineKeyboardButton("❓ Кому подходит", callback_data="esp_who")
    )
    
    bot.send_message(
        message.chat.id,
        "💰 *Единый совокупный платёж (ЕСП)*\n\n"
        "Простой способ платить налоги для самозанятых.\n\n"
        "Выбери раздел:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("esp_"))
def handle_esp(call):
    if call.data == "esp_rates":
        text = "📊 *Ставки ЕСП (2024)*\n\n"
        text += f"1 МРП = {esp_data['categories']['🏠 За себя (город)']['mci']} тг\n\n"
        for cat, data in esp_data['categories'].items():
            text += f"{cat}\n└ {data['amount']} тг/мес ({data['rate']} МРП)\n\n"
    
    elif call.data == "esp_covers":
        text = "📋 *Что входит в ЕСП:*\n\n"
        for item in esp_data['covers']:
            text += f"{item}\n"
        text += "\n💡 Один платёж — и все взносы уплачены!"
    
    elif call.data == "esp_who":
        text = "❓ *Кому подходит ЕСП:*\n\n"
        text += "✅ Репетиторы\n"
        text += "✅ Няни, сиделки\n"
        text += "✅ Домработницы\n"
        text += "✅ Мастера маникюра (на дому)\n"
        text += "✅ Фрилансеры (услуги физлицам)\n"
        text += "✅ Кондитеры (на дому)\n\n"
        text += "❌ *Не подходит:* торговля, услуги юрлицам"
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

# --- КАЛЬКУЛЯТОР ---
@bot.message_handler(func=lambda m: m.text == "🧮 Калькулятор налогов")
def calculator_start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📊 ФНО 910 (Упрощёнка)", callback_data="calc_910"),
        types.InlineKeyboardButton("💳 Патент", callback_data="calc_patent"),
        types.InlineKeyboardButton("🛒 Розничный налог", callback_data="calc_retail")
    )
    
    bot.send_message(
        message.chat.id,
        "🧮 *Калькулятор налогов*\n\n"
        "Выбери налоговый режим:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("calc_"))
def calculator_select(call):
    calc_type = call.data.replace("calc_", "")
    user_calc_data[call.message.chat.id] = {"type": calc_type}
    
    if calc_type == "910":
        text = "📊 *Калькулятор ФНО 910*\n\n"
        text += "Введи сумму дохода за *полугодие* (в тенге):\n\n"
        text += "_Пример: 1000000_"
    elif calc_type == "patent":
        text = "💳 *Калькулятор Патента*\n\n"
        text += "Введи планируемый доход за *период патента* (в тенге):\n\n"
        text += "_Пример: 500000_"
    elif calc_type == "retail":
        text = "🛒 *Калькулятор Розничного налога*\n\n"
        text += "Введи сумму дохода за *квартал* (в тенге):\n\n"
        text += "_Пример: 5000000_"
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.chat.id in user_calc_data)
def calculate_tax(message):
    try:
        amount = int(message.text.replace(" ", "").replace(",", ""))
        calc_type = user_calc_data[message.chat.id]["type"]
        
        if calc_type == "910":
            tax = amount * 0.03
            ipn = amount * 0.015
            social = amount * 0.015
            text = f"📊 *Расчёт ФНО 910*\n\n"
            text += f"💵 Доход: {amount:,} тг\n\n"
            text += f"📍 ИПН (1.5%): {ipn:,.0f} тг\n"
            text += f"📍 Соц. налог (1.5%): {social:,.0f} тг\n"
            text += f"━━━━━━━━━━━━━━━\n"
            text += f"💰 *Итого налог: {tax:,.0f} тг*"
        
        elif calc_type == "patent":
            tax = amount * 0.01
            text = f"💳 *Расчёт Патента*\n\n"
            text += f"💵 Доход: {amount:,} тг\n\n"
            text += f"📍 Налог (1%): {tax:,.0f} тг\n"
            text += f"━━━━━━━━━━━━━━━\n"
            text += f"💰 *Итого к оплате: {tax:,.0f} тг*"
        
        elif calc_type == "retail":
            tax = amount * 0.03
            text = f"🛒 *Расчёт Розничного налога*\n\n"
            text += f"💵 Доход: {amount:,} тг\n\n"
            text += f"📍 Налог (3%): {tax:,.0f} тг\n"
            text += f"━━━━━━━━━━━━━━━\n"
            text += f"💰 *Итого к оплате: {tax:,.0f} тг*"
        
        del user_calc_data[message.chat.id]
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число без букв и символов\n\n_Пример: 1000000_", parse_mode="Markdown")

# --- СРОКИ СДАЧИ ---
@bot.message_handler(func=lambda m: m.text == "📅 Сроки сдачи отчётности")
def show_deadlines(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for deadline in deadlines_data.keys():
        markup.add(types.InlineKeyboardButton(deadline, callback_data=f"deadline_{deadline}"))
    
    bot.send_message(
        message.chat.id,
        "📅 *Сроки сдачи отчётности*\n\nВыбери налоговый режим:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("deadline_"))
def show_deadline_details(call):
    deadline_name = call.data.replace("deadline_", "")
    deadline = deadlines_data.get(deadline_name)
    
    if deadline:
        text = f"📅 *{deadline_name}*\n\n"
        text += f"📆 Период: {deadline['period']}\n\n"
        text += "*Сроки сдачи:*\n"
        for d in deadline['deadlines']:
            text += f"{d}\n"
        text += f"\n💳 {deadline['payment']}"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
    
    bot.answer_callback_query(call.id)

# --- КОНТАКТЫ ---
@bot.message_handler(func=lambda m: m.text == "📞 Контакты госорганов")
def show_contacts(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for org in contacts_data.keys():
        markup.add(types.InlineKeyboardButton(org, callback_data=f"contact_{org}"))
    
    bot.send_message(
        message.chat.id,
        "📞 *Контакты госорганов*\n\nВыбери организацию:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("contact_"))
def show_contact_details(call):
    org_name = call.data.replace("contact_", "")
    org = contacts_data.get(org_name)
    
    if org:
        text = f"*{org_name}*\n\n"
        text += f"{org['phone']}\n"
        text += f"{org['website']}\n"
        text += f"{org['cabinet']}\n\n"
        text += f"📝 _{org['description']}_"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("« Назад", callback_data="contacts_back"))
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "contacts_back")
def contacts_back(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for org in contacts_data.keys():
        markup.add(types.InlineKeyboardButton(org, callback_data=f"contact_{org}"))
    
    bot.edit_message_text(
        "📞 *Контакты госорганов*\n\nВыбери организацию:",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# --- ЧЕК-ЛИСТ ---
@bot.message_handler(func=lambda m: m.text == "✅ Чек-лист открытия ИП")
def show_checklist(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, item in enumerate(checklist_ip):
        markup.add(types.InlineKeyboardButton(item['step'], callback_data=f"check_{i}"))
    
    bot.send_message(
        message.chat.id,
        "✅ *Чек-лист открытия ИП*\n\n"
        "5 простых шагов для старта бизнеса.\n"
        "Нажми на шаг для подробностей:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def show_checklist_item(call):
    idx = int(call.data.replace("check_", ""))
    item = checklist_ip[idx]
    
    text = f"*{item['step']}*\n\n"
    text += f"📝 {item['description']}\n\n"
    text += f"📍 *Где:* {item['where']}\n"
    text += f"💵 *Стоимость:* {item['cost']}\n"
    text += f"⏱ *Время:* {item['time']}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("« Назад к списку", callback_data="checklist_back"))
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "checklist_back")
def checklist_back(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, item in enumerate(checklist_ip):
        markup.add(types.InlineKeyboardButton(item['step'], callback_data=f"check_{i}"))
    
    bot.edit_message_text(
        "✅ *Чек-лист открытия ИП*\n\n"
        "5 простых шагов для старта бизнеса.\n"
        "Нажми на шаг для подробностей:",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# --- ЧАСТЫЕ ВОПРОСЫ ---
@bot.message_handler(func=lambda m: m.text == "❓ Частые вопросы")
def show_faq(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, question in enumerate(faq_data.keys()):
        markup.add(types.InlineKeyboardButton(question, callback_data=f"faq_{i}"))
    
    bot.send_message(
        message.chat.id,
        "❓ *Частые вопросы*\n\nВыбери вопрос:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("faq_"))
def show_faq_answer(call):
    idx = int(call.data.replace("faq_", ""))
    questions = list(faq_data.keys())
    answers = list(faq_data.values())
    
    if idx < len(questions):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("« Назад к вопросам", callback_data="faq_back"))
        
        bot.edit_message_text(
            f"*{questions[idx]}*\n\n{answers[idx]}",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "faq_back")
def faq_back(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, question in enumerate(faq_data.keys()):
        markup.add(types.InlineKeyboardButton(question, callback_data=f"faq_{i}"))
    
    bot.edit_message_text(
        "❓ *Частые вопросы*\n\nВыбери вопрос:",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

# --- ШАБЛОНЫ ДОГОВОРОВ ---
@bot.message_handler(func=lambda m: m.text == "📄 Шаблоны договоров")
def show_contracts(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🏠 Договор аренды", callback_data="contract_аренда"),
        types.InlineKeyboardButton("🤝 Договор оказания услуг", callback_data="contract_услуги"),
        types.InlineKeyboardButton("💼 Трудовой договор", callback_data="contract_трудовой"),
        types.InlineKeyboardButton("📦 Договор поставки", callback_data="contract_поставка")
    )
    
    bot.send_message(
        message.chat.id,
        "📄 *Шаблоны договоров*\n\n"
        "Готовые шаблоны по законодательству РК.\n"
        "Выбери тип договора для скачивания:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("contract_"))
def send_contract(call):
    contract_type = call.data.replace("contract_", "")
    contract = contracts_templates.get(contract_type)
    
    if contract:
        # Отправляем файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(contract['content'])
            temp_path = f.name
        
        with open(temp_path, 'rb') as doc:
            bot.send_document(
                call.message.chat.id,
                doc,
                visible_file_name=contract['filename'],
                caption=f"📄 *{contract['name']}*\n\n✅ Шаблон по законодательству РК\n📝 Заполни пустые поля и распечатай",
                parse_mode="Markdown"
            )
        
        os.unlink(temp_path)
    
    bot.answer_callback_query(call.id, "📄 Отправляю шаблон...")

# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    print("Бот запущен!")
    bot.polling(none_stop=True)
