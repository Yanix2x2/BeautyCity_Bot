from telegram.ext import CallbackContext, MessageHandler, Filters
from telegram_bot.utils.master_flow import show_salon_selection


def get_booking_entry_handler():
    return MessageHandler(Filters.text("🗓 Записаться"), show_salon_selection)
