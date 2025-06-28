from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, MessageHandler, Filters
from bot.models import Salon
from telegram_bot.utils.reply_or_edit import reply_or_edit


def get_salon_handler():
    return MessageHandler(Filters.text("📍 Адреса салонов"), show_salon_addresses)


def show_salon_addresses(update: Update, context: CallbackContext) -> None:
    """Показывает список салонов с кликабельными кнопками для записи."""

    context.user_data["flow"] = "by_salon"
    
    salons = Salon.objects.all()

    if salons.exists():
        buttons = [
            [InlineKeyboardButton(f"📍 {salon.address}", callback_data=f"select_salon_{salon.id}")]
            for salon in salons
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        text = "Выберите салон для записи:"
        reply_or_edit(update, text, reply_markup=reply_markup)
    else:
        update.message.reply_text("Пока что салоны не добавлены")
