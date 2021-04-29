from django.core.management.base import BaseCommand
from api.communities.models import Community


class Command(BaseCommand):

    def handle(self, *args, **options):
        Community.objects.all().delete()
        Community.objects.create(name="Development")
        Community.objects.create(name="Business")
        Community.objects.create(name="Finance & Accounting")
        Community.objects.create(name="IT & Software")
        Community.objects.create(name="Office Productivity")
        Community.objects.create(name="Personal Development")
        Community.objects.create(name="Design")
        Community.objects.create(name="Marketing")
        Community.objects.create(name="Health & Fitness")
        Community.objects.create(name="Music")
