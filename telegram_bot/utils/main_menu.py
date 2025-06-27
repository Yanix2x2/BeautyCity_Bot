from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot.keyboards import get_main_keyboard


def send_main_menu(update: Update, context: CallbackContext, text: str = "Вы в главном меню.") -> None:
    if update.callback_query:
        update.callback_query.message.reply_text(
            text,
            reply_markup=get_main_keyboard()
        )
    else:
        update.message.reply_text(
            text,
            reply_markup=get_main_keyboard()
        )
