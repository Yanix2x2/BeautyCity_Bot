from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler

from bot.models import Service, Salon
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.calendar_tools import parse_date_from_str
from telegram_bot.handlers.booking.date_select_handler import show_date_selection
from telegram_bot.handlers.booking.salon_select_handler import show_salon_selection_for_master_date


def get_service_select_handlers():
    return [
        CallbackQueryHandler(save_selected_service, pattern=r"^select_service_"),
    ]


def show_service_selection(update: Update, context: CallbackContext) -> None:
    master_id = context.user_data.get("selected_master_id")
    services = Service.objects.filter(master__id=master_id) if master_id else Service.objects.all()

    if not services.exists():
        reply_or_edit(update, "К сожалению, пока нет доступных процедур.")
        return

    buttons = [
        [InlineKeyboardButton(
            f"{s.treatment} — {int(s.price):,} ₽".replace(",", " "),
            callback_data=f"select_service_{s.id}"
        )] for s in services
    ]

    flow = context.user_data.get("flow")
    if flow == "by_master":
        back_btn = "back_to_masters"
    else:
        back_btn = "back_to_salons"
    
    buttons.append([InlineKeyboardButton("Назад", callback_data=back_btn)])

    reply_or_edit(update, "Выберите процедуру:", reply_markup=InlineKeyboardMarkup(buttons))


def save_selected_service(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    try:
        service_id = int(query.data.replace("select_service_", ""))
        Service.objects.get(id=service_id)
        context.user_data["selected_service_id"] = service_id
        print("[DEBUG] после выбора услуги:", context.user_data)
    except (ValueError, Service.DoesNotExist):
        reply_or_edit(update, "Ошибка при выборе услуги.")
        return

    flow = context.user_data.get("flow")

    if flow == "by_master" and not context.user_data.get("selected_salon_id"):
        master_id = context.user_data.get("selected_master_id")
        date_str = context.user_data.get("selected_date")

        if master_id and date_str:
            selected_date = parse_date_from_str(date_str)
            salons = Salon.objects.filter(
                schedules__master_id=master_id,
                schedules__work_date=selected_date
            ).distinct()

            if salons.count() == 1:
                context.user_data["selected_salon_id"] = salons.first().id
            elif salons.exists():
                show_salon_selection_for_master_date(update, context)
                return
            else:
                reply_or_edit(update, "Мастер не работает ни в одном салоне в эту дату.")
                return

    if flow == "by_salon":
        show_date_selection(update, context, action_prefix="slot")
    elif context.user_data.get("selected_date"):
        from telegram_bot.handlers.booking.slot_select_handler import show_slot_selection
        show_slot_selection(update, context)
    else:
        show_date_selection(update, context, action_prefix="master")
