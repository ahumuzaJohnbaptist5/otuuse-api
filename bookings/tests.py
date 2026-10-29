from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import Booking, Service


class BookingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.active = Service.objects.create(name="Boda", slug="boda", is_active=True)
        self.inactive = Service.objects.create(name="Inactive", slug="inactive", is_active=False)
        self.payload = {
            "customer_name": "Test Customer",
            "phone": "0700000000",
            "service": self.active.pk,
            "pickup": "Kabale",
            "destination": "Town",
        }

    def test_active_services_only(self):
        response = self.client.get("/api/services/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["slug"] for item in response.data], ["boda"])

    def test_booking_created_with_server_controlled_status(self):
        response = self.client.post("/api/bookings/", {**self.payload, "status": "COMPLETED"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Booking.objects.get(pk=response.data["id"]).status, Booking.Status.PENDING)

    def test_inactive_service_rejected(self):
        response = self.client.post("/api/bookings/", {**self.payload, "service": self.inactive.pk}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Booking.objects.count(), 0)

    def test_missing_required_fields_rejected(self):
        response = self.client.post("/api/bookings/", {"customer_name": "Test"}, format="json")
        self.assertEqual(response.status_code, 400)
