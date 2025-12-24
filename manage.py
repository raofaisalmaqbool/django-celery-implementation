#!/usr/bin/env python
"""
Django Management Script
========================

Django's command-line utility for administrative tasks.

This script is the entry point for all Django management commands:
    - python manage.py runserver      : Start development server
    - python manage.py migrate         : Run database migrations
    - python manage.py createsuperuser : Create admin user
    - python manage.py test            : Run tests
    - python manage.py shell           : Open Django shell
    
For a complete list of commands:
    python manage.py help
"""

import os
import sys


def main():
    """
    Run administrative tasks.
    
    This function sets up Django's settings module and executes
    the command-line utility for Django management commands.
    """
    # Set the Django settings module
    # This can be overridden by setting DJANGO_SETTINGS_MODULE environment variable
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'celerytest.settings')
    
    try:
        # Import Django's command execution function
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Provide helpful error message if Django is not installed
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Execute the command provided via command line arguments
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
