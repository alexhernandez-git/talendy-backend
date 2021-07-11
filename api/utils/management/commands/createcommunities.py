from django.core.management.base import BaseCommand
from rest_framework.generics import get_object_or_404
from api.portals.models import Community, Portal


class Command(BaseCommand):

    def handle(self, *args, **options):
        Community.objects.all().delete()
        portal = get_object_or_404(Portal, url='oficial')
        Community.objects.create(name="Development", portal=portal)
        Community.objects.create(name="Business", portal=portal)
        Community.objects.create(name="Finance & Accounting", portal=portal)
        Community.objects.create(name="IT & Software", portal=portal)
        Community.objects.create(name="Office Productivity", portal=portal)
        Community.objects.create(name="Personal Development", portal=portal)
        Community.objects.create(name="Lifestyle", portal=portal)
        Community.objects.create(name="Photography & Video", portal=portal)
        Community.objects.create(name="Design", portal=portal)
        Community.objects.create(name="Marketing", portal=portal)
        Community.objects.create(name="Health & Fitness", portal=portal)
        Community.objects.create(name="Music", portal=portal)
        Community.objects.create(name="Teaching & Academics", portal=portal)
