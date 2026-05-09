from aiogram import Router, F, types
from aiogram.filters import Command
from sqlalchemy import select, func
from database.models import User # Твоя модель из БД

router = Router()

@router.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_panel(message: types.Message):
    async with async_session() as session:
        # Считаем количество юзеров в БД
        count = await session.execute(select(func.count(User.id)))
        total_users = count.scalar()
        
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="📊 Выгрузить БД", callback_data="admin_export_db")]
    ])
    await message.answer(f"👑 **Админ-панель**\n\nВсего пользователей в БД: `{total_users}`", 
                         reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data == "admin_broadcast", F.from_user.id == ADMIN_ID)
async def start_broadcast(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите текст для рассылки всем пользователям:")
    await state.set_state("waiting_for_broadcast_text")