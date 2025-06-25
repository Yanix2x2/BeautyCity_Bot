from dal.autocomplete import Select2QuerySetView
from .models import Master


class MasterAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        salon_id = self.forwarded.get('salon', None)
        if salon_id:
            return Master.objects.filter(salon_id=salon_id)
        return Master.objects.none()
