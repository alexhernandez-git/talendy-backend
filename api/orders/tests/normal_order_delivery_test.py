
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
from api.orders.tests.normal_order_test import NormalOrderAPITestCase


class DeliveryNormalOrderAPITestCase(NormalOrderAPITestCase):
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
        order = Order.objects.get(id=self.order['id'])
        self.client.credentials(HTTP_AUTHORIZATION="Token {}".format(self.buyer_token))

        accept_delivery_response = self.client.patch(
            '/api/orders/{}/deliveries/{}/accept_delivery/'.format(order.id, self.delivery['id']), {}, format='json')

        self.accept_delivery_response = accept_delivery_response

    def test_delivery_request_sent(self):

        self.assertEqual(self.accept_delivery_response.status_code, status.HTTP_200_OK)
