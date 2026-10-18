from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def home(request):
    return JsonResponse({
        "status": "online",
        "service": "Otuuse API",
        "endpoints": ["/admin/", "/api/services/", "/api/bookings/"],
    })


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/", include("bookings.urls")),
]