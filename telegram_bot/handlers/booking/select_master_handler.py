from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.registration import get_available_masters
from telegram_bot.utils.calendar_tools import parse_date_from_str
from bot.models import Salon, Service
from telegram_bot.utils.callback import parse_callback_id


def get_master_select_handlers():
    return [
        CallbackQueryHandler(show_master_selection, pattern=r"^select_date_master_"),
    ]


def show_master_selection(update: Update, context: CallbackContext) -> None:
    print("[DEBUG] show_master_selection вызван")

    query = update.callback_query
    query.answer()

    selected_date_str = query.data.replace("select_date_master_", "")
    context.user_data["selected_date"] = selected_date_str

    salon_id = context.user_data.get("selected_salon_id")
    service_id = context.user_data.get("selected_service_id")
    slot = context.user_data.get("selected_slot")

    if not salon_id or not service_id:
        reply_or_edit(update, "Не выбраны салон или услуга.")
        return

    if not slot:
        reply_or_edit(update, "Не выбрано время.")
        return

    try:
        salon = Salon.objects.get(id=salon_id)
        service = Service.objects.get(id=service_id)
    except (Salon.DoesNotExist, Service.DoesNotExist):
        reply_or_edit(update, "Салон или услуга не найдены.")
        return

    selected_date = parse_date_from_str(selected_date_str)

    available_masters = get_available_masters(salon, service, selected_date, slot)

    if not available_masters:
        reply_or_edit(update, "Нет доступных мастеров на выбранную дату и время.")
        return

    buttons = [
        [InlineKeyboardButton(master.name, callback_data=f"select_master_{master.id}")]
        for master in available_masters
    ]
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_dates")])

    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите мастера:", reply_markup=reply_markup)
