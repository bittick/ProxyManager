from django.contrib.auth.models import User, Group, Permission
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import jwt
from datetime import datetime
from ProxyManager.settings import SECRET_KEY
from .backend_exceptions import InvalidTokenError, UnverifiedAccountError
from django.utils import timezone


class AppUser(User):
    extension_groups = models.ManyToManyField(Group, related_name='extension_users')
    extension_permissions = models.ManyToManyField(Permission, related_name='extension_users')
    jwt_access_token = models.CharField(max_length=100, blank=True, unique=True)

    @classmethod
    def authenticate_jwt(cls, token):
        try:
            user = cls.objects.get(jwt_access_token=token)
            if user.username == jwt.decode(token, options={"verify_signature": False}).get('username'):
                if not user.is_active:
                    raise UnverifiedAccountError('User account not verified')
                return user
        except ObjectDoesNotExist:
            raise InvalidTokenError('Token failed to authenticate')

    @staticmethod
    def generate_token(username, password, secretkey=SECRET_KEY):
        time = str(datetime.now())
        secret = password + time + secretkey
        return jwt.encode({'username': username, 'time': time}, secret, algorithm="HS256")

    @classmethod
    def validate_token(cls, token, password, secretkey=SECRET_KEY):
        raw_data = jwt.decode(token, options={"verify_signature": False})
        try:
            time = raw_data.get('time')
            if not time:
                raise jwt.exceptions.InvalidSignatureError()
            secret = password + time + secretkey
            decoded_data = jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError as e:
            return False
        return raw_data == decoded_data

    def regenerate_token(self, secretkey=SECRET_KEY):
        time = str(datetime.now())
        secret = self.password + time + secretkey
        return jwt.encode({'username': self.username}, secret, algorithm="HS256")

    def update_last_login(self, commit=True):
        self.last_login = timezone.now()  # Устанавливаем текущую дату и время
        if commit:
            self.save()

    class Meta:
        verbose_name = 'Extension User'
        verbose_name_plural = 'Extension Users'


class ConfirmationCode(models.Model):
    code = models.CharField(max_length=5)
    user_link = models.ForeignKey(to=AppUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Код подтверждения'
        verbose_name_plural = 'Коды подтверждения'


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Proxy(models.Model):
    host = models.CharField(max_length=15)
    port = models.IntegerField()
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    tag = models.CharField(max_length=30, blank=True, null=True)
    country = models.ForeignKey(to=Country, on_delete=models.PROTECT, blank=True, null=True)
    counter = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Proxy model'
        verbose_name_plural = 'Proxy models'


class DomainList(models.Model):
    domain = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey(to=Country, on_delete=models.PROTECT)
