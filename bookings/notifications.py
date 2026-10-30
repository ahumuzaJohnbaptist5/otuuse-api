import logging
from django.conf import settings
from django.core.mail import send_mail
from .models import Booking

logger = logging.getLogger(__name__)

def send_assignment_email(booking_id, driver_id):
    booking = Booking.objects.select_related("driver__user", "service").filter(pk=booking_id, driver_id=driver_id).first()
    if not booking:
        return
    driver = booking.driver.user
    if not driver.email:
        logger.warning("Driver %s has no email address", driver_id)
        return
    message = "\n".join([
        f"Hello {driver.get_full_name() or driver.username},", "",
        f"You have been assigned OTUUSE booking #{booking.id}.",
        f"Service: {booking.service.name}",
        f"Customer: {booking.customer_name}",
        f"Customer phone: {booking.phone}",
        f"Pickup: {booking.pickup}",
        f"Destination: {booking.destination}",
        f"Notes: {booking.notes or 'None'}", "",
        "Please contact the customer to coordinate the journey.",
    ])
    try:
        send_mail(f"OTUUSE: Booking assignment #{booking.id}", message, settings.DEFAULT_FROM_EMAIL, [driver.email], fail_silently=False)
    except Exception:
        logger.exception("Driver assignment email failed for booking %s", booking_id)


def send_driver_welcome_email(driver_id):
    from .models import Driver
    driver = Driver.objects.select_related("user").filter(pk=driver_id).first()
    if not driver or not driver.user.email:
        logger.warning("Driver %s has no email for registration notice", driver_id)
        return
    name = driver.user.get_full_name() or driver.user.username
    message = (
        f"Hello {name},\n\n"
        "You have been registered as a driver on the OTUUSE platform.\n"
        f"Driver ID: {driver.id}\n"
        f"Vehicle type: {driver.vehicle_type}\n"
        "Account status: Pending activation by OTUUSE administration.\n\n"
        "You will receive further instructions before accessing a driver account. "
        "Do not share passwords or verification codes with anyone.\n\n"
        "Welcome to OTUUSE!\nOTUUSE Administration"
    )
    try:
        send_mail("Welcome to OTUUSE - Driver Registration", message,
                  settings.DEFAULT_FROM_EMAIL, [driver.user.email], fail_silently=False)
    except Exception:
        logger.exception("Driver welcome email failed for driver %s", driver_id)
