from django.db import models
from django.contrib.auth.models import User


class Service(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    base_price_ugx = models.PositiveIntegerField(default=0)
    per_km_ugx = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Driver(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        BUSY = "BUSY", "Busy"
        OFFLINE = "OFFLINE", "Offline"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="driver")
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, blank=True)
    vehicle_type = models.CharField(max_length=20, default="boda")
    is_electric = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OFFLINE)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)

    def __str__(self):
        return f"{self.user.username} ({self.vehicle_type})"


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        ASSIGNED = "ASSIGNED", "Assigned"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="bookings")
    pickup = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    fare_quote_ugx = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer_name} - {self.service.name} ({self.status})"
    