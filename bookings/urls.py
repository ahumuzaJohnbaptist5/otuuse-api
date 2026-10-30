from django.urls import path
from . import views
from . import admin_api

urlpatterns = [
    path('admin/login/', admin_api.admin_login),
    path('admin/logout/', admin_api.admin_logout),
    path('admin/dashboard/', admin_api.DashboardView.as_view()),
    path('admin/bookings/', admin_api.BookingListView.as_view()),
    path('admin/bookings/<int:booking_id>/', admin_api.BookingUpdateView.as_view()),
    path('admin/drivers/', admin_api.DriverListView.as_view()),
    path('admin/drivers/<int:driver_id>/resend-welcome/', admin_api.DriverWelcomeResendView.as_view()),
    path('admin/services/', admin_api.ServiceAdminListView.as_view()),
    path('services/', views.ServiceList.as_view(), name='service-list'),
    path('bookings/', views.BookingCreate.as_view(), name='booking-create'),
]