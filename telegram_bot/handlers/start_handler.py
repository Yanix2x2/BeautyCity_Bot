from telegram import Update
from telegram.ext import CommandHandler, CallbackContext


def start(update: Update, context: CallbackContext) -> None:
    user_first_name = update.effective_user.first_name
    update.message.reply_text(
        f"Привет, {user_first_name}!\n"
        "Я бот сети салонов BeautyCity.\n\n"
        "Готов записать тебя на процедуру!"
        "Выбери удобный для тебя салон"
    )


def get_start_handler() -> CommandHandler:
    return CommandHandler("start", start)