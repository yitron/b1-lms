"""
DRF Views for LMS API
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .serializers import SignupSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    User signup endpoint
    Creates new user and returns authentication token
    """
    serializer = SignupSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Create or get auth token
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
