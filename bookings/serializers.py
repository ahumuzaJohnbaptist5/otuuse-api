from rest_framework import serializers
from .models import Service, Booking

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'slug', 'base_price_ugx', 'per_km_ugx', 'description']

class BookingSerializer(serializers.ModelSerializer):
    # This lets us see the service name in the JSON instead of just an ID number
    service_name = serializers.CharField(source='service.name', read_only=True) 

    def validate_service(self, service):
        if not service.is_active:
            raise serializers.ValidationError("This service is currently unavailable.")
        return service

    class Meta:
        model = Booking
        fields = [
            'id', 'customer_name', 'phone', 'service', 'service_name', 
            'pickup', 'destination', 'notes', 'status', 'created_at'
        ]
        # The agent decides the status, and the server decides the time. Customers can't fake these.
        read_only_fields = ['status', 'created_at'] 