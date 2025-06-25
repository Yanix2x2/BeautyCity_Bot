from telegram.ext import Dispatcher
from handlers.start_handler import get_start_handler


def register_handlers(dp: Dispatcher) -> None:
    dp.add_handler(get_start_handler())

    # Здесь буду добавлять хендлеры
