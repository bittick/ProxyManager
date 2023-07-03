from .celery import send_confirm_code_on_email, send_recovery_code_on_email
from rest_framework import serializers
from .models import AppUser, Proxy, ConfirmationCode
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Subquery
import random


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    email = serializers.EmailField(max_length=100)
    user = None

    def validate_username(self, value):
        if AppUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if AppUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def create_confirm_code(self):
        code = ConfirmationCode.objects.create(code=random.randint(10000, 99999),
                                               user_link=self.user, type='registration')
        send_confirm_code_on_email.delay(self.user.email, code.code)

    def create(self, validated_data):
        user = AppUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
        )
        user.jwt_access_token = AppUser.generate_token(
            user.username,
            user.password,
        )
        user.save()
        self.user = user
        self.create_confirm_code()
        return user


class AuthorizationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

    def create(self, validated_data):
        user = authenticate(
            request=self.context.get('request'),
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user.jwt_access_token if user else None


class ProxySerializer(serializers.ModelSerializer):
    class Meta:
        model = Proxy
        fields = ['host', 'port', 'username', 'password']


class ConfirmCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5)

    def __init__(self, **kwargs):
        data = kwargs.get('data')
        if data:
            self.code = data.get('code')
            self.email = data.get('email')
        super().__init__(**kwargs)

    def verify_code(self, user: AppUser):
        try:
            code_model = ConfirmationCode.objects.get(user_link=user, type='registration')
            if code_model.code == self.code:
                user.is_active = True
                user.save()
                code_model.delete()
                return True
            else:
                return False
        except ObjectDoesNotExist:
            raise serializers.ValidationError('User does not exist ')

    def start_recover(self):
        try:
            user = AppUser.objects.get(email=self.email)
            code_model = ConfirmationCode.objects.create(code=random.randint(10000, 99999),
                                                         user_link=user, type='recovery')
            send_confirm_code_on_email.delay(user.email, code_model.code)
            return True

        except ObjectDoesNotExist:
            raise serializers.ValidationError('User does not exist ')

    def verify_recovery_code(self):
        try:
            user = AppUser.objects.get(email=self.email)
            code_models = ConfirmationCode.objects.filter(user_link=user, type='recovery')
            values = [code_model.code for code_model in code_models]
            if self.code in values:
                code_models.delete()
                return user.jwt_access_token

        except ObjectDoesNotExist as e:
            raise serializers.ValidationError('User does not exist ')
