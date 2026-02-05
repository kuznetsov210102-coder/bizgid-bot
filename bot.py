cat > bot.py << 'EOF'
import telebot
from telebot import types
import os
import tempfile
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN", "8553508437:AAEwuLlhelaNjVqqtmxUwLsxkbHn3PAioPI")
bot = telebot.TeleBot(BOT_TOKEN)

# OpenAI клиент
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# Частые вопросы
faq_data = {
    "Как открыть ИП?": "Для открытия ИП нужно:\n1. Зарегистрироваться на egov.kz\n2. Получить ЭЦП\n3. Подать заявление онлайн\n4. Выбрать налоговый режим\n\n⏱ Время: 1 день\n💵 Стоимость: бесплатно",
    "Какой режим выбрать?": "📊 *Рекомендации:*\n\n• Доход до 3 528 МРП/год → *Патент*\n• Доход до 24 038 МРП/полугодие → *Упрощёнка (910)*\n• Розничная торговля → *Розничный налог*\n• Услуги физлицам на дому → *ЕСП*",
    "Когда платить налоги?": "📅 *Сроки уплаты:*\n\n• Упрощёнка (910) — до 25 числа после отчёта\n• Патент — до получения патента\n• Розничный налог — до 25 числа после квартала\n• ЕСП — ежемесячно до 25 числа",
    "Нужна ли касса?": "🧾 *ККМ обязателен если:*\n\n• Работаете с наличными\n• Розничная торговля\n• Общепит\n\n*Не нужен:* при безналичных расчётах B2B, ЕСП",
    "Какие лицензии нужны?": "📜 *Лицензируемые виды деятельности:*\n\n• 🏥 Медицина и фармацевтика\n• 🎓 Образовательные услуги\n• 🚕 Пассажирские перевозки\n• 🏗 Строительство (1-3 категории)\n• 💰 Финансовые услуги\n• 🔒 Охранная деятельность\n• 🍺 Продажа алкоголя/табака\n\n*Где получить:* egov.kz → Лицензии и разрешения\n*Стоимость:* 10 МРП (≈ 40 000 тг)\n*Срок:* до 15 рабочих дней",
    "Что умеет этот бот?": "🤖 *Возможности БизГид:*\n\n📋 Налоговые режимы — сравнение всех режимов РК\n\n💰 ЕСП — информация о едином платеже\n\n🧮 Калькулятор — расчёт налогов\n\n📅 Сроки сдачи — когда сдавать отчётность\n\n📞 Контакты — телефоны госорганов\n\n✅ Чек-лист — пошаговое открытие ИП\n\n📄 Договоры — готовые шаблоны\n\n🤖 AI-консультант — ответы на любые вопросы",
    "Как закрыть ИП?": "🚪 *Закрытие ИП:*\n\n1. Сдать всю отчётность\n2. Оплатить все налоги и взносы\n3. Подать заявление на egov.kz\n4. Дождаться проверки (до 3 дней)\n\n⏱ Время: 3-5 дней\n💵 Стоимость: бесплатно\n\n⚠️ *Важно:* нельзя закрыть при наличии долгов по налогам"
}

# ==================== ШАБЛОНЫ ДОГОВОРОВ ====================

contracts_templates = {
    "аренда": {
        "name": "📝 Договор аренды помещения",
        "filename": "dogovor_arendy.txt",
        "content": """ДОГОВОР АРЕНДЫ НЕЖИЛОГО ПОМЕЩЕНИЯ

г. _________________ «___» _____________ 20__ г.

АРЕНДОДАТЕЛЬ: ____________________________________________
ИИН/БИН: _____________________

АРЕНДАТОР: _______________________________________________
ИИН/БИН: _____________________

1. ПРЕДМЕТ ДОГОВОРА
1.1. Арендодатель передаёт Арендатору нежилое помещение по адресу:
_____________________________________________________________
1.2. Площадь: ________ кв.м.
1.3. Цель использования: _____________________________________

2. СРОК АРЕНДЫ
2.1. С «___» _________ 20__ г. по «___» _________ 20__ г.

3. АРЕНДНАЯ ПЛАТА
3.1. Размер: __________________ тенге в месяц.
3.2. Оплата до _____ числа каждого месяца.

4. РЕКВИЗИТЫ И ПОДПИСИ

АРЕНДОДАТЕЛЬ: _______________    АРЕНДАТОР: _______________
"""
    },
    "услуги": {
        "name": "🤝 Договор оказания услуг",
        "filename": "dogovor_uslugi.txt",
        "content": """ДОГОВОР ОКАЗАНИЯ УСЛУГ

г. _________________ «___» _____________ 20__ г.

ИСПОЛНИТЕЛЬ: _____________________________________________
ИИН/БИН: _____________________

ЗАКАЗЧИК: ________________________________________________
ИИН/БИН: _____________________

1. ПРЕДМЕТ ДОГОВОРА
1.1. Исполнитель оказывает услуги:
_____________________________________________________________

2. СРОКИ
2.1. Начало: «___» _____________ 20__ г.
2.2. Окончание: «___» _____________ 20__ г.

3. СТОИМОСТЬ
3.1. Сумма: _________________ тенге.

4. РЕКВИЗИТЫ И ПОДПИСИ

ИСПОЛНИТЕЛЬ: _______________    ЗАКАЗЧИК: _______________
"""
    },
    "трудовой": {
        "name": "💼 Трудовой договор",
        "filename": "trudovoy_dogovor.txt",
        "content": """ТРУДОВОЙ ДОГОВОР

г. _________________ «___» _____________ 20__ г.

РАБОТОДАТЕЛЬ: ____________________________________________
БИН: ________________________

РАБОТНИК: ________________________________________________
ИИН: ________________________

1. ПРЕДМЕТ ДОГОВОРА
1.1. Должность: _____________________________________________
1.2. Место работы: ___________________________________________
1.3. Дата начала: «___» _____________ 20__ г.

2. ОПЛАТА ТРУДА
2.1. Оклад: __________________ тенге в месяц.

3. РЕЖИМ РАБОТЫ
3.1. Пятидневная рабочая неделя (40 часов)
3.2. Отпуск: 24 календарных дня

4. РЕКВИЗИТЫ И ПОДПИСИ

РАБОТОДАТЕЛЬ: _______________    РАБОТНИК: _______________
"""
    },
    "поставка": {
        "name": "📦 Договор поставки",
        "filename": "dogovor_postavki.txt",
        "content": """ДОГОВОР ПОСТАВКИ ТОВАРОВ

г. _________________ «___» _____________ 20__ г.

ПОСТАВЩИК: _______________________________________________
ИИН/БИН: _____________________

ПОКУПАТЕЛЬ: ______________________________________________
ИИН/БИН: _____________________

1. ПРЕДМЕТ ДОГОВОРА
1.1. Поставщик передаёт товар:
_____________________________________________________________

2. СРОКИ И ДОСТАВКА
2.1. Срок поставки: до «___» _____________ 20__ г.
2.2. Место: _________________________________________

3. СТОИМОСТЬ
3.1. Сумма: __________________ тенге.

4. РЕКВИЗИТЫ И ПОДПИСИ

ПОСТАВЩИК: _______________    ПОКУПАТЕЛЬ: _______________
"""
    }
}

# Хранилище данных пользователей
user_calc_data = {}
user_ai_mode = {}

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
        types.KeyboardButton("📄 Шаблоны договоров"),
        types.KeyboardButton("🤖 AI-консультант")
    )
    return markup

# ==================== ОБРАБОТЧИКИ ====================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ai_mode.pop(message.chat.id, None)
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я *БизГид* — твой помощник по налогам и бизнесу в Казахстане.\n\n"
        "Выбери раздел:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# --- AI-КОНСУЛЬТАНТ ---
@bot.message_handler(func=lambda m: m.text == "🤖 AI-консультант")
def ai_consultant(message):
    user_ai_mode[message.chat.id] = True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("◀️ Выйти из AI-режима"))
    
    bot.send_message(
        message.chat.id,
        "🤖 *AI-консультант*\n\n"
        "Задай любой вопрос о бизнесе в Казахстане:\n"
        "• Налоги и отчётность\n"
        "• Регистрация ИП/ТОО\n"
        "• Лицензии и разрешения\n"
        "• Трудовое право\n"
        "• И многое другое!\n\n"
        "✍️ Просто напиши свой вопрос:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == "◀️ Выйти из AI-режима")
def exit_ai_mode(message):
    user_ai_mode.pop(message.chat.id, None)
    bot.send_message(
        message.chat.id,
        "🏠 *Главное меню*\n\nВыбери раздел:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.chat.id in user_ai_mode and user_ai_mode.get(m.chat.id))
def process_ai_question(message):
    if message.text.startswith("◀️"):
        return
    
    wait_msg = bot.send_message(message.chat.id, "🤔 Думаю...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": """Ты — эксперт по бизнесу и налогам в Казахстане. 
Отвечай кратко, структурировано, на русском языке.
Используй актуальную информацию по законодательству РК.
Давай практичные советы с конкретными шагами.
Если не уверен — честно скажи об этом.
МРП в 2024 году = 3 946 тенге."""
                },
                {"role": "user", "content": message.text}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        bot.delete_message(message.chat.id, wait_msg.message_id)
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("◀️ Выйти из AI-режима"))
        
        bot.send_message(
            message.chat.id, 
            f"🤖 {answer}\n\n_Задай ещё вопрос или выйди из AI-режима_",
            parse_mode="Markdown",
            reply_markup=markup
        )
        
    except Exception as e:
        bot.delete_message(message.chat.id, wait_msg.message_id)
        bot.send_message(
            message.chat.id, 
            f"❌ Ошибка: {str(e)}\n\nПопробуй ещё раз или выйди из AI-режима.",
            reply_markup=main_menu()
        )
        user_ai_mode.pop(message.chat.id, None)

# --- НАЛОГОВЫЕ РЕЖИМЫ ---
@bot.message_handler(func=lambda m: m.text == "📋 Налоговые режимы")
def show_tax_regimes(message):
    user_ai_mode.pop(message.chat.id, None)
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
    user_ai_mode.pop(message.chat.id, None)
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
        text += "✅ Репетиторы\n✅ Няни, сиделки\n✅ Домработницы\n"
        text += "✅ Мастера маникюра (на дому)\n✅ Фрилансеры\n✅ Кондитеры (на дому)\n\n"
        text += "❌ *Не подходит:* торговля, услуги юрлицам"
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

# --- КАЛЬКУЛЯТОР ---
@bot.message_handler(func=lambda m: m.text == "🧮 Калькулятор налогов")
def calculator_start(message):
    user_ai_mode.pop(message.chat.id, None)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📊 ФНО 910 (Упрощёнка)", callback_data="calc_910"),
        types.InlineKeyboardButton("💳 Патент", callback_data="calc_patent"),
        types.InlineKeyboardButton("🛒 Розничный налог", callback_data="calc_retail")
    )
    
    bot.send_message(
        message.chat.id,
        "🧮 *Калькулятор налогов*\n\nВыбери налоговый режим:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("calc_"))
def calculator_select(call):
    calc_type = call.data.replace("calc_", "")
    user_calc_data[call.message.chat.id] = {"type": calc_type}
    
    texts = {
        "910": "📊 *Калькулятор ФНО 910*\n\nВведи сумму дохода за *полугодие* (в тенге):\n\n_Пример: 1000000_",
        "patent": "💳 *Калькулятор Патента*\n\nВведи планируемый доход за *период патента* (в тенге):\n\n_Пример: 500000_",
        "retail": "🛒 *Калькулятор Розничного налога*\n\nВведи сумму дохода за *квартал* (в тенге):\n\n_Пример: 5000000_"
    }
    
    bot.edit_message_text(texts[calc_type], call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.chat.id in user_calc_data and not user_ai_mode.get(m.chat.id))
def calculate_tax(message):
    try:
        amount = int(message.text.replace(" ", "").replace(",", ""))
        calc_type = user_calc_data[message.chat.id]["type"]
        
        if calc_type == "910":
            tax = amount * 0.03
            text = f"📊 *Расчёт ФНО 910*\n\n💵 Доход: {amount:,} тг\n\n"
            text += f"📍 ИПН (1.5%): {amount * 0.015:,.0f} тг\n📍 Соц. налог (1.5%): {amount * 0.015:,.0f} тг\n"
            text += f"━━━━━━━━━━━━━━━\n💰 *Итого налог: {tax:,.0f} тг*"
        elif calc_type == "patent":
            tax = amount * 0.01
            text = f"💳 *Расчёт Патента*\n\n💵 Доход: {amount:,} тг\n\n"
            text += f"📍 Налог (1%): {tax:,.0f} тг\n━━━━━━━━━━━━━━━\n💰 *Итого: {tax:,.0f} тг*"
        elif calc_type == "retail":
            tax = amount * 0.03
            text = f"🛒 *Расчёт Розничного налога*\n\n💵 Доход: {amount:,} тг\n\n"
            text += f"📍 Налог (3%): {tax:,.0f} тг\n━━━━━━━━━━━━━━━\n💰 *Итого: {tax:,.0f} тг*"
        
        del user_calc_data[message.chat.id]
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu())
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число без букв\n\n_Пример: 1000000_", parse_mode="Markdown")

# --- СРОКИ СДАЧИ ---
@bot.message_handler(func=lambda m: m.text == "📅 Сроки сдачи отчётности")
def show_deadlines(message):
    user_ai_mode.pop(message.chat.id, None)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for deadline in deadlines_data.keys():
        markup.add(types.InlineKeyboardButton(deadline, callback_data=f"deadline_{deadline}"))
    
    bot.send_message(message.chat.id, "📅 *Сроки сдачи отчётности*\n\nВыбери режим:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("deadline_"))
def show_deadline_details(call):
    deadline_name = call.data.replace("deadline_", "")
    deadline = deadlines_data.get(deadline_name)
    
    if deadline:
        text = f"📅 *{deadline_name}*\n\n📆 Период: {deadline['period']}\n\n*Сроки:*\n"
        for d in deadline['deadlines']:
            text += f"{d}\n"
        text += f"\n💳 {deadline['payment']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

# --- КОНТАКТЫ ---
@bot.message_handler(func=lambda m: m.text == "📞 Контакты госорганов")
def show_contacts(message):
    user_ai_mode.pop(message.chat.id, None)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for org in contacts_data.keys():
        markup.add(types.InlineKeyboardButton(org, callback_data=f"contact_{org}"))
    
    bot.send_message(message.chat.id, "📞 *Контакты госорганов*\n\nВыбери:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("contact_"))
def show_contact_details(call):
    org_name = call.data.replace("contact_", "")
    org = contacts_data.get(org_name)
    
    if org:
        text = f"*{org_name}*\n\n{org['phone']}\n{org['website']}\n{org['cabinet']}\n\n📝 _{org['description']}_"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("« Назад", callback_data="contacts_back"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "contacts_back")
def contacts_back(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for org in contacts_data.keys():
        markup.add(types.InlineKeyboardButton(org, callback_data=f"contact_{org}"))
    bot.edit_message_text("📞 *Контакты госорганов*\n\nВыбери:", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)

# --- ЧЕК-ЛИСТ ---
@bot.message_handler(func=lambda m: m.text == "✅ Чек-лист открытия ИП")
def show_checklist(message):
    user_ai_mode.pop(message.chat.id, None)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, item in enumerate(checklist_ip):
        markup.add(types.InlineKeyboardButton(item['step'], callback_data=f"check_{i}"))
    
    bot.send_message(message.chat.id, "✅ *Чек-лист открытия ИП*\n\n5 шагов для старта бизнеса:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def show_checklist_item(call):
    idx = int(call.data.replace("check_", ""))
    item = checklist_ip[idx]
    
    text = f"*{item['step']}*\n\n📝 {item['description']}\n\n"
    text += f"📍 *Где:* {item['where']}\n💵 *Стоимость:* {item['cost']}\n⏱ *Время:* {item['time']}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("« Назад", callback_data="checklist_back"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "checklist_back")
def checklist_back(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, item in enumerate(checklist_ip):
        markup.add(types.InlineKeyboardButton(item['step'], callback_data=f"check_{i}"))
    bot.edit_message_text("✅ *Чек-лист открытия ИП*\n\n5 шагов для старта бизнеса:", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)

# --- ЧАСТЫЕ ВОПРОСЫ ---
@bot.message_handler(func=lambda m: m.text == "❓ Частые вопросы")
def show_faq(message):
    user_ai_mode.pop(message.chat.id, None)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, question in enumerate(faq_data.keys()):
        markup.add(types.InlineKeyboardButton(question, callback_data=f"faq_{i}"))
    
    bot.send_message(message.chat.id, "❓ *Частые вопросы*\n\nВыбери:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("faq_"))
def show_faq_answer(call):
    idx = int(call.data.replace("faq_", ""))
    questions = list(faq_data.keys())
    answers = list(faq_data.values())
    
    if idx < len(questions):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("« Назад", callback_data="faq_back"))
        bot.edit_message_text(f"*{questions[idx]}*\n\n{answers[idx]}", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "faq_back")
def faq_back(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, question in enumerate(faq_data.keys()):
        markup.add(types.InlineKeyboardButton(question, callback_data=f"faq_{i}"))
    bot.edit_message_text("❓ *Частые вопросы*\n\nВыбери:", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
    bot.answer_callback_query(call.id)

# --- ШАБЛОНЫ ДОГОВОРОВ ---
@bot.message_handler(func=lambda m: m.text == "📄 Шаблоны договоров")
def show_contracts(message):
    user_ai_mode.pop(message.chat.id, None)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🏠 Договор аренды", callback_data="contract_аренда"),
        types.InlineKeyboardButton("🤝 Договор оказания услуг", callback_data="contract_услуги"),
        types.InlineKeyboardButton("💼 Трудовой договор", callback_data="contract_трудовой"),
        types.InlineKeyboardButton("📦 Договор поставки", callback_data="contract_поставка")
    )
    
    bot.send_message(message.chat.id, "📄 *Шаблоны договоров*\n\nВыбери тип:", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("contract_"))
def send_contract(call):
    contract_type = call.data.replace("contract_", "")
    contract = contracts_templates.get(contract_type)
    
    if contract:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(contract['content'])
            temp_path = f.name
        
        with open(temp_path, 'rb') as doc:
            bot.send_document(call.message.chat.id, doc, visible_file_name=contract['filename'],
                caption=f"📄 *{contract['name']}*\n\n✅ Шаблон по законодательству РК", parse_mode="Markdown")
        os.unlink(temp_path)
    
    bot.answer_callback_query(call.id, "📄 Отправляю...")

# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    print("Бот запущен!")
    bot.polling(none_stop=True)
EOF
