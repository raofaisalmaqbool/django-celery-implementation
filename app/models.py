"""
Django Models for Celery Task Management
========================================
Models for tracking task execution, results, and reports.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TaskLog(models.Model):
    """
    Model to track Celery task execution history.
    Useful for monitoring, debugging, and auditing.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('STARTED', 'Started'),
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
        ('RETRY', 'Retry'),
        ('REVOKED', 'Revoked'),
    ]
    
    task_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique Celery task ID"
    )
    task_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Name of the Celery task"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
        help_text="Current status of the task"
    )
    result = models.TextField(
        null=True,
        blank=True,
        help_text="Task result or error message"
    )
    args = models.JSONField(
        null=True,
        blank=True,
        help_text="Task arguments"
    )
    kwargs = models.JSONField(
        null=True,
        blank=True,
        help_text="Task keyword arguments"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the task was created"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the task started execution"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the task completed"
    )
    retry_count = models.IntegerField(
        default=0,
        help_text="Number of retry attempts"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task Log'
        verbose_name_plural = 'Task Logs'
        indexes = [
            models.Index(fields=['task_name', 'status']),
            models.Index(fields=['created_at', 'status']),
        ]
    
    def __str__(self):
        return f"{self.task_name} - {self.status} ({self.task_id[:8]})"
    
    @property
    def duration(self):
        """Calculate task execution duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def mark_started(self):
        """Mark task as started."""
        self.status = 'STARTED'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def mark_success(self, result=None):
        """Mark task as successfully completed."""
        self.status = 'SUCCESS'
        self.completed_at = timezone.now()
        if result:
            self.result = str(result)
        self.save(update_fields=['status', 'completed_at', 'result'])
    
    def mark_failure(self, error):
        """Mark task as failed."""
        self.status = 'FAILURE'
        self.completed_at = timezone.now()
        self.result = str(error)
        self.save(update_fields=['status', 'completed_at', 'result'])


class Report(models.Model):
    """
    Model for storing generated reports.
    """
    
    REPORT_TYPES = [
        ('USER', 'User Report'),
        ('TASK', 'Task Report'),
        ('SALES', 'Sales Report'),
        ('ANALYTICS', 'Analytics Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES,
        db_index=True,
        help_text="Type of report"
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Report title"
    )
    description = models.TextField(
        blank=True,
        help_text="Report description"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
        help_text="Report generation status"
    )
    data = models.JSONField(
        default=dict,
        help_text="Report data in JSON format"
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to generated report file"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        help_text="User who requested the report"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the report was created"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the report was completed"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        indexes = [
            models.Index(fields=['report_type', 'status']),
            models.Index(fields=['created_at', 'status']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.status} ({self.created_at.strftime('%Y-%m-%d')})"
    
    def mark_processing(self):
        """Mark report as processing."""
        self.status = 'PROCESSING'
        self.save(update_fields=['status'])
    
    def mark_completed(self, file_path=None):
        """Mark report as completed."""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if file_path:
            self.file_path = file_path
        self.save(update_fields=['status', 'completed_at', 'file_path'])
    
    def mark_failed(self):
        """Mark report as failed."""
        self.status = 'FAILED'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])


class ScheduledTask(models.Model):
    """
    Model for managing scheduled/periodic tasks.
    """
    
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique name for the scheduled task"
    )
    task_name = models.CharField(
        max_length=255,
        help_text="Celery task name to execute"
    )
    crontab_schedule = models.CharField(
        max_length=100,
        blank=True,
        help_text="Crontab schedule (e.g., '0 0 * * *' for daily at midnight)"
    )
    interval_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Interval in seconds (alternative to crontab)"
    )
    args = models.JSONField(
        default=list,
        blank=True,
        help_text="Task arguments"
    )
    kwargs = models.JSONField(
        default=dict,
        blank=True,
        help_text="Task keyword arguments"
    )
    enabled = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether the task is enabled"
    )
    last_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last execution time"
    )
    next_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Next scheduled execution time"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the schedule was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update time"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Scheduled Task'
        verbose_name_plural = 'Scheduled Tasks'
    
    def __str__(self):
        return f"{self.name} ({'Enabled' if self.enabled else 'Disabled'})"
