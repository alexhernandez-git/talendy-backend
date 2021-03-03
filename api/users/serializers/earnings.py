
"""Users serializers."""

# Django REST Framework
from rest_framework import serializers

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

# Models
from api.users.models import Earning, User
from djmoney.models.fields import Money

# Utils


class EarningModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = Earning
        fields = (
            "id",
            "type",
            "amount",
            "created",
        )

        read_only_fields = ("id",)


class WithdrawFundsModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = Earning
        fields = (
            "id",
            "type",
            "amount",
            "created",
        )

        read_only_fields = (
            "id",
            "type",
            "created",
        )

    def validate(self, data):
        amount = Money(amount=data['amount'], currency="USD")
        request = self.context['request']
        user = request.user
        if amount > user.available_for_withdawal:
            raise serializers.ValidationError('The amount is greater than your budget')

        if not user.stripe_account_id:
            raise serializers.ValidationError('You don\'t have a stripe account')

        return data

    def create(self, validated_data):
        from api.utils.helpers import convert_currency
        amount = Money(amount=validated_data['amount'], currency="USD")
        stripe = self.context['stripe']
        request = self.context['request']
        user = request.user

        converted_unit_amount, rate_date = convert_currency('USD', user.currency, validated_data['amount'])
        transfer = stripe.Transfer.create(
            amount=int(converted_unit_amount * 100),
            currency=user.currency,
            destination=user.stripe_account_id,
        )

        withdrawn = Earning.objects.create(
            type=Earning.WITHDRAWN,
            amount=amount,
            transfer_id=transfer['id'],
            user=user
        )

        user.withdrawn = user.withdrawn + amount
        user.available_for_withdawal = user.available_for_withdawal - amount
        user.save()

        return withdrawn
