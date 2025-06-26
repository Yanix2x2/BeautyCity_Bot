def parse_callback_id(callback_data: str, prefix: str) -> int | None:
    """
    Извлекает числовой ID из callback_data с заданным префиксом.
    Если невалидный формат или не число — возвращает None.
    """
    if not callback_data.startswith(prefix):
        return None
    try:
        return int(callback_data[len(prefix):])
    except ValueError:
        return None
