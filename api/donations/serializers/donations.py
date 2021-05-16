
"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

# Models
from api.donations.models import Donation, DonationOption, DonationPayment
from api.users.models import User, Earning

# Serializers
from api.users.serializers import UserModelSerializer
from .donation_payments import DonationPaymentModelSerializer
from .donation_options import DonationOptionModelSerializer

# Utils
import string
import random
from api.utils import helpers
from datetime import timedelta
from django.utils import timezone


class DonationModelSerializer(serializers.ModelSerializer):
    """User model serializer."""
    from_user = UserModelSerializer(read_only=True)
    donation_option = DonationOptionModelSerializer(required=False)
    donation_payment = DonationPaymentModelSerializer(read_only=True)

    class Meta:
        """Meta class."""

        model = Donation
        fields = (
            "id",
            "is_other_amount",
            "donation_option",
            "donation_payment",
            "from_user",
            "usd_amount",
            "created"
        )

        read_only_fields = ("id", "usd_amount")


class CreateDonationSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField()
    donation_option = serializers.UUIDField(required=False)
    other_amount = serializers.FloatField(required=False)
    to_user = serializers.UUIDField()

    def validate(self, data):
        stripe = self.context['stripe']
        payment_method_id = data['payment_method_id']
        to_user = get_object_or_404(User, id=data['to_user'])
        user = None
        is_anonymous = True
        if self.context['request'].user.id:
            user = self.context['request'].user
            is_anonymous = False
        donation_option = None
        if 'donation_option' in data and data['donation_option']:
            donation_option = get_object_or_404(DonationOption, id=data['to_user'])
        other_amount = None
        if 'other_amount' in data and data['other_amount']:
            other_amount = data['other_amount']

        # Check if there is almost one of the donation_option and other amount
        if not donation_option and not other_amount:
            raise serializers.ValidationError(
                "You need at least one of the two amount options")
        is_other_amount = False
        if other_amount:
            is_other_amount = True
        # If there is not, create stripe customer account and save the stripe customer id

        rand_string = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=10))

        if not is_anonymous and user:
            if user.stripe_customer_id:
                stripe_customer_id = user
            else:
                new_customer = stripe.Customer.create(
                    description="talenCustomer_" + user.first_name + '_' + user.last_name,
                    name=user.first_name + ' ' + user.last_name, email=user.email + rand_string,)
                stripe_customer_id = new_customer['id']
                user.stripe_customer_id = stripe_customer_id
                user.save()

            # Add to default paymet method this payment id
            stripe.Customer.modify(
                stripe_customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
        else:

            new_customer = stripe.Customer.create(
                description="talenAnonymousCustomer_"+rand_string,
                name=rand_string,
            )
            stripe_customer_id = new_customer['id']

        # If is other amount create the new stripe product and price
        if is_other_amount:
            if not is_anonymous and user:

                product = stripe.Product.create(name=other_amount + '_donation_by_' + user.username)
            else:
                product = stripe.Product.create(name=other_amount + '_donation_' + rand_string)
            price = stripe.Price.create(
                unit_amount=int(other_amount * 100),
                currency=user.currency,
                product=product['id']
            )

        # If is donation option retrieve it
        else:
            product = stripe.Product.retrieve(donation_option.stripe_product_id)
            price = stripe.Price.retrieve(donation_option.stripe_price_id)

        # Create the stripe invocie item
        stripe.InvoiceItem.create(
            customer=stripe_customer_id,
            price=price['id'],
        )

        # Create the invocie
        invoice = stripe.Invoice.create(
            customer=stripe_customer_id,
            default_payment_method=payment_method_id

        )
        if not is_anonymous and user:

            user.default_payment_method = payment_method_id
            user.save()

        # Pay the invocie
        invoice_paid = stripe.Invoice.pay(invoice['id'])

        # Convert the amount paid to USD
        if is_other_amount:

            gross_amount, rate_date = helpers.convert_currency('USD', user.currency, other_amount)
        else:
            gross_amount, rate_date = helpers.convert_currency(
                'USD', donation_option.currency, donation_option.unit_amount)

        # Get and substract the service fee (5%)
        service_fee = (gross_amount * 5) / 100
        net_amount = gross_amount - service_fee
        # Pass to data the donation option or other amount, the user,
        # the  product, the price, the invoice paid and the to user
        return {
            'is_anonymous': is_anonymous,
            'user': user,
            'to_user': to_user,
            'is_other_amount': is_other_amount,
            'other_amount': other_amount,
            'donation_option': donation_option,
            'price': price,
            'product': product,
            'invoice_paid': invoice_paid,
            'gross_amount': gross_amount,
            'net_amount': net_amount,
            'service_fee': service_fee,
            'rate_date': rate_date

        }

    def create(self, validated_data):

        # Get the validated data
        is_anonymous = validated_data["is_anonymous"]
        to_user = validated_data["to_user"]
        user = validated_data["user"]
        is_other_amount = validated_data["is_other_amount"]
        other_amount = validated_data["other_amount"]
        donation_option = validated_data["donation_option"]
        price = validated_data["price"]
        product = validated_data["product"]
        invoice_paid = validated_data["invoice_paid"]
        gross_amount = validated_data["gross_amount"]
        net_amount = validated_data["net_amount"]
        service_fee = validated_data["service_fee"]
        rate_date = validated_data["rate_date"]

        # Create the donation payment
        invoice_id = invoice_paid['id']
        currency = invoice_paid['currency']
        charge_id = invoice_paid['charge']
        amount_paid = invoice_paid['amount_paid']
        status = invoice_paid['status']
        invoice_pdf = invoice_paid['invoice_pdf']

        donation_payment = DonationPayment.objects.create(
            invoice_id=invoice_id,
            invoice_pdf=invoice_pdf,
            charge_id=charge_id,
            amount_paid=float(amount_paid) / 100,
            currency=currency,
            status=status,
        )

        # Create the donation
        donation = Donation.objects.create(
            is_other_amount=is_other_amount,
            donation_option=donation_option,
            donation_payment=donation_payment,
            is_anonymous=is_anonymous,
            from_user=user,
            to_user=to_user,
            gross_amount=gross_amount,
            net_amount=net_amount,
            service_fee=service_fee,
            rate_date=rate_date,
        )

        # Create the to user earning
        Earning.objects.create(
            user=to_user,
            amount=net_amount,
            available_for_withdrawn_date=timezone.now() + timedelta(days=14)
        )

        # Add donations_received_count to to_user
        to_user.donations_received_count += 1
        to_user.net_income = to_user.net_income + net_amount

        to_user.pending_clearance += net_amount
        to_user.save()

        if not is_anonymous and user:
            user.donations_made_count += 1
            user.save()
        return donation
