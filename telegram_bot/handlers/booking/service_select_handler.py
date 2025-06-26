from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler
from bot.models import Service
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.handlers.booking.date_select_handler import show_date_selection


def get_service_select_handlers():
    return [
        CallbackQueryHandler(save_selected_service, pattern=r"^select_service_"),
    ]


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
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_salons")])

    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите процедуру:", reply_markup=reply_markup)


def save_selected_service(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    service_id = int(query.data.replace("select_service_", ""))
    context.user_data["selected_service_id"] = service_id

    try:
        Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        reply_or_edit(update, "Услуга не найдена.")
        return

    context.user_data["date_action_prefix"] = "slot"
    show_date_selection(update, context, action_prefix="slot")
