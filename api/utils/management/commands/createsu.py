from django.core.management.base import BaseCommand
from api.users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):

        if not User.objects.filter(username="alexadmin").exists():
            User.objects.create_superuser(
                "alexadmin", "alexandrehernandez@talendy.com", "password123")
            print("Super user created")
