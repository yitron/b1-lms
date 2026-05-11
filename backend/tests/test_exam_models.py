import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestExamModel:
    """Test Exam model"""

    def test_exam_creation(self):
        """Test creating an exam"""
        from lms.models import Exam

        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        assert exam.exam_id == 'picoshell'
        assert exam.title == 'Picoshell Implementation'
        assert exam.time_limit_minutes == 60
        assert exam.created_at is not None

    def test_exam_str_representation(self):
        """Test exam __str__ method"""
        from lms.models import Exam

        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        assert str(exam) == 'picoshell: Picoshell Implementation'

    def test_exam_id_is_unique(self):
        """Test exam_id must be unique"""
        from lms.models import Exam
        from django.db import IntegrityError

        Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        with pytest.raises(IntegrityError):
            Exam.objects.create(
                exam_id='picoshell',  # Duplicate
                title='Another Exam',
                instructions='Different instructions',
                time_limit_minutes=30
            )


@pytest.mark.django_db
class TestExamSessionModel:
    """Test ExamSession model"""

    def test_exam_session_creation(self):
        """Test creating an exam session"""
        from lms.models import Exam, ExamSession

        user = User.objects.create_user(username='testuser', password='test123')
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        started_at = timezone.now()
        expires_at = started_at + timedelta(minutes=60)

        session = ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at
        )

        assert session.user == user
        assert session.exam == exam
        assert session.started_at is not None
        assert session.expires_at == expires_at
        assert session.completed is False

    def test_exam_session_is_expired(self):
        """Test is_expired() method"""
        from lms.models import Exam, ExamSession

        user = User.objects.create_user(username='testuser', password='test123')
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create expired session (expires in the past)
        expires_at = timezone.now() - timedelta(minutes=10)
        session = ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at
        )

        assert session.is_expired() is True

    def test_exam_session_time_remaining(self):
        """Test time_remaining() method"""
        from lms.models import Exam, ExamSession

        user = User.objects.create_user(username='testuser', password='test123')
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create session that expires in 45 minutes
        expires_at = timezone.now() + timedelta(minutes=45)
        session = ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at
        )

        time_remaining = session.time_remaining()
        assert 44 <= time_remaining <= 45  # Account for execution time

    def test_one_active_session_per_user_per_exam(self):
        """Test unique constraint for active sessions"""
        from lms.models import Exam, ExamSession
        from django.db import IntegrityError

        user = User.objects.create_user(username='testuser', password='test123')
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create first active session
        expires_at = timezone.now() + timedelta(minutes=60)
        ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=False
        )

        # Try to create second active session - should fail
        with pytest.raises(IntegrityError):
            ExamSession.objects.create(
                user=user,
                exam=exam,
                expires_at=expires_at,
                completed=False
            )

    def test_multiple_completed_sessions_allowed(self):
        """Test multiple completed sessions are allowed"""
        from lms.models import Exam, ExamSession

        user = User.objects.create_user(username='testuser', password='test123')
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        expires_at = timezone.now() + timedelta(minutes=60)

        # Create first completed session
        ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=True
        )

        # Create second completed session - should work
        ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=True
        )

        assert ExamSession.objects.filter(user=user, exam=exam, completed=True).count() == 2


@pytest.mark.django_db
class TestExamSubmissionModel:
    """Test ExamSubmission model"""

    def test_exam_submission_creation(self):
        """Test creating an exam submission"""
        from lms.models import Exam, ExamSession, ExamSubmission

        user = User.objects.create_user(username='testuser', password='test123')
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        expires_at = timezone.now() + timedelta(minutes=60)
        session = ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at
        )

        submission = ExamSubmission.objects.create(
            session=session,
            language='c',
            grade='pass',
            test_results={
                'tests_passed': 5,
                'tests_total': 5,
                'tests': []
            }
        )

        assert submission.session == session
        assert submission.language == 'c'
        assert submission.grade == 'pass'
        assert submission.test_results['tests_passed'] == 5
        assert submission.submitted_at is not None

    def test_exam_submission_ordering(self):
        """Test submissions are ordered by most recent first"""
        from lms.models import Exam, ExamSession, ExamSubmission

        user = User.objects.create_user(username='testuser', password='test123')
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        expires_at = timezone.now() + timedelta(minutes=60)
        session = ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at
        )

        # Create submissions in order
        submission1 = ExamSubmission.objects.create(
            session=session,
            language='c',
            grade='fail',
            test_results={}
        )

        submission2 = ExamSubmission.objects.create(
            session=session,
            language='c',
            grade='pass',
            test_results={}
        )

        # Get all submissions - should be ordered by most recent first
        submissions = ExamSubmission.objects.filter(session=session)
        assert submissions[0] == submission2  # Most recent
        assert submissions[1] == submission1

    def test_multiple_submissions_same_language(self):
        """Test multiple submissions for same language are allowed"""
        from lms.models import Exam, ExamSession, ExamSubmission

        user = User.objects.create_user(username='testuser', password='test123')
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        expires_at = timezone.now() + timedelta(minutes=60)
        session = ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at
        )

        # Create multiple C submissions
        ExamSubmission.objects.create(
            session=session,
            language='c',
            grade='fail',
            test_results={}
        )

        ExamSubmission.objects.create(
            session=session,
            language='c',
            grade='pass',
            test_results={}
        )

        assert ExamSubmission.objects.filter(session=session, language='c').count() == 2
