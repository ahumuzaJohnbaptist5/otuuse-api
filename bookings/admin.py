from django.contrib import admin
from .models import Service, Driver, Booking


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price_ugx", "per_km_ugx", "is_active")
    search_fields = ("name",)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "vehicle_type", "is_electric", "status", "rating")
    list_filter = ("status", "vehicle_type", "is_electric")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "service", "pickup", "destination", "status", "created_at")
    list_filter = ("status", "service")
    search_fields = ("customer_name", "phone", "pickup", "destination")
    date_hierarchy = "created_at"