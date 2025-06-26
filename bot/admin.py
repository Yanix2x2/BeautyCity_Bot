from django.contrib import admin
from django import forms
from dal import autocomplete
from datetime import datetime

from .models import Client, Salon, Service, Registration, Master


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    class MasterInline(admin.TabularInline):
        model = Master
        extra = 1

    inlines = [MasterInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('treatment', 'price')
    search_fields = ('treatment',)
    list_editable = ('price',)


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = '__all__'
        widgets = {
            'master': autocomplete.ModelSelect2(
                url='master-autocomplete',
                forward=['salon'],
                attrs={'data-placeholder': 'Выберите мастера...'}
            ),
            'salon': autocomplete.ModelSelect2(
                url='salon-autocomplete',
                forward=['master'],
                attrs={'data-placeholder': 'Выберите салон...'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Предзаполняем салон по мастеру
        if self.instance and self.instance.master:
            self.initial.setdefault('salon', self.instance.master.salon)

        service_date = self.data.get('service_date') or self.initial.get('service_date')
        master_id = self.data.get('master') or self.initial.get('master')

        raw_date = self.data.get('service_date') or self.initial.get('service_date')
        master_id = self.data.get('master') or self.initial.get('master')

        try:
            if raw_date and isinstance(raw_date, str) and '.' in raw_date:
                service_date = datetime.strptime(raw_date, "%d.%m.%Y").date()
            else:
                service_date = raw_date  # Уже в формате даты или ISO-строка
        except ValueError:
            service_date = None

        if service_date and master_id:
            booked_slots = Registration.objects.filter(
                service_date=service_date,
                master_id=master_id
            ).values_list('slot', flat=True)

            self.fields['slot'].choices = [
                (slot, name) for slot, name in Registration.TIME_SLOTS
                if slot not in booked_slots
            ]

    def clean(self):
        cleaned_data = super().clean()
        master, salon = cleaned_data.get('master'), cleaned_data.get('salon')
        if master and salon and master.salon != salon:
            raise forms.ValidationError("Мастер не работает в выбранном салоне")
        return cleaned_data


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    form = RegistrationForm
    list_display = ('client', 'service', 'master_link', 'salon_link', 'service_date')

    @admin.display(description='Мастер')
    def master_link(self, obj):
        return obj.master.name if obj.master else "Не выбран"

    @admin.display(description='Салон')
    def salon_link(self, obj):
        return obj.salon.address if obj.salon else "Не выбран"


admin.site.register(Client)
admin.site.register(Master)
