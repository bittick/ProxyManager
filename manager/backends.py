from django.contrib.auth.backends import ModelBackend
from .models import ExtensionUser


class ExtensionUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = ExtensionUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except ExtensionUser.DoesNotExist:
            return None
