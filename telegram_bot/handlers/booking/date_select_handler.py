from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.calendar_tools import format_date_russian_weekday, get_week_dates
from telegram_bot.handlers.booking.slot_select_handler import show_slot_selection


def get_date_select_handlers():
    return [
        CallbackQueryHandler(save_selected_date, pattern=r"^select_date_(slot|master)_"),
        CallbackQueryHandler(change_date_page, pattern=r"^change_date_page_"),
    ]


def show_date_selection(update: Update, context: CallbackContext, action_prefix: str = "slot") -> None:
    page = context.user_data.get('date_page', 0)
    days = get_week_dates(page)

    callback_prefix = f"select_date_{action_prefix}_"

    buttons = [
        [
            InlineKeyboardButton(
                format_date_russian_weekday(day),
                callback_data=f"{callback_prefix}{day}"
            )
        ]
        for day in days
    ]

    nav_buttons = [
        [
            InlineKeyboardButton("Следующая неделя", callback_data="change_date_page_1")
        ]
    ]
    if page > 0:
        nav_buttons.append([InlineKeyboardButton("Предыдущая неделя", callback_data="change_date_page_-1")])

    buttons.extend(nav_buttons)
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_services")])

    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите удобную дату:", reply_markup=reply_markup)


def change_date_page(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    delta = int(query.data.split("_")[-1])
    current_page = context.user_data.get('date_page', 0)
    new_page = max(0, current_page + delta)
    context.user_data['date_page'] = new_page

    action_prefix = context.user_data.get("date_action_prefix", "slot")
    show_date_selection(update, context, action_prefix)


def save_selected_date(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    callback = query.data
    if callback.startswith("select_date_slot_"):
        selected_date_str = callback.replace("select_date_slot_", "")
    elif callback.startswith("select_date_master_"):
        selected_date_str = callback.replace("select_date_master_", "")
    else:
        reply_or_edit(update, "Ошибка: неизвестный формат даты.")
        return

    context.user_data["selected_date"] = selected_date_str
    print(f"[DEBUG] Сохранена дата: {selected_date_str}")

    if context.user_data.get("selected_master_id"):
        from telegram_bot.handlers.booking.slot_select_handler import show_slot_selection
        show_slot_selection(update, context)
    else:
        from telegram_bot.handlers.booking.select_master_handler import show_master_selection
        show_master_selection(update, context)
