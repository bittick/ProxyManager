import random
from rest_framework.decorators import api_view
from .proxylist import proxylist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, AuthorizationSerializer, ProxySerializer
from django.http import JsonResponse
from functools import wraps
from .models import AppUser, Proxy, ConfirmationCode
from .backend_exceptions import InvalidTokenError, UnverifiedAccountError
from .tools import app_user_auth


@api_view(['POST'])
def test(request):
    print(request.body)
    i = random.randint(0, len(proxylist) - 1)
    data = {
        'proxy':
            proxylist[i]
    }
    return Response(data)


@api_view(['POST'])
@app_user_auth
def test_auth(request):
    print(request.user)
    return Response(status=status.HTTP_200_OK)


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
