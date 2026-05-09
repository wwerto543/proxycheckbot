from aiogram.fsm.state import StatesGroup, State

class ProxyFilter(StatesGroup):
    confirm_sub = State()        # Ожидание подписки
    choosing_filter = State()    # Выбор типа фильтрации
    picking_country = State()    # Выбор конкретной страны