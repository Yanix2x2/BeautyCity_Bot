from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters
from bot.models import Salon


def get_salon_handler():
    return MessageHandler(Filters.text("📍 Адреса салонов"), show_salon_addresses)


def show_salon_addresses(update: Update, context: CallbackContext) -> None:
    salons = Salon.objects.all()

    if salons.exists():
        addresses = "\n\n".join([f"📍 {salon.address}" for salon in salons])
        text = (
            f"Наши салоны:\n\n{addresses}\n\n"  
            "💬 Чтобы записаться, нажмите «🗓 Записаться» ниже 👇"
        )
        update.message.reply_text(text)
    else:
        update.message.reply_text("Пока что салоны не добавлены")
