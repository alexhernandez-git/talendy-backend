
"""Delivery normal order tests."""

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
from api.orders.tests.two_payments_order_test import TwoPaymentsOrderAPITestCase


class DeliveryTwoPaymentsOrderAPITestCase(TwoPaymentsOrderAPITestCase):
    def setUp(self):
        super().setUp()
        self.create_delivery()
        self.accept_delivery()

    def create_delivery(self):
        order = Order.objects.get(id=self.order['id'])

        # Attach payment method
        self.client.credentials(HTTP_AUTHORIZATION="Token {}".format(self.seller_token))

        delivery_data = {
            "response": "Here is your delivery",
            "order": order.id
        }
        delivery_response = self.client.post(
            '/api/orders/{}/deliveries/'.format(order.id), delivery_data, format='json')

        self.delivery_response = delivery_response
        self.delivery = delivery_response.data

    def accept_delivery(self):
        order = self.order
        delivery = self.delivery
        buyer = User.objects.get(id=self.buyer['id'])

        currencyRate, _ = helpers.get_currency_rate(buyer.currency, order['rate_date'])
        subtotal = float(order['payment_at_delivery']) * currencyRate

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
        order['subtotal'] = round(subtotal, 2)
        order['service_fee'] = round(service_fee, 2)
        order['unit_amount'] = round(unit_amount, 2)
        order['used_credits'] = round(used_credits, 2)

        # Petition data

        # Attach payment method
        self.client.credentials(HTTP_AUTHORIZATION="Token {}".format(self.buyer_token))

        # Send accepting oportunity
        buyer = User.objects.get(id=self.buyer['id'])
        order_data = {
            "order_checkout": order,
            "payment_method_id": buyer.default_payment_method
        }
        accept_delivery_response = self.client.patch(
            '/api/orders/{}/deliveries/{}/accept_delivery/'.format(order['id'],
                                                                   delivery['id']),
            order_data, format='json')
        self.accept_delivery_response = accept_delivery_response
        self.accepted_delivery = accept_delivery_response.data

        self.accept_delivery_response = accept_delivery_response

    def test_delivery_request_sent(self):

        self.assertEqual(self.delivery_response.status_code, status.HTTP_201_CREATED)

    def test_delivery_request_accepted(self):

        self.assertEqual(self.accept_delivery_response.status_code, status.HTTP_200_OK)
