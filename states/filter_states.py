from aiogram.fsm.state import StatesGroup, State

class ProxyFilterState(StatesGroup):
    waiting_for_filter_choice = State() # Выбор: Страны / Протоколы / Все
    waiting_for_country = State()       # Юзер выбирает конкретную страну
    waiting_for_protocol = State()      # Юзер выбирает SOCKS/HTTP
    waiting_for_amount = State()        # Юзер вводит количество (или "Все")