import telebot
from openai import OpenAI
import os
from gtts import gTTS

# Инициализация клиента OpenAI с вашим API ключом
openai_api_key = "API_ключ"
openai = OpenAI(api_key=openai_api_key, base_url="https://api.proxyapi.ru/openai/v1")

TELEGRAM_TOKEN = 'токен_телеграм_бота'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Словарь для хранения историй бесед по каждому пользователю.
conversation_histories = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который может поддержать разговор на любую тему.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_input = message.text

    # Если история для пользователя не существует, создаем новую
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    # Добавление ввода пользователя в историю разговора
    conversation_history = conversation_histories[user_id]
    conversation_history.append({"role": "user", "content": user_input})

    # Отправка запроса в нейронную сеть
    chat_completion = openai.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=conversation_history
    )

    # Извлечение и ответ на сообщение пользователя
    ai_response_content = chat_completion.choices[0].message.content
    # Преобразование текстового ответа в аудио
    tts = gTTS(ai_response_content, lang='ru')
    temp_file = "temp_audio.mp3"
    tts.save(temp_file)

    # Отправляем аудио-сообщение пользователю
    with open(temp_file, 'rb') as audio:
        bot.send_voice(user_id, audio)

    # Добавление ответа нейронной сети в историю разговора
    conversation_history.append({"role": "system", "content": ai_response_content})

    # Удаляем временный файл
    os.remove(temp_file)

if __name__ == "main":
    bot.polling()