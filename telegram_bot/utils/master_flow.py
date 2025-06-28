from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from bot.models import Salon, Service
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.calendar_tools import parse_date_from_str
from telegram_bot.utils.registration import get_available_masters


def show_master_selection_after_slot(update: Update, context: CallbackContext) -> None:
    salon_id = context.user_data.get("selected_salon_id")
    service_id = context.user_data.get("selected_service_id")
    slot = context.user_data.get("selected_slot")
    date_str = context.user_data.get("selected_date")


    if not all([salon_id, service_id, slot, date_str]):
        reply_or_edit(update, "Ошибка. Попробуйте ещё раз.")
        return

    selected_date = parse_date_from_str(date_str)

    try:
        salon = Salon.objects.get(id=salon_id)
        service = Service.objects.get(id=service_id)
    except (Salon.DoesNotExist, Service.DoesNotExist):
        reply_or_edit(update, "Ошибка при загрузке салона или услуги.")
        return

    masters = get_available_masters(salon, service, selected_date, slot)

    if not masters:
        reply_or_edit(update, "К сожалению, на это время нет доступных мастеров.")
        return

    buttons = [
        [InlineKeyboardButton(f"👤 {master.name}", callback_data=f"select_master_{master.id}")]
        for master in masters
    ]
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_slots")])

    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите мастера, доступного в это время:", reply_markup=reply_markup)


def show_service_selection(update: Update, context: CallbackContext) -> None:
    master_id = context.user_data.get("selected_master_id")
    if master_id:
        services = Service.objects.filter(master__id=master_id)
    else:
        services = Service.objects.all()

    if not services.exists():
        reply_or_edit(update, "К сожалению, пока нет доступных процедур.")
        return

    buttons = [
        [InlineKeyboardButton(
            text=f"{service.treatment} — {int(service.price):,} ₽".replace(",", " "),
            callback_data=f"select_service_{service.id}"
        )] for service in services
    ]

    flow = context.user_data.get("flow")

    if flow == "by_master":
        back_callback = "back_to_dates"
    else:
        back_callback = "back_to_salons"

    buttons.append([InlineKeyboardButton("Назад", callback_data=back_callback)])

    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите процедуру:", reply_markup=reply_markup)


def show_salon_selection(update, context):
    context.user_data["flow"] = "by_salon"
    salons = Salon.objects.all()

    if not salons.exists():
        reply_or_edit(update, "Нет доступных салонов для записи.")
        return

    buttons = [
        [InlineKeyboardButton(salon.address, callback_data=f"select_salon_{salon.id}")]
        for salon in salons
    ]
    reply_or_edit(update, "Выберите салон для записи:", reply_markup=InlineKeyboardMarkup(buttons))
