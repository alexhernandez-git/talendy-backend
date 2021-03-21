# Django
from django.test import TestCase
from django.core.management import call_command

# Django REST Framework
from rest_framework import status
from rest_framework.test import APITestCase

# Model
from api.users.models import User

# Utils


class SetupUsersInitialData(APITestCase):
    def setUp(self):

        # Create the plans
        call_command("createplans")

        seller_data = {
            "email": "alex@gmail.com",
            "username": "alex",
            "password": "admin321",
            "password_confirmation": "admin321",
            "first_name": "Alex",
            "last_name": "Hernandez",
            "currency": "USD"
        }
        buyer_data = {
            "email": "ivan@gmail.com",
            "username": "ivan",
            "password": "admin321",
            "password_confirmation": "admin321",
            "first_name": "Ivan",
            "last_name": "Herms"
        }

        # Register seller
        seller_response = self.client.post("/api/users/signup_seller/", seller_data)
        self.seller_response = seller_response

        # Register buyer
        buyer_response = self.client.post("/api/users/signup_buyer/", buyer_data)
        self.buyer_response = buyer_response

        self.seller = User.objects.get(id=self.seller_response.data['user']['id'])

        self.seller_token = self.seller_response.data['access_token']

        self.buyer = User.objects.get(id=self.buyer_response.data['user']['id'])

        self.buyer_token = self.buyer_response.data['access_token']


class RegisterTestAPITestCase(SetupUsersInitialData):

    def test_is_seller_registered(self):
        """Seller should be created"""
        self.assertEqual(self.seller_response.status_code, status.HTTP_201_CREATED)

    def test_is_buyer_registered(self):
        """Buyer should be created"""
        self.assertEqual(self.buyer_response.status_code, status.HTTP_201_CREATED)
