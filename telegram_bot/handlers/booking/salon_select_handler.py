from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler, Filters

from bot.models import Salon
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.master_flow import show_service_selection
from telegram_bot.utils.calendar_tools import parse_date_from_str
from telegram_bot.utils.master_flow import show_salon_selection
from telegram_bot.utils.validation import check_required_fields


def get_salon_select_handlers():
    return [
        MessageHandler(Filters.text("🗓 Записаться"), show_salon_selection),
        CallbackQueryHandler(save_selected_salon, pattern=r"^select_salon_"),
    ]


def show_salon_selection_for_master_date(update: Update, context: CallbackContext) -> None:
    if not check_required_fields(update, context, ["selected_master_id", "selected_date"]):
        return

    master_id = context.user_data["selected_master_id"]
    date_str = context.user_data["selected_date"]

    selected_date = parse_date_from_str(date_str)
    salons = Salon.objects.filter(schedules__master_id=master_id, schedules__work_date=selected_date).distinct()

    if not salons.exists():
        reply_or_edit(update, "В этот день мастер не работает ни в одном салоне.")
        return

    buttons = [[InlineKeyboardButton(salon.address, callback_data=f"select_salon_{salon.id}")] for salon in salons]
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_slots")])
    reply_or_edit(update, "Выберите салон, где хотите записаться:", reply_markup=InlineKeyboardMarkup(buttons))


def save_selected_salon(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    try:
        salon_id = int(query.data.replace("select_salon_", ""))
        context.user_data["selected_salon_id"] = salon_id
        print("[DEBUG] после выбора салона:", context.user_data)
    except Exception:
        reply_or_edit(update, "Ошибка при выборе салона.")
        return

    context.user_data["flow"] = context.user_data.get("flow", "by_salon")
    show_service_selection(update, context)
