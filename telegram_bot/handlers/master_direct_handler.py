from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, MessageHandler, Filters, CallbackQueryHandler
from bot.models import Master
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.handlers.booking.date_select_handler import show_date_selection
from telegram_bot.handlers.booking.service_select_handler import show_service_selection


def get_master_direct_handlers():
    return [
        MessageHandler(Filters.text("👤 Выбрать мастера"), show_master_list),
        CallbackQueryHandler(handle_master_selected, pattern=r"^direct_master_"),
    ]


def show_master_list(update: Update, context: CallbackContext) -> None:
    masters = Master.objects.all()
    if not masters:
        reply_or_edit(update, "Мастера пока не добавлены.")
        return

    buttons = [
        [InlineKeyboardButton(f"👤 {master.name}", callback_data=f"direct_master_{master.id}")]
        for master in masters
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите мастера:", reply_markup=reply_markup)


def handle_master_selected(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    master_id = int(query.data.replace("direct_master_", ""))
    context.user_data["selected_master_id"] = master_id
    context.user_data["flow"] = "by_master"

    show_date_selection(update, context, action_prefix="master")
