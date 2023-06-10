from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    readonly_fields = [
        'request_date',
        'longitude',
        'latitude',
    ]
