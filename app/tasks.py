"""
Celery Tasks Module
===================
This module demonstrates various Celery task patterns and best practices:
- Simple tasks
- Task chaining
- Task groups
- Chords
- Error handling and retries
- Periodic tasks
- Callbacks
- Canvas primitives
"""

import logging
import random
import time
from typing import List, Dict, Any

from celery import shared_task, group, chain, chord
from celery.exceptions import SoftTimeLimitExceeded
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from app.models import TaskLog, Report

logger = logging.getLogger(__name__)


# ============================================================================
# SIMPLE TASKS
# ============================================================================

@shared_task(bind=True, name='app.tasks.simple_addition')
def add(self, x: int, y: int) -> int:
    """
    Simple task demonstrating basic Celery functionality.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        Sum of x and y
    """
    logger.info(f"Adding {x} + {y}")
    return x + y


@shared_task(bind=True, name='app.tasks.multiply')
def multiply(self, x: int, y: int) -> int:
    """
    Simple multiplication task.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        Product of x and y
    """
    logger.info(f"Multiplying {x} * {y}")
    return x * y


# ============================================================================
# LONG-RUNNING TASKS WITH PROGRESS TRACKING
# ============================================================================

@shared_task(bind=True, name='app.tasks.long_running_task')
def long_running_task(self, total_steps: int = 10) -> Dict[str, Any]:
    """
    Demonstrates a long-running task with progress updates.
    
    Args:
        total_steps: Number of steps to simulate
        
    Returns:
        Dictionary with completion status
    """
    for i in range(total_steps):
        time.sleep(1)
        # Update task state to track progress
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': total_steps,
                'percent': int((i + 1) / total_steps * 100),
                'status': f'Processing step {i + 1} of {total_steps}'
            }
        )
    
    return {
        'status': 'completed',
        'total_steps': total_steps,
        'message': 'Task completed successfully'
    }


# ============================================================================
# TASKS WITH RETRY LOGIC
# ============================================================================

@shared_task(
    bind=True,
    name='app.tasks.task_with_retry',
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 5},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def task_with_retry(self, fail_probability: float = 0.5) -> Dict[str, Any]:
    """
    Demonstrates automatic retry on failure with exponential backoff.
    
    Args:
        fail_probability: Probability of task failure (0-1)
        
    Returns:
        Success message
        
    Raises:
        Exception: Random failure for demonstration
    """
    if random.random() < fail_probability:
        logger.warning(f"Task {self.request.id} failed, will retry...")
        raise Exception("Random failure occurred")
    
    logger.info(f"Task {self.request.id} completed successfully")
    return {
        'status': 'success',
        'task_id': self.request.id,
        'attempts': self.request.retries + 1
    }


# ============================================================================
# TIME-LIMITED TASKS
# ============================================================================

@shared_task(
    bind=True,
    name='app.tasks.time_limited_task',
    time_limit=30,  # Hard time limit
    soft_time_limit=25  # Soft time limit
)
def time_limited_task(self, duration: int = 20) -> Dict[str, Any]:
    """
    Task with time limits to prevent hanging operations.
    
    Args:
        duration: How long the task should run
        
    Returns:
        Completion status
    """
    try:
        logger.info(f"Starting time-limited task for {duration} seconds")
        time.sleep(duration)
        return {'status': 'completed', 'duration': duration}
    except SoftTimeLimitExceeded:
        logger.warning("Soft time limit exceeded, cleaning up...")
        return {'status': 'time_limit_exceeded', 'duration': duration}


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

@shared_task(bind=True, name='app.tasks.create_users_batch')
def create_users_batch(self, count: int = 10, prefix: str = 'user') -> Dict[str, Any]:
    """
    Create multiple users in batch.
    
    Args:
        count: Number of users to create
        prefix: Username prefix
        
    Returns:
        Dictionary with created user count
    """
    logger.info(f"Creating {count} users with prefix '{prefix}'")
    created_users = []
    
    for i in range(count):
        username = f"{prefix}_{int(time.time())}_{i}"
        email = f"{username}@example.com"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password='defaultpassword123'
        )
        created_users.append(user.id)
    
    # Log the task execution
    TaskLog.objects.create(
        task_id=self.request.id,
        task_name=self.name,
        status='SUCCESS',
        result=f'Created {count} users'
    )
    
    return {
        'status': 'success',
        'count': count,
        'user_ids': created_users
    }


@shared_task(bind=True, name='app.tasks.cleanup_old_users')
def cleanup_old_users(self, days: int = 30) -> Dict[str, int]:
    """
    Clean up inactive users older than specified days.
    
    Args:
        days: Age threshold in days
        
    Returns:
        Count of deleted users
    """
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    old_users = User.objects.filter(
        last_login__lt=cutoff_date,
        is_active=False
    )
    
    deleted_count = old_users.count()
    old_users.delete()
    
    logger.info(f"Cleaned up {deleted_count} old users")
    
    return {
        'status': 'success',
        'deleted_count': deleted_count,
        'cutoff_days': days
    }


# ============================================================================
# EMAIL TASKS
# ============================================================================

@shared_task(
    bind=True,
    name='app.tasks.send_email_task',
    max_retries=3,
    default_retry_delay=60
)
def send_email_task(
    self,
    subject: str,
    message: str,
    recipient_list: List[str]
) -> Dict[str, Any]:
    """
    Send email asynchronously with retry logic.
    
    Args:
        subject: Email subject
        message: Email body
        recipient_list: List of recipient email addresses
        
    Returns:
        Success status
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f"Email sent to {len(recipient_list)} recipients")
        return {
            'status': 'success',
            'recipients': len(recipient_list)
        }
    except Exception as exc:
        logger.error(f"Failed to send email: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, name='app.tasks.send_bulk_emails')
def send_bulk_emails(self, user_ids: List[int], subject: str, message: str) -> Dict[str, int]:
    """
    Send emails to multiple users using task grouping.
    
    Args:
        user_ids: List of user IDs
        subject: Email subject
        message: Email message
        
    Returns:
        Count of emails sent
    """
    users = User.objects.filter(id__in=user_ids, is_active=True)
    email_tasks = []
    
    for user in users:
        email_tasks.append(
            send_email_task.s(
                subject=subject,
                message=message,
                recipient_list=[user.email]
            )
        )
    
    # Execute all email tasks in parallel
    job = group(email_tasks)
    result = job.apply_async()
    
    return {
        'status': 'queued',
        'email_count': len(email_tasks),
        'group_id': result.id
    }


# ============================================================================
# DATA PROCESSING TASKS
# ============================================================================

@shared_task(bind=True, name='app.tasks.process_data_chunk')
def process_data_chunk(self, chunk_id: int, data: List[Any]) -> Dict[str, Any]:
    """
    Process a chunk of data.
    
    Args:
        chunk_id: Identifier for this chunk
        data: List of data items to process
        
    Returns:
        Processing results
    """
    logger.info(f"Processing chunk {chunk_id} with {len(data)} items")
    
    processed_items = []
    for item in data:
        # Simulate processing
        time.sleep(0.1)
        processed_items.append({'original': item, 'processed': item * 2})
    
    return {
        'chunk_id': chunk_id,
        'items_processed': len(processed_items),
        'results': processed_items
    }


@shared_task(bind=True, name='app.tasks.aggregate_results')
def aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate results from multiple processing tasks.
    Used as callback in chord pattern.
    
    Args:
        results: List of results from previous tasks
        
    Returns:
        Aggregated data
    """
    logger.info(f"Aggregating {len(results)} results")
    
    total_items = sum(r['items_processed'] for r in results)
    all_results = []
    
    for result in results:
        all_results.extend(result['results'])
    
    return {
        'status': 'aggregated',
        'total_chunks': len(results),
        'total_items': total_items,
        'aggregated_data': all_results
    }


# ============================================================================
# REPORT GENERATION TASKS
# ============================================================================

@shared_task(bind=True, name='app.tasks.generate_report')
def generate_report(self, report_type: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate various types of reports.
    
    Args:
        report_type: Type of report to generate
        filters: Optional filters for report data
        
    Returns:
        Report generation status
    """
    logger.info(f"Generating {report_type} report")
    
    # Simulate report generation
    time.sleep(5)
    
    report = Report.objects.create(
        report_type=report_type,
        status='COMPLETED',
        data={'filters': filters or {}, 'generated_at': str(timezone.now())}
    )
    
    return {
        'status': 'success',
        'report_id': report.id,
        'report_type': report_type
    }


# ============================================================================
# CALLBACK TASKS
# ============================================================================

@shared_task(bind=True, name='app.tasks.task_success_callback')
def task_success_callback(self, result: Any) -> None:
    """
    Callback executed on task success.
    
    Args:
        result: Result from the parent task
    """
    logger.info(f"Task completed successfully with result: {result}")
    
    TaskLog.objects.create(
        task_id=self.request.id,
        task_name='callback',
        status='SUCCESS',
        result=str(result)
    )


@shared_task(bind=True, name='app.tasks.task_error_callback')
def task_error_callback(self, task_id: str, error: str) -> None:
    """
    Callback executed on task failure.
    
    Args:
        task_id: ID of the failed task
        error: Error message
    """
    logger.error(f"Task {task_id} failed with error: {error}")
    
    TaskLog.objects.create(
        task_id=task_id,
        task_name='error_callback',
        status='FAILURE',
        result=error
    )


# ============================================================================
# WORKFLOW TASKS (Canvas Primitives)
# ============================================================================

@shared_task(bind=True, name='app.tasks.workflow_step_1')
def workflow_step_1(self, value: int) -> int:
    """First step in a workflow chain."""
    logger.info(f"Workflow Step 1: Processing value {value}")
    time.sleep(2)
    return value * 2


@shared_task(bind=True, name='app.tasks.workflow_step_2')
def workflow_step_2(self, value: int) -> int:
    """Second step in a workflow chain."""
    logger.info(f"Workflow Step 2: Processing value {value}")
    time.sleep(2)
    return value + 10


@shared_task(bind=True, name='app.tasks.workflow_step_3')
def workflow_step_3(self, value: int) -> Dict[str, int]:
    """Final step in a workflow chain."""
    logger.info(f"Workflow Step 3: Finalizing value {value}")
    time.sleep(2)
    return {
        'final_result': value,
        'status': 'completed'
    }


# ============================================================================
# MONITORING AND HEALTH CHECK TASKS
# ============================================================================

@shared_task(bind=True, name='app.tasks.health_check')
def health_check(self) -> Dict[str, Any]:
    """
    Perform health check of the Celery system.
    
    Returns:
        Health status information
    """
    from celery import current_app
    
    inspect = current_app.control.inspect()
    
    # Get active tasks
    active_tasks = inspect.active()
    scheduled_tasks = inspect.scheduled()
    
    return {
        'status': 'healthy',
        'timestamp': str(timezone.now()),
        'active_tasks': len(active_tasks) if active_tasks else 0,
        'scheduled_tasks': len(scheduled_tasks) if scheduled_tasks else 0
    }


@shared_task(bind=True, name='app.tasks.cleanup_task_logs')
def cleanup_task_logs(self, days: int = 7) -> Dict[str, int]:
    """
    Clean up old task logs.
    
    Args:
        days: Age threshold in days
        
    Returns:
        Count of deleted logs
    """
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    old_logs = TaskLog.objects.filter(created_at__lt=cutoff_date)
    
    deleted_count = old_logs.count()
    old_logs.delete()
    
    logger.info(f"Cleaned up {deleted_count} old task logs")
    
    return {
        'status': 'success',
        'deleted_count': deleted_count
    }
