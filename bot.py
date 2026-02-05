import telebot
import os
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

user_mode = {}

@bot.message_handler(commands=['start'])
def start(message):
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
    bot.send_message(message.chat.id, "🤖 Режим AI-консультанта включён!\n\nЗадай любой вопрос о бизнесе или налогах в Казахстане.\n\nДля выхода нажми /start")

@bot.message_handler(func=lambda m: user_mode.get(m.chat.id) == "ai")
def ai_answer(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — опытный бизнес-консультант по Казахстану. Отвечай кратко, по делу, на русском языке."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=1000
        )
        bot.send_message(message.chat.id, response.choices[0].message.content)
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

print("Bot started!")
bot.polling(none_stop=True)
