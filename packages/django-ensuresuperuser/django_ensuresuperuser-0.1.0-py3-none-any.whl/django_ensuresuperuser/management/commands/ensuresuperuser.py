import os
import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates an admin user non-interactively if it doesn't exist"

    def handle(self, *args, **options):
        User = get_user_model()

        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", None)
        if not password:
            self.stderr.write(self.style.ERROR("DJANGO_SUPERUSER_PASSWORD environment variable is not set"))
            sys.exit(1)

        default_email = "admin@example.com"
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", None)
        if not email:
            self.stderr.write(self.style.ERROR(f"DJANGO_SUPERUSER_EMAIL environment variable is not set, using the {default_email=}"))

        email = email or default_email

        if User.objects.filter(username="admin").exists():
            self.stdout.write(self.style.SUCCESS("Admin user already exists"))
        else:
            User.objects.create_superuser(
                username="admin",
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS("Admin user created"))
