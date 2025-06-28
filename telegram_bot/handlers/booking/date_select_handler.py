from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.calendar_tools import format_date_russian_weekday, get_week_dates
from telegram_bot.handlers.booking.slot_select_handler import show_slot_selection
from bot.models import MasterSchedule
from telegram_bot.utils.calendar_tools import parse_date_from_str


def get_date_select_handlers():
    return [
        CallbackQueryHandler(save_selected_date, pattern=r"^select_date_(slot|master)_"),
        CallbackQueryHandler(change_date_page, pattern=r"^change_date_page_"),
    ]


def show_date_selection(update: Update, context: CallbackContext, action_prefix: str = "slot") -> None:
    print("[DEBUG] show_date_selection user_data:", context.user_data)
    context.user_data["date_action_prefix"] = action_prefix

    page = context.user_data.get("date_page", 0)
    days = get_week_dates(page)
    prefix = f"select_date_{action_prefix}_"

    buttons = [
        [InlineKeyboardButton(format_date_russian_weekday(day), callback_data=f"{prefix}{day.strftime('%d.%m.%Y')}")]
        for day in days
    ]

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("Предыдущая неделя", callback_data="change_date_page_-1"))
    nav.append(InlineKeyboardButton("Следующая неделя", callback_data="change_date_page_1"))
    buttons.append(nav)

    flow = context.user_data.get("flow")
    if flow == "by_master":
        back_btn = "back_to_masters"
    else:
        back_btn = "back_to_services"
    
    buttons.append([InlineKeyboardButton("Назад", callback_data=back_btn)])
    reply_or_edit(update, "Выберите удобную дату:", reply_markup=InlineKeyboardMarkup(buttons))


def change_date_page(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    delta = int(query.data.split("_")[-1])
    context.user_data["date_page"] = max(0, context.user_data.get("date_page", 0) + delta)
    prefix = context.user_data.get("date_action_prefix", "slot")
    show_date_selection(update, context, prefix)


def save_selected_date(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = query.data
    if "select_date_slot_" in data:
        context.user_data["flow"] = "by_salon"
        context.user_data["selected_date"] = data.replace("select_date_slot_", "")

    elif "select_date_master_" in data:
        context.user_data["flow"] = "by_master"
        context.user_data["selected_date"] = data.replace("select_date_master_", "")

        master_id = context.user_data.get("selected_master_id")
        selected_date = parse_date_from_str(context.user_data["selected_date"])

        if master_id and not context.user_data.get("selected_salon_id"):
            schedule = MasterSchedule.objects.filter(master_id=master_id, work_date=selected_date).first()
            if schedule:
                context.user_data["selected_salon_id"] = schedule.salon_id
            else:
                reply_or_edit(update, "Мастер не работает в эту дату.")
                return
    else:
        reply_or_edit(update, "Ошибка: неизвестный формат даты.")
        return

    print(f"[DEBUG] Сохранена дата: {context.user_data['selected_date']}")
    show_slot_selection(update, context)
