import os
from decimal import Decimal
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, PreCheckoutQueryHandler, MessageHandler, Filters

from bot.models import Registration
from telegram_bot.utils.reply_or_edit import reply_or_edit
from telegram_bot.utils.main_menu import send_main_menu


def get_payment_handlers():
    """Возвращает список обработчиков для платежей"""
    return [
        CallbackQueryHandler(handle_payment_callback, pattern=r"^(pay_registration_|pay_later)"),
        PreCheckoutQueryHandler(precheckout_callback),
        MessageHandler(Filters.successful_payment, handle_successful_payment),
        MessageHandler(Filters.text("❌ Оплата не прошла"), handle_failed_payment),
    ]


def offer_payment_after_registration(update: Update, context: CallbackContext, registration: Registration) -> None:
    """Предлагает оплату после успешной записи"""
    try:
        buttons = [
            [InlineKeyboardButton(
                f"💳 Оплатить {registration.service.price} ₽", 
                callback_data=f"pay_registration_{registration.pk}"
            )],
            [InlineKeyboardButton("💳 Оплатить позже", callback_data="pay_later")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        message = (
            f"✅ Запись успешно создана!\n\n"
            f"📋 Детали записи:\n"
            f"• Услуга: {registration.service.treatment}\n"
            f"• Мастер: {registration.master.name}\n"
            f"• Дата: {registration.service_date}\n"
            f"• Время: {registration.slot}\n"
            f"• Салон: {registration.salon.address}\n"
            f"• Сумма: {registration.service.price} ₽\n\n"
            f"💳 Хотите оплатить сейчас?"
        )
        
        reply_or_edit(update, message, reply_markup=reply_markup)
        
    except Exception as e:
        print(f"Ошибка предложения оплаты: {e}")
        send_main_menu(update, context, "Запись создана! Вы в главном меню.")


def handle_payment_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает callback'и для платежей"""
    query = update.callback_query
    query.answer()
    
    if query.data.startswith("pay_registration_"):
        registration_id = int(query.data.replace("pay_registration_", ""))
        handle_pay_registration(update, context, registration_id)
        
    elif query.data == "pay_later":
        handle_pay_later(update, context)
        
    elif query.data == "main_menu":
        send_main_menu(update, context)


def handle_pay_registration(update: Update, context: CallbackContext, registration_id: int) -> None:
    """Обрабатывает запрос на оплату записи"""
    try:
        registration = Registration.objects.get(pk=registration_id)
        
        context.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title=f"Оплата записи №{registration.pk}",
            description=(
                f"Услуга: {registration.service.treatment}\n"
                f"Мастер: {registration.master.name}\n"
                f"Дата: {registration.service_date}\n"
                f"Время: {registration.slot}\n"
                f"Салон: {registration.salon.address}"
            ),
            payload=f"payment_registration_{registration.pk}",
            provider_token=os.getenv("TELEGRAM_PROVIDER_TOKEN"),
            currency="RUB",
            prices=[LabeledPrice(
                label=registration.service.treatment, 
                amount=int(registration.service.price * 100)  # Сумма в копейках
            )],
            start_parameter="beauty_city_payment"
        )
        
        reply_or_edit(
            update,
            f"💳 Создан счет для оплаты записи №{registration.pk}\n\n"
            f"Сумма: {registration.service.price} ₽\n"
            f"Нажмите кнопку 'Оплатить' для завершения платежа."
        )
            
    except Registration.DoesNotExist:
        buttons = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        reply_or_edit(update, "❌ Запись не найдена.", reply_markup=reply_markup)
    except Exception as e:
        print(f"Ошибка обработки платежа: {e}")
        buttons = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        reply_or_edit(update, "❌ Произошла ошибка при создании платежа.", reply_markup=reply_markup)


def handle_pay_later(update: Update, context: CallbackContext) -> None:
    """Обрабатывает отложенную оплату"""
    reply_or_edit(
        update,
        "💳 Оплата будет произведена в салоне при посещении.\n\n"
        "Запись сохранена и подтверждена!\n"
        "Ждем вас в назначенное время."
    )
    send_main_menu(update, context)


def precheckout_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает предварительную проверку платежа"""
    query = update.pre_checkout_query
    if query.invoice_payload.startswith("payment_registration_"):
        query.answer(ok=True)
    else:
        query.answer(ok=False, error_message="Ошибка: неправильный payload.")


def handle_successful_payment(update: Update, context: CallbackContext) -> None:
    """Обрабатывает успешный платеж"""
    try:
        payload = update.message.successful_payment.invoice_payload
        registration_id = int(payload.replace("payment_registration_", ""))
        
        registration = Registration.objects.get(pk=registration_id)
        
        registration.is_paid = True
        registration.save()
        
        reply_or_edit(
            update, 
            f"✅ Оплата прошла успешно!\n\n"
            f"Запись №{registration.pk} оплачена.\n"
            f"Сумма: {registration.service.price} ₽\n\n"
            f"Ждем вас {registration.service_date} в {registration.slot}!"
        )
        
    except (Registration.DoesNotExist, ValueError) as e:
        print(f"Ошибка обработки успешного платежа: {e}")
        buttons = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        reply_or_edit(update, "❌ Ошибка обработки платежа. Обратитесь к администратору.", reply_markup=reply_markup)
    except Exception as e:
        print(f"Неожиданная ошибка при обработке платежа: {e}")
        buttons = [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        reply_or_edit(update, "❌ Произошла ошибка. Обратитесь к администратору.", reply_markup=reply_markup)


def handle_failed_payment(update: Update, context: CallbackContext) -> None:
    """Обрабатывает неудачную оплату"""
    reply_or_edit(
        update,
        "❌ Оплата не прошла. Пожалуйста, попробуйте позже или обратитесь к администратору."
    )
    send_main_menu(update, context)
