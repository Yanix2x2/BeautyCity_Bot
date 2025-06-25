from django.contrib import admin
from django import forms
from dal import autocomplete

from .models import Client, Salon, Service, Registration, Master


class MasterInline(admin.TabularInline):
    model = Master
    extra = 1


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    inlines = [
        MasterInline,
    ]


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
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.instance.master = None
            self.instance.salon = None
        
        # Если мастер уже выбран, устанавливаем соответствующий салон
        if self.instance and self.instance.master:
            self.initial['salon'] = self.instance.master.salon

    def clean(self):
        cleaned_data = super().clean()
        master = cleaned_data.get('master')
        salon = cleaned_data.get('salon')
        
        if master and salon and master.salon != salon:
            raise forms.ValidationError("Мастер не работает в выбранном салоне")
        
        return cleaned_data


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    form = RegistrationForm
    list_display = ('client', 'service', 'master_link', 'salon_link', 'service_date')
    
    def master_link(self, obj):
        return obj.master.name if obj.master else "Не выбран"
    master_link.short_description = 'Мастер'
    
    def salon_link(self, obj):
        return obj.salon.address if obj.salon else "Не выбран"
    salon_link.short_description = 'Салон'


admin.site.register(Client)
admin.site.register(Master)
