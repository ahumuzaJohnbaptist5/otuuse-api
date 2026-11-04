from django.test import TestCase
from rest_framework.test import APIClient
from .models import Service

class BookingTrackingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.service = Service.objects.create(name="Test Ride", slug="test-ride", is_active=True)

    def test_tracking_token_required_and_status_visible(self):
        created = self.client.post("/api/bookings/", {
            "customer_name": "Customer", "phone": "0700000000",
            "service": self.service.pk, "pickup": "Campus",
            "destination": "Town"
        }, format="json")
        self.assertEqual(created.status_code, 201)
        token = created.data["tracking_token"]
        self.assertTrue(token)
        tracked = self.client.post("/api/bookings/track/", {"tracking_token": token}, format="json")
        self.assertEqual(tracked.status_code, 200)
        self.assertEqual(tracked.data["status"], "PENDING")
        self.assertNotIn("phone", tracked.data)
        self.assertNotIn("customer_name", tracked.data)

    def test_invalid_token_cannot_access_booking(self):
        response = self.client.post("/api/bookings/track/", {"tracking_token": "invalid"}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_tracking_reflects_updated_booking_status(self):
        created = self.client.post("/api/bookings/", {
            "customer_name": "Customer", "phone": "0700000000",
            "service": self.service.pk, "pickup": "Campus",
            "destination": "Town"
        }, format="json")
        from .models import Booking
        booking = Booking.objects.get(pk=created.data["id"])
        booking.status = Booking.Status.ASSIGNED
        booking.save()
        tracked = self.client.post("/api/bookings/track/", {
            "tracking_token": created.data["tracking_token"]
        }, format="json")
        self.assertEqual(tracked.status_code, 200)
        self.assertEqual(tracked.data["status"], "ASSIGNED")
        self.assertNotIn("driver", tracked.data)
