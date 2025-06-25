from django.core.management.base import BaseCommand
from telegram.ext import Updater
import os
from dotenv import load_dotenv
from telegram_bot.dispatcher import register_handlers


class Command(BaseCommand):
    help = "Запуск Telegram-бота"

    def handle(self, *args, **kwargs):
        load_dotenv()
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            self.stderr.write("Ошибка: токен не найден")
            return

        updater = Updater(token, use_context=True)
        dp = updater.dispatcher

        register_handlers(dp)

        self.stdout.write("Бот запущен")
        updater.start_polling()
        updater.idle()
