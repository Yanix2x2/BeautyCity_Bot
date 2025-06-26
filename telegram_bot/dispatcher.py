from telegram.ext import Dispatcher
from telegram_bot.handlers.start_handler import get_start_handler
from telegram_bot.handlers.salon_handler import get_salon_handler
from telegram_bot.handlers.booking_handler import get_booking_handlers


def register_handlers(dp: Dispatcher) -> None:
    dp.add_handler(get_start_handler())
    dp.add_handler(get_salon_handler())

    for handler in get_booking_handlers():
        dp.add_handler(handler)

    # Здесь буду добавлять хендлеры
