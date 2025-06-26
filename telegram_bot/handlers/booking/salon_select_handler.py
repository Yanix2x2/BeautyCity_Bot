from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from bot.models import Salon
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.handlers.booking.service_select_handler import show_service_selection


def get_salon_select_handlers():
    return [
        MessageHandler(Filters.text("🗓 Записаться"), show_salon_selection),
        CallbackQueryHandler(save_selected_salon, pattern=r"^select_salon_"),
    ]


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


def save_selected_salon(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    salon_id = query.data.replace("select_salon_", "")
    context.user_data["selected_salon_id"] = salon_id

    show_service_selection(update, context)
