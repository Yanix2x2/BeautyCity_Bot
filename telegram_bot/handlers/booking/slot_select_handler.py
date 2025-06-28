from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler

from bot.models import Registration, MasterSchedule
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.calendar_tools import parse_date_from_str
from telegram_bot.handlers.booking.slot_confirm_handler import request_phone_number
from telegram_bot.utils.master_flow import show_service_selection
from telegram_bot.utils.master_flow import show_master_selection_after_slot


def get_slot_select_handlers():
    return [
        CallbackQueryHandler(show_slot_selection, pattern=r"^select_date_master_"),
        CallbackQueryHandler(handle_slot_selected, pattern=r"^select_slot_"),
    ]


def show_slot_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    date_str = context.user_data.get("selected_date")
    flow = context.user_data.get("flow")
    if not date_str or not flow:
        reply_or_edit(update, "Ошибка: не выбрана дата или сценарий записи.")
        return

    selected_date = parse_date_from_str(date_str)
    all_slots = [slot for slot, _ in Registration.TIME_SLOTS]

    if flow == "by_master":
        master_id = context.user_data.get("selected_master_id")
        if not master_id:
            reply_or_edit(update, "Ошибка: мастер не выбран.")
            return
        taken_slots = Registration.objects.filter(master_id=master_id, service_date=selected_date)\
            .values_list("slot", flat=True)

    elif flow == "by_salon":
        salon_id = context.user_data.get("selected_salon_id")
        service_id = context.user_data.get("selected_service_id")
        if not salon_id or not service_id:
            reply_or_edit(update, "Ошибка: не выбран салон или услуга.")
            return

        master_ids = MasterSchedule.objects.filter(
            salon_id=salon_id, work_date=selected_date, master__services__id=service_id
        ).values_list("master_id", flat=True).distinct()

        if not master_ids:
            reply_or_edit(update, "Нет мастеров, работающих в эту дату в выбранном салоне.")
            return

        taken_slots = Registration.objects.filter(master_id__in=master_ids, service_date=selected_date)\
            .values_list("slot", flat=True)

    else:
        reply_or_edit(update, "Ошибка: неизвестный сценарий записи.")
        return

    available_slots = [slot for slot in all_slots if slot not in taken_slots]
    if not available_slots:
        reply_or_edit(update, "Все слоты заняты на эту дату.\nПопробуйте другую дату.")
        return

    buttons = [[InlineKeyboardButton(slot, callback_data=f"select_slot_{slot}")] for slot in available_slots]
    
    if flow == "by_master":
        buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_services")])
    else:
        buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_dates")])
        
    reply_or_edit(update, "Выберите удобное время:", reply_markup=InlineKeyboardMarkup(buttons))


def handle_slot_selected(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    slot = query.data.replace("select_slot_", "")
    context.user_data["selected_slot"] = slot
    flow = context.user_data.get("flow")

    if flow == "by_master":
        request_phone_number(update, context)

    elif flow == "by_salon":
        show_master_selection_after_slot(update, context)

    else:
        reply_or_edit(update, "Ошибка: сценарий записи не определён.")
