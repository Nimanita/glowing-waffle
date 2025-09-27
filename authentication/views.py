from django.shortcuts import render
# Create your views here.
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import LoginSerializer, TokenResponseSerializer

User = get_user_model()
from .serializers import RegisterSerializer

@swagger_auto_schema(
    method='post',
    operation_description='Register a new user',
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response(
            description='User created',
            examples={
                'application/json': {
                    'success': True,
                    'user_id': 1,
                    'username': 'alice',
                    'email': 'alice@example.com',
                    'message': 'Registration successful'
                }
            }
        ),
        400: openapi.Response(
            description='Bad Request - validation errors',
            examples={
                'application/json': {
                    'success': False,
                    'errors': {'password_confirm': ['Passwords do not match']},
                    'message': 'Invalid data'
                }
            }
        )
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def register_user(request):
    """Register a new user and return basic info (no auto-login)"""
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'errors': serializer.errors, 'message': 'Invalid data'},
                        status=status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    return Response({
        'success': True,
        'user_id': user.id,
        'username': user.username,
        'email': getattr(user, 'email', ''),
        'message': 'Registration successful'
    }, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    operation_description='Authenticate user and get access token',
    request_body=LoginSerializer,
    responses={
        200: TokenResponseSerializer,
        400: 'Bad Request - Invalid credentials',
        401: 'Unauthorized - Invalid username/password'
    },
    tags=['Authentication']
)
@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
@permission_classes([AllowAny])
def get_auth_token(request):
    """Authenticate user and return access token."""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                'success': False,
                'errors': serializer.errors,
                'message': 'Invalid request data'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    user = authenticate(username=username, password=password)
    if not user:
        return Response(
            {'success': False, 'message': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'success': False, 'message': 'User account is disabled'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token, created = Token.objects.get_or_create(user=user)
    return Response(
        {
            'success': True,
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': getattr(user, 'email', ''),
            'is_staff': user.is_staff,
            'message': 'Authentication successful'
        },
        status=status.HTTP_200_OK
    )


@swagger_auto_schema(
    method='post',
    operation_description='Logout user by deleting auth token',
    responses={
        200: 'Successfully logged out',
        401: 'Unauthorized - Token required'
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user by deleting the auth token."""
    try:
        # Try to retrieve the token attached to the current user
        token = Token.objects.filter(user=request.user).first()
        if not token:
            return Response(
                {'success': False, 'message': 'Token not found for user'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        token.delete()
        return Response(
            {'success': True, 'message': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'success': False, 'message': 'Logout failed', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    operation_description='Verify the provided token and return user info. Useful to confirm authentication and complete registration flow.',
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            description='Token <token>',
            required=True
        )
    ],
    responses={
        200: TokenResponseSerializer,
        401: 'Unauthorized - Invalid or missing token'
    },
    tags=['Authentication']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_token(request):
    """
    Verify token from Authorization header and return basic user info.
    This endpoint accepts header: Authorization: Token <key>
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header or not auth_header.startswith('Token '):
        return Response(
            {'success': False, 'message': 'Token required in Authorization header'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    token_key = auth_header.split(' ')[1]
    try:
        token = Token.objects.select_related('user').get(key=token_key)
        user = token.user
        if not user.is_active:
            return Response(
                {'success': False, 'message': 'User account is disabled'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
            {
                'success': True,
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': getattr(user, 'email', ''),
                'is_staff': user.is_staff,
                'message': 'Token is valid'
            },
            status=status.HTTP_200_OK
        )
    except Token.DoesNotExist:
        return Response(
            {'success': False, 'message': 'Invalid token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response(
            {'success': False, 'message': 'Verification failed', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
