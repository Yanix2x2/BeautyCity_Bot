from django.contrib import admin
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
    list_filter = ('treatment',) 
    search_fields = ('treatment',)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('admin/css/autocomplete.css',)}
        js = ('admin/js/autocomplete.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['master'].widget = autocomplete.ModelSelect2(
            url='master-autocomplete',
            forward=['salon']
        )
        return form


admin.site.register(Client)
admin.site.register(Master)
