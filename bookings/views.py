from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from .models import Service, Booking
from .serializers import ServiceSerializer, BookingSerializer

TRACKING_SALT = "otuuse-customer-booking-tracking-v1"

class ServiceList(generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

class BookingCreate(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        booking_id = response.data["id"]
        response.data["tracking_token"] = signing.dumps({"booking_id": booking_id}, salt=TRACKING_SALT)
        return response

class BookingTracking(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "booking_tracking"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        token = request.data.get("tracking_token")
        if not isinstance(token, str) or len(token) > 1024 or not token:
            return Response({"detail": "A valid tracking token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = signing.loads(token, salt=TRACKING_SALT, max_age=60 * 60 * 24 * 90)
            booking_id = payload["booking_id"]
        except (BadSignature, SignatureExpired, KeyError, TypeError, ValueError):
            return Response({"detail": "Tracking link is invalid or expired."}, status=status.HTTP_404_NOT_FOUND)
        booking = Booking.objects.select_related("service").filter(pk=booking_id).first()
        if not booking:
            return Response({"detail": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "id": booking.id,
            "service": booking.service.name,
            "status": booking.status,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at,
        })
