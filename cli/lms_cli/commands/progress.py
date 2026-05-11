"""
Progress commands for B1 LMS CLI

Commands:
- progress: Show user's progress and completion status
- complete: Mark a lesson as complete
"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from lms_cli.api_client import APIClient
from lms_cli.config import Config


@click.command(name='progress')
def show_progress():
    """Show your learning progress"""
    config = Config()

    # Check if logged in
    if not config.has_token():
        click.echo(click.style('✗ You are not logged in.', fg='red'), err=True)
        click.echo('Please use "lms login" to authenticate.')
        raise click.Abort()

    token = config.load_token()
    api = APIClient(token=token)

    try:
        # Fetch all lessons
        lessons_response = api.get('lessons/')
        lessons = lessons_response.get('lessons', [])

        # Fetch user progress
        progress_response = api.get('progress/')
        progress_list = progress_response.get('progress', [])

        # Create map of completed lessons
        completed_lessons = {p['lesson_id']: p for p in progress_list if p.get('completed')}

        if not lessons:
            click.echo(click.style('No lessons available.', fg='yellow'))
            return

        # Create Rich table
        console = Console()
        table = Table(title="Your Learning Progress", show_header=True, header_style="bold magenta")
        table.add_column("Module", style="cyan", width=12)
        table.add_column("Title", style="white")
        table.add_column("Status", justify="center", width=15)
        table.add_column("Completed", style="dim", width=20)

        for lesson in lessons:
            lesson_id = lesson['lesson_id']
            title = lesson['title']
            module_num = lesson.get('module_number', 0)

            if lesson_id in completed_lessons:
                status = click.style('✓ Complete', fg='green')
                completed_at = completed_lessons[lesson_id].get('completed_at', '')
                # Format date if available
                if completed_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                        completed_date = dt.strftime('%Y-%m-%d')
                    except (ValueError, AttributeError):
                        completed_date = completed_at[:10] if len(completed_at) >= 10 else ''
                else:
                    completed_date = ''
            else:
                status = '○ Not started'
                completed_date = ''

            table.add_row(
                f"Module {module_num:02d}",
                title,
                status,
                completed_date
            )

        console.print(table)

        # Show summary
        completed_count = len(completed_lessons)
        total_count = len(lessons)
        percentage = (completed_count * 100 // total_count) if total_count > 0 else 0

        console.print()
        if completed_count == total_count:
            console.print(Panel(
                f"[bold green]🎉 Congratulations! You've completed all {total_count} lessons![/bold green]",
                border_style="green"
            ))
        elif completed_count == 0:
            console.print("[yellow]You haven't completed any lessons yet.[/yellow]")
            console.print("Use [bold]lms view <lesson-id>[/bold] to start learning!")
        else:
            console.print(f"Progress: [bold]{completed_count}/{total_count}[/bold] lessons completed ([green]{percentage}%[/green])")
            console.print(f"Keep going! [bold]{total_count - completed_count}[/bold] lesson{'s' if total_count - completed_count != 1 else ''} remaining.")

    except Exception as e:
        click.echo(click.style(f'✗ Failed to fetch progress: {str(e)}', fg='red'), err=True)
        raise click.Abort()


@click.command(name='complete')
@click.argument('lesson_id')
def mark_complete(lesson_id):
    """Mark a lesson as complete

    Args:
        lesson_id: The lesson ID (e.g., module-00)
    """
    config = Config()

    # Check if logged in
    if not config.has_token():
        click.echo(click.style('✗ You are not logged in.', fg='red'), err=True)
        click.echo('Please use "lms login" to authenticate.')
        raise click.Abort()

    token = config.load_token()
    api = APIClient(token=token)

    try:
        # Mark lesson as complete
        api.post('progress/complete/', {
            'lesson_id': lesson_id
        })

        # Success!
        click.echo(click.style(f'✓ Lesson "{lesson_id}" marked as complete!', fg='green'))
        click.echo()
        click.echo('Great job! 🎉')
        click.echo('Use [bold]lms progress[/bold] to see your overall progress.')

    except Exception as e:
        error_msg = str(e)
        if '404' in error_msg or 'not found' in error_msg.lower():
            click.echo(click.style(f'✗ Lesson not found: {lesson_id}', fg='red'), err=True)
            click.echo('Use "lms lessons" to see available lessons.')
        else:
            click.echo(click.style(f'✗ Error: {error_msg}', fg='red'), err=True)
        raise click.Abort()
