import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import select, update

# Импорт твоих модулей
from database.models import init_db, async_session, User
from keyboards.inline import get_sub_keyboard
from handlers import checker

# --- ГИБКИЙ КОНФИГ ЧЕРЕЗ ENV ---
# Эти переменные ты задаешь в панели управления хостингом
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@IPhone_Canada")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/IPhone_Canada")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Подключаем логику чекера
dp.include_router(checker.router)

async def check_subscription(user_id: int) -> bool:
    """Проверка подписки через API Telegram."""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        return False

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    async with async_session() as session:
        # Регистрация пользователя в БД (Shared Storage)
        res = await session.execute(select(User).where(User.user_id == message.from_user.id))
        user = res.scalar_one_or_none()

        if not user:
            user = User(user_id=message.from_user.id, username=message.from_user.username)
            session.add(user)
            await session.commit()

    if await check_subscription(message.from_user.id):
        welcome_text = (
            f"🚀 <b>Доступ открыт!</b>\n\n"
            f"Вы авторизованы. Пришлите список прокси (текст или .txt файл)."
        )
        await message.answer(welcome_text, parse_mode="HTML")
    else:
        await message.answer(
            "⚠️ <b>Доступ ограничен!</b>\nПодпишитесь на канал для активации бота.",
            reply_markup=get_sub_keyboard(CHANNEL_URL),
            parse_mode="HTML"
        )

@dp.callback_query(F.data == "check_sub")
async def callback_check_sub(call: types.CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.edit_text("✅ <b>Доступ активирован!</b> Присылайте прокси.", parse_mode="HTML")
    else:
        await call.answer("❌ Вы всё еще не подписаны!", show_alert=True)

# Хендлер для админ-панели
@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_main(message: types.Message):
    await message.answer("👑 Добро пожаловать в админ-панель!")

async def main():
    # Инициализация БД в SHARED_DIR
    await init_db()
    
    logging.basicConfig(level=logging.INFO)
    print(f"--- БОТ ЗАПУЩЕН | ADMIN: {ADMIN_ID} ---")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())