from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Booking, Driver, Service


@api_view(["POST"])
@permission_classes([AllowAny])
def admin_login(request):
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active or not user.is_staff:
        return Response({"detail": "Invalid administrator credentials."}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})


class StaffView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]


class DashboardView(StaffView):
    def get(self, request):
        return Response({
            "bookings": Booking.objects.count(),
            "pending": Booking.objects.filter(status="PENDING").count(),
            "confirmed": Booking.objects.filter(status="CONFIRMED").count(),
            "assigned": Booking.objects.filter(status="ASSIGNED").count(),
            "completed": Booking.objects.filter(status="COMPLETED").count(),
            "drivers": Driver.objects.count(),
            "services": Service.objects.filter(is_active=True).count(),
        })


class BookingListView(StaffView):
    def get(self, request):
        bookings = Booking.objects.select_related("service", "driver__user").order_by("-created_at")[:200]
        return Response([{
            "id": b.id, "customer_name": b.customer_name, "phone": b.phone,
            "service": b.service.name, "pickup": b.pickup, "destination": b.destination,
            "notes": b.notes, "status": b.status, "driver_id": b.driver_id,
            "driver": str(b.driver) if b.driver else None, "created_at": b.created_at,
        } for b in bookings])


class DriverListView(StaffView):
    def get(self, request):
        return Response([{
            "id": d.id, "name": d.user.get_full_name() or d.user.username,
            "email": d.user.email, "phone": d.phone, "status": d.status,
            "vehicle_type": d.vehicle_type,
        } for d in Driver.objects.select_related("user").order_by("id")])


class ServiceAdminListView(StaffView):
    def get(self, request):
        return Response(list(Service.objects.values("id", "name", "is_active", "base_price_ugx", "per_km_ugx").order_by("id")))


class BookingUpdateView(StaffView):
    def patch(self, request, booking_id):
        from django.db import transaction
        from django.shortcuts import get_object_or_404
        from .notifications import send_assignment_email
        with transaction.atomic():
            booking = get_object_or_404(Booking.objects.select_for_update(), pk=booking_id)
            old_driver = booking.driver_id
            if "driver_id" in request.data:
                driver_id = request.data["driver_id"]
                if driver_id in ("", None):
                    booking.driver = None
                else:
                    booking.driver = get_object_or_404(Driver, pk=driver_id)
            if "status" in request.data:
                allowed = {choice[0] for choice in Booking.Status.choices}
                if request.data["status"] not in allowed:
                    return Response({"detail": "Invalid booking status."}, status=400)
                booking.status = request.data["status"]
            if booking.driver_id and old_driver != booking.driver_id and "status" not in request.data:
                booking.status = Booking.Status.ASSIGNED
            booking.save()
            if booking.driver_id and old_driver != booking.driver_id:
                bid, did = booking.id, booking.driver_id
                transaction.on_commit(lambda: send_assignment_email(bid, did))
        return Response({"id": booking.id, "status": booking.status, "driver_id": booking.driver_id})


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_logout(request):
    request.auth.delete()
    return Response({"detail": "Logged out."})
