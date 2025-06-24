from telegram import Update, InputFile
from telegram.ext import CommandHandler, CallbackContext
from pathlib import Path
from keyboards import get_main_keyboard


def send_personal_agreement(update: Update) -> None:
    doc_directory = Path(__file__).resolve().parent.parent / "documents" / "pd_agreement.pdf"
    if doc_directory.exists():
        with open(doc_directory, "rb") as pdf_file:
            update.message.reply_document(document=InputFile(pdf_file, filename="pd_agreement.pdf"))
    else:
        update.message.reply_text("Документ не найден. Обратитесь к администратору.")


def start(update: Update, context: CallbackContext) -> None:
    user_first_name = update.effective_user.first_name

    update.message.reply_text(
        f"Привет, {user_first_name}!\n"
        "Я бот сети салонов BeautyCity\n\n"
        "Перед началом работы, пожалуйста, ознакомься с документом об обработке персональных данных:"
    )

    send_personal_agreement(update)
    update.message.reply_text(
        "Когда будешь готов, выбери нужный пункт ниже 👇",
        reply_markup=get_main_keyboard()
    )


def get_start_handler() -> CommandHandler:
    return CommandHandler("start", start)
