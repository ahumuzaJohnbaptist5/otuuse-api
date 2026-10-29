import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Reset the existing cloud administrator password"

    def handle(self, *args, **options):
        password = os.environ.get("ADMIN_RESET_PASSWORD")

        if not password:
            raise CommandError(
                "ADMIN_RESET_PASSWORD is not configured"
            )

        User = get_user_model()

        try:
            user = User.objects.get(username="cloud_admin")
        except User.DoesNotExist:
            raise CommandError(
                "Administrator not found. Check database persistence."
            )

        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Administrator password reset successfully."
            )
        )
