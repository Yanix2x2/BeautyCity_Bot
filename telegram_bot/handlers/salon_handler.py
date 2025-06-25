from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters
from bot.models import Salon


def get_salon_handler():
    return MessageHandler(Filters.text("📍 Адреса салонов"), show_salon_addresses)


def show_salon_addresses(update: Update, context: CallbackContext) -> None:
    salons = Salon.objects.all()

    if salons.exists():
        addresses = "\n\n".join([f"📍 {salon.address}" for salon in salons])
        update.message.reply_text(f"Наши салоны:\n\n{addresses}")
    else:
        update.message.reply_text("Пока что салоны не добавлены")
