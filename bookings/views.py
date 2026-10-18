from rest_framework import generics
from .models import Service, Booking
from .serializers import ServiceSerializer, BookingSerializer

# GET /api/services/ -> Returns the list of active services
class ServiceList(generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer

# POST /api/bookings/ -> Creates a new booking in the database
class BookingCreate(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer