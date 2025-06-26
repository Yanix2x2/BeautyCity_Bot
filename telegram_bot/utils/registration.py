from bot.models import Registration, Master


def is_master_available(master, service_date, slot) -> bool:
    """Проверяет, свободен ли мастер на указанную дату и время."""
    return not Registration.objects.filter(
        master=master,
        service_date=service_date,
        slot=slot
    ).exists()


def get_available_masters(salon, service, service_date, slot):
    """
    Возвращает всех мастеров, работающих в указанном салоне,
    выполняющих данную услугу и свободных в указанную дату и слот.
    """
    masters = Master.objects.filter(
        salon=salon,
        services=service
    ).distinct()

    available = [
        master for master in masters
        if is_master_available(master, service_date, slot)
    ]

    return available
