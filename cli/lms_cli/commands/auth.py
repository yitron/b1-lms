"""
Authentication commands for B1 LMS CLI

Commands:
- signup: Create new account
- login: Authenticate and save token
- logout: Clear authentication token
- whoami: Show current authentication status
"""
import click

from lms_cli.api_client import APIClient
from lms_cli.config import Config


@click.command()
@click.option('--username', prompt='Username', help='Your username')
@click.option('--password', prompt='Password', hide_input=True, help='Your password')
@click.option('--email', prompt='Email (optional)', default='', help='Your email address')
def signup(username, password, email):
    """Create a new account"""
    config = Config()
    api = APIClient()

    try:
        # Call signup API
        response = api.post('auth/signup/', {
            'username': username,
            'password': password,
            'email': email
        })

        # Extract token and user info
        token = response['token']
        user = response['user']

        # Save token
        config.save_token(token)

        # Success message
        click.echo(click.style('✓ Account created successfully!', fg='green'))
        click.echo(f"Username: {user['username']}")
        if user.get('email'):
            click.echo(f"Email: {user['email']}")
        click.echo('\nYou are now logged in.')

    except Exception as e:
        click.echo(click.style(f'✗ Signup failed: {str(e)}', fg='red'), err=True)
        raise click.Abort()


@click.command()
@click.option('--username', prompt='Username', help='Your username')
@click.option('--password', prompt='Password', hide_input=True, help='Your password')
def login(username, password):
    """Login to your account"""
    config = Config()

    # Check if already logged in
    if config.has_token():
        click.echo(click.style('⚠ You are already logged in.', fg='yellow'))
        if not click.confirm('Do you want to login again?'):
            return

    api = APIClient()

    try:
        # Call login API
        response = api.post('auth/login/', {
            'username': username,
            'password': password
        })

        # Extract token
        token = response['token']
        user = response['user']

        # Save token
        config.save_token(token)

        # Success message
        click.echo(click.style('✓ Login successful!', fg='green'))
        click.echo(f"Logged in as: {user['username']}")

    except Exception as e:
        click.echo(click.style(f'✗ Login failed: {str(e)}', fg='red'), err=True)
        raise click.Abort()


@click.command()
def logout():
    """Logout from your account"""
    config = Config()

    # Check if logged in
    if not config.has_token():
        click.echo(click.style('✗ You are not logged in.', fg='red'), err=True)
        raise click.Abort()

    # Get token
    token = config.load_token()

    # Try to call logout API (best effort)
    try:
        api = APIClient(token=token)
        api.post('auth/logout/', {})
    except Exception as e:
        # Even if API fails, we'll delete local token
        click.echo(click.style(f'⚠ API logout failed: {str(e)}', fg='yellow'))

    # Delete local token
    config.delete_token()

    # Success message
    click.echo(click.style('✓ Logged out successfully.', fg='green'))
    click.echo('Local authentication token removed.')


@click.command()
def whoami():
    """Show current authentication status"""
    config = Config()

    if config.has_token():
        token = config.load_token()
        # Show partial token for security (first 6 chars)
        partial_token = token[:6] + '...' if len(token) > 6 else token

        click.echo(click.style('✓ You are logged in', fg='green'))
        click.echo(f'Token: {partial_token}')
    else:
        click.echo(click.style('✗ You are not logged in', fg='yellow'))
        click.echo('Use "lms login" or "lms signup" to authenticate.')
