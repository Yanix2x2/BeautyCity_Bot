from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, MessageHandler, Filters, CallbackQueryHandler
from bot.models import Registration
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.main_menu import send_main_menu
from django.utils import timezone


def get_history_handlers():
    return [
        MessageHandler(Filters.text("📋 История записей"), show_client_history),
        CallbackQueryHandler(handle_history_filter, pattern=r"^history_"),
        CallbackQueryHandler(handle_main_menu, pattern="^main_menu$"),
    ]


def show_client_history(update: Update, context: CallbackContext) -> None:
    """Показывает меню выбора типа записей для просмотра."""
    buttons = [
        [InlineKeyboardButton("⏳ Активные записи", callback_data="history_active")],
        [InlineKeyboardButton("✅ Завершенные записи", callback_data="history_completed")],
        [InlineKeyboardButton("📋 Все записи", callback_data="history_all")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    
    reply_or_edit(update, "Выберите тип записей для просмотра:", 
                 reply_markup=InlineKeyboardMarkup(buttons))


def handle_history_filter(update: Update, context: CallbackContext) -> None:
    """Обрабатывает выбор фильтра для истории записей."""
    query = update.callback_query
    query.answer()
    
    if query.data == "history_back":
        show_client_history(update, context)
        return
    
    tg_user = update.effective_user
    now = timezone.now().date()
    
    if query.data == "history_active":
        registrations = Registration.objects.filter(
            client__tg_id=tg_user.id,
            service_date__gte=now
        )
        title = "⏳ Активные записи"
    elif query.data == "history_completed":
        registrations = Registration.objects.filter(
            client__tg_id=tg_user.id,
            service_date__lt=now
        )
        title = "✅ Завершенные записи"
    else:  # history_all
        registrations = Registration.objects.filter(client__tg_id=tg_user.id)
        title = "📋 Все записи"
    
    registrations = registrations.select_related('master', 'salon', 'service').order_by('-service_date', '-slot')
    
    if not registrations.exists():
        buttons = [
            [InlineKeyboardButton("🔙 Назад к фильтрам", callback_data="history_back")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_or_edit(update, f"У вас нет {title.lower()}.", reply_markup=InlineKeyboardMarkup(buttons))
        return
    
    message = f"{title}:\n\n"
    for reg in registrations:
        status = "✅ Завершена" if reg.service_date < now else "⏳ Ожидает"
        payment_status = "💳 Оплачено" if reg.is_paid else "💰 Не оплачено"
        message += (
            f"📅 {reg.service_date.strftime('%d.%m.%Y')} в {reg.slot}\n"
            f"👤 {reg.master.name}\n"
            f"🏠 {reg.salon.address}\n"
            f"💇 {reg.service.treatment}\n"
            f"📊 {status}\n"
            f"💳 {payment_status}\n\n"
        )
    
    buttons = [
        [InlineKeyboardButton("🔙 Назад к фильтрам", callback_data="history_back")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_or_edit(update, message, reply_markup=InlineKeyboardMarkup(buttons))


def handle_main_menu(update: Update, context: CallbackContext) -> None:
    """Возвращает пользователя в главное меню."""
    query = update.callback_query
    query.answer()
    send_main_menu(update, context)
