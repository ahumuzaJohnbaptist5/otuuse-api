from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.ServiceList.as_view(), name='service-list'),
    path('bookings/', views.BookingCreate.as_view(), name='booking-create'),
]