import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Create or recover the cloud administrator using a private environment variable"

    def handle(self, *args, **options):
        password = os.environ.get("ADMIN_RESET_PASSWORD")
        if not password:
            raise CommandError("ADMIN_RESET_PASSWORD is not configured")
        User = get_user_model()
        user, created = User.objects.get_or_create(username="cloud_admin")
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(self.style.SUCCESS("Administrator credentials configured successfully."))
