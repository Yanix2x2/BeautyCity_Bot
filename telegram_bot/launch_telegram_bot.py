import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "beauty_city.settings")
import django
django.setup()

from dotenv import load_dotenv
from telegram.ext import Updater
from telegram_bot.dispatcher import register_handlers


def main():
    load_dotenv()
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не найден в .env")

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    register_handlers(dp)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
