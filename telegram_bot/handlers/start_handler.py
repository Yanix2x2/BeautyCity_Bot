from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from pathlib import Path
from telegram_bot.keyboards import get_main_keyboard


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
        "Перед началом работы, пожалуйста, ознакомьтесь с документом об обработке персональных данных:"
    )
    send_personal_agreement(update)

    agreement_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Согласен", callback_data="agree_personal_data"),
            InlineKeyboardButton("Не согласен", callback_data="decline_personal_data")
        ]
    ])

    update.message.reply_text(
        "Когда ознакомитесь, нажмите кнопку ниже 👇",
        reply_markup=agreement_keyboard
    )


def agree_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    query.edit_message_text(
        "Спасибо! Теперь вы можете записаться или выбрать мастера!"
    )

    query.message.reply_text(
        "Чем могу помочь?",
        reply_markup=get_main_keyboard()
    )


def decline_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    query.edit_message_text(
        "Чтобы пользоваться ботом, необходимо согласиться на обработку персональных данных.\n\n"
        "Если вы передумали — просто введите /start ещё раз."
    )


def get_start_handler() -> list:
    return [
        CommandHandler("start", start),
        CallbackQueryHandler(agree_callback, pattern="^agree_personal_data$"),
        CallbackQueryHandler(decline_callback, pattern="^decline_personal_data$"),
    ]
