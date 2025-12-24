"""
Django Celery Test Project Initialization
=========================================

This module initializes the Celery app when Django starts.

The Celery app instance is imported here to ensure it's loaded when Django
starts, making it possible to use the @shared_task decorator in other parts
of the application. This follows the recommended pattern from the Celery
documentation for Django integration.

Without this import, Celery would not be properly initialized and tasks
decorated with @shared_task would fail to execute.
"""

from __future__ import absolute_import, unicode_literals

# Import the Celery app instance from celery.py
# This ensures Celery is loaded when Django starts so that shared_task will use this app
from .celery import app as celery_app

# Define what should be available when this module is imported with *
__all__ = ('celery_app',)
