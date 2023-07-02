from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from manager.models import ExtensionUser
from manager.serializers import RegistrationSerializer, AuthorizationSerializer, ConfirmCodeSerializer
from manager.tools import extension_user_auth
from django.contrib.auth.forms import SetPasswordForm


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'Auth': user.jwt_access_token}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def authorization(request):
    serializer = AuthorizationSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    token = serializer.save()
    if token:
        return Response({'Auth': token}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@extension_user_auth
def confirm_code(request):
    serializer = ConfirmCodeSerializer(data=request.data)
    success = serializer.verify_code(request.user)
    if success:
        return Response({'message': 'Account verified'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Account not verified'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def start_account_recovery(request):
    serializer = ConfirmCodeSerializer(data=request.data)
    success = serializer.start_recover()
    if success:
        return Response({'message': 'Recovery started'}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def finish_account_recovery(request):
    serializer = ConfirmCodeSerializer(data=request.data)
    token = serializer.verify_recovery_code()
    if token:
        return Response({'Auth': token}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@extension_user_auth
def change_password(request):
    user = request.user
    form = SetPasswordForm(user=user, data=request.data)
    if form.is_valid():
        print(form.save())
        # ExtensionUser.generate_token()
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
    else:
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
