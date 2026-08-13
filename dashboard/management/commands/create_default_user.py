from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Crea un usuario por defecto si no existe'

    def handle(self, *args, **options):
        username = os.environ.get('DEFAULT_USER', 'admin')
        password = os.environ.get('DEFAULT_PASSWORD', 'admin123')
        email = os.environ.get('DEFAULT_EMAIL', 'admin@example.com')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Usuario "{username}" creado correctamente'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Usuario "{username}" ya existe'
                )
            )
