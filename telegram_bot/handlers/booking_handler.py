from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, MessageHandler, Filters, CallbackQueryHandler
from bot.models import Salon, Service
from telegram_bot.utils.reply_or_edit import reply_or_edit
from datetime import date, timedelta


def get_booking_handlers():
    return [
        MessageHandler(Filters.text("🗓 Записаться"), show_salon_selection),
        CallbackQueryHandler(save_selected_salon, pattern=r"^select_salon_"),
        CallbackQueryHandler(save_selected_service, pattern=r"^select_service_"),
        CallbackQueryHandler(handle_date_selection, pattern=r"^select_date_"),
        CallbackQueryHandler(handle_back_action, pattern=r"^back_to_"),
    ]


def show_salon_selection(update: Update, context: CallbackContext) -> None:
    salons = Salon.objects.all()
    if not salons.exists():
        reply_or_edit(update, "Нет доступных салонов для записи.")
        return

    buttons = [
        [InlineKeyboardButton(text=salon.address, callback_data=f"select_salon_{salon.id}")]
        for salon in salons
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите салон для записи:", reply_markup=reply_markup)


def save_selected_salon(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    selected_salon_id = query.data.replace("select_salon_", "")
    context.user_data["selected_salon_id"] = selected_salon_id

    show_service_selection(update, context)


def show_service_selection(update: Update, context: CallbackContext) -> None:
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


def show_available_dates(update: Update, context: CallbackContext) -> None:
    today = date.today()
    days = [today + timedelta(days=i) for i in range(5)]

    buttons = [
        [InlineKeyboardButton(day.strftime("%d.%m.%Y"), callback_data=f"select_date_{day}")]
        for day in days
    ]
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_services")])

    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите удобную дату:", reply_markup=reply_markup)


def save_selected_service(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    selected_service_id = query.data.replace("select_service_", "")
    context.user_data["selected_service_id"] = selected_service_id

    try:
        service = Service.objects.get(id=selected_service_id)
    except Service.DoesNotExist:
        reply_or_edit(update, "Услуга не найдена.")
        return

    show_available_dates(update, context)


def handle_date_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    selected_date = query.data.replace("select_date_", "")
    context.user_data["selected_date"] = selected_date

    reply_or_edit(
        update,
        f"📅 Дата выбрана: <b>{selected_date}</b>\nДалее — выбор времени (в разработке).",
        reply_markup=None
    )


def handle_back_action(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == "back_to_salons":
        show_salon_selection(update, context)
    elif query.data == "back_to_services":
        show_service_selection(update, context)
