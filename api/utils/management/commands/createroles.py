from django.core.management.base import BaseCommand
from api.portals.models import PortalRole


class Command(BaseCommand):

    def handle(self, *args, **options):
        PortalRole.objects.all().delete()

        PortalRole.objects.create(
            code="BASE"
        )
        PortalRole.objects.create(
            code="MODERATOR"
        )
        PortalRole.objects.create(
            code="ADMINISTRATOR"
        )
