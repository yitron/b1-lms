"""
DRF Views for LMS API
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .serializers import SignupSerializer, UserSerializer, LoginSerializer, LessonSerializer, UserProgressSerializer
from .models import Lesson, UserProgress


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


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    User login endpoint
    Authenticates user and returns token
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Get or create token
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    User logout endpoint
    Deletes user's authentication token
    """
    # Delete user's token
    request.user.auth_token.delete()

    return Response({
        'message': 'Successfully logged out'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def lessons_list(request):
    """
    Get all lessons
    Public endpoint - no authentication required
    """
    lessons = Lesson.objects.all()
    serializer = LessonSerializer(lessons, many=True)

    return Response({
        'lessons': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def lesson_detail(request, lesson_id):
    """
    Get specific lesson by lesson_id
    Public endpoint - no authentication required
    """
    try:
        lesson = Lesson.objects.get(lesson_id=lesson_id)
    except Lesson.DoesNotExist:
        return Response({
            'error': 'Lesson not found'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = LessonSerializer(lesson)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_progress(request):
    """
    Get authenticated user's progress
    Requires authentication
    """
    progress = UserProgress.objects.filter(user=request.user, completed=True)
    serializer = UserProgressSerializer(progress, many=True)

    return Response({
        'progress': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_complete(request):
    """
    Mark a lesson as complete for authenticated user
    Requires authentication
    """
    lesson_id = request.data.get('lesson_id')

    if not lesson_id:
        return Response({
            'error': 'lesson_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Verify lesson exists
    try:
        lesson = Lesson.objects.get(lesson_id=lesson_id)
    except Lesson.DoesNotExist:
        return Response({
            'error': 'Lesson not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Create or update progress
    progress, created = UserProgress.objects.update_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': True}
    )

    # Manually trigger save to set completed_at
    if not progress.completed_at:
        progress.save()

    serializer = UserProgressSerializer(progress)

    return Response({
        'message': 'Lesson marked as complete',
        'progress': serializer.data
    }, status=status.HTTP_200_OK)
