from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram_bot.handlers.booking.salon_select_handler import show_salon_selection
from telegram_bot.handlers.booking.service_select_handler import show_service_selection


def get_back_handlers():
    return [
        CallbackQueryHandler(handle_back_action, pattern=r"^back_to_"),
    ]


def handle_back_action(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == "back_to_salons":
        show_salon_selection(update, context)
    elif query.data == "back_to_services":
        show_service_selection(update, context)
