from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .backend_exceptions import InvalidTokenError, UnverifiedAccountError
from .models import AppUser
from django.contrib.auth.forms import SetPasswordForm


def app_user_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if 'Auth' not in request.headers:
            return Response({'message': 'Unauthorized response status'}, status=status.HTTP_401_UNAUTHORIZED)
        token = request.headers['Auth']
        try:
            user = AppUser.authenticate_jwt(token)
            request.user = user
            user.update_last_login()
            return view_func(request, *args, **kwargs)
        except InvalidTokenError as e:
            return Response({'message': e.msg}, status=status.HTTP_403_FORBIDDEN)
        except UnverifiedAccountError as e:
            return Response({'message': e.msg}, status=status.HTTP_412_PRECONDITION_FAILED)

    return wrapper


class AppUserPasswordChangeForm(SetPasswordForm):
    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        self.user.jwt_access_token = AppUser.generate_token(
            self.user.username,
            self.user.password,
        )
        if commit:
            self.user.save()
        return self.user
