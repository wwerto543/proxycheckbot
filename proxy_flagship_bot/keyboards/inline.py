from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_sub_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    """Клавиатура для обязательной подписки."""
    kb = InlineKeyboardBuilder()
    kb.button(text="🛡 Перейти в канал", url=channel_url)
    kb.button(text="✅ Проверить подписку", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()

def get_post_check_kb() -> InlineKeyboardMarkup:
    """Главное меню фильтрации после завершения чека."""
    kb = InlineKeyboardBuilder()
    kb.button(text="🌍 Фильтр по странам", callback_data="filter_countries")
    kb.button(text="🔒 Фильтр по протоколам", callback_data="filter_protocols")
    kb.button(text="📦 Скачать всё (TXT)", callback_data="export_all")
    kb.button(text="🗑 Очистить", callback_data="clear_state")
    kb.adjust(1)
    return kb.as_markup()

def get_countries_kb(countries_dict: dict) -> InlineKeyboardMarkup:
    """Генерирует кнопки стран с указанием количества прокси для каждой."""
    kb = InlineKeyboardBuilder()
    # Сортируем по названию страны
    sorted_countries = sorted(countries_dict.items())
    
    for country, count in sorted_countries:
        # В callback_data передаем код страны для экономии лимита символов ТГ
        kb.button(text=f"{country} ({count})", callback_data=f"co_{country}")
    
    kb.button(text="🔙 Назад", callback_data="back_to_main")
    kb.adjust(2) # По 2 страны в ряд
    return kb.as_markup()

def get_protocols_kb(protocols_dict: dict) -> InlineKeyboardMarkup:
    """Генерирует кнопки для выбора протоколов (HTTP/SOCKS)."""
    kb = InlineKeyboardBuilder()
    for proto, count in protocols_dict.items():
        kb.button(text=f"⚡️ {proto.upper()} ({count})", callback_data=f"pr_{proto}")
    
    kb.button(text="🔙 Назад", callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()

def get_admin_kb() -> InlineKeyboardMarkup:
    """Клавиатура админ-панели."""
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Рассылка", callback_data="admin_broadcast")
    kb.button(text="📊 Статистика", callback_data="admin_stats")
    kb.button(text="📥 Выгрузить логи", callback_data="admin_get_logs")
    kb.adjust(1)
    return kb.as_markup()