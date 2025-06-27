from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram_bot.handlers.booking.salon_select_handler import show_salon_selection
from telegram_bot.handlers.booking.service_select_handler import show_service_selection
from telegram_bot.handlers.booking.select_master_handler import show_master_selection
from telegram_bot.handlers.booking.date_select_handler import show_date_selection
from telegram_bot.handlers.booking.slot_select_handler import show_slot_selection


def get_back_handlers():
    return [
        CallbackQueryHandler(handle_back_action, pattern=r"^back_to_"),
    ]


def handle_back_action(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == "back_to_salons":
        show_salon_selection(update, context)
        return

    elif query.data == "back_to_services":
        show_service_selection(update, context)
        return

    elif query.data == "back_to_masters":
        show_master_selection(update, context)
        return

    elif query.data == "back_to_dates":
        action_prefix = context.user_data.get("date_action_prefix", "slot")
        show_date_selection(update, context, action_prefix)
        return

    elif query.data == "back_to_slots":
        show_slot_selection(update, context)
        return

    else:
        query.edit_message_text("Неверное действие возврата.")
