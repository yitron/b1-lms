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


# Exam APIs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_exams(request):
    """
    List all available exams
    Requires authentication
    """
    from .models import Exam
    from .serializers import ExamSerializer

    exams = Exam.objects.all()
    serializer = ExamSerializer(exams, many=True)

    return Response({
        'exams': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_exam(request):
    """
    Start an exam session
    Requires authentication
    """
    from .models import Exam, ExamSession
    from django.utils import timezone
    from datetime import timedelta

    exam_id = request.data.get('exam_id')

    if not exam_id:
        return Response({
            'error': 'exam_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Verify exam exists
    try:
        exam = Exam.objects.get(exam_id=exam_id)
    except Exam.DoesNotExist:
        return Response({
            'error': 'Exam not found'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check for active session
    active_session = ExamSession.objects.filter(
        user=request.user,
        exam=exam,
        completed=False
    ).first()

    if active_session:
        return Response({
            'error': 'Active session already exists'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create new session
    started_at = timezone.now()
    expires_at = started_at + timedelta(minutes=exam.time_limit_minutes)

    session = ExamSession.objects.create(
        user=request.user,
        exam=exam,
        expires_at=expires_at
    )

    return Response({
        'session_id': session.id,
        'exam_id': exam.exam_id,
        'started_at': session.started_at.isoformat(),
        'expires_at': session.expires_at.isoformat(),
        'time_limit_minutes': exam.time_limit_minutes,
        'instructions': exam.instructions
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_exam(request):
    """
    Submit code for exam grading
    Requires authentication
    """
    from .models import Exam, ExamSession, ExamSubmission
    from .grading import ExamGrader

    # Validate required fields
    exam_id = request.data.get('exam_id')
    language = request.data.get('language')
    code = request.data.get('code')

    if not exam_id or not language or not code:
        return Response({
            'error': 'exam_id, language, and code are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate language
    if language not in ['c', 'python', 'typescript']:
        return Response({
            'error': 'Language must be one of: c, python, typescript'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Verify exam exists
    try:
        exam = Exam.objects.get(exam_id=exam_id)
    except Exam.DoesNotExist:
        return Response({
            'error': 'Exam not found'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check for active session
    active_session = ExamSession.objects.filter(
        user=request.user,
        exam=exam,
        completed=False
    ).first()

    if not active_session:
        return Response({
            'error': 'No active session found. Start exam first.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if session expired
    if active_session.is_expired():
        return Response({
            'error': 'Session expired'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Grade the submission
    grader = ExamGrader(exam_id)
    grade_result = grader.grade_submission(code, language)

    # Save submission
    submission = ExamSubmission.objects.create(
        session=active_session,
        language=language,
        grade=grade_result['grade'],
        test_results=grade_result
    )

    return Response({
        'submission_id': submission.id,
        'session_id': active_session.id,
        'language': language,
        'grade': grade_result['grade'],
        'test_results': grade_result,
        'submitted_at': submission.submitted_at.isoformat()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exam_status(request, exam_id):
    """
    Get exam session status
    Shows time remaining and submission attempts by language
    Requires authentication
    """
    from .models import Exam, ExamSession, ExamSubmission

    # Verify exam exists
    try:
        exam = Exam.objects.get(exam_id=exam_id)
    except Exam.DoesNotExist:
        return Response({
            'error': 'Exam not found'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get active session
    active_session = ExamSession.objects.filter(
        user=request.user,
        exam=exam,
        completed=False
    ).first()

    if not active_session:
        return Response({
            'error': 'No active session found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Get submissions summary by language
    submissions_summary = {}
    for language in ['c', 'python', 'typescript']:
        language_submissions = ExamSubmission.objects.filter(
            session=active_session,
            language=language
        ).order_by('-submitted_at')

        attempts = language_submissions.count()
        latest_grade = language_submissions.first().grade if language_submissions.exists() else None

        submissions_summary[language] = {
            'attempts': attempts,
            'latest_grade': latest_grade
        }

    return Response({
        'session_id': active_session.id,
        'exam_id': exam.exam_id,
        'started_at': active_session.started_at.isoformat(),
        'expires_at': active_session.expires_at.isoformat(),
        'time_remaining_minutes': active_session.time_remaining(),
        'expired': active_session.is_expired(),
        'completed': active_session.completed,
        'submissions': submissions_summary
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exam_results(request, exam_id):
    """
    Get detailed exam results
    Shows all submissions with test results in reverse chronological order
    Requires authentication
    """
    from .models import Exam, ExamSession, ExamSubmission

    # Verify exam exists
    try:
        exam = Exam.objects.get(exam_id=exam_id)
    except Exam.DoesNotExist:
        return Response({
            'error': 'Exam not found'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get most recent session (active or completed)
    session = ExamSession.objects.filter(
        user=request.user,
        exam=exam
    ).order_by('-started_at').first()

    if not session:
        return Response({
            'error': 'No session found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Get all submissions in reverse chronological order
    submissions = ExamSubmission.objects.filter(
        session=session
    ).order_by('-submitted_at')

    submissions_data = []
    for sub in submissions:
        submissions_data.append({
            'submission_id': sub.id,
            'language': sub.language,
            'grade': sub.grade,
            'test_results': sub.test_results,
            'submitted_at': sub.submitted_at.isoformat()
        })

    return Response({
        'session_id': session.id,
        'exam_id': exam.exam_id,
        'submissions': submissions_data
    }, status=status.HTTP_200_OK)
