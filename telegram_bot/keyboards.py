from telegram import ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        ["🗓 Записаться"],
        ["📍 Адреса салонов"],
        ["💬 Связаться с менеджером"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
