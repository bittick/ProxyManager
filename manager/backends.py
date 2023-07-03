from django.contrib.auth.backends import ModelBackend
from .models import AppUser


class ExtensionUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = AppUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except AppUser.DoesNotExist:
            return None
