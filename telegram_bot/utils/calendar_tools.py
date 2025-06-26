from datetime import date, datetime, timedelta


RUSSIAN_WEEKDAYS = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Вс",
}


def parse_date_from_str(date_str: str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def format_date_russian_weekday(d: date) -> str:
    weekday = RUSSIAN_WEEKDAYS.get(d.weekday(), "")
    return f"{weekday} {d.strftime('%d.%m')}"


def get_monday_of_week(any_day: date) -> date:
    return any_day - timedelta(days=any_day.weekday())


def get_week_dates(page: int):
    today = date.today()
    current_monday = get_monday_of_week(today)
    target_monday = current_monday + timedelta(weeks=page)

    week_days = [target_monday + timedelta(days=i) for i in range(7)]

    if page == 0:
        week_days = [d for d in week_days if d >= today]

    return week_days
