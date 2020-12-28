"""Users serializers."""

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Models
from api.users.models import User, UserLoginActivity


# Serializers

import re

# Utilities
import jwt
import datetime
from api.utils import helpers


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    class Meta:
        """Meta class."""

        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'country',
            'is_staff',
            'is_verified',
            'is_seller',
            'seller_view',
            'is_free_trial',
            'passed_free_trial_once',
            'free_trial_expiration',
            'plan_type',
            'stripe_customer_id',
            'currency',
            'stripe_account_id',
            'money_balance'
        )

        read_only_fields = (
            'id',
            'username',
        )


class UserSignUpSerializer(serializers.Serializer):
    """Useer sign up serializer.

    Handle sign up data validation and user/profile creation.
    """

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
    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    # Name
    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    def validate(self, data):
        """Verify passwords match."""
        passwd = data['password']
        passwd_conf = data['password_confirmation']
        if passwd != passwd_conf:
            raise serializers.ValidationError('Las contraseñas no coinciden')
        password_validation.validate_password(passwd)

        return data

    def create(self, data):
        """Handle user and profile creation."""
        request = self.context['request']

        data.pop('password_confirmation')

        # Create the free trial expiration date
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=14)

        user = User.objects.create_user(**data, is_verified=False, is_client=True,
                                        is_seller=True, is_free_trial=True, free_trial_expiration=expiration_date)
        token, created = Token.objects.get_or_create(
            user=user)

        current_login_ip = helpers.get_client_ip(request)

        if UserLoginActivity.objects.filter(user=user.pk).exists():
            user_login_activity = UserLoginActivity.objects.filter(
                user=user.pk)[0]
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

        helpers.send_confirmation_email(user_pk=user.pk)

        return user, token.key


class UserLoginSerializer(serializers.Serializer):
    """User login serializer.

    Handle the login request
    """

    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """Check credentials."""
        # Validation with email or password
        email = data['email']
        password = data['password']
        request = self.context['request']
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        # for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
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
            raise serializers.ValidationError(
                'Las credenciales no son correctas')

        if user:
            current_login_ip = helpers.get_client_ip(request)

            if UserLoginActivity.objects.filter(user=user.pk).exists():
                user_login_activity = UserLoginActivity.objects.filter(
                    user=user.pk)[0]
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

        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retrieve new token."""

        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key


class AccountVerificationSerializer(serializers.Serializer):
    """Acount verification serializer."""

    token = serializers.CharField()

    def validate_token(self, data):
        """Verifiy token is valid."""
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
        """Update user's verified status."""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        if user.is_verified:
            raise serializers.ValidationError('Tu cuenta ya esta validada')

        user.is_verified = True
        user.save()


class IsEmailAvailableSerializer(serializers.Serializer):
    """Acount verification serializer."""

    email = serializers.CharField()

    def validate(self, data):
        """Update user's verified status."""

        email = data['email']

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already in use')

        return {"email":email}



class ChangeEmailSerializer(serializers.Serializer):
    """Acount verification serializer."""

    email = serializers.CharField()

    def validate(self, data):
        """Update user's verified status."""

        email = data['email']

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Este email ya esta en uso')

        user = self.context['user']

        helpers.send_change_email(user, email)
        return {'email': email, 'user': user}


class ValidateChangeEmail(serializers.Serializer):
    """Acount verification serializer."""

    email = serializers.CharField()

    def validate_email(self, data):

        email = data
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Este email ya esta en uso')
        self.context['email'] = email
        return data

    def save(self):
        """Update user's verified status."""
        user = self.context['user']
        email = self.context['email']
        user.email = email
        user.save()
        return user


class ForgetPasswordSerializer(serializers.Serializer):
    """Acount verification serializer."""

    email = serializers.CharField()

    def validate(self, data):
        """Update user's verified status."""

        email = data['email']

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Este email no existe')

        user = User.objects.filter(email=email).first()
        token = Token.objects.get(user=user)

        helpers.send_reset_password(user, token.key)
        return {'email': email, 'user': user}


class ResetPasswordSerializer(serializers.Serializer):
    """Acount verification serializer."""

    password = serializers.CharField(min_length=8, max_length=64)
    confirm_password = serializers.CharField(min_length=8, max_length=64)

    def validate_password(self, data):

        password = data
        confirm_password = self.context['confirm_password']
        if password != confirm_password:
            raise serializers.ValidationError('Passwords don\'t match')
        self.context['password'] = password
        return data

    def save(self):
        """Update user's verified status."""
        user = self.context['user']
        password = self.context['password']
        user.set_password(password)
        user.save()
        return user


class AddInstructorAccountsSerializer(serializers.Serializer):
    def validate(self, data):
        user = self.instance
        accounts_acquired = self.context['accounts_acquired']
        data = {
            'accounts_acquired': accounts_acquired,
        }
        return data

    def update(self, instance, validated_data):

        accounts_acquired = validated_data['accounts_acquired']

        instance.teacher.current_accounts = accounts_acquired['accounts']

        instance.teacher.accounts_to_create_left = int(
            accounts_acquired['accounts']) - instance.teacher.instructors.count()

        instance.teacher.currency = accounts_acquired['currency']
        instance.teacher.accounts_price = accounts_acquired['price']

        instance.teacher.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """User login serializer.

    Handle the login request
    """
    email = serializers.CharField()
    password = serializers.CharField(min_length=8, max_length=64)
    new_password = serializers.CharField(min_length=8, max_length=64)
    repeat_password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """Check credentials."""
        # Validation with email or password

        new_password = self.context['new_password']
        repeat_password = self.context['repeat_password']
        email = data['email']
        password = data['password']
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        # for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

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
            raise serializers.ValidationError('Credenciales invalidas')
        if new_password != repeat_password:
            raise serializers.ValidationError('Las contraseñas no coinciden')
        user.set_password(new_password)
        user.password_changed = True
        user.save()

        return data
