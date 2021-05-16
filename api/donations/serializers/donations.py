
"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404


# Models
from api.donations.models import Donation, DonationOption
from api.users.models import User

# Serializers
from api.users.serializers import UserModelSerializer
from .donation_payments import DonationPaymentModelSerializer
from .donation_options import DonationOptionModelSerializer


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
        to_user = get_object_or_404(User, id=data['to_user'])
        user = None
        if self.context['request'].user.id:
            user = self.context['request'].user
        donation_option = None
        if 'donation_option' in data and data['donation_option']:
            donation_option = get_object_or_404(DonationOption, id=data['to_user'])
        other_amount = None
        if 'other_amount' in data and data['other_amount']:
            other_amount = data['other_amount']

        # Get user stripe customer id

        # If there is not, create stripe customer account and save the stripe customer id

        # Add to default paymet method this payment id

        # Check if there is almost one of the donation_option and other amount

        # If is other amount create the new stripe product and price

        # If is donation option retrieve it

        # Create the stripe invocie item

        # Create the invocie

        # Pay the invocie

        # Convert the amount paid to USD

        # Substract the transfer fee

        # Pass to data the donation option or other amount, the user,
        # the  product, the price, the invoice paid and the to user
        import pdb
        pdb.set_trace()
        pass

    def create(self, validated_data):
        # Get the validated data

        # Create the donation payment

        # Create the donation
        pass
