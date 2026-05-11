"""
Lessons commands for B1 LMS CLI

Commands:
- lessons: List all available lessons
- view: View a specific lesson with markdown rendering
"""
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from lms_cli.api_client import APIClient
from lms_cli.config import Config


@click.command(name='lessons')
def lessons_list():
    """List all available lessons"""
    config = Config()
    api = APIClient()

    try:
        # Get all lessons
        response = api.get('lessons/')
        lessons = response.get('lessons', [])

        if not lessons:
            click.echo(click.style('No lessons available.', fg='yellow'))
            return

        # Check if user is logged in to show progress
        progress_map = {}
        if config.has_token():
            try:
                token = config.load_token()
                auth_api = APIClient(token=token)
                progress_response = auth_api.get('progress/')
                progress_list = progress_response.get('progress', [])

                # Create map of lesson_id -> completed status
                for progress in progress_list:
                    progress_map[progress['lesson_id']] = progress.get('completed', False)
            except Exception:
                # If progress fetch fails, just don't show progress
                pass

        # Create table with Rich
        console = Console()
        table = Table(title="Available Lessons", show_header=True, header_style="bold magenta")
        table.add_column("Module", style="cyan", width=12)
        table.add_column("Title", style="white")
        table.add_column("Subtitle", style="dim")
        table.add_column("Status", justify="center", width=10)

        for lesson in lessons:
            lesson_id = lesson['lesson_id']
            title = lesson['title']
            subtitle = lesson.get('subtitle', '')
            module_num = lesson.get('module_number', 0)

            # Check completion status
            is_complete = progress_map.get(lesson_id, False)
            status = click.style('✓', fg='green') if is_complete else '○'

            table.add_row(
                f"Module {module_num:02d}",
                title,
                subtitle,
                status
            )

        console.print(table)

        # Show summary
        if progress_map:
            completed = sum(1 for v in progress_map.values() if v)
            total = len(lessons)
            console.print(f"\nProgress: {completed}/{total} lessons completed ({completed*100//total if total > 0 else 0}%)")

    except Exception as e:
        click.echo(click.style(f'✗ Failed to fetch lessons: {str(e)}', fg='red'), err=True)
        raise click.Abort()


@click.command(name='view')
@click.argument('lesson_id')
def view_lesson(lesson_id):
    """View a specific lesson

    Args:
        lesson_id: The lesson ID (e.g., module-00)
    """
    api = APIClient()

    try:
        # Fetch lesson
        lesson = api.get(f'lessons/{lesson_id}/')

        title = lesson['title']
        subtitle = lesson.get('subtitle', '')
        content = lesson['content']
        quiz_data = lesson.get('quiz_data')

        # Display with Rich
        console = Console()

        # Print header
        console.print()
        console.print(Panel(
            f"[bold]{title}[/bold]\n{subtitle}",
            title=f"📚 {lesson_id}",
            border_style="blue"
        ))
        console.print()

        # Render markdown content
        md = Markdown(content)
        console.print(md)

        # Show quiz info if available
        if quiz_data and quiz_data.get('questions'):
            num_questions = len(quiz_data['questions'])
            console.print()
            console.print(Panel(
                f"This lesson has a quiz with {num_questions} question{'s' if num_questions != 1 else ''}.\n"
                f"Use [bold]lms quiz {lesson_id}[/bold] to take the quiz.",
                title="📝 Quiz Available",
                border_style="yellow"
            ))

        console.print()

    except Exception as e:
        error_msg = str(e)
        if '404' in error_msg or 'not found' in error_msg.lower():
            click.echo(click.style(f'✗ Lesson not found: {lesson_id}', fg='red'), err=True)
        else:
            click.echo(click.style(f'✗ Error: {error_msg}', fg='red'), err=True)
        raise click.Abort()
