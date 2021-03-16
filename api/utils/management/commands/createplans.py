from django.core.management.base import BaseCommand
from api.plans.models import Plan


class Command(BaseCommand):

    def handle(self, *args, **options):

        Plan.objects.create(
            type=Plan.BASIC,
            unit_amount=9.99,
            currency="EUR",
            price_label="9.99€"
        )
        Plan.objects.create(
            type=Plan.BASIC,
            unit_amount=12.99,
            currency="USD",
            price_label="$11.99"
        )
