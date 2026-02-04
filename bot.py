import telebot
from telebot import types
import os

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

# Частые вопросы
faq_data = {
    "Как открыть ИП?": "Для открытия ИП нужно:\n1. Зарегистрироваться на egov.kz\n2. Получить ЭЦП\n3. Подать заявление онлайн\n4. Выбрать налоговый режим\n\n⏱ Время: 1 день\n💵 Стоимость: бесплатно",
    "Какой режим выбрать?": "📊 *Рекомендации:*\n\n• Доход до 3 528 МРП/год → *Патент*\n• Доход до 24 038 МРП/полугодие → *Упрощёнка (910)*\n• Розничная торговля → *Розничный налог*\n• Услуги физлицам на дому → *ЕСП*",
    "Когда платить налоги?": "📅 *Сроки уплаты:*\n\n• Упрощёнка (910) — до 25 числа после отчёта\n• Патент — до получения патента\n• Розничный налог — до 25 числа после квартала\n• ЕСП — ежемесячно до 25 числа",
    "Нужна ли касса?": "🧾 *ККМ обязателен если:*\n\n• Работаете с наличными\n• Розничная торговля\n• Общепит\n\n*Не нужен:* при безналичных расчётах B2B, ЕСП"
}

# Шаблоны договоров
contracts_data = {
    "📝 Договор оказания услуг": "Шаблон договора на оказание услуг между ИП и заказчиком",
    "🤝 Договор подряда": "Шаблон договора подряда на выполнение работ",
    "🏠 Договор аренды": "Шаблон договора аренды помещения для бизнеса",
    "💼 Трудовой договор": "Шаблон трудового договора с работником"
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
    for question in faq_data.keys():
        markup.add(types.InlineKeyboardButton(question, callback_data=f"faq_{question[:20]}"))
    
    bot.send_message(
        message.chat.id,
        "❓ *Частые вопросы*\n\nВыбери вопрос:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("faq_"))
def show_faq_answer(call):
    faq_key = call.data.replace("faq_", "")
    for question, answer in faq_data.items():
        if question.startswith(faq_key):
            bot.edit_message_text(
                f"*{question}*\n\n{answer}",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )
            break
    bot.answer_callback_query(call.id)

# --- ШАБЛОНЫ ДОГОВОРОВ ---
@bot.message_handler(func=lambda m: m.text == "📄 Шаблоны договоров")
def show_contracts(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for contract in contracts_data.keys():
        markup.add(types.InlineKeyboardButton(contract, callback_data=f"contract_{contract[:15]}"))
    
    bot.send_message(
        message.chat.id,
        "📄 *Шаблоны договоров*\n\nВыбери тип договора:\n\n_Скоро здесь будут готовые шаблоны для скачивания_",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("contract_"))
def show_contract_info(call):
    contract_key = call.data.replace("contract_", "")
    for name, desc in contracts_data.items():
        if name.startswith(contract_key):
            bot.edit_message_text(
                f"*{name}*\n\n{desc}\n\n🔜 _Шаблон будет доступен в ближайшее время_",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )
            break
    bot.answer_callback_query(call.id)

# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    print("Бот запущен!")
    bot.polling(none_stop=True)
