from django.core.management.base import BaseCommand
from api.users.models import User

import random

from api.users.models import User
from faker import Faker

import uuid

fakegen = Faker()

class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username="alexadmin").exists():
                User.objects.create_superuser(
                "alexadmin", "alexandrehernandez@classlineacademy.com", "admin321")
                print("Admin user created...")

        if not User.objects.filter(username="alex").exists():
            user = User.objects.create(
                first_name="Alex",
                last_name="Hernandez",
                username="alex",
                email="alex@gmail.com"
                
            )
            user.set_password("admin321")
            user.save()
            print("Alex user created...")

        def add_users(N=5):
            for entry in range(N):
                fake_first_name = fakegen.first_name()
                fake_last_name = fakegen.last_name()
                fake_email = fakegen.email()
                fake_username = fakegen.email()
                User.objects.create(first_name=fake_first_name, last_name=fake_last_name, email=fake_email, username=fake_username)
            print("Fake data users created...")
        
        def add_contacts():
            users = User.objects.all().exclude(username="alex")
            alex_user = User.objects.get(username="alex")
            for user in users:
                alex_user.contacts.add(user)
                alex_user.save()
            print("Contacts added to alex...")

        add_users(5)
        add_contacts()