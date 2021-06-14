from django.core.management.base import BaseCommand
from api.plans.models import Plan


class Command(BaseCommand):

    def handle(self, *args, **options):

        Plan.objects.create(
            type=Plan.SILVER,
            interval=Plan.MONTHLY,
            unit_amount=99.99,
            users_amount=50,
            currency="EUR",
            price_label="99.99€",
            stripe_price_id="price_1J2GwJKRJ23zrNRs6lQ9yQTw",
            stripe_product_id="prod_JfcAeK8Jf6tlWl"
        )
        Plan.objects.create(
            type=Plan.GOLD,
            interval=Plan.MONTHLY,
            unit_amount=149.99,
            users_amount=100,
            currency="EUR",
            price_label="149.99€",
            stripe_price_id="price_1J2GwlKRJ23zrNRsfAXwVdnP",
            stripe_product_id="prod_JfcBUSbjQhWqyI"
        )
        Plan.objects.create(
            type=Plan.PLATINUM,
            interval=Plan.MONTHLY,
            unit_amount=299.99,
            users_amount=200,
            currency="EUR",
            price_label="299.99€",
            stripe_price_id="price_1J2GxjKRJ23zrNRsmtmhtwqe",
            stripe_product_id="prod_JfcCaJ89gok4m1"
        )

        print("Plans created")
