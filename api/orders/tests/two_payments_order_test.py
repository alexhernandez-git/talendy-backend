
"""Invitations tests."""

# Django
from django.test import TestCase

# Django REST Framework
from rest_framework import status
from rest_framework.test import APITestCase

# Model
from api.users.models import User
from rest_framework.authtoken.models import Token

# Utils
import stripe
from api.utils import helpers

# Tests
from api.users.tests.register_test import SetupUsersInitialData


class TwoPaymentsOrderAPITestCase(SetupUsersInitialData):

    def setUp(self):
        super().setUp()
        stripe.api_key = 'sk_test_51I4AQuCob7soW4zYOgn6qWIigjeue6IGon27JcI3sN00dAq7tPJAYWx9vN8iLxSbfFh4mLxTW3PhM33cds8GBuWr00P3tPyMGw'
        self.stripe = stripe

        # In dollars
        self.buyer_credits = 10
        self.buyer.net_income = self.buyer_credits
        self.buyer.available_for_withdrawal = self.buyer_credits
        self.buyer.save()

        self.create_offer()

        self.accept_offer()

    def create_offer(self):
        offer_data = {
            "buyer": self.buyer.id,
            "buyer_email": "",
            "delivery_time": "7",
            "send_offer_by_email": False,
            "title": "Two payments order",
            "description": "Two payments order offer",
            "first_payment": "50",
            "type": "TP",
            "unit_amount": "100"
        }

        self.client.credentials(HTTP_AUTHORIZATION="Token {}".format(self.seller_token))

        create_offer_response = self.client.post("/api/offers/", offer_data)
        self.create_offer_response = create_offer_response
        self.offer = create_offer_response.data

    def accept_offer(self):
        # Convert the offer in buyer currency
        offer = self.offer
        buyer = self.buyer

        currencyRate, _ = helpers.get_currency_rate(buyer.currency, offer['rate_date'])
        subtotal = float(offer['first_payment']) * currencyRate
        first_payment = subtotal
        payment_at_delivery = float(offer['payment_at_delivery']) * currencyRate
        fixed_price = 0.3 * currencyRate
        service_fee = (subtotal * 5) / 100 + fixed_price
        unit_amount = subtotal + service_fee
        available_for_withdrawal = (float(buyer.available_for_withdrawal.amount) +
                                    float(buyer.pending_clearance.amount))
        used_credits = 0
        if available_for_withdrawal > 0:
            if available_for_withdrawal > subtotal:
                used_credits = subtotal
            else:
                diff = available_for_withdrawal - subtotal
                used_credits = subtotal + diff

        offer['subtotal'] = round(subtotal, 2)
        offer['service_fee'] = round(service_fee, 2)
        offer['unit_amount'] = round(unit_amount, 2)
        offer['used_credits'] = round(used_credits, 2)
        offer['first_payment'] = round(first_payment, 2)
        offer['payment_at_delivery'] = round(payment_at_delivery, 2)

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

        # Send accepting offer
        order_data = {
            "offer": offer,
            "payment_method_id": payment_method['id']
        }

        accept_order_response = self.client.post("/api/orders/", order_data, format='json')
        self.accept_order_response = accept_order_response
        self.order = accept_order_response.data

    def test_is_offer_created(self):
        self.assertEqual(self.create_offer_response.status_code, status.HTTP_201_CREATED)

    def test_if_payment_method_has_been_attached(self):
        self.assertEqual(self.attach_payment_method_response.status_code, status.HTTP_200_OK)

    def test_is_offer_accepted(self):
        self.assertEqual(self.accept_order_response.status_code, status.HTTP_201_CREATED)
