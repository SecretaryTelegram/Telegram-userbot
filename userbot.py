import os
import random
import json
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===============================
# Данные для подключения
# ===============================
API_ID = 21321325
API_HASH = "93e7c730ce8992e378b2225471f2f860"
SESSION_NAME = "afk_userbot"

# ===============================
# Файлы для хранения данных
# ===============================
DATA_FILE = "afk_messages.json"
LOG_FILE = "afk_log.txt"

# ===============================
# Настройки автоответа
# ===============================
AFK_MODE = False
AFK_MESSAGES = []   # список AFK-сообщений пользователя
AFK_PERSONAL = {}
AFK_ONLY_LS = False
AFK_CHATS = []
AFK_ONE_REPLY = True
AFK_RANDOM = True
AFK_START_TIME = None
ANTI_FLOOD = {}

# ===============================
# Работа с файлами
# ===============================
def load_afk_messages():
    global AFK_MESSAGES
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            AFK_MESSAGES = json.load(f)
    else:
        # Стартовый набор "богатых" ответов
        AFK_MESSAGES = [
            "В данный момент недоступен. Ваше сообщение будет учтено.",
            "Сейчас я занят важными делами. Отвечу, как только появится возможность.",
            "Ваше сообщение ценно для меня. Вернусь и отвечу при первой возможности.",
            "Сейчас нахожусь вне доступа. Благодарю за понимание."
        ]
        save_afk_messages()

def save_afk_messages():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(AFK_MESSAGES, f, ensure_ascii=False, indent=2)

# ===============================
# Создаем клиент Pyrogram
# ===============================
app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH
)

# ===============================
# Вспомогательные функции
# ===============================
def can_reply(user_id):
    if AFK_ONE_REPLY and user_id in ANTI_FLOOD:
        return False
    ANTI_FLOOD[user_id] = True
    return True

def get_afk_text(user_id=None):
    if user_id in AFK_PERSONAL:
        return AFK_PERSONAL[user_id]
    if AFK_MESSAGES:
        if AFK_RANDOM:
            return random.choice(AFK_MESSAGES)
        else:
            return AFK_MESSAGES[0]
    return "Сейчас недоступен."

# ===============================
# Команды управления AFK
# ===============================
@app.on_message(filters.command(["afk"], prefixes="/") & filters.me)
async def go_afk(client, message):
    global AFK_MODE, AFK_START_TIME, ANTI_FLOOD
    AFK_MODE = True
    AFK_START_TIME = datetime.now()
    ANTI_FLOOD.clear()
    await message.edit("✅ Режим AFK активирован.")

@app.on_message(filters.command(["back"], prefixes="/") & filters.me)
async def back_from_afk(client, message):
    global AFK_MODE, AFK_START_TIME, ANTI_FLOOD
    AFK_MODE = False
    AFK_START_TIME = None
    ANTI_FLOOD.clear()
    await message.edit("✅ Режим AFK отключён.")

# ===============================
# Управление шаблонами AFK
# ===============================
@app.on_message(filters.command(["addafk"], prefixes="/") & filters.me)
async def add_afk_message(client, message):
    global AFK_MESSAGES
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.edit("⚠️ Укажи текст для добавления.")
        return
    AFK_MESSAGES.append(text[1])
    save_afk_messages()
    await message.edit(f"✅ Добавлен новый AFK-вариант:\n{text[1]}")

@app.on_message(filters.command(["listafk"], prefixes="/") & filters.me)
async def list_afk_messages(client, message):
    if not AFK_MESSAGES:
        await message.edit("⚠️ Список AFK пуст.")
        return
    text = "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(AFK_MESSAGES)])
    await message.edit("📜 Сохранённые AFK-варианты:\n\n" + text)

@app.on_message(filters.command(["delafk"], prefixes="/") & filters.me)
async def delete_afk_message(client, message):
    global AFK_MESSAGES
    args = message.text.split(maxsplit=1)
    if len(args) == 1:
        await message.edit("⚠️ Укажи номер варианта для удаления или 'all'.")
        return
    if args[1].lower() == "all":
        AFK_MESSAGES.clear()
        save_afk_messages()
        await message.edit("🗑 Все AFK-варианты удалены.")
    else:
        try:
            idx = int(args[1]) - 1
            removed = AFK_MESSAGES.pop(idx)
            save_afk_messages()
            await message.edit(f"🗑 Удалён вариант: {removed}")
        except:
            await message.edit("⚠️ Неверный номер варианта.")

# ===============================
# Основной обработчик входящих
# ===============================
@app.on_message(filters.private | filters.group)
async def afk_reply(client, message):
    global AFK_MODE
    if not AFK_MODE:
        return
    if AFK_ONLY_LS and message.chat.type != "private":
        return
    if AFK_CHATS and message.chat.id not in AFK_CHATS:
        return
    if not can_reply(message.from_user.id if message.from_user else 0):
        return

    afk_text = get_afk_text(message.from_user.id if message.from_user else None)

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Оставить сообщение", url="https://t.me/")]]
    )

    try:
        await message.reply(afk_text, reply_markup=buttons)
    except:
        pass

# ===============================
# Ответ на упоминания
# ===============================
@app.on_message(filters.mentioned & filters.group)
async def mention_reply(client, message):
    global AFK_MODE
    if not AFK_MODE:
        return
    if not can_reply(message.from_user.id if message.from_user else 0):
        return
    reply_text = get_afk_text(message.from_user.id if message.from_user else None)
    try:
        await message.reply(reply_text)
    except:
        pass

# ===============================
# Запуск юзербота
# ===============================
if __name__ == "__main__":
    load_afk_messages()
    print("✅ Юзербот запущен и слушает входящие сообщения...")
    app.run()
