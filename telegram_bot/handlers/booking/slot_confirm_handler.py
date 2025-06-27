from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.master_flow import show_master_selection_after_slot
from telegram_bot.utils.calendar_tools import parse_date_from_str
from telegram_bot.utils.main_menu import send_main_menu
from telegram_bot.utils.validation import check_required_fields
from bot.models import Registration, Client, MasterSchedule


def get_slot_confirm_handler():
    return [
        CallbackQueryHandler(handle_slot_selected, pattern=r"^select_slot_"),
        MessageHandler(Filters.text & ~Filters.command, handle_phone_and_confirm),
        CallbackQueryHandler(confirm_registration, pattern="^confirm_registration$"),
        CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"),
    ]


def handle_slot_selected(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    slot = query.data.replace("select_slot_", "")
    context.user_data["selected_slot"] = slot
    show_master_selection_after_slot(update, context)


def request_phone_number(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if not context.user_data.get("selected_slot"):
        reply_or_edit(update, "Пожалуйста, выберите время записи.")
        return

    reply_or_edit(
        update,
        "Пожалуйста, введите свой номер телефона:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад", callback_data="back_to_masters")]
        ])
    )


def handle_phone_and_confirm(update: Update, context: CallbackContext) -> None:
    phone = update.message.text.strip()
    context.user_data["phone_number"] = phone
    update.message.reply_text(
        f"Вы указали номер: {phone}\nВсе верно?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Хочу записаться уже!", callback_data="confirm_registration")],
            [InlineKeyboardButton("Отменить запись", callback_data="cancel_registration")]
        ])
    )


def cancel_registration(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    context.user_data.clear()
    reply_or_edit(update, "Запись отменена. Вы в главном меню.")
    send_main_menu(update, context)


def confirm_registration(update: Update, context: CallbackContext) -> None:
    print("[DEBUG] confirm_registration user_data:", context.user_data)

    query = update.callback_query
    query.answer()
    user_data = context.user_data
    tg_user = update.effective_user

    if not check_required_fields(update, context, [
        "selected_slot", "selected_date", "selected_service_id",
        "selected_master_id", "selected_salon_id", "phone_number"
    ]):
        return

    is_taken = Registration.objects.filter(
        master_id=user_data["selected_master_id"],
        service_date=parse_date_from_str(user_data["selected_date"]),
        slot=user_data["selected_slot"]
    ).exists()

    if is_taken:
        reply_or_edit(update, "Упс! Это время уже занято. Попробуйте выбрать другое.")
        return

    client, _ = Client.objects.get_or_create(
        tg_id=tg_user.id,
        defaults={"name": tg_user.full_name or tg_user.username or "Без имени", "phonenumber": user_data["phone_number"]}
    )

    if client.phonenumber != user_data["phone_number"]:
        client.phonenumber = user_data["phone_number"]
        client.save()

    registration = Registration.objects.create(
        salon_id=user_data["selected_salon_id"],
        master_id=user_data["selected_master_id"],
        client=client,
        service_id=user_data["selected_service_id"],
        service_date=parse_date_from_str(user_data["selected_date"]),
        slot=user_data["selected_slot"]
    )

    context.user_data.clear()

    reply_or_edit(
        update,
        f"📌 *Запись подтверждена!*\n\n"
        f"📅 Дата: *{registration.service_date.strftime('%d.%m.%Y')}*\n"
        f"🕒 Время: *{registration.slot}*\n"
        f"👤 Мастер: *{registration.master.name}*\n"
        f"🏠 Салон: *{registration.salon.address}*\n"
        f"📞 Телефон: *{client.phonenumber}*",
        parse_mode="Markdown"
    )

    send_main_menu(update, context)
