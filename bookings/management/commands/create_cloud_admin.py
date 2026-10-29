from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Deprecated: use fix_admin with ADMIN_RESET_PASSWORD"

    def handle(self, *args, **options):
        raise CommandError("Use fix_admin with ADMIN_RESET_PASSWORD instead.")
