from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.registration import get_available_masters
from telegram_bot.utils.calendar_tools import parse_date_from_str
from telegram_bot.utils.validation import check_required_fields
from telegram_bot.handlers.booking.slot_confirm_handler import request_phone_number
from bot.models import Salon, Service, Master, MasterSchedule
from telegram_bot.utils.master_flow import show_service_selection


def get_master_select_handlers():
    return [
        CallbackQueryHandler(save_selected_master, pattern=r"^select_master_"),
    ]


def show_master_list(update: Update, context: CallbackContext) -> None:
    """
    Показывает список мастеров для выбора (используется для кнопки "Назад").
    """
    flow = context.user_data.get("flow")
    
    if flow == "by_master":
        context.user_data.pop("selected_service_id", None)
        context.user_data.pop("selected_date", None)
        
        masters = Master.objects.all()
        if not masters.exists():
            reply_or_edit(update, "К сожалению, пока нет доступных мастеров.")
            return
            
        buttons = [
            [InlineKeyboardButton(f"👤 {master.name}", callback_data=f"select_master_{master.id}")]
            for master in masters
        ]
        buttons.append([InlineKeyboardButton("Назад", callback_data="main_menu")])
        
        reply_or_edit(update, "Выберите мастера:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        from telegram_bot.utils.master_flow import show_service_selection
        show_service_selection(update, context)


def show_master_selection(update: Update, context: CallbackContext) -> None:
    print("[DEBUG] show_master_selection вызван")

    query = update.callback_query
    query.answer()

    selected_date_str = query.data.replace("select_date_master_", "")
    context.user_data["selected_date"] = selected_date_str

    required = ["selected_salon_id", "selected_service_id", "selected_slot"]
    if not check_required_fields(update, context, required):
        return

    salon_id = context.user_data.get("selected_salon_id")
    service_id = context.user_data.get("selected_service_id")
    slot = context.user_data.get("selected_slot")

    try:
        salon = Salon.objects.get(id=salon_id)
        service = Service.objects.get(id=service_id)
    except (Salon.DoesNotExist, Service.DoesNotExist):
        reply_or_edit(update, "Салон или услуга не найдены.")
        return

    selected_date = parse_date_from_str(selected_date_str)

    available_masters = get_available_masters(salon, service, selected_date, slot)

    if not available_masters:
        reply_or_edit(update, "Нет доступных мастеров на выбранную дату и время.")
        return

    buttons = [
        [InlineKeyboardButton(f"👤 {master.name}", callback_data=f"select_master_{master.id}")]
        for master in available_masters
    ]
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_dates")])

    reply_markup = InlineKeyboardMarkup(buttons)
    reply_or_edit(update, "Выберите мастера:", reply_markup=reply_markup)


def show_master_selection_after_slot(update: Update, context: CallbackContext) -> None:
    flow = context.user_data.get("flow")
    service_id = context.user_data.get("selected_service_id")
    slot = context.user_data.get("selected_slot")
    date_str = context.user_data.get("selected_date")

    if not all([flow, service_id, slot, date_str]):
        reply_or_edit(update, "Ошибка: отсутствуют данные для отображения мастеров.")
        return

    selected_date = parse_date_from_str(date_str)

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        reply_or_edit(update, "Услуга не найдена.")
        return

    if flow == "by_master":
        master_id = context.user_data.get("selected_master_id")
        if not master_id:
            reply_or_edit(update, "Мастер не выбран.")
            return
        try:
            master = Master.objects.get(id=master_id)
        except Master.DoesNotExist:
            reply_or_edit(update, "Мастер не найден.")
            return

        masters = get_available_masters(
            master=master,
            service=service,
            work_date=selected_date,
            slot=slot
        )
    else:
        salon_id = context.user_data.get("selected_salon_id")
        if not salon_id:
            reply_or_edit(update, "Салон не выбран.")
            return
        try:
            salon = Salon.objects.get(id=salon_id)
        except Salon.DoesNotExist:
            reply_or_edit(update, "Салон не найден.")
            return

        masters = get_available_masters(
            salon=salon,
            service=service,
            work_date=selected_date,
            slot=slot
        )

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


def save_selected_master(update: Update, context: CallbackContext) -> None:
    print("[DEBUG] save_selected_master вызван")
    query = update.callback_query
    query.answer()

    master_id = int(query.data.replace("select_master_", ""))
    context.user_data["selected_master_id"] = master_id

    try:
        master = Master.objects.get(id=master_id)
        print(f"[DEBUG] Мастер найден: {master.name}")
    except Master.DoesNotExist:
        reply_or_edit(update, "Мастер не найден.")
        return

    flow = context.user_data.get("flow")
    if not flow:
        reply_or_edit(update, "Ошибка: сценарий записи не определён. Начните сначала.")
        return

    if flow == "by_master":
        if not context.user_data.get("selected_date"):
            from telegram_bot.handlers.booking.date_select_handler import show_date_selection
            show_date_selection(update, context, action_prefix="master")
            return
        
        selected_date = parse_date_from_str(context.user_data["selected_date"])
        try:
            schedule = MasterSchedule.objects.get(master_id=master_id, work_date=selected_date)
            context.user_data["selected_salon_id"] = schedule.salon_id
            print(f"[DEBUG] Установлен salon_id через расписание: {schedule.salon_id}")
        except MasterSchedule.DoesNotExist:
            reply_or_edit(update, "Ошибка: у мастера нет расписания на выбранную дату.")
            return

    if not context.user_data.get("selected_service_id"):
        from telegram_bot.utils.master_flow import show_service_selection
        show_service_selection(update, context)
        return

    print(f"[DEBUG] Мастер выбран: {master_id}")
    print(f"[DEBUG] user_data после выбора мастера: {context.user_data}")

    request_phone_number(update, context)


def show_masters_for_salon(update: Update, context: CallbackContext) -> None:
    """
    Показывает мастеров для выбранного салона, услуги, даты и времени (flow "by_salon").
    """
    salon_id = context.user_data.get("selected_salon_id")
    service_id = context.user_data.get("selected_service_id")
    slot = context.user_data.get("selected_slot")
    date_str = context.user_data.get("selected_date")

    if not all([salon_id, service_id, slot, date_str]):
        reply_or_edit(update, "Ошибка: отсутствуют данные для отображения мастеров.")
        return

    selected_date = parse_date_from_str(date_str)

    try:
        salon = Salon.objects.get(id=salon_id)
        service = Service.objects.get(id=service_id)
    except (Salon.DoesNotExist, Service.DoesNotExist):
        reply_or_edit(update, "Салон или услуга не найдены.")
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
