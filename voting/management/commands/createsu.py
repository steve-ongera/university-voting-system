from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create a default superuser for the custom Student model"

    def handle(self, *args, **kwargs):
        registration_number = "SC211/0001/1996"
        birth_certificate_number = "cp7kvt"

        if not User.objects.filter(registration_number=registration_number).exists():
            User.objects.create_superuser(
                registration_number=registration_number,
                birth_certificate_number=birth_certificate_number,
                first_name="Admin",
                last_name="User",
                email="admin@gmail.com",
                is_staff=True,
                is_superuser=True,
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS("✅ Superuser created successfully!"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Superuser already exists."))
