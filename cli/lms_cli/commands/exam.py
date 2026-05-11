"""
Exam commands for B1 LMS CLI

Commands:
- exams: List all available exams
- exam start: Start an exam session
- exam status: Check exam status (time remaining, attempts)
- exam submit: Submit code for grading
- exam results: View detailed test results
"""
import os

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from lms_cli.api_client import APIClient
from lms_cli.config import Config


@click.command(name='exams')
def exams_list():
    """List all available exams"""
    config = Config()

    # Check authentication
    if not config.has_token():
        click.echo(click.style('✗ Not logged in. Please run: lms login', fg='red'), err=True)
        raise click.Abort()

    token = config.load_token()
    api = APIClient(token=token)

    try:
        # Fetch exams
        response = api.get('exams/')
        exams = response.get('exams', [])

        if not exams:
            click.echo(click.style('No exams available.', fg='yellow'))
            return

        # Display with Rich
        console = Console()
        table = Table(title="Available Exams", show_header=True, header_style="bold magenta")
        table.add_column("Exam ID", style="cyan", width=15)
        table.add_column("Title", style="white")
        table.add_column("Time Limit", justify="center", width=12)

        for exam in exams:
            exam_id = exam['exam_id']
            title = exam['title']
            time_limit = exam['time_limit_minutes']

            table.add_row(
                exam_id,
                title,
                f"{time_limit} min"
            )

        console.print(table)
        console.print("\n💡 Start an exam with: [bold]lms exam start <exam_id>[/bold]")

    except Exception as e:
        click.echo(click.style(f'✗ Failed to fetch exams: {str(e)}', fg='red'), err=True)
        raise click.Abort()


@click.group(name='exam')
def exam_group():
    """Exam commands (start, status, submit, results)"""
    pass


@exam_group.command(name='start')
@click.argument('exam_id')
def start_exam(exam_id):
    """Start an exam session

    Args:
        exam_id: The exam identifier (e.g., picoshell)
    """
    config = Config()

    # Check authentication
    if not config.has_token():
        click.echo(click.style('✗ Not logged in. Please run: lms login', fg='red'), err=True)
        raise click.Abort()

    token = config.load_token()
    api = APIClient(token=token)

    try:
        # Start exam session
        response = api.post('exams/start/', {'exam_id': exam_id})

        session_id = response['session_id']
        time_limit = response['time_limit_minutes']
        instructions = response.get('instructions', '')
        started_at = response['started_at']
        expires_at = response['expires_at']

        # Display with Rich
        console = Console()

        console.print()
        console.print(Panel(
            f"[bold green]✓ Exam session started![/bold green]\n\n"
            f"Session ID: {session_id}\n"
            f"Time Limit: {time_limit} minutes\n"
            f"Started: {started_at}\n"
            f"Expires: {expires_at}",
            title=f"📝 {exam_id}",
            border_style="green"
        ))

        # Show instructions
        if instructions:
            console.print()
            console.print(Panel(
                Markdown(instructions),
                title="📋 Instructions",
                border_style="blue"
            ))

        console.print()
        console.print("💡 Commands:")
        console.print(f"  • Check status: [bold]lms exam status {exam_id}[/bold]")
        console.print(f"  • Submit code:  [bold]lms exam submit {exam_id} --lang <c|python|typescript> --file <path>[/bold]")
        console.print(f"  • View results: [bold]lms exam results {exam_id}[/bold]")
        console.print()

    except Exception as e:
        error_msg = str(e)
        if 'active' in error_msg.lower() or 'already exists' in error_msg.lower():
            click.echo(click.style(f'✗ Active session already exists for {exam_id}', fg='red'), err=True)
        else:
            click.echo(click.style(f'✗ Error: {error_msg}', fg='red'), err=True)
        raise click.Abort()


@exam_group.command(name='status')
@click.argument('exam_id')
def exam_status(exam_id):
    """Check exam session status

    Args:
        exam_id: The exam identifier
    """
    config = Config()

    # Check authentication
    if not config.has_token():
        click.echo(click.style('✗ Not logged in. Please run: lms login', fg='red'), err=True)
        raise click.Abort()

    token = config.load_token()
    api = APIClient(token=token)

    try:
        # Get exam status
        response = api.get(f'exams/status/{exam_id}/')

        session_id = response['session_id']
        time_remaining = response['time_remaining_minutes']
        expired = response['expired']
        completed = response['completed']
        submissions = response['submissions']

        # Display with Rich
        console = Console()

        # Session info
        console.print()
        status_text = "[bold red]EXPIRED[/bold red]" if expired else "[bold yellow]IN PROGRESS[/bold yellow]"
        if completed:
            status_text = "[bold blue]COMPLETED[/bold blue]"

        console.print(Panel(
            f"Session ID: {session_id}\n"
            f"Status: {status_text}\n"
            f"Time Remaining: {time_remaining} minutes",
            title=f"📝 {exam_id} - Status",
            border_style="yellow"
        ))

        # Submissions summary
        console.print()
        table = Table(title="Submissions by Language", show_header=True, header_style="bold cyan")
        table.add_column("Language", style="white", width=12)
        table.add_column("Attempts", justify="center", width=10)
        table.add_column("Latest Grade", justify="center", width=15)

        for lang in ['c', 'python', 'typescript']:
            lang_data = submissions.get(lang, {'attempts': 0, 'latest_grade': None})
            attempts = lang_data['attempts']
            grade = lang_data['latest_grade']

            if grade == 'pass':
                grade_display = click.style('✓ PASS', fg='green')
            elif grade == 'fail':
                grade_display = click.style('✗ FAIL', fg='red')
            else:
                grade_display = '—'

            table.add_row(
                lang.capitalize(),
                str(attempts),
                grade_display
            )

        console.print(table)
        console.print()

    except Exception as e:
        error_msg = str(e)
        if 'no' in error_msg.lower() and 'session' in error_msg.lower():
            click.echo(click.style(f'✗ No active session found for {exam_id}', fg='red'), err=True)
        else:
            click.echo(click.style(f'✗ Error: {error_msg}', fg='red'), err=True)
        raise click.Abort()


@exam_group.command(name='submit')
@click.argument('exam_id')
@click.option('--lang', '-l', type=click.Choice(['c', 'python', 'typescript']), required=True, help='Programming language')
def submit_exam(exam_id, lang):
    """Submit code for grading

    Files must be named {exam_id}.{ext} and located in ~/exam/
    - C:          picoshell.c
    - Python:     picoshell.py
    - TypeScript: picoshell.ts

    Args:
        exam_id: The exam identifier
        lang: Programming language (c, python, typescript)
    """
    config = Config()

    # Check authentication
    if not config.has_token():
        click.echo(click.style('✗ Not logged in. Please run: lms login', fg='red'), err=True)
        raise click.Abort()

    # Determine file extension based on language
    extensions = {
        'c': 'c',
        'python': 'py',
        'typescript': 'ts'
    }
    ext = extensions[lang]

    # Build file path: ~/exam/{exam_id}.{ext}
    exam_dir = os.path.expanduser('~/exam')
    filename = f'{exam_id}.{ext}'
    file_path = os.path.join(exam_dir, filename)

    # Check if file exists
    if not os.path.exists(file_path):
        click.echo(click.style(f'✗ File not found: {file_path}', fg='red'), err=True)
        click.echo(f'\nExpected file: [bold]{filename}[/bold] in directory: [bold]{exam_dir}/[/bold]')
        click.echo(f'\nCreate your file with: vim {file_path}', err=True)
        raise click.Abort()

    # Read file
    try:
        with open(file_path, 'r') as f:
            code = f.read()
    except Exception as e:
        click.echo(click.style(f'✗ Error reading file: {str(e)}', fg='red'), err=True)
        raise click.Abort()

    token = config.load_token()
    api = APIClient(token=token)

    try:
        # Submit code
        console = Console()
        console.print(f"\n🚀 Submitting {lang} code for grading...")

        response = api.post('exams/submit/', {
            'exam_id': exam_id,
            'language': lang,
            'code': code
        })

        submission_id = response['submission_id']
        grade = response['grade']
        test_results = response['test_results']
        tests_passed = test_results['tests_passed']
        tests_total = test_results['tests_total']

        console.print()

        # Show grade
        if grade == 'pass':
            console.print(Panel(
                f"[bold green]✓ ALL TESTS PASSED![/bold green]\n\n"
                f"Submission ID: {submission_id}\n"
                f"Tests Passed: {tests_passed}/{tests_total}\n"
                f"Grade: PASS",
                title="🎉 Success",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[bold red]✗ Some tests failed[/bold red]\n\n"
                f"Submission ID: {submission_id}\n"
                f"Tests Passed: {tests_passed}/{tests_total}\n"
                f"Grade: FAIL",
                title="Test Results",
                border_style="red"
            ))

            # Show test details
            console.print("\n📋 Test Details:")
            for test in test_results.get('tests', []):
                test_name = test['name']
                passed = test['passed']

                if passed:
                    console.print(f"  [green]✓[/green] {test_name}")
                else:
                    console.print(f"  [red]✗[/red] {test_name}")
                    console.print(f"      Expected: {test.get('expected', 'N/A')}")
                    console.print(f"      Got: {test.get('actual', 'N/A')}")

        console.print(f"\n💡 View full results: [bold]lms exam results {exam_id}[/bold]\n")

    except Exception as e:
        error_msg = str(e)
        click.echo(click.style(f'✗ Submission failed: {error_msg}', fg='red'), err=True)
        raise click.Abort()


@exam_group.command(name='results')
@click.argument('exam_id')
def exam_results(exam_id):
    """View detailed exam results

    Args:
        exam_id: The exam identifier
    """
    config = Config()

    # Check authentication
    if not config.has_token():
        click.echo(click.style('✗ Not logged in. Please run: lms login', fg='red'), err=True)
        raise click.Abort()

    token = config.load_token()
    api = APIClient(token=token)

    try:
        # Get results
        response = api.get(f'exams/results/{exam_id}/')

        session_id = response['session_id']
        submissions = response['submissions']

        console = Console()

        if not submissions:
            console.print()
            console.print(Panel(
                "No submissions yet.\n\n"
                f"Submit your code with:\n"
                f"[bold]lms exam submit {exam_id} --lang <language> --file <path>[/bold]",
                title=f"📝 {exam_id} - Results",
                border_style="yellow"
            ))
            console.print()
            return

        # Display submissions
        console.print()
        console.print(Panel(
            f"Session ID: {session_id}\n"
            f"Total Submissions: {len(submissions)}",
            title=f"📝 {exam_id} - Results",
            border_style="blue"
        ))

        # Create table
        console.print()
        table = Table(title="All Submissions (Most Recent First)", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=5)
        table.add_column("Language", style="white", width=12)
        table.add_column("Grade", justify="center", width=10)
        table.add_column("Tests", justify="center", width=10)
        table.add_column("Submitted", style="dim", width=20)

        for idx, sub in enumerate(submissions, 1):
            lang = sub['language']
            grade = sub['grade']
            test_results = sub['test_results']
            tests_passed = test_results['tests_passed']
            tests_total = test_results['tests_total']
            submitted_at = sub['submitted_at']

            if grade == 'pass':
                grade_display = click.style('✓ PASS', fg='green')
            else:
                grade_display = click.style('✗ FAIL', fg='red')

            table.add_row(
                str(idx),
                lang.capitalize(),
                grade_display,
                f"{tests_passed}/{tests_total}",
                submitted_at[:19]  # Trim to YYYY-MM-DDTHH:MM:SS
            )

        console.print(table)
        console.print()

    except Exception as e:
        error_msg = str(e)
        click.echo(click.style(f'✗ Error: {error_msg}', fg='red'), err=True)
        raise click.Abort()
