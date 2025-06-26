from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, MessageHandler, Filters
from bot.models import Salon
from telegram_bot.utils.reply_or_edit import reply_or_edit


def get_booking_entry_handler():
    return MessageHandler(Filters.text("🗓 Записаться"), show_salon_selection)


def show_salon_selection(update: Update, context: CallbackContext) -> None:
    salons = Salon.objects.all()
    if not salons.exists():
        reply_or_edit(update, "Нет доступных салонов для записи.")
        return

    buttons = [
        [InlineKeyboardButton(text=salon.address, callback_data=f"select_salon_{salon.id}")]
        for salon in salons
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите салон для записи:", reply_markup=reply_markup)
