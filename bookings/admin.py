import logging
from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.db import transaction

logger = logging.getLogger(__name__)
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
    def save_model(self, request, obj, form, change):
        old_driver_id = (
            Booking.objects.filter(pk=obj.pk).values_list("driver_id", flat=True).first()
            if change else None
        )
        super().save_model(request, obj, form, change)
        if not obj.driver_id or old_driver_id == obj.driver_id:
            return

        booking_id, driver_id = obj.pk, obj.driver_id

        def notify_driver():
            booking = Booking.objects.select_related("driver__user", "service").get(pk=booking_id)
            if booking.driver_id != driver_id:
                return
            driver = booking.driver.user
            if not driver.email:
                logger.warning("Driver %s has no email for booking %s", driver_id, booking_id)
                return
            body = "\n".join([
                f"Hello {driver.get_full_name() or driver.username},",
                "",
                f"You have been assigned OTUUSE booking #{booking.pk}.",
                f"Service: {booking.service.name}",
                f"Customer: {booking.customer_name}",
                f"Customer phone: {booking.phone}",
                f"Pickup: {booking.pickup}",
                f"Destination: {booking.destination}",
                f"Notes: {booking.notes or 'None'}",
                "",
                "Please contact the customer to coordinate the journey.",
            ])
            try:
                send_mail(
                    f"OTUUSE: Booking assignment #{booking.pk}",
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [driver.email],
                    fail_silently=False,
                )
            except Exception:
                logger.exception("Failed to notify driver for booking %s", booking_id)

        transaction.on_commit(notify_driver)
