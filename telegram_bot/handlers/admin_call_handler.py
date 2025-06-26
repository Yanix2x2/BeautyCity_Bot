from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, Filters
from telegram_bot.utils.reply_or_edit import reply_or_edit


def get_help_call_handler():
    return MessageHandler(Filters.text("💬 Связаться с администратором"), show_admin_contact)


def show_admin_contact(update: Update, context: CallbackContext) -> None:
    phone = "+7 (999)-999-99-99"
    reply_or_edit(
        update,
        f"Вы можете позвонить администратору по номеру:\n📞 {phone}"
    )
