

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator, validate_email
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q
from django.contrib.gis.geos import Point

# Channels
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Models
from api.users.models import User, UserLoginActivity, Earning, Connection, Follow, Blacklist, KarmaEarning
from api.notifications.models import Notification, NotificationUser
from api.donations.models import DonationOption
from djmoney.models.fields import Money
from api.donations.models import Donation, DonationOption, DonationPayment
from api.portals.models import Portal, PortalMember

# Serializers


# Celery
from api.taskapp.tasks import (
    send_confirmation_email,
    send_change_email_email,
    send_new_donation,
    send_reset_password_email,
    send_invitation_email
)


# Utilities
import jwt
import datetime
from django.utils import timezone
import string
import random
from datetime import timedelta
from api.utils import helpers
import re
import geoip2.database
import ccy
import tldextract
import environ
env = environ.Env()


class DetailedUserModelSerializer(serializers.ModelSerializer):

    member = serializers.SerializerMethodField(read_only=True)

    class Meta:

        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'about',
            'phone_number',
            'country',
            'is_staff',
            'is_verified',
            'picture',
            'stripe_customer_id',
            'currency',
            'paypal_email',
            'net_income',
            'withdrawn',
            'karma_amount',
            'available_for_withdrawal',
            'pending_clearance',
            'pending_messages',
            'pending_notifications',
            'default_payment_method',
            'invitations_count',
            'connections_count',
            'followed_count',
            'following_count',
            'posts_count',
            'created_posts_count',
            'created_active_posts_count',
            'created_solved_posts_count',
            'collaborated_posts_count',
            'collaborated_active_posts_count',
            'collaborated_solved_posts_count',
            'reputation',
            'reviews_count',
            'is_currency_permanent',
            'email_notifications_allowed',
            'geolocation',
            'member'

        )

        read_only_fields = (
            'id',
        )

    def get_member(self, obj):

        if 'request' in self.context:
            subdomain = tldextract.extract(self.context['request'].META['HTTP_ORIGIN']).subdomain
            portal = None

            try:
                portal = Portal.objects.get(url=subdomain)
            except Portal.DoesNotExist:
                pass

            if portal:
                from api.portals.serializers import PortalMemberModelSerializer
                portal_member = PortalMember.objects.get(portal=portal, user=obj)
                return PortalMemberModelSerializer(portal_member).data

        return None


class UserModelSerializer(serializers.ModelSerializer):

    is_followed = serializers.SerializerMethodField(read_only=True)
    connection_invitation_sent = serializers.SerializerMethodField(read_only=True)
    is_connection = serializers.SerializerMethodField(read_only=True)
    accept_invitation = serializers.SerializerMethodField(read_only=True)
    member = serializers.SerializerMethodField(read_only=True)

    class Meta:

        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'about',
            'phone_number',
            'country',
            'is_staff',
            'is_verified',
            'picture',
            'currency',
            'paypal_email',
            'karma_amount',
            'is_followed',
            'connection_invitation_sent',
            'is_connection',
            'is_online',
            'accept_invitation',
            'posts_count',
            'created_posts_count',
            'created_active_posts_count',
            'created_solved_posts_count',
            'collaborated_posts_count',
            'collaborated_active_posts_count',
            'collaborated_solved_posts_count',
            'reputation',
            'reviews_count',
            'geolocation',
            'member'
        )

        read_only_fields = (
            'id',
        )

    def get_is_followed(self, obj):
        if 'request' in self.context and self.context['request'].user.id:
            user = self.context['request'].user
            return Follow.objects.filter(from_user=user, followed_user=obj).exists()
        return False

    def get_connection_invitation_sent(self, obj):
        if 'request' in self.context and self.context['request'].user.id:
            user = self.context['request'].user
            return Connection.objects.filter(requester=user, addressee=obj, accepted=False).exists()
        return False

    def get_accept_invitation(self, obj):
        if 'request' in self.context and self.context['request'].user.id:
            user = self.context['request'].user
            return Connection.objects.filter(requester=obj, addressee=user, accepted=False).exists()
        return False

    def get_is_connection(self, obj):
        if 'request' in self.context and self.context['request'].user.id:
            user = self.context['request'].user
            return Connection.objects.filter(Q(requester=user, addressee=obj) |
                                             Q(requester=obj, addressee=user), accepted=True).exists()
        return False

    def get_member(self, obj):

        if 'request' in self.context:
            subdomain = tldextract.extract(self.context['request'].META['HTTP_ORIGIN']).subdomain
            portal = None

            try:
                portal = Portal.objects.get(url=subdomain)
            except Portal.DoesNotExist:
                pass

            if portal:
                from api.portals.serializers import PortalMemberModelSerializer
                portal_member = PortalMember.objects.get(portal=portal, user=obj)
                return PortalMemberModelSerializer(portal_member).data

        return None


class GetUserByJwtSerializer(serializers.Serializer):
    user = DetailedUserModelSerializer(read_only=True)
    access_token = serializers.CharField(read_only=True)
    token = serializers.CharField()

    def validate_token(self, data):

        try:
            payload = jwt.decode(data, settings.SECRET_KEY,
                                 algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'user_token':
            raise serializers.ValidationError('Invalid token')

        self.context['payload'] = payload

        return data

    def validate(self, data):
        payload = self.context['payload']
        user = User.objects.get(id=payload['user'])
        token, created = Token.objects.get_or_create(
            user=user)
        data['access_token'] = token
        data['user'] = user
        return data


class GetCurrencySerializer(serializers.Serializer):
    currency = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        request = self.context['request']
        current_login_ip = helpers.get_client_ip(request)
        # Remove this line in production
        if env.bool("DEBUG", default=True):
            current_login_ip = "147.161.106.227"
        data['currency'] = helpers.get_currency_api(current_login_ip)
        return data


class UserSignUpSerializer(serializers.Serializer):

    # Future me: filter email UniqueValidator by only public client
    email = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=False,
    )

    username = serializers.CharField(
        min_length=4,
        max_length=40,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    # Phone number
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: +999999999. Up to 15 digits allowed."
    )
    phone_number = serializers.CharField(
        validators=[phone_regex], required=False)

    # Password
    password = serializers.CharField(min_length=8, max_length=64)

    # Name
    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    # Currency for seller subscription
    currency = serializers.CharField(max_length=3, required=False)

    def validate(self, data):

        passwd = data['password']

        password_validation.validate_password(passwd)

        # Verifiy token is valid
        if 'invitation_token' in self.context and self.context['invitation_token']:
            invitation_token = self.context['invitation_token']
            try:
                payload = jwt.decode(invitation_token, settings.SECRET_KEY,
                                     algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                raise serializers.ValidationError('Token has expired')
            except jwt.PyJWTError:
                raise serializers.ValidationError('Invalid token')
            if payload['type'] != 'invitation_token':
                raise serializers.ValidationError('Invalid token')
            self.context['payload'] = payload

        # Check if there is a portal

        # If not get or 404 the oficial portal

        # If there is a portal check if allow registers

        return data

    def create(self, data):

        request = self.context['request']
        portal = self.context['portal']

        # Create the free trial expiration date

        currency, country, country_name, region, region_name, city, zip, lat, lon = helpers.get_location_data(request)

        if not 'currency' in data or not data['currency'] and currency:
            data['currency'] = currency

        karma_amount = 1000

        user = User.objects.create_user(**data,
                                        is_verified=False,
                                        is_client=True,
                                        country=country,
                                        country_name=country_name,
                                        region=region,
                                        region_name=region_name,
                                        city=city,
                                        zip=zip,
                                        geolocation=Point(lon, lat),
                                        karma_amount=karma_amount,
                                        )
        # Add this user to oficial portal and update the statistics
        # (

        oficial_portal = get_object_or_404(Portal, url='oficial')

        if portal != oficial_portal:
            helpers.addNewMemberToOficialPortal(user)
        # Add user to users in portal
        member = PortalMember.objects.create(portal=portal, user=user, is_active=True, role=PortalMember.BASIC)

        # Update portal statistics
        portal.members_count += 1
        portal.active_members_count += 1
        portal.basic_members_count += 1
        portal.active_basic_members_count += 1
        portal.save()

        # )
        # Set the 1000 karma earned
        KarmaEarning.objects.create(user=user, amount=karma_amount,
                                    type=KarmaEarning.EARNED_BY_JOIN_PORTAL, portal=portal)

        # Update member statistics
        member.karma_earned += karma_amount
        member.karma_earned_by_join_portal += karma_amount
        # Calc karma ratio
        karma_earned = 1
        karma_spent = 1

        if member.karma_earned > 1:
            karma_earned = member.karma_earned
        if member.karma_spent > 1:
            karma_spent = member.karma_spent
        member.karma_ratio = karma_earned / karma_spent
        member.save()

        # Update user statistics
        user.karma_earned += karma_amount
        user.karma_earned_by_join_portal += karma_amount
        # Calc karma ratio
        karma_earned = 1
        karma_spent = 1

        if user.karma_earned > 1:
            karma_earned = user.karma_earned
        if user.karma_spent > 1:
            karma_spent = user.karma_spent
        user.karma_ratio = karma_earned / karma_spent
        user.save()
        token, created = Token.objects.get_or_create(
            user=user)

        current_login_ip = helpers.get_client_ip(request)

        if Blacklist.objects.filter(IP=current_login_ip).exists():
            raise serializers.ValidationError(
                'Not allowed')

        if UserLoginActivity.objects.filter(user=user).exists():
            user_login_activity = UserLoginActivity.objects.filter(
                user=user)[0]
            if user_login_activity.login_IP != current_login_ip:
                if Token.objects.filter(user=user).exists():
                    last_token = Token.objects.get(user=user)
                    last_token.delete()
            UserLoginActivity.objects.filter(
                login_username=user.username).delete()

        user_agent_info = request.META.get(
            'HTTP_USER_AGENT', '<unknown>')[:255],
        user_login_activity_log = UserLoginActivity(login_IP=helpers.get_client_ip(request),
                                                    user=user,
                                                    login_username=user.username,
                                                    user_agent_info=user_agent_info,
                                                    status=UserLoginActivity.SUCCESS)
        user_login_activity_log.save()

        send_confirmation_email(user)

        return user, token.key


class UserLoginSerializer(serializers.Serializer):

    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):

        # Validation with email or password

        email = data['email']
        password = data['password']
        request = self.context['request']
        subdomain = tldextract.extract(request.META['HTTP_ORIGIN']).subdomain
        portal = None

        try:
            portal = Portal.objects.get(url=subdomain)
        except Portal.DoesNotExist:
            pass

        if portal:
            # Check if have a inactive member of this portal
            members = PortalMember.objects.filter(is_active=False, email=email, password=password)
            if members.exists():

                # Get the member
                new_member = members.first()

                # Get the random username
                username = helpers.get_random_username()

                user = None
                # Check if the user exists
                users = User.objects.filter(email=email)
                if users.exists():
                    user = users.first()
                else:
                    # Create the user
                    user = User.objects.create_user(
                        first_name=new_member.first_name,
                        last_name=new_member.last_name,
                        email=new_member.email,
                        username=username,
                        password=new_member.password,
                        is_verified=False,
                        is_client=True,
                        karma_amount=new_member.initial_karma_amount,
                    )

                # Add the new user to the membership
                new_member.user = user

                # Update the portal statistics
                portal.active_members_count += 1
                if new_member.role == PortalMember.BASIC:
                    portal.active_basic_members_count += 1
                elif new_member.role == PortalMember.MANAGER:
                    portal.active_manager_members_count += 1
                elif new_member.role == PortalMember.ADMIN:
                    portal.active_admin_members_count += 1
                new_member.is_active = True
                new_member.save()
                portal.save()
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        # for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if email and password:
            if re.search(regex, email):

                # ¡Alert in the future filter also by client!
                user_request = get_object_or_404(
                    User,
                    email=email
                )
                email = user_request.username

        # Check if user set email

        users = User.objects.filter(username=email, account_deactivated=True)

        if users.exists():

            raise serializers.ValidationError(
                'This account has already been desactivated')

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError(
                'Invalid credentials')
        # If there is a portal check if user is a member of this portal

        if portal and not PortalMember.objects.filter(user=user, portal=portal).exists():
            raise serializers.ValidationError(
                'You are not a member of this portal')

        if user:
            current_login_ip = helpers.get_client_ip(request)
            if Blacklist.objects.filter(IP=current_login_ip).exists():
                raise serializers.ValidationError(
                    'Not allowed')
            if UserLoginActivity.objects.filter(user=user).exists():
                user_login_activity = UserLoginActivity.objects.filter(
                    user=user)[0]
                if user_login_activity.login_IP != current_login_ip:
                    if Token.objects.filter(user=user).exists():
                        last_token = Token.objects.get(user=user)
                        last_token.delete()
                UserLoginActivity.objects.filter(
                    user=user).delete()
            user_agent_info = request.META.get(
                'HTTP_USER_AGENT', '<unknown>')[:255],
            user_login_activity_log = UserLoginActivity(login_IP=helpers.get_client_ip(request),
                                                        user=user,
                                                        login_username=user.username,
                                                        user_agent_info=user_agent_info,
                                                        status=UserLoginActivity.SUCCESS)
            user_login_activity_log.save()

        self.context['user'] = user
        return data

    def create(self, data):

        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key


class AccountVerificationSerializer(serializers.Serializer):

    token = serializers.CharField()

    def validate_token(self, data):

        try:
            payload = jwt.decode(data, settings.SECRET_KEY,
                                 algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token')
        self.context['payload'] = payload
        return data

    def save(self):

        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        if user.is_verified:
            raise serializers.ValidationError('Your account is already validated')

        user.is_verified = True
        user.save()


class IsEmailAvailableSerializer(serializers.Serializer):

    email = serializers.CharField()

    def validate(self, data):

        email = data['email']

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already in use')

        return {"email": email}


class IsUsernameAvailableSerializer(serializers.Serializer):

    username = serializers.CharField()

    def validate(self, data):

        username = data['username']

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('This username is already in use')

        return True


class ChangeEmailSerializer(serializers.Serializer):

    email = serializers.CharField()

    def validate(self, data):

        email = data['email']
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already in use')

        user = self.context['user']

        send_change_email_email(user, email)
        return {'email': email, 'user': user}


class ValidateChangeEmail(serializers.Serializer):

    token = serializers.CharField()

    def validate_token(self, data):

        try:
            payload = jwt.decode(data, settings.SECRET_KEY,
                                 algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'change_email':
            raise serializers.ValidationError('Invalid token')
        self.context['payload'] = payload
        return data

    def save(self):

        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        email = payload['email']

        user.email = email
        user.save()
        return email


class ForgetPasswordSerializer(serializers.Serializer):

    email = serializers.CharField()

    def validate(self, data):

        email = data['email']

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email does not exists')

        send_reset_password_email(email)
        return {'email': email}


class ResetPasswordSerializer(serializers.Serializer):

    token = serializers.CharField()
    password = serializers.CharField(min_length=8, max_length=64)
    confirm_password = serializers.CharField(min_length=8, max_length=64)

    def validate_token(self, data):

        try:
            payload = jwt.decode(data, settings.SECRET_KEY,
                                 algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token')
        self.context['payload'] = payload
        return data

    def validate(self, data):

        password = data['password']
        confirm_password = data['confirm_password']
        if password != confirm_password:
            raise serializers.ValidationError('Passwords don\'t match')
        return data

    def save(self):

        username = self.context['payload']['user']

        password = self.data['password']
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):

    password = serializers.CharField(min_length=8, max_length=64)
    new_password = serializers.CharField(min_length=8, max_length=64)
    repeat_password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):

        # Validation with email or password
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        # for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        user = self.context['request'].user
        password = data['password']
        email = user.email
        if email and password:
            if re.search(regex, email):
                user_request = get_object_or_404(
                    User,
                    email=email
                )
                email = user_request.username
            # Check if user set email

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Current password is not correct')
        new_password = data['new_password']
        repeat_password = data['repeat_password']
        if new_password != repeat_password:
            raise serializers.ValidationError('Passwords not match')
        user.set_password(new_password)
        user.password_changed = True
        user.save()

        return data


class ConfirmUserSerializer(serializers.Serializer):

    password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):

        # Validation with email or password
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        # for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        user = self.context['request'].user
        password = data['password']
        email = user.email
        if email and password:
            if re.search(regex, email):
                user_request = get_object_or_404(
                    User,
                    email=email
                )
                email = user_request.username
            # Check if user set email

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Password is not correct')

        return user


class InviteUserSerializer(serializers.Serializer):

    email = serializers.CharField()
    type = serializers.CharField()
    message = serializers.CharField(allow_blank=True)

    def validate(self, data):

        email = data['email']
        type = data['type']
        message = data['message']
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This user already exists')
        if(type != "seller" and type != "buyer"):
            raise serializers.ValidationError('Type not valid')

        request = self.context['request']
        user = request.user

        send_invitation_email(user, email, message, type)
        return data


class PaypalConnectSerializer(serializers.Serializer):

    email = serializers.CharField()
    email_confirmation = serializers.CharField()

    def validate(self, data):

        email = data['email']
        email_confirmation = data['email_confirmation']
        if email != email_confirmation:
            raise serializers.ValidationError('Emails don\'t match')

        return data

    def update(self, instance, validated_data):
        user = instance
        email = validated_data['email']
        user.paypal_email = email
        user.save()

        return {"email": email}


class AttachPaymentMethodSerializer(serializers.Serializer):

    payment_method_id = serializers.CharField(required=True)
    card_name = serializers.CharField(required=True)

    def validate(self, data):

        stripe = self.context['stripe']
        user = self.context['request'].user
        payment_method_id = data['payment_method_id']
        payment_method_object = stripe.PaymentMethod.retrieve(
            payment_method_id,
        )
        if not user.stripe_customer_id:
            new_customer = stripe.Customer.create(
                description="claCustomer_"+user.first_name+'_'+user.last_name,
                name=user.first_name+' '+user.last_name,
                email=user.email,
            )
            user.stripe_customer_id = new_customer['id']
            user.save()

        payment_methods = helpers.get_payment_methods(stripe, user.stripe_customer_id)
        if payment_methods:
            for payment_method in payment_methods:
                if payment_method.card.fingerprint == payment_method_object.card.fingerprint:
                    raise serializers.ValidationError(
                        'This payment method is already added')

        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=user.stripe_customer_id,
        )
        if not payment_methods or len(payment_method) == 0:
            stripe.Customer.modify(
                user.stripe_customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
            user.default_payment_method = payment_method_id

        stripe.PaymentMethod.modify(
            payment_method_id,
            billing_details={
                "name": data.get('card_name', " "),
            }
        )

        return data

    def update(self, instance, validated_data):

        return instance


class DetachPaymentMethodSerializer(serializers.Serializer):

    payment_method_id = serializers.CharField()

    def validate(self, data):

        stripe = self.context['stripe']
        user = self.context['request'].user
        payment_method_id = data['payment_method_id']
        if payment_method_id == user.plan_default_payment_method:
            raise serializers.ValidationError(
                'This payment method is attached to a plan subscription')

        stripe.PaymentMethod.detach(
            "pm_1ICOvTCob7soW4zYIiXsCA4C",
        )

        return data

    def update(self, instance, validated_data):

        return instance


class CreateDonationSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField()
    donation_option_id = serializers.UUIDField(required=False)
    other_amount = serializers.FloatField(required=False)
    other_amount_karma = serializers.FloatField(required=False)
    email = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    currency = serializers.CharField()

    def validate(self, data):
        stripe = self.context['stripe']
        request = self.context['request']
        subdomain = tldextract.extract(request.META['HTTP_ORIGIN']).subdomain
        portal = get_object_or_404(Portal, url=subdomain)
        currency = data['currency']
        payment_method_id = data['payment_method_id']
        to_user = self.instance
        user = None
        is_anonymous = True
        message = None
        if 'message' in data and data['message']:
            message = data['message']
        email = None
        if 'email' in data and data['email']:
            email = data['email']
        if self.context['request'].user.id:
            user = self.context['request'].user
            email = user.email
            is_anonymous = False
        if not is_anonymous and user:
            currency = user.currency
        donation_option = None
        if 'donation_option_id' in data and data['donation_option_id']:
            donation_option = get_object_or_404(DonationOption, id=data['donation_option_id'])
        other_amount = None
        if 'other_amount' in data and data['other_amount']:
            other_amount = data['other_amount']
        paid_karma = None
        if donation_option:
            paid_karma = donation_option.paid_karma
        elif 'other_amount_karma' in data and data['other_amount_karma']:
            paid_karma = data['other_amount_karma']

        # Check if there is almost one of the donation_option and other amount
        if not donation_option and not other_amount:
            raise serializers.ValidationError(
                "You need at least one of the two amount options")
        is_other_amount = False
        if other_amount:
            is_other_amount = True

        rand_string = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=15))

        if not is_anonymous and user:
            if user.stripe_customer_id:
                stripe_customer_id = user.stripe_customer_id
            else:
                new_customer = stripe.Customer.create(
                    description="talenCustomer_" + user.first_name + '_' + user.last_name,
                    name=user.first_name + ' ' + user.last_name + '_' + rand_string,
                    email=email
                )
                stripe_customer_id = new_customer['id']
                user.stripe_customer_id = stripe_customer_id
                user.save()

        else:

            new_customer = stripe.Customer.create(
                description="talenAnonymousCustomer_" + email,
                name=email + '_' + rand_string,
                email=email
            )
            stripe_customer_id = new_customer['id']
        payment_method_object = stripe.PaymentMethod.retrieve(
            payment_method_id,
        )

        # Add to default paymet method this payment id
        payment_methods = helpers.get_payment_methods(stripe, stripe_customer_id)
        if payment_methods:
            for payment_method in payment_methods:
                # Check if payment method not already added

                if payment_method.card.fingerprint != payment_method_object.card.fingerprint:
                    stripe.PaymentMethod.attach(
                        payment_method_id,
                        customer=stripe_customer_id,
                    )
                    stripe.Customer.modify(
                        stripe_customer_id,
                        invoice_settings={
                            "default_payment_method": payment_method_id
                        }
                    )
        else:
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=stripe_customer_id,
            )
            stripe.Customer.modify(
                stripe_customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
        # If is other amount create the new stripe product and price
        if is_other_amount:
            if not is_anonymous and user:

                product = stripe.Product.create(name=str(other_amount) + '_donation_by_' + user.username)

            else:
                product = stripe.Product.create(name=str(other_amount) + '_donation_' + rand_string)
            price = stripe.Price.create(
                unit_amount=int(other_amount * 100),
                currency=currency,
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

        # Get and substract the service fee (20%)
        service_fee = (gross_amount * 20) / 100
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
            'rate_date': rate_date,
            'stripe_customer_id': stripe_customer_id,
            'default_payment_method': payment_method_id,
            'paid_karma': paid_karma,
            'message': message,
            'email': email,
            'portal': portal,
        }

    def update(self, instance, validated_data):

        # Get the validated data
        portal = validated_data['portal']
        is_anonymous = validated_data["is_anonymous"]
        to_user = instance
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
        stripe_customer_id = validated_data["stripe_customer_id"]
        default_payment_method = validated_data["default_payment_method"]
        paid_karma = validated_data["paid_karma"]
        message = validated_data["message"]
        email = validated_data["email"]

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
            stripe_price_id=price['id'],
            stripe_product_id=product['id']
        )

        # Create the donation
        donation = Donation.objects.create(
            portal=portal,
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
            message=message,
            email=email,
        )

        # Create the to user earning
        Earning.objects.create(
            portal=portal,
            user=to_user,
            amount=net_amount,
            available_for_withdrawn_date=timezone.now() + timedelta(days=14)
        )

        # Add donations_received_count to to_user

        to_user_member = PortalMember.objects.get(user=to_user, portal=portal)
        to_user_member.donations_received_count += 1
        to_user_member.save()

        to_user.donations_received_count += 1
        to_user.net_income = to_user.net_income + Money(amount=net_amount, currency="USD")

        to_user.pending_clearance += Money(amount=net_amount, currency="USD")
        to_user.save()
        # Notificate the invitation to the addressee
        notification = Notification.objects.create(
            type=Notification.NEW_DONATION,
            donation=donation,
        )
        user_notification = NotificationUser.objects.create(
            portal=portal,
            notification=notification,
            user=to_user
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            '{}-{}'.format(to_user.id, portal.id), {
                "type": "send.notification",
                "event": "NEW_DONATION",
                "notification__pk": str(user_notification.pk),
            }
        )
        if not to_user.is_online and to_user.email_notifications_allowed:
            send_new_donation(user, to_user, is_anonymous)
        if not is_anonymous and user:
            KarmaEarning.objects.create(user=user, amount=paid_karma,
                                        type=KarmaEarning.EARNED_BY_DONATION, portal=portal)

            # Update member statistics
            member = PortalMember.objects.get(user=user, portal=portal)
            if member.role == PortalMember.BASIC:

                member.karma_amount += paid_karma
                member.karma_earned += paid_karma
                member.karma_earned_by_donations += paid_karma
                # Calc member karma ratio
                karma_earned = 1
                karma_spent = 1

                if member.karma_earned > 1:
                    karma_earned = member.karma_earned
                if member.karma_spent > 1:
                    karma_spent = member.karma_spent

                member.karma_ratio = karma_earned / karma_spent

                # Update user statistics

                user.karma_amount += paid_karma
                user.karma_earned += paid_karma
                user.karma_earned_by_donations += paid_karma
                # Calc karma ratio
                karma_earned = 1
                karma_spent = 1

                if user.karma_earned > 1:
                    karma_earned = user.karma_earned
                if user.karma_spent > 1:
                    karma_spent = user.karma_spent
                user.karma_ratio = karma_earned / karma_spent

            member.donations_made_count += 1
            member.save()

            user.is_currency_permanent = True
            user.donations_made_count += 1
            user.save()

        return to_user, user


class UpdateGeolocation(serializers.Serializer):

    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    def update(self, instance, validated_data):
        longitude = validated_data["longitude"]
        latitude = validated_data["latitude"]
        instance.geolocation = Point(longitude, latitude)
        instance.save()
        return instance
