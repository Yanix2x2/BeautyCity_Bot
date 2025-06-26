from telegram.ext import Dispatcher
from telegram_bot.handlers.start_handler import get_start_handler
from telegram_bot.handlers.salon_handler import get_salon_handler
from telegram_bot.handlers.booking.booking_entry_handler import get_booking_entry_handler
from telegram_bot.handlers.booking.salon_select_handler import get_salon_select_handlers
from telegram_bot.handlers.booking.service_select_handler import get_service_select_handlers
from telegram_bot.handlers.booking.date_select_handler import get_date_select_handlers
from telegram_bot.handlers.booking.select_master_handler import get_master_select_handlers
from telegram_bot.handlers.booking.slot_select_handler import get_slot_select_handlers
from telegram_bot.handlers.booking.back_handler import get_back_handlers
from telegram_bot.handlers.master_direct_handler import get_master_direct_handlers
from telegram_bot.handlers.booking.slot_confirm_handler import get_slot_confirm_handler
from telegram_bot.handlers.admin_call_handler import get_help_call_handler


def register_handlers(dp: Dispatcher) -> None:
    dp.add_handler(get_start_handler())
    dp.add_handler(get_salon_handler())
    dp.add_handler(get_booking_entry_handler())
    dp.add_handler(get_help_call_handler())

    for handler in (
        *get_salon_select_handlers(),
        *get_service_select_handlers(),
        *get_date_select_handlers(),
        *get_master_select_handlers(),
        *get_slot_select_handlers(),
        *get_back_handlers(),
        *get_master_direct_handlers(),
        *get_slot_confirm_handler(),
    ):
        dp.add_handler(handler)

    # Здесь буду добавлять хендлеры
