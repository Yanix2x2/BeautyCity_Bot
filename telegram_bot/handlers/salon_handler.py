from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext
from beauty_city.bot.models import Salon


def handle_address_request(update: Update, context: CallbackContext) -> None:
    salons = Salon.objects.all()
    if salons.exists():
        message = "\n\n".join(
            f"🏢 {salon.name}\n📍 {salon.address}" for salon in salons
        )
    else:
        message = "Список салонов пока пуст."

    update.message.reply_text(message)


def get_salon_handler() -> MessageHandler:
    return MessageHandler(Filters.text("📍 Адреса салонов"), handle_address_request)
