"""Users serializers."""

# Django REST Framework
from api.orders.models.offers import Offer
from api.orders.serializers.offers import OfferModelSerializer
from rest_framework import serializers

# Django
from django.conf import settings
from django.shortcuts import get_object_or_404


# Models
from api.orders.models import Order
from api.users.models import User

# Utils
from api.utils import helpers


class OrderModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = Order
        fields = (
            "__all__"
        )

        read_only_fields = ("id",)


class AcceptOrderSerializer(serializers.Serializer):
    """Acount verification serializer."""
    card_name = serializers.CharField()
    payment_method_id = serializers.CharField()
    order = OrderModelSerializer(read_only=True)

    def validate(self, data):
        """Update user's verified status."""

        payment_method_id = data['payment_method_id']
        offer = self.context['offer']
        stripe = self.context['stripe']
        request = self.context['request']
        user = request.user
        # Check if offer is not accepted
        if 'accepted' in offer and offer['accepted']:
            raise serializers.ValidationError(
                "This offer is already accepted")
        try:

            if not user.stripe_customer_id:

                new_customer = stripe.Customer.create(
                    description="claCustomer_"+user.first_name+'_'+user.last_name,
                    name=user.first_name+' '+user.last_name,
                    email=user.email,
                )
                user.stripe_customer_id = new_customer['id']
                user.save()
            product = stripe.Product.create(name=offer['title'] + '_' + user.username)
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=user.stripe_customer_id,
            )
            stripe.PaymentMethod.modify(
                payment_method_id,
                billing_details={
                    "name": data.get('card_name', " "),
                }
            )
            if not 'type' in offer:
                raise serializers.ValidationError(
                    "Not a valid order type")

            if not 'seller' in offer:
                raise serializers.ValidationError(
                    "Not seller in offer")
            seller = get_object_or_404(User, id=offer['seller'])
            if not 'unit_amount' in offer:
                raise serializers.ValidationError(
                    "Not unit amount in offer")
            unit_amount = float(offer['unit_amount'])
            if not 'service_fee' in offer:
                raise serializers.ValidationError(
                    "There is not service fee in this offer")
            service_fee = float(offer['service_fee'])

            price = None
            if offer['type'] == Order.NORMAL_ORDER:
                price = stripe.Price.create(
                    unit_amount=int(unit_amount * 100),
                    currency=user.currency,
                    product=product['id']
                )
                invoice_item = stripe.InvoiceItem.create(
                    customer=user.stripe_customer_id,
                    price=price.id,
                )
                invoice = stripe.Invoice.create(
                    customer=user.stripe_customer_id,
                    # transfer_data={
                    #     "destination": serialised_course.get('instructor').get('profile').get('stripe_account_id'),
                    # },
                    default_payment_method=payment_method_id
                )
                user.default_payment_method = payment_method_id
                user.save()
                invoice_paid = stripe.Invoice.pay(invoice['id'])
                # Invoice paid succesfully, do actions
            elif offer['type'] == Order.TWO_PAYMENTS_ORDER:

                price = stripe.Price.create(
                    unit_amount=int(unit_amount * 100),
                    currency=user.currency,
                    product=product['id']
                )
                invoice_item = stripe.InvoiceItem.create(
                    customer=user.stripe_customer_id,
                    price=price.id,
                )
                invoice = stripe.Invoice.create(
                    customer=user.stripe_customer_id,
                    transfer_data={
                        "destination": seller.stripe_account_id,
                    },
                    application_fee_amount=int(service_fee * 100),
                    # application_fee=5,
                    default_payment_method=payment_method_id
                )
                user.default_payment_method = payment_method_id
                user.save()
                invoice_paid = stripe.Invoice.pay(invoice['id'])
            elif offer['type'] == Order.RECURRENT_ORDER:
                if not 'interval_subscription' in offer:
                    raise serializers.ValidationError(
                        "Not interval subscription in offer")
                switcher = {
                    Order.MONTH: "month",
                    Order.YEAR: "year"
                }
                interval = switcher.get(offer['interval_subscription'], None)
                if not interval:
                    raise serializers.ValidationError(
                        "Interval not valid")
                price = stripe.Price.create(
                    unit_amount=int(unit_amount * 100),
                    currency=user.currency,
                    recurring={"interval": interval},
                    product=product['id']
                )
                subscription = stripe.Subscription.create(
                    customer=user.stripe_customer_id,
                    items=[
                        {"price": price['id']}
                    ],
                )
            else:
                raise serializers.ValidationError(
                    "Not a valid order type")

        except stripe.error.StripeError as e:

            raise serializers.ValidationError(
                'Something went wrong with stripe')
        except Exception as e:

            raise serializers.ValidationError(
                'Something went wrong')

        return data

    def create(self, validated_data):
        offer = self.context['offer']

        offer_object = Offer.objects.get(id=offer['id'])
        new_order = Order.objects.create(
            buyer=offer_object.buyer,
            seller=offer_object.seller,
            title=offer_object.title,
            description=offer_object.description,
            unit_amount=offer_object.unit_amount,
            first_payment=offer_object.first_payment,
            payment_at_delivery=offer_object.payment_at_delivery,
            delivery_date=offer_object.delivery_date,
            delivery_time=offer_object.delivery_time,
            interval_subscription=offer_object.interval_subscription,
            type=offer_object.type
        )
        offer_object.accepted = True
        offer_object.save()
        return new_order
