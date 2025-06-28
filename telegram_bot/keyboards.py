from telegram import ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        ["📍 Адреса салонов"],
        ["👤 Выбрать мастера"],
        ["🗓 Записаться"],
        ["📋 История записей"],
        ["💬 Связаться с администратором"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
