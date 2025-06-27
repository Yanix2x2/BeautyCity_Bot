from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot.utils.reply_or_edit import reply_or_edit


def check_required_fields(update: Update, context: CallbackContext, required_keys: list) -> bool:
    missing = [key for key in required_keys if key not in context.user_data]
    if missing:
        reply_or_edit(update, f"Ошибка: не хватает данных: {', '.join(missing)}")
        return False
    return True
