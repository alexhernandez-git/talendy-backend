
"""Invitations tests."""

# Django
from django.test import TestCase

# Django REST Framework
from rest_framework import status
from rest_framework.test import APITestCase

# Model
from api.users.models import User, Earning
from api.orders.models import Order
from rest_framework.authtoken.models import Token

# Utils
import stripe
from api.utils import helpers

# Tests
from api.users.tests.register_test import SetupUsersInitialData


class TwoPaymentsOrderAPITestCase(SetupUsersInitialData):

    def setUp(self):
        super().setUp()
        stripe.api_key = 'sk_test_51IZy28Dieqyg7vAImOKb5hg7amYYGSzPTtSqoT9RKI69VyycnqXV3wCPANyYHEl2hI7KLHHAeIPpC7POg7I4WMwi00TSn067f4'
        self.stripe = stripe

        # In dollars
        buyer = User.objects.get(id=self.buyer['id'])

        self.buyer_credits = 75
        buyer.net_income = self.buyer_credits
        buyer.available_for_withdrawal = self.buyer_credits
        buyer.save()

        self.create_oportunity()

        self.accept_oportunity()

    def create_oportunity(self):
        oportunity_data = {
            "buyer": self.buyer['id'],
            "buyer_email": "",
            "delivery_time": "7",
            "send_oportunity_by_email": False,
            "title": "Two payments order",
            "description": "Two payments order oportunity",
            "first_payment": "50",
            "type": "TP",
            "unit_amount": "100"
        }

        self.client.credentials(HTTP_AUTHORIZATION="Token {}".format(self.seller_token))

        create_oportunity_response = self.client.post("/api/oportunities/", oportunity_data)
        self.create_oportunity_response = create_oportunity_response
        self.oportunity = create_oportunity_response.data

    def accept_oportunity(self):
        # Convert the oportunity in buyer currency
        oportunity = self.oportunity
        buyer = User.objects.get(id=self.buyer['id'])

        currencyRate, _ = helpers.get_currency_rate(buyer.currency, oportunity['rate_date'])
        subtotal = float(oportunity['first_payment']) * currencyRate
        first_payment = subtotal
        payment_at_delivery = float(oportunity['payment_at_delivery']) * currencyRate

        available_for_withdrawal = (float(buyer.available_for_withdrawal.amount) +
                                    float(buyer.pending_clearance.amount)) * currencyRate
        used_credits = 0
        if available_for_withdrawal > 0:
            if available_for_withdrawal > subtotal:
                used_credits = subtotal
            else:
                diff = available_for_withdrawal - subtotal
                used_credits = subtotal + diff
        fixed_price = 0.3 * currencyRate
        service_fee = ((subtotal - used_credits) * 5) / 100 + fixed_price
        unit_amount = subtotal + service_fee

        oportunity['subtotal'] = round(subtotal, 2)
        oportunity['service_fee'] = round(service_fee, 2)
        oportunity['unit_amount'] = round(unit_amount, 2)
        oportunity['used_credits'] = round(used_credits, 2)
        oportunity['first_payment'] = round(first_payment, 2)
        oportunity['payment_at_delivery'] = round(payment_at_delivery, 2)

        # Petition data

        # Get the payment method id
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": "4242424242424242",
                "exp_month": 3,
                "exp_year": 2022,
                "cvc": "314",
            },
        )

        # Attach payment method
        self.client.credentials(HTTP_AUTHORIZATION="Token {}".format(self.buyer_token))

        attach_payment_method_data = {
            "payment_method_id": payment_method['id'],
            "card_name": "Ivan Herms"
        }
        attach_payment_method_response = self.client.patch(
            "/api/users/attach_payment_method/", attach_payment_method_data, format='json')
        self.attach_payment_method_response = attach_payment_method_response

        # Send accepting oportunity
        order_data = {
            "oportunity": oportunity,
            "payment_method_id": payment_method['id']
        }

        accept_order_response = self.client.post("/api/orders/", order_data, format='json')
        self.accept_order_response = accept_order_response
        self.order = accept_order_response.data

    def test_is_oportunity_created(self):
        self.assertEqual(self.create_oportunity_response.status_code, status.HTTP_201_CREATED)

    def test_if_payment_method_has_been_attached(self):
        self.assertEqual(self.attach_payment_method_response.status_code, status.HTTP_200_OK)

    def test_is_oportunity_accepted(self):
        self.assertEqual(self.accept_order_response.status_code, status.HTTP_201_CREATED)
