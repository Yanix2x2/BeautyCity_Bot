from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from telegram_bot.utils.reply_or_edit import reply_or_edit


def get_slot_confirm_handler():
    return [
        CallbackQueryHandler(request_phone_number, pattern=r"^select_slot_"),
        MessageHandler(Filters.text & ~Filters.command, handle_phone_and_confirm),
        CallbackQueryHandler(confirm_registration, pattern="^confirm_registration$")
    ]


def request_phone_number(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    slot = query.data.replace("select_slot_", "")
    context.user_data["selected_slot"] = slot

    reply_or_edit(
        update,
        "Пожалуйста, введите свой номер телефона для подтверждения записи:"
    )


def handle_phone_and_confirm(update: Update, context: CallbackContext) -> None:
    phone = update.message.text
    context.user_data["phone_number"] = phone

    buttons = [[InlineKeyboardButton("Хочу записаться уже!", callback_data="confirm_registration")]]
    reply_markup = InlineKeyboardMarkup(buttons)

    update.message.reply_text(
        f"Вы указали номер: {phone}\nВсе верно?",
        reply_markup=reply_markup
    )


def confirm_registration(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    slot = context.user_data.get("selected_slot")
    phone = context.user_data.get("phone_number")

    if not slot:
        reply_or_edit(update, "Время не выбрано.")
        print("[DEBUG] Не удалось найти выбранный слот.")
        return

    if not phone:
        reply_or_edit(update, "Номер телефона не указан.")
        print("[DEBUG] Не удалось найти номер телефона.")
        return

    print(f"[DEBUG] Подтверждение записи — слот: {slot}, телефон: {phone}")

    # Здесь можно создать запись в модели Registration

    reply_or_edit(
        update,
        "Запись подтверждена! \nСкоро мы свяжемся с вами для уточнения деталей.",
    )
