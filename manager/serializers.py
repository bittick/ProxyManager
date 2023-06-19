from rest_framework import serializers

from rest_framework import serializers
from .models import ExtensionUser, Proxy
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)
    email = serializers.EmailField(max_length=100)
    def validate_username(self, value):
        if ExtensionUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        user = ExtensionUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
        )
        user.jwt_access_token = ExtensionUser.generate_token(
            user.username,
            user.password,
        )
        user.save()
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

