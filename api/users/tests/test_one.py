# Django
from django.test import TestCase

# Model
from api.users.models import User

# Utils
from faker import Faker

fakegen = Faker()


class TestTestCase(TestCase):
    def setUp(self):

        fake_first_name = fakegen.first_name()
        fake_last_name = fakegen.last_name()
        fake_email = fakegen.email()
        fake_username = fakegen.email()
        user = User.objects.create(
            first_name=fake_first_name,
            last_name=fake_last_name,
            email=fake_email,
            username=fake_username,
        )
        user.set_password("admin321")
        user.save()
        self.user = user

    def test_one(self):
        """Random user should be generated"""
        self.assertIsNotNone(self.user)
