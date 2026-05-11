"""
Main CLI entry point for B1 LMS

Uses Click framework for command-line interface
"""
import click

from lms_cli.commands import auth, exam, lessons, progress


@click.group()
def cli():
    """B1 LMS - Learning Management System CLI"""
    pass


# Register auth commands
cli.add_command(auth.signup)
cli.add_command(auth.login)
cli.add_command(auth.logout)
cli.add_command(auth.whoami)

# Register lessons commands
cli.add_command(lessons.lessons_list, name='lessons')
cli.add_command(lessons.view_lesson, name='view')

# Register progress commands
cli.add_command(progress.show_progress, name='progress')
cli.add_command(progress.mark_complete, name='complete')

# Register exam commands
cli.add_command(exam.exams_list, name='exams')
cli.add_command(exam.exam_group)  # exam group (start, status, submit, results)


if __name__ == '__main__':
    cli()
