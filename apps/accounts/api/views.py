from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from apps.accounts.api.serializer import RegisterSerializer, RegisterResponseSerializer, LoginSerializer, LoginResponseSerializer, MeResponseSerializer
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

@extend_schema(
        request=RegisterSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: None,
        }
)
@api_view(["POST"])
def register(request):
    data = request.data
    serializer = RegisterSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "register_successfull": "You have been registered successfully"
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            400: None,
        }
)
@api_view(["POST"])
def login(request):
    data = request.data
    try:
        user = User.objects.get(username=data["username"])
    except User.DoesNotExist:
        return Response({
            "error": "Username or Password Invalid"
        }, status=status.HTTP_400_BAD_REQUEST)

    if user.check_password(data["password"]):
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        return Response({
            "refresh_token": str(refresh),
            "access_token": str(access)
        })
    return Response({
        "error": "Username or Password Invalid"
    }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
        responses={
            200: MeResponseSerializer,
            401: None,
        }
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({
        "me": request.user.username
    })