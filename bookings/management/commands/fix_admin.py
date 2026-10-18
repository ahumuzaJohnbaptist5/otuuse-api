from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Force creates or fixes the cloud admin user'

    def handle(self, *args, **options):
        username = 'cloud_admin'
        email = 'admin@otuuse.com'
        password = 'OtuuseCloud2026!'
        
        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,      # CRITICAL for admin access
                'is_superuser': True,  # CRITICAL for full permissions
                'is_active': True
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✅ Created new admin: {username}'))
        else:
            # Even if user existed, force reset password and flags
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f' Fixed existing admin: {username}'))
