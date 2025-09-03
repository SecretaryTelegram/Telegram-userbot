import asyncio
import os
import random
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===============================
# Данные для подключения (твои данные)
# ===============================
API_ID = 21321325
API_HASH = "93e7c730ce8992e378b2225471f2f860"
SESSION_NAME = "afk_userbot"

# ===============================
# Настройки автоответа
# ===============================
AFK_MODE = False
AFK_MESSAGE = "Я сейчас не могу ответить, свяжусь позже."
AFK_MESSAGES = [
    "Сейчас занят, напишу позже.",
    "Не доступен, оставьте сообщение.",
    "Я оффлайн, отвечу позже."
]
AFK_PERSONAL = {}  # персональные автоответы {user_id: "текст"}
AFK_LOG = []  # лог всех автоответов
AFK_ONLY_LS = False  # отвечать только в ЛС
AFK_CHATS = []  # список ID чатов для автоответов
AFK_ONE_REPLY = True  # один ответ на пользователя
AFK_RANDOM = True  # использовать случайный текст
AFK_START_TIME = None
ANTI_FLOOD = {}  # чтобы не спамить одного пользователя

# ===============================
# Создаем клиент Pyrogram
# ===============================
app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH
)

# ===============================
# Команда включения/выключения AFK
# ===============================
@app.on_message(filters.command("afk") & filters.me)
async def go_afk(client, message):
    global AFK_MODE, AFK_START_TIME
    AFK_MODE = True
    AFK_START_TIME = datetime.now()
    await message.edit("✅ Режим AFK включен.")

@app.on_message(filters.command("back") & filters.me)
async def back_from_afk(client, message):
    global AFK_MODE, AFK_START_TIME
    AFK_MODE = False
    AFK_START_TIME = None
    await message.edit("✅ Режим AFK выключен.")
    # Можно лог сохранить в файл
    if AFK_LOG:
        with open("afk_log.txt", "a") as f:
            for log in AFK_LOG:
                f.write(f"{log}\n")
        AFK_LOG.clear()

# ===============================
# Функция получения текста AFK
# ===============================
def get_afk_text(user_id=None):
    if user_id in AFK_PERSONAL:
        return AFK_PERSONAL[user_id]
    if AFK_RANDOM:
        return random.choice(AFK_MESSAGES)
    return AFK_MESSAGE

# ===============================
# Функция, чтобы не спамить
# ===============================
def can_reply(user_id):
    if AFK_ONE_REPLY:
        if user_id in ANTI_FLOOD:
            return False
    ANTI_FLOOD[user_id] = True
    return True

# ===============================
# Основной обработчик входящих сообщений
# ===============================
@app.on_message(filters.private | filters.group)
async def afk_reply(client, message):
    global AFK_MODE, AFK_START_TIME

    if not AFK_MODE:
        return

    # ЛС только
    if AFK_ONLY_LS and message.chat.type != "private":
        return

    # Проверка выбранных чатов
    if AFK_CHATS and message.chat.id not in AFK_CHATS:
        return

    # Не спамим
    if not can_reply(message.from_user.id if message.from_user else None):
        return

    # Формируем сообщение с временем AFK
    afk_text = get_afk_text(message.from_user.id if message.from_user else None)
    if AFK_START_TIME:
        delta = datetime.now() - AFK_START_TIME
        afk_text += f"\n⏱ Оффлайн уже: {delta}"

    # Кнопки
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Оставить сообщение", url="https://t.me/")]]
    )

    # Отправка автоответа
    try:
        await message.reply(afk_text, reply_markup=buttons)
        AFK_LOG.append(f"{datetime.now()} - {message.from_user.first_name if message.from_user else 'Unknown'}: {message.text}")
    except:
        pass

# ===============================
# Запуск юзербота
# ===============================
print("✅ Юзербот запущен и слушает входящие сообщения...")
app.run()
