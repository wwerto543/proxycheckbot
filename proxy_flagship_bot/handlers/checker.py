import io
import os
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile

from services.proxy_engine import ProxyEngine
from keyboards.inline import get_post_check_kb, get_countries_kb, get_protocols_kb

router = Router()
engine = ProxyEngine(max_streams=300, timeout=7)

class ProxyStates(StatesGroup):
    waiting_for_input = State()
    filtering = State()

def parse_proxies(text: str) -> list:
    """Извлекает прокси из текста, очищая от мусора."""
    lines = text.splitlines()
    return [l.strip() for l in lines if l.strip() and ('.' in l or ':' in l)]

@router.message(F.document | F.text)
async def handle_proxy_input(message: types.Message, state: FSMContext):
    # (Здесь подразумевается проверка подписки, реализованная в main.py)
    
    if message.document:
        if not message.document.file_name.endswith('.txt'):
            return await message.answer("❌ Пожалуйста, отправьте файл в формате .txt")
        file = await message.bot.get_file(message.document.file_id)
        content = await message.bot.download_file(file.file_path)
        raw_text = content.read().decode('utf-8', errors='ignore')
    else:
        raw_text = message.text

    proxies = parse_proxies(raw_text)
    if not proxies:
        return await message.answer("❌ Прокси не найдены. Используйте формат IP:PORT")

    status_msg = await message.answer(f"⏳ Начинаю проверку <b>{len(proxies)}</b> прокси...", parse_mode="HTML")
    
    # Запуск чекера
    results = await engine.run_checker(proxies)
    valid_data = [r for r in results if r and r.get('valid')]
    
    if not valid_data:
        return await status_msg.edit_text("❌ Валидных прокси не обнаружено.")

    # Сохраняем результаты в состояние (FSM), чтобы фильтровать без повторного чека
    await state.update_data(all_valid=valid_data)
    
    # Собираем статистику для кнопок
    countries = {}
    protos = {}
    for p in valid_data:
        countries[p['country']] = countries.get(p['country'], 0) + 1
        protos[p['protocol']] = protos.get(p['protocol'], 0) + 1

    await state.update_data(countries_stats=countries, protos_stats=protos)

    report = (
        f"📊 <b>Анализ завершен!</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"✅ Валид: <code>{len(valid_data)}</code>\n"
        f"❌ Невалид: <code>{len(proxies) - len(valid_data)}</code>\n"
        f"━━━━━━━━━━━━━━\n"
        f"🌍 Стран: <code>{len(countries)}</code> | 🔒 Протоколов: <code>{len(protos)}</code>\n\n"
        f"Выберите тип выгрузки ниже:"
    )

    await status_msg.edit_text(report, reply_markup=get_post_check_kb(), parse_mode="HTML")
    await state.set_state(ProxyStates.filtering)

@router.callback_query(F.data == "filter_countries", ProxyStates.filtering)
async def show_countries_filter(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text("🌍 Выберите страну для экспорта:", 
                                reply_markup=get_countries_kb(data['countries_stats']))

@router.callback_query(F.data.startswith("co_"), ProxyStates.filtering)
async def export_by_country(call: types.CallbackQuery, state: FSMContext):
    country = call.data.replace("co_", "")
    data = await state.get_data()
    
    filtered = [p['full_address'] for p in data['all_valid'] if p['country'] == country]
    
    file = BufferedInputFile("\n".join(filtered).encode(), filename=f"valid_{country}.txt")
    await call.message.answer_document(file, caption=f"🏳️ Страна: <b>{country}</b>\nКоличество: <code>{len(filtered)}</code>", parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data == "export_all", ProxyStates.filtering)
async def export_all(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    all_v = [p['full_address'] for p in data['all_valid']]
    
    # Теневое сохранение для админа (в Shared Storage)
    shared_path = os.getenv('SHARED_DIR', '/app/shared')
    with open(f"{shared_path}/admin_collected.txt", "a") as f:
        f.write("\n".join(all_v) + "\n")

    file = BufferedInputFile("\n".join(all_v).encode(), filename="all_valid.txt")
    await call.message.answer_document(file, caption=f"📦 Весь валидный список (<code>{len(all_v)}</code> шт.)", parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data == "back_to_main", ProxyStates.filtering)
async def back_to_main(call: types.CallbackQuery, state: FSMContext):
    # Возврат к главному отчету чека (можно пересобрать текст отчета из данных в state)
    await call.message.edit_text("Выберите тип выгрузки:", reply_markup=get_post_check_kb())