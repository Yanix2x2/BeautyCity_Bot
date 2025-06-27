from django.contrib import admin
from django import forms
from dal import autocomplete
from datetime import datetime, timedelta, date
from django.forms.widgets import CheckboxSelectMultiple

from .models import Client, Salon, Service, Registration, Master, MasterSchedule


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    search_fields = ("address",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("treatment", "price")
    search_fields = ("treatment",)
    list_editable = ("price",)


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = "__all__"
        widgets = {
            "master": autocomplete.ModelSelect2(
                url="master-autocomplete",
                forward=["salon"],
                attrs={"data-placeholder": "Выберите мастера..."}
            ),
            "salon": autocomplete.ModelSelect2(
                url="salon-autocomplete",
                forward=["master"],
                attrs={"data-placeholder": "Выберите салон..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        raw_date = self.data.get("service_date") or self.initial.get("service_date")
        master_id = self.data.get("master") or self.initial.get("master")

        try:
            if raw_date and isinstance(raw_date, str) and "." in raw_date:
                service_date = datetime.strptime(raw_date, "%d.%m.%Y").date()
            else:
                service_date = raw_date
        except ValueError:
            service_date = None

        if service_date and master_id:
            booked_slots = Registration.objects.filter(
                service_date=service_date,
                master_id=master_id
            ).values_list("slot", flat=True)

            self.fields["slot"].choices = [
                (slot, name) for slot, name in Registration.TIME_SLOTS
                if slot not in booked_slots
            ]

    def clean(self):
        cleaned_data = super().clean()
        master = cleaned_data.get("master")
        salon = cleaned_data.get("salon")
        date_ = cleaned_data.get("service_date")

        if master and salon and date_:
            is_scheduled = MasterSchedule.objects.filter(
                master=master,
                salon=salon,
                work_date=date_
            ).exists()
            if not is_scheduled:
                raise forms.ValidationError("Мастер не работает в выбранном салоне в выбранную дату")

        return cleaned_data


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    form = RegistrationForm
    list_display = (
        'client',
        'master_link',
        'service',
        'salon_link',
        'service_date',
        'slot',
    )

    @admin.display(description='Мастер')
    def master_link(self, obj):
        return obj.master.name if obj.master else "Не выбран"

    @admin.display(description='Салон')
    def salon_link(self, obj):
        return obj.salon.address if obj.salon else "Не выбран"


class MasterScheduleInline(admin.TabularInline):
    model = MasterSchedule
    extra = 0
    fields = ("work_date", "salon")
    ordering = ("-work_date",)


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [MasterScheduleInline]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "phonenumber", "tg_id")
    search_fields = ("name", "phonenumber", "tg_id")


class MasterScheduleForm(forms.ModelForm):
    multiple_dates = forms.MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple,
        label="Рабочие даты (несколько)"
    )

    class Meta:
        model = MasterSchedule
        fields = ("master", "salon", "work_date")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        self.fields["multiple_dates"].choices = [
            (str(today + timedelta(days=i)), (today + timedelta(days=i)).strftime("%d.%m.%Y"))
            for i in range(14)
        ]

    def save(self, commit=True):
        multiple_dates = self.cleaned_data.get("multiple_dates", [])
        master = self.cleaned_data["master"]
        salon = self.cleaned_data["salon"]

        instances = []
        for raw_date in multiple_dates:
            obj, _ = MasterSchedule.objects.get_or_create(
                master=master,
                salon=salon,
                work_date=raw_date
            )
            instances.append(obj)

        return instances


@admin.register(MasterSchedule)
class MasterScheduleAdmin(admin.ModelAdmin):
    form = MasterScheduleForm
    list_display = ("master", "salon", "work_date")
    list_filter = ("salon", "master", "work_date")
    search_fields = ("master__name", "salon__address")
    ordering = ("-work_date",)
    autocomplete_fields = ("master", "salon")
    date_hierarchy = "work_date"

    def save_model(self, request, obj, form, change):
        if hasattr(form, "cleaned_data") and form.cleaned_data.get("multiple_dates"):
            form.save()
        else:
            super().save_model(request, obj, form, change)
