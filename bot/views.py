from dal.autocomplete import Select2QuerySetView
from .models import Master, Salon


class MasterAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        salon_id = self.forwarded.get('salon')
        qs = Master.objects.select_related('salon')
        if salon_id:
            qs = qs.filter(salon_id=salon_id)
        return qs

    def get_result_label(self, item):
        return f"{item.name} ({item.salon.address if item.salon else 'Без салона'})"


class SalonAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        master_id = self.forwarded.get('master')
        qs = Salon.objects.all()
        if master_id:
            master = Master.objects.get(pk=master_id)
            qs = qs.filter(pk=master.salon_id)
        return qs
