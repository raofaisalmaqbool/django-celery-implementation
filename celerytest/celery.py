"""
Celery Configuration Module
============================
Celery application instance for distributed task queue.

This module sets up Celery with Django integration, enabling:
- Asynchronous task execution
- Periodic task scheduling
- Task monitoring and management
- Result backend configuration
"""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

# Set default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'celerytest.settings')

# Create Celery application instance
app = Celery('celerytest')

# Load configuration from Django settings
# - namespace='CELERY' means all Celery-related settings should have a `CELERY_` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from all installed apps
# This will look for tasks.py in each installed Django app
app.autodiscover_tasks()


# ============================================================================
# CELERY SIGNAL HANDLERS
# ============================================================================

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """
    Signal handler called before a task is executed.
    Useful for logging, monitoring, or custom pre-execution logic.
    
    Args:
        sender: Task class
        task_id: Unique task ID
        task: Task object
        args: Task positional arguments
        kwargs: Task keyword arguments
    """
    from app.models import TaskLog
    
    # Create or update task log
    TaskLog.objects.update_or_create(
        task_id=task_id,
        defaults={
            'task_name': task.name,
            'status': 'STARTED',
            'args': args,
            'kwargs': kwargs,
        }
    )


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, retval=None, state=None, **extra):
    """
    Signal handler called after a task completes successfully.
    
    Args:
        sender: Task class
        task_id: Unique task ID
        task: Task object
        retval: Task return value
        state: Task state
    """
    from app.models import TaskLog
    
    try:
        task_log = TaskLog.objects.get(task_id=task_id)
        task_log.mark_success(result=retval)
    except TaskLog.DoesNotExist:
        # Create log if it doesn't exist
        TaskLog.objects.create(
            task_id=task_id,
            task_name=task.name,
            status='SUCCESS',
            result=str(retval) if retval else None
        )


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, **extra):
    """
    Signal handler called when a task fails.
    
    Args:
        sender: Task class
        task_id: Unique task ID
        exception: Exception that caused the failure
        traceback: Exception traceback
    """
    from app.models import TaskLog
    
    try:
        task_log = TaskLog.objects.get(task_id=task_id)
        task_log.mark_failure(error=str(exception))
        task_log.retry_count += 1
        task_log.save()
    except TaskLog.DoesNotExist:
        # Create log if it doesn't exist
        TaskLog.objects.create(
            task_id=task_id,
            task_name=sender.name if sender else 'unknown',
            status='FAILURE',
            result=str(exception),
            retry_count=1
        )


@app.task(bind=True)
def debug_task(self):
    """
    Debug task for testing Celery configuration.
    Use: celery -A celerytest call celerytest.celery.debug_task
    """
    print(f'Request: {self.request!r}')