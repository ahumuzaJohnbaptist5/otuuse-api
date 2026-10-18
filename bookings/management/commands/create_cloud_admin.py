from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a cloud admin user if none exists'

    def handle(self, *args, **options):
        if not User.objects.filter(username='cloud_admin').exists():
            User.objects.create_superuser(
                username='cloud_admin',
                email='admin@otuuse.com',
                password='OtuuseCloud2026!'
            )
            self.stdout.write(self.style.SUCCESS('✅ Cloud Admin created!'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Admin already exists.'))
