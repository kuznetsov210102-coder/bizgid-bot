import telebot
import requests
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
user_mode = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_mode[message.chat.id] = None
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "💼 Налоговые режимы", "💰 Единый совокупный платеж",
        "🧮 Калькулятор налогов", "📅 Сроки сдачи отчётности",
        "📞 Контакты госорганов", "✅ Чек-лист открытия ИП",
        "❓ Частые вопросы", "📄 Шаблоны договоров",
        "🤖 AI-консультант"
    ]
    markup.add(*[telebot.types.KeyboardButton(b) for b in buttons])
    bot.send_message(message.chat.id, "👋 Привет! Я БизГид — твой помощник по налогам и бизнесу в Казахстане.\n\nВыбери раздел:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🤖 AI-консультант")
def ai_mode(message):
    user_mode[message.chat.id] = "ai"
    # Отладка - показать есть ли ключ
    key_status = "✅ Ключ найден" if GROQ_API_KEY else "❌ Ключ НЕ найден"
    bot.send_message(message.chat.id, f"🤖 AI-консультант включён!\n\n{key_status}\n\nЗадай вопрос или /start для выхода")

@bot.message_handler(func=lambda m: user_mode.get(m.chat.id) == "ai")
def ai_answer(message):
    if not GROQ_API_KEY:
        bot.send_message(message.chat.id, "❌ GROQ_API_KEY не найден в переменных окружения!")
        return
        
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "Ты — опытный бизнес-консультант по Казахстану. Отвечай кратко, по делу, на русском языке."},
                    {"role": "user", "content": message.text}
                ],
                "max_tokens": 1000
            }
        )
        result = response.json()
        
        if "choices" in result:
            answer = result["choices"][0]["message"]["content"]
            bot.send_message(message.chat.id, answer)
        else:
            bot.send_message(message.chat.id, f"Ошибка: {result}")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    responses = {
        "💼 Налоговые режимы": "📊 Налоговые режимы в Казахстане:\n\n1️⃣ Общеустановленный режим\n2️⃣ Упрощённая декларация\n3️⃣ Патент\n4️⃣ Единый совокупный платёж (ЕСП)",
        "💰 Единый совокупный платеж": "💰 ЕСП — это упрощённый режим для микробизнеса.\n\nСтавка: 1 МРП в месяц.",
        "📞 Контакты госорганов": "📞 Полезные контакты:\n\n• Комитет госдоходов: 1414\n• eGov: egov.kz\n• Первичная регистрация ИП: psu.gov.kz"
    }
    if message.text in responses:
        bot.send_message(message.chat.id, responses[message.text])
    else:
        bot.send_message(message.chat.id, "Выбери раздел из меню 👇")

print(f"Bot starting... GROQ_API_KEY exists: {bool(GROQ_API_KEY)}")
bot.polling(none_stop=True)
