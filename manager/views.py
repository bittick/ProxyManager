import random
from rest_framework.decorators import api_view
from .proxylist import proxylist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, AuthorizationSerializer, ProxySerializer
from django.http import JsonResponse
from functools import wraps
from .models import ExtensionUser, Proxy


@api_view(['POST'])
def test(request):
    print(request.body)
    i = random.randint(0, len(proxylist) - 1)
    data = {
        'proxy':
            proxylist[i]
    }
    return Response(data)


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Создание нового пользователя
            user = serializer.save()
            # Дополнительные действия, если необходимо
            # ...
            return Response({'Auth': user.jwt_access_token}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def extension_user_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if 'Auth' not in request.headers:
            return JsonResponse({'message': 'Unauthorized response status'}, status=401)
        token = request.headers['Auth']
        user = ExtensionUser.authenticate_jwt(token)
        if not user:
            return JsonResponse({'message': 'Access denied'}, status=403)
        request.user = user
        return view_func(request, *args, **kwargs)

    return wrapper


@api_view(['POST'])
@extension_user_auth
def test_auth(request):
    print(request.user)
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def authorization(request):
    serializer = AuthorizationSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    token = serializer.save()

    if token:
        return Response({'Auth': token}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_free_proxy(request):
    def get_advertising_link():
        return 'https://google.com/'

    def choose_free_proxy():
        tmp = Proxy.objects.order_by('counter').first()
        tmp.counter += 1
        tmp.save()
        return tmp

    proxy = choose_free_proxy()
    serializer = ProxySerializer(proxy, many=False)
    ad = get_advertising_link()
    return Response({'proxy': serializer.data, 'ad': ad}, status=status.HTTP_200_OK)

