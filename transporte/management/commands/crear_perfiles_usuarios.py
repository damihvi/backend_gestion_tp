from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from transporte.models import UserProfile


class Command(BaseCommand):
    help = 'Crear perfiles para usuarios existentes sin perfil'

    def handle(self, *args, **options):
        usuarios_sin_perfil = User.objects.filter(profile__isnull=True)
        count = 0
        
        for user in usuarios_sin_perfil:
            UserProfile.objects.create(user=user, is_conductor=False)
            count += 1
            self.stdout.write(f'Perfil creado para: {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'Se crearon {count} perfiles'))
