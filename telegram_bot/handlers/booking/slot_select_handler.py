from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from bot.models import Registration
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.calendar_tools import parse_date_from_str
from telegram_bot.utils.callback import parse_callback_id


def get_slot_select_handlers():
    return [
        CallbackQueryHandler(show_slot_selection, pattern=r"^select_master_"),
    ]


def show_slot_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    master_id = parse_callback_id(query.data, "select_master_")
    if master_id is None:
        reply_or_edit(update, "Такого мастера нет.")
        return

    context.user_data["selected_master_id"] = master_id

    date_str = context.user_data.get("selected_date")
    selected_date = parse_date_from_str(date_str)

    all_slots = [slot for slot, _ in Registration.TIME_SLOTS]

    taken_slots = Registration.objects.filter(
        master_id=master_id,
        service_date=selected_date
    ).values_list("slot", flat=True)

    available_slots = [slot for slot in all_slots if slot not in taken_slots]

    if not available_slots:
        reply_or_edit(update, "У этого мастера нет свободных слотов на выбранную дату.")
        return

    buttons = [
        [InlineKeyboardButton(slot, callback_data=f"select_slot_{slot}")]
        for slot in available_slots
    ]
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_masters")])

    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите удобное время:", reply_markup=reply_markup)
