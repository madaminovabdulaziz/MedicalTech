from aiogram.dispatcher.filters.state import State, StatesGroup


class Main(StatesGroup):
    main_menu = State()