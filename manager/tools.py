from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .backend_exceptions import InvalidTokenError, UnverifiedAccountError
from .models import ExtensionUser


def extension_user_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if 'Auth' not in request.headers:
            return Response({'message': 'Unauthorized response status'}, status=status.HTTP_401_UNAUTHORIZED)
        token = request.headers['Auth']
        try:
            user = ExtensionUser.authenticate_jwt(token)
            request.user = user
            return view_func(request, *args, **kwargs)
        except InvalidTokenError as e:
            return Response({'message': e.msg}, status=status.HTTP_403_FORBIDDEN)
        except UnverifiedAccountError as e:
            return Response({'message': e.msg}, status=status.HTTP_412_PRECONDITION_FAILED)

    return wrapper
