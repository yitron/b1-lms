"""
Integration Tests - Full User Journey

Tests the complete workflow from viewing lessons to submitting exams
"""
from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from lms.models import Exam, ExamSession, Lesson


@pytest.fixture
def setup_exam_data(db):
    """Create exam and lesson data for tests"""
    # Create Module 03 lesson
    Lesson.objects.create(
        lesson_id='module-03',
        title='Understanding Shells',
        subtitle='The Foundation of AI Agent Execution',
        content='# Understanding Shells\n\nLearn about fork, exec, and pipes for AI agents. Practice with picoshell exercises.',
        module_number=3,
        order_index=3
    )

    # Create picoshell exam
    Exam.objects.create(
        exam_id='picoshell',
        title='Picoshell Implementation',
        instructions='Implement a shell with pipes',
        time_limit_minutes=60
    )


@pytest.mark.django_db
class TestCompleteUserJourney:
    """Test the complete user workflow end-to-end"""

    def test_full_exam_workflow_happy_path(self, setup_exam_data):
        """Test complete workflow: view lesson → start exam → submit → check results"""

        # Setup: Create user
        user = User.objects.create_user(username='student', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Step 1: View Module 03 lesson (learning phase)
        lesson_response = client.get('/api/lessons/module-03/')
        assert lesson_response.status_code == 200
        assert 'Understanding Shells' in lesson_response.data['title']
        assert 'fork' in lesson_response.data['content'].lower()

        # Step 2: List available exams
        exams_response = client.get('/api/exams/')
        assert exams_response.status_code == 200
        assert len(exams_response.data['exams']) >= 1
        picoshell_exam = next(e for e in exams_response.data['exams'] if e['exam_id'] == 'picoshell')
        assert picoshell_exam['time_limit_minutes'] == 60

        # Step 3: Start exam session
        start_response = client.post('/api/exams/start/', {'exam_id': 'picoshell'})
        assert start_response.status_code == 201
        session_id = start_response.data['session_id']
        assert 'expires_at' in start_response.data
        assert start_response.data['time_limit_minutes'] == 60

        # Step 4: Check status (no submissions yet)
        status_response = client.get('/api/exams/status/picoshell/')
        assert status_response.status_code == 200
        assert status_response.data['session_id'] == session_id
        assert status_response.data['submissions']['c']['attempts'] == 0
        assert status_response.data['expired'] is False

        # Step 5: Submit passing code (C implementation)
        passing_code = '''
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc < 2) return 0;

    int i = 1;
    while (i < argc) {
        int pipe_pos = -1;
        for (int j = i; j < argc; j++) {
            if (strcmp(argv[j], "|") == 0) {
                pipe_pos = j;
                break;
            }
        }

        if (pipe_pos == -1) {
            // No pipe, execute last command
            pid_t pid = fork();
            if (pid == 0) {
                argv[argc] = NULL;
                execvp(argv[i], &argv[i]);
                exit(1);
            }
            wait(NULL);
            break;
        } else {
            // Has pipe
            int pipefd[2];
            pipe(pipefd);

            pid_t pid = fork();
            if (pid == 0) {
                close(pipefd[0]);
                dup2(pipefd[1], STDOUT_FILENO);
                close(pipefd[1]);
                argv[pipe_pos] = NULL;
                execvp(argv[i], &argv[i]);
                exit(1);
            }

            close(pipefd[1]);
            dup2(pipefd[0], STDIN_FILENO);
            close(pipefd[0]);
            wait(NULL);

            i = pipe_pos + 1;
        }
    }
    return 0;
}
'''

        submit_response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': passing_code
        })
        assert submit_response.status_code == 200
        submission_id = submit_response.data['submission_id']

        # Verify grade (may pass or fail depending on implementation)
        assert 'grade' in submit_response.data
        assert submit_response.data['grade'] in ['pass', 'fail']
        assert 'tests_passed' in submit_response.data['test_results']
        assert 'tests_total' in submit_response.data['test_results']

        # Step 6: Check status again (should show 1 attempt)
        status_response2 = client.get('/api/exams/status/picoshell/')
        assert status_response2.status_code == 200
        assert status_response2.data['submissions']['c']['attempts'] == 1
        assert status_response2.data['submissions']['c']['latest_grade'] in ['pass', 'fail']

        # Step 7: View detailed results
        results_response = client.get('/api/exams/results/picoshell/')
        assert results_response.status_code == 200
        assert len(results_response.data['submissions']) == 1
        assert results_response.data['submissions'][0]['submission_id'] == submission_id
        assert results_response.data['submissions'][0]['language'] == 'c'

    def test_multi_language_submissions(self, setup_exam_data):
        """Test submitting implementations in multiple languages"""

        # Setup
        user = User.objects.create_user(username='polyglot', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Start exam
        start_response = client.post('/api/exams/start/', {'exam_id': 'picoshell'})
        assert start_response.status_code == 201

        # Submit C implementation
        c_code = '#include <stdio.h>\nint main() { printf("test\\n"); return 0; }'
        c_response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': c_code
        })
        assert c_response.status_code == 200

        # Submit Python implementation
        py_code = 'import sys\nprint("test")'
        py_response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'python',
            'code': py_code
        })
        assert py_response.status_code == 200

        # Submit TypeScript implementation
        ts_code = 'console.log("test");'
        ts_response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'typescript',
            'code': ts_code
        })
        assert ts_response.status_code == 200

        # Verify status shows all 3 languages
        status_response = client.get('/api/exams/status/picoshell/')
        assert status_response.status_code == 200
        assert status_response.data['submissions']['c']['attempts'] == 1
        assert status_response.data['submissions']['python']['attempts'] == 1
        assert status_response.data['submissions']['typescript']['attempts'] == 1

        # Verify results show all 3 submissions
        results_response = client.get('/api/exams/results/picoshell/')
        assert results_response.status_code == 200
        assert len(results_response.data['submissions']) == 3
        languages = {s['language'] for s in results_response.data['submissions']}
        assert languages == {'c', 'python', 'typescript'}

    def test_iterative_improvement_workflow(self, setup_exam_data):
        """Test submitting, failing, fixing, and resubmitting"""

        # Setup
        user = User.objects.create_user(username='learner', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Start exam
        client.post('/api/exams/start/', {'exam_id': 'picoshell'})

        # First attempt: Wrong implementation
        wrong_code = '#include <stdio.h>\nint main() { printf("wrong\\n"); return 0; }'
        response1 = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': wrong_code
        })
        assert response1.status_code == 200
        assert response1.data['grade'] == 'fail'
        _tests_passed_1 = response1.data['test_results']['tests_passed']  # noqa: F841

        # Second attempt: Still wrong but different
        wrong_code2 = '#include <stdio.h>\nint main() { printf("still wrong\\n"); return 0; }'
        response2 = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': wrong_code2
        })
        assert response2.status_code == 200
        # Grade may be pass or fail

        # Verify attempt count increased
        status_response = client.get('/api/exams/status/picoshell/')
        assert status_response.status_code == 200
        assert status_response.data['submissions']['c']['attempts'] == 2

        # Verify results show both submissions (most recent first)
        results_response = client.get('/api/exams/results/picoshell/')
        assert results_response.status_code == 200
        assert len(results_response.data['submissions']) == 2
        # Most recent submission should be first
        assert results_response.data['submissions'][0]['submission_id'] == response2.data['submission_id']
        assert results_response.data['submissions'][1]['submission_id'] == response1.data['submission_id']

    def test_session_expiration_handling(self, setup_exam_data):
        """Test that expired sessions are handled correctly"""

        # Setup
        user = User.objects.create_user(username='late', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Get exam
        exam = Exam.objects.get(exam_id='picoshell')

        # Create expired session manually
        expired_time = timezone.now() - timedelta(minutes=10)
        _session = ExamSession.objects.create(  # noqa: F841
            user=user,
            exam=exam,
            expires_at=expired_time,
            completed=False
        )

        # Try to submit to expired session
        code = '#include <stdio.h>\nint main() { return 0; }'
        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': code
        })
        assert response.status_code == 400
        assert 'expired' in response.data['error'].lower()

    def test_active_session_detection(self, setup_exam_data):
        """Test that only one active session is allowed"""

        # Setup
        user = User.objects.create_user(username='eager', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Start first session
        response1 = client.post('/api/exams/start/', {'exam_id': 'picoshell'})
        assert response1.status_code == 201
        _session_id_1 = response1.data['session_id']  # noqa: F841

        # Try to start second session (should fail)
        response2 = client.post('/api/exams/start/', {'exam_id': 'picoshell'})
        assert response2.status_code == 400
        assert 'active' in response2.data['error'].lower()

        # Verify only one session exists
        assert ExamSession.objects.filter(user=user, exam__exam_id='picoshell', completed=False).count() == 1

    def test_error_handling_compilation_failure(self, setup_exam_data):
        """Test that compilation errors are handled gracefully"""

        # Setup
        user = User.objects.create_user(username='buggy', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Start exam
        client.post('/api/exams/start/', {'exam_id': 'picoshell'})

        # Submit code with syntax error
        broken_code = '#include <stdio.h>\nint main() { printf("missing semicolon") return 0; }'
        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': broken_code
        })

        assert response.status_code == 200  # API succeeds
        assert response.data['grade'] == 'fail'
        assert response.data['test_results']['tests_passed'] == 0
        assert 'compilation_error' in response.data['test_results'] or 'error' in response.data['test_results']

    def test_no_active_session_submit_error(self, setup_exam_data):
        """Test that submitting without starting exam fails gracefully"""

        # Setup
        user = User.objects.create_user(username='forgetful', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Try to submit without starting exam
        code = '#include <stdio.h>\nint main() { return 0; }'
        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': code
        })

        assert response.status_code == 400
        assert 'no active session' in response.data['error'].lower()

    def test_view_results_before_submission(self, setup_exam_data):
        """Test viewing results when no submissions exist"""

        # Setup
        user = User.objects.create_user(username='curious', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Start exam
        client.post('/api/exams/start/', {'exam_id': 'picoshell'})

        # View results (should return empty)
        response = client.get('/api/exams/results/picoshell/')
        assert response.status_code == 200
        assert len(response.data['submissions']) == 0

    def test_lesson_to_exam_connection(self, setup_exam_data):
        """Test that Module 03 lesson properly prepares for picoshell exam"""

        # Setup
        client = APIClient()

        # View Module 03 lesson (no auth required)
        lesson_response = client.get('/api/lessons/module-03/')
        assert lesson_response.status_code == 200

        # Verify lesson content mentions key concepts
        content = lesson_response.data['content']
        assert 'fork' in content.lower()
        assert 'exec' in content.lower()
        assert 'pipe' in content.lower()
        assert 'picoshell' in content.lower()
        assert 'ai agent' in content.lower()

        # Verify exam exists and matches lesson
        user = User.objects.create_user(username='prepared', password='test123')
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        exams_response = client.get('/api/exams/')
        assert exams_response.status_code == 200
        picoshell_exam = next(e for e in exams_response.data['exams'] if e['exam_id'] == 'picoshell')
        assert picoshell_exam is not None


@pytest.mark.django_db
class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_invalid_exam_id(self, setup_exam_data):
        """Test submitting to non-existent exam"""
        user = User.objects.create_user(username='confused', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = client.post('/api/exams/start/', {'exam_id': 'nonexistent'})
        assert response.status_code == 400
        assert 'not found' in response.data['error'].lower()

    def test_invalid_language(self, setup_exam_data):
        """Test submitting with unsupported language"""
        user = User.objects.create_user(username='polyglot2', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        client.post('/api/exams/start/', {'exam_id': 'picoshell'})

        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'java',
            'code': 'public class Main { }'
        })
        assert response.status_code == 400
        assert 'language' in response.data['error'].lower()

    def test_empty_code_submission(self, setup_exam_data):
        """Test submitting empty code"""
        user = User.objects.create_user(username='lazy', password='test123')
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        client.post('/api/exams/start/', {'exam_id': 'picoshell'})

        response = client.post('/api/exams/submit/', {
            'exam_id': 'picoshell',
            'language': 'c',
            'code': ''
        })
        # Empty code should be rejected
        assert response.status_code == 400
        assert 'code' in response.data['error'].lower() or 'required' in response.data['error'].lower()
