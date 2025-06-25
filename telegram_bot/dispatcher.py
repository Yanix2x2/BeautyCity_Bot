from telegram.ext import Dispatcher
from handlers.start_handler import get_start_handler
from handlers.salon_handler import get_salon_handler


def register_handlers(dp: Dispatcher) -> None:
    dp.add_handler(get_start_handler())
    dp.add_handler(get_salon_handler())

    # Здесь буду добавлять хендлеры
