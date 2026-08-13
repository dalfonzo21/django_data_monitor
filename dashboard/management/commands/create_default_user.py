from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
import os


class Command(BaseCommand):
    help = 'Crea un usuario por defecto con todos los permisos'

    def handle(self, *args, **options):
        username = os.environ.get('DEFAULT_USER', 'admin')
        password = os.environ.get('DEFAULT_PASSWORD', 'admin123')
        email = os.environ.get('DEFAULT_EMAIL', 'admin@example.com')

        user, created = User.objects.get_or_create(username=username)
        
        if created:
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Usuario "{username}" creado correctamente'
                )
            )
        else:
            # Actualizar contraseña si el usuario ya existe
            user.set_password(password)
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.WARNING(
                    f'✓ Usuario "{username}" actualizado'
                )
            )
        
        # Asignar el permiso específico dashboard.index_viewer
        try:
            from dashboard.models import DashboardModel
            content_type = ContentType.objects.get_for_model(DashboardModel)
            permission = Permission.objects.get(
                content_type=content_type,
                codename='index_viewer'
            )
            user.user_permissions.add(permission)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Permiso "index_viewer" asignado'
                )
            )
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    'Permiso "index_viewer" no encontrado'
                )
            )

