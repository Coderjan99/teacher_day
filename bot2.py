import asyncio
import sqlite3
import shutil
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.types import ReplyKeyboardRemove
from datetime import datetime
from openpyxl import Workbook



TOKEN = "8477592546:AAHjx4B1KYOFgB0DkfLKdHQG0rQhoiOrLxk"
CHANNEL_1_ID = -1002058967454
CHANNEL_2_ID = -1002365066379
CHANNEL_USERNAME = "@maktab_317_matbuot_xizmati"   # masalan @maktab_ovoz
CHANNEL_USERNAME ="@programms_we"
ADMINS = [5306366307]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== DATABASE =====

conn = sqlite3.connect("votes.db",check_same_thread=False,timeout=30)
cursor = conn.cursor()
cursor.execute("PRAGMA journal_mode=WAL;")
cursor.execute("PRAGMA synchronous=NORMAL;")

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    votes INTEGER DEFAULT 0
)
""")


conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    username TEXT,
    full_name TEXT,
    candidate_id INTEGER,
    candidate_name TEXT,
    voted_at TEXT
)
""")
conn.commit()



# ===== NOMZODLAR =====
candidates = [
    "Sadinova Xolida Normamatovna",
    "Qodirov Elbek Husenovich",
    "Azimova Dono Abdukarimovna",
    "Norqobilova Marjona Rauf qizi",
    "Yuldasheva Nasiba Ilhomovna",
    "Boymatova Surayyo Isomiddin qizi",
    "Rabbimova Umida Ismatullayevna",
    "Nazarov Akbar Javliyevich",
    "Ravshanova Nilufar Bahodirovna",
    

]

for name in candidates:
    cursor.execute("INSERT OR IGNORE INTO candidates(name) VALUES(?)", (name,))
conn.commit()

# ===== /start =====
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📢 1-KANAL",
                url="https://t.me/maktab_317_matbuot_xizmati",
            )
        ],
          [
            InlineKeyboardButton(
                text="📢 2-KANAL",
                url="https://t.me/programms_we",
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ A’zo bo‘ldim",
                callback_data="check_sub"
            )
        ]
    ])

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "🗳 Ovoz berish uchun kanallarga a’zo bo‘lishingiz kerak.\n\n"
        "👇 Avval kanalga kiring, so‘ng «A’zo bo‘ldim» tugmasini bosing.",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    try:
        member1 = await bot.get_chat_member(CHANNEL_1_ID, user_id)
        member2 = await bot.get_chat_member(CHANNEL_2_ID, user_id)

        if member1.status not in ("member", "administrator", "creator") \
           or member2.status not in ("member", "administrator", "creator"):

            await callback.answer(
                "❌ Siz hali ikkala kanalga ham a’zo bo‘lmagansiz!",
                show_alert=True
            )
            return

    except:
        await callback.answer(
            "❌ A’zolikni tekshirib bo‘lmadi.\nIltimos, ikkala kanalga ham a’zo bo‘ling.",
            show_alert=True
        )
        return

    # ✅ IKKALA KANALGA HAM A’ZO
    contact_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="📞 Telefon raqamni yuborish",
                request_contact=True
            )]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await callback.message.answer(
        "✅ A’zolik tasdiqlandi!\n\n📲 Telefon raqamingizni yuboring:",
        reply_markup=contact_kb
    )

    await callback.answer()



# ===== CONTACT QABUL =====
@dp.message(lambda m: m.contact)
async def get_contact(message: types.Message):
    await message.answer(
        "✅ Rahmat!\n\n🗳 Endi ovoz berishingiz mumkin",
       reply_markup=ReplyKeyboardRemove()
    )
    await send_vote_buttons(message.chat.id)

# ===== OVOZ TUGMALARI =====
async def send_vote_buttons(chat_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    cursor.execute("SELECT id, name, votes FROM candidates")
    for cid, name, votes in cursor.fetchall():
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{name} — {votes}",
                callback_data=f"vote_{cid}"
            )
        ])

    await bot.send_message(
        chat_id,
        "👇 Nomzodni tanlang:",
        reply_markup=keyboard
    )

# ===== OVOZ BERISH =====
@dp.callback_query(lambda c: c.data.startswith("vote_"))
async def vote(callback: types.CallbackQuery):
    user = callback.from_user
    user_id = user.id
    cid = int(callback.data.split("_")[1])

    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone():
        await callback.answer("❌ Siz allaqachon ovoz bergansiz", show_alert=True)
        return

    cursor.execute("SELECT name FROM candidates WHERE id=?", (cid,))
    candidate_name = cursor.fetchone()[0]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("BEGIN IMMEDIATE")

    cursor.execute("INSERT INTO users(user_id) VALUES(?)", (user_id,))
    cursor.execute("""
        INSERT INTO votes (
            user_id, username, full_name,
            candidate_id, candidate_name, voted_at
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        user.username,
        f"{user.first_name or ''} {user.last_name or ''}",
        cid,
        candidate_name,
        now
    ))

    cursor.execute("UPDATE candidates SET votes = votes + 1 WHERE id=?", (cid,))
    conn.commit()

    # natijani qayta chiqarish (sizdagi kod qoladi)




    # Yangilangan tugmalarni qayta yaratamiz
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    cursor.execute("SELECT id, name, votes FROM candidates")
    for cid, name, votes in cursor.fetchall():
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{name} — {votes}",
                callback_data="voted"  # endi bosilmaydi
            )
        ])
    await callback.answer("✅ Ovoz qabul qilindi", show_alert=True)
    await callback.message.edit_text( "🎉 Rahmat! Ovozingiz qabul qilindi.\n\n📊 Joriy holat:",reply_markup=keyboard)

# ===== /publish (KANALGA) =====
@dp.message(Command("publish"))
async def publish(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    cursor.execute("SELECT id, name, votes FROM candidates")
    for cid, name, votes in cursor.fetchall():
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{name} — {votes}",
                callback_data=f"vote_{cid}"
            )
        ])

    await bot.send_message(
        CHANNEL_1_ID,
        CHANNEL_2_ID,
        "📊 <b>Ovoz berish boshlandi!</b>\n👇 Nomzodni tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# ===== /results =====
@dp.message(Command("results"))
async def results(message: types.Message):
    text = "📊 Natijalar:\n\n"
    cursor.execute("SELECT name, votes FROM candidates ORDER BY votes DESC")
    for name, votes in cursor.fetchall():
        text += f"{name} — {votes}\n"
    await message.answer(text)

@dp.message(Command("export"))
async def export_votes(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Votes"

    ws.append([
        "User ID",
        "Username",
        "Full Name",
        "Candidate",
        "Voted At"
    ])

    cursor.execute("""
        SELECT user_id, username, full_name, candidate_name, voted_at
        FROM votes
        ORDER BY voted_at
    """)

    for row in cursor.fetchall():
        ws.append(row)

    file_name = "votes.xlsx"
    wb.save(file_name)

    await message.answer_document(
        types.FSInputFile(file_name),
        caption="📊 Ovozlar Excel formatda"
    )



# ===== RUN =====
async def auto_backup():
    import shutil
    while True:
        await asyncio.sleep(600)  # 10 daqiqa
        shutil.copy("votes.db", "backup_votes.db")

async def main():
    asyncio.create_task(auto_backup())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
