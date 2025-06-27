from bot.models import MasterSchedule, Registration, Master


def is_master_available(master, service_date, slot) -> bool:
    """Проверяет, свободен ли мастер на указанную дату и время."""
    return not Registration.objects.filter(
        master=master,
        service_date=service_date,
        slot=slot
    ).exists()


def get_available_masters(salon=None, service=None, work_date=None, slot=None, master=None):
    """
    Универсальная функция для потока by_salon и by_master:
    - by_salon → передаются salon и service
    - by_master → передаются master и service
    """
    if master:
        master_ids = [master.id]
    else:
        schedule_qs = MasterSchedule.objects.filter(
            salon=salon,
            work_date=work_date,
            master__services=service
        ).select_related("master")
        master_ids = schedule_qs.values_list("master_id", flat=True).distinct()

    if slot:
        taken_master_ids = Registration.objects.filter(
            master_id__in=master_ids,
            service_date=work_date,
            slot=slot
        ).values_list("master_id", flat=True)

        master_ids = [mid for mid in master_ids if mid not in taken_master_ids]

    return Master.objects.filter(id__in=master_ids)
