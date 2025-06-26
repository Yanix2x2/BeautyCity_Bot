from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from bot.models import Registration
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.calendar_tools import parse_date_from_str


def get_slot_select_handlers():
    return [
        CallbackQueryHandler(show_slot_selection, pattern=r"^select_master_"),
    ]


def show_slot_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    master_id = context.user_data.get("selected_master_id")
    if not master_id:
        reply_or_edit(update, "Ошибка: мастер не выбран.")
        return

    date_str = context.user_data.get("selected_date")
    if not date_str:
        reply_or_edit(update, "Ошибка: дата не выбрана.")
        return

    selected_date = parse_date_from_str(date_str)
    all_slots = [slot for slot, _ in Registration.TIME_SLOTS]

    taken_slots = Registration.objects.filter(
        master_id=master_id,
        service_date=selected_date
    ).values_list("slot", flat=True)

    available_slots = [slot for slot in all_slots if slot not in taken_slots]

    if not available_slots:
        reply_or_edit(update, "На выбранную дату у этого мастера пока нет свободного времени.")
        return

    buttons = [
        [InlineKeyboardButton(slot, callback_data=f"select_slot_{slot}")]
        for slot in available_slots
    ]

    prefix = context.user_data.get("date_action_prefix", "slot")
    back_callback = "back_to_dates" if prefix == "slot" else "back_to_masters"

    buttons.append([InlineKeyboardButton("Назад", callback_data=back_callback)])

    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите удобное время:", reply_markup=reply_markup)
