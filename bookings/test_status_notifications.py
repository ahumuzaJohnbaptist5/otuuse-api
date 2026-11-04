from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from .models import Booking, Driver, Service

class DriverStatusNotificationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        staff = User.objects.create_user(username="staff_test", password="testpass", is_staff=True)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + Token.objects.create(user=staff).key)
        driver_user = User.objects.create_user(username="driver_test", email="driver@example.com")
        self.driver = Driver.objects.create(user=driver_user, phone="0700000000")
        service = Service.objects.create(name="Test Ride", slug="status-test")
        self.booking = Booking.objects.create(customer_name="Test", phone="0700000001",
            service=service, pickup="A", destination="B", driver=self.driver)

    @patch("bookings.notifications.send_booking_status_email")
    def test_status_change_triggers_notification(self, notify):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(f"/api/admin/bookings/{self.booking.pk}/",
                {"status": "CONFIRMED"}, format="json")
        self.assertEqual(response.status_code, 200)
        notify.assert_called_once_with(self.booking.pk, self.driver.pk, "CONFIRMED")

    @patch("bookings.notifications.send_booking_status_email")
    def test_unchanged_status_does_not_notify(self, notify):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(f"/api/admin/bookings/{self.booking.pk}/",
                {"status": "PENDING"}, format="json")
        self.assertEqual(response.status_code, 200)
        notify.assert_not_called()
