from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestExamListAPI:
    """Test GET /api/exams/ endpoint"""

    def test_list_exams_authenticated(self):
        """Test listing exams when authenticated"""
        from lms.models import Exam

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exams
        Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )
        Exam.objects.create(
            exam_id='minishell',
            title='Minishell Implementation',
            instructions='Write minishell program...',
            time_limit_minutes=120
        )

        # Make API request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.get('/api/exams/')

        # Assert response
        assert response.status_code == 200
        assert 'exams' in response.data
        assert len(response.data['exams']) == 2

        # Check exam data
        exam_ids = [exam['exam_id'] for exam in response.data['exams']]
        assert 'picoshell' in exam_ids
        assert 'minishell' in exam_ids

        # Check fields present
        first_exam = response.data['exams'][0]
        assert 'exam_id' in first_exam
        assert 'title' in first_exam
        assert 'time_limit_minutes' in first_exam
        # Instructions should NOT be in list view
        assert 'instructions' not in first_exam

    def test_list_exams_unauthenticated(self):
        """Test listing exams without authentication returns 401"""
        from lms.models import Exam

        # Create test exam
        Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Make API request without auth
        client = APIClient()
        response = client.get('/api/exams/')

        # Assert 401 Unauthorized
        assert response.status_code == 401

    def test_list_exams_empty(self):
        """Test listing exams when no exams exist"""
        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Make API request (no exams created)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.get('/api/exams/')

        # Assert response
        assert response.status_code == 200
        assert 'exams' in response.data
        assert len(response.data['exams']) == 0


@pytest.mark.django_db
class TestStartExamAPI:
    """Test POST /api/exams/start/ endpoint"""

    def test_start_exam_success(self):
        """Test starting an exam creates session"""
        from lms.models import Exam, ExamSession

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Make API request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/exams/start/', {'exam_id': 'picoshell'})

        # Assert response
        assert response.status_code == 201
        assert 'session_id' in response.data
        assert response.data['exam_id'] == 'picoshell'
        assert 'started_at' in response.data
        assert 'expires_at' in response.data
        assert response.data['time_limit_minutes'] == 60
        assert 'instructions' in response.data
        assert response.data['instructions'] == 'Write picoshell function...'

        # Verify session created in database
        session = ExamSession.objects.get(id=response.data['session_id'])
        assert session.user == user
        assert session.exam == exam
        assert session.completed is False

        # Verify expires_at is correct (started_at + 60 minutes)
        time_diff = session.expires_at - session.started_at
        assert abs(time_diff.total_seconds() - 3600) < 5  # Within 5 seconds of 1 hour

    def test_start_exam_not_found(self):
        """Test starting non-existent exam returns 400"""
        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Make API request with non-existent exam
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/exams/start/', {'exam_id': 'nonexistent'})

        # Assert 400 Bad Request
        assert response.status_code == 400
        assert 'error' in response.data
        assert 'not found' in response.data['error'].lower()

    def test_start_exam_active_session_exists(self):
        """Test starting exam when active session exists returns 400"""
        from lms.models import Exam, ExamSession

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create existing active session
        expires_at = timezone.now() + timedelta(minutes=60)
        ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=False
        )

        # Try to start another session
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/exams/start/', {'exam_id': 'picoshell'})

        # Assert 400 Bad Request
        assert response.status_code == 400
        assert 'error' in response.data
        assert 'active session' in response.data['error'].lower()

    def test_start_exam_after_completed_session(self):
        """Test starting exam after previous session completed is allowed"""
        from lms.models import Exam, ExamSession

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create completed session
        expires_at = timezone.now() + timedelta(minutes=60)
        ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=True  # Completed
        )

        # Start new session should work
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/exams/start/', {'exam_id': 'picoshell'})

        # Assert success
        assert response.status_code == 201
        assert 'session_id' in response.data

    def test_start_exam_unauthenticated(self):
        """Test starting exam without authentication returns 401"""
        from lms.models import Exam

        # Create test exam
        Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Make API request without auth
        client = APIClient()
        response = client.post('/api/exams/start/', {'exam_id': 'picoshell'})

        # Assert 401 Unauthorized
        assert response.status_code == 401

    def test_start_exam_missing_exam_id(self):
        """Test starting exam without exam_id returns 400"""
        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Make API request without exam_id
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/exams/start/', {})

        # Assert 400 Bad Request
        assert response.status_code == 400
        assert 'error' in response.data


@pytest.mark.django_db
class TestSubmitExamAPI:
    """Test POST /api/exams/submit/ endpoint"""

    def test_submit_exam_success(self):
        """Test submitting code for grading"""
        from lms.models import Exam, ExamSession, ExamSubmission

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create active session
        expires_at = timezone.now() + timedelta(minutes=60)
        session = ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=False
        )

        # Simple C code
        c_code = '''
#include <stdio.h>
int main() {
    printf("test\\n");
    return 0;
}
'''

        # Make API request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': c_code
        })

        # Assert response
        assert response.status_code == 200
        assert 'submission_id' in response.data
        assert 'session_id' in response.data
        assert 'language' in response.data
        assert 'grade' in response.data
        assert 'test_results' in response.data
        assert 'submitted_at' in response.data

        # Verify submission created in database
        submission = ExamSubmission.objects.get(id=response.data['submission_id'])
        assert submission.session == session
        assert submission.language == 'c'
        assert submission.grade in ['pass', 'fail']

    def test_submit_exam_no_active_session(self):
        """Test submitting without active session returns 400"""
        from lms.models import Exam

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam (but no session)
        Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Make API request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': 'int main() { return 0; }'
        })

        # Assert 400 Bad Request
        assert response.status_code == 400
        assert 'error' in response.data
        assert 'no active session' in response.data['error'].lower()

    def test_submit_exam_expired_session(self):
        """Test submitting with expired session returns 400"""
        from lms.models import Exam, ExamSession

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create expired session
        expires_at = timezone.now() - timedelta(minutes=10)
        ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=False
        )

        # Make API request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': 'int main() { return 0; }'
        })

        # Assert 400 Bad Request
        assert response.status_code == 400
        assert 'error' in response.data
        assert 'expired' in response.data['error'].lower()

    def test_submit_exam_multiple_attempts(self):
        """Test multiple submissions for same language allowed"""
        from lms.models import Exam, ExamSession, ExamSubmission

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create active session
        expires_at = timezone.now() + timedelta(minutes=60)
        session = ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=False
        )

        # First submission
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response1 = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': 'int main() { return 0; }'
        })
        assert response1.status_code == 200

        # Second submission (same language)
        response2 = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': 'int main() { return 1; }'
        })
        assert response2.status_code == 200

        # Verify 2 submissions exist
        assert ExamSubmission.objects.filter(session=session, language='c').count() == 2

    def test_submit_exam_unauthenticated(self):
        """Test submitting without authentication returns 401"""
        from lms.models import Exam

        # Create test exam
        Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Make API request without auth
        client = APIClient()
        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': 'int main() { return 0; }'
        })

        # Assert 401 Unauthorized
        assert response.status_code == 401

    def test_submit_exam_missing_fields(self):
        """Test submitting without required fields returns 400"""
        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Make API request without code field
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c'
            # Missing 'code'
        })

        # Assert 400 Bad Request
        assert response.status_code == 400
        assert 'error' in response.data

    def test_submit_exam_invalid_language(self):
        """Test submitting with invalid language returns 400"""
        from lms.models import Exam, ExamSession

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create active session
        expires_at = timezone.now() + timedelta(minutes=60)
        ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=False
        )

        # Make API request with invalid language
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'java',  # Invalid
            'code': 'public class Main { }'
        })

        # Assert 400 Bad Request
        assert response.status_code == 400
        assert 'error' in response.data


@pytest.mark.django_db
class TestExamStatusAPI:
    """Test GET /api/exams/status/<exam_id>/ endpoint"""

    def test_get_exam_status_active_session(self):
        """Test getting exam status with active session"""
        from lms.models import Exam, ExamSession, ExamSubmission

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create active session
        started_at = timezone.now()
        expires_at = started_at + timedelta(minutes=60)
        session = ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=False
        )

        # Create some submissions
        ExamSubmission.objects.create(
            session=session,
            language='c',
            grade='fail',
            test_results={'tests_passed': 2, 'tests_total': 5}
        )
        ExamSubmission.objects.create(
            session=session,
            language='c',
            grade='pass',
            test_results={'tests_passed': 5, 'tests_total': 5}
        )
        ExamSubmission.objects.create(
            session=session,
            language='python',
            grade='fail',
            test_results={'tests_passed': 3, 'tests_total': 5}
        )

        # Make API request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.get(f'/api/exams/status/{exam.exam_id}/')

        # Assert response
        assert response.status_code == 200
        assert response.data['session_id'] == session.id
        assert response.data['exam_id'] == exam.exam_id
        assert 'started_at' in response.data
        assert 'expires_at' in response.data
        assert 'time_remaining_minutes' in response.data
        assert response.data['expired'] is False
        assert response.data['completed'] is False

        # Check submissions summary
        assert 'submissions' in response.data
        submissions = response.data['submissions']
        assert 'c' in submissions
        assert 'python' in submissions
        assert 'typescript' in submissions

        # C submissions
        assert submissions['c']['attempts'] == 2
        assert submissions['c']['latest_grade'] == 'pass'

        # Python submissions
        assert submissions['python']['attempts'] == 1
        assert submissions['python']['latest_grade'] == 'fail'

        # TypeScript submissions
        assert submissions['typescript']['attempts'] == 0
        assert submissions['typescript']['latest_grade'] is None

    def test_get_exam_status_no_session(self):
        """Test getting exam status without session returns 404"""
        from lms.models import Exam

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam (but no session)
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Make API request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.get(f'/api/exams/status/{exam.exam_id}/')

        # Assert 404 Not Found
        assert response.status_code == 404
        assert 'error' in response.data

    def test_get_exam_status_unauthenticated(self):
        """Test getting exam status without authentication returns 401"""
        from lms.models import Exam

        # Create test exam
        Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Make API request without auth
        client = APIClient()
        response = client.get('/api/exams/status/picoshell/')

        # Assert 401 Unauthorized
        assert response.status_code == 401


@pytest.mark.django_db
class TestExamResultsAPI:
    """Test GET /api/exams/results/<exam_id>/ endpoint"""

    def test_get_exam_results_with_submissions(self):
        """Test getting detailed exam results"""
        from lms.models import Exam, ExamSession, ExamSubmission

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create session
        expires_at = timezone.now() + timedelta(minutes=60)
        session = ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=False
        )

        # Create submissions with detailed test results
        sub1 = ExamSubmission.objects.create(
            session=session,
            language='c',
            grade='pass',
            test_results={
                'grade': 'pass',
                'tests_passed': 5,
                'tests_total': 5,
                'tests': [
                    {'name': 'test1', 'passed': True},
                    {'name': 'test2', 'passed': True}
                ]
            }
        )

        sub2 = ExamSubmission.objects.create(
            session=session,
            language='python',
            grade='fail',
            test_results={
                'grade': 'fail',
                'tests_passed': 3,
                'tests_total': 5,
                'tests': [
                    {'name': 'test1', 'passed': True},
                    {'name': 'test2', 'passed': False}
                ]
            }
        )

        # Make API request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.get(f'/api/exams/results/{exam.exam_id}/')

        # Assert response
        assert response.status_code == 200
        assert response.data['session_id'] == session.id
        assert response.data['exam_id'] == exam.exam_id
        assert 'submissions' in response.data

        submissions = response.data['submissions']
        assert len(submissions) == 2

        # Check first submission (most recent = python)
        assert submissions[0]['submission_id'] == sub2.id
        assert submissions[0]['language'] == 'python'
        assert submissions[0]['grade'] == 'fail'
        assert 'test_results' in submissions[0]
        assert 'submitted_at' in submissions[0]

        # Check second submission (older = c)
        assert submissions[1]['submission_id'] == sub1.id
        assert submissions[1]['language'] == 'c'
        assert submissions[1]['grade'] == 'pass'

    def test_get_exam_results_no_session(self):
        """Test getting exam results without session returns 404"""
        from lms.models import Exam

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam (but no session)
        Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Make API request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.get('/api/exams/results/picoshell/')

        # Assert 404 Not Found
        assert response.status_code == 404
        assert 'error' in response.data

    def test_get_exam_results_empty_submissions(self):
        """Test getting exam results with no submissions"""
        from lms.models import Exam, ExamSession

        # Create test user and token
        user = User.objects.create_user(username='testuser', password='test123')
        token = Token.objects.create(user=user)

        # Create test exam
        exam = Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Create session (no submissions)
        expires_at = timezone.now() + timedelta(minutes=60)
        ExamSession.objects.create(
            user=user,
            exam=exam,
            expires_at=expires_at,
            completed=False
        )

        # Make API request
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.get(f'/api/exams/results/{exam.exam_id}/')

        # Assert response
        assert response.status_code == 200
        assert 'submissions' in response.data
        assert len(response.data['submissions']) == 0

    def test_get_exam_results_unauthenticated(self):
        """Test getting exam results without authentication returns 401"""
        from lms.models import Exam

        # Create test exam
        Exam.objects.create(
            exam_id='picoshell',
            title='Picoshell Implementation',
            instructions='Write picoshell function...',
            time_limit_minutes=60
        )

        # Make API request without auth
        client = APIClient()
        response = client.get('/api/exams/results/picoshell/')

        # Assert 401 Unauthorized
        assert response.status_code == 401
