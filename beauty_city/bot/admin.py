from django.contrib import admin

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


admin.site.register(Client)
admin.site.register(Master)
admin.site.register(Registration)
