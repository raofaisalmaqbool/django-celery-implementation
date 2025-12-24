"""
Django Admin Configuration for Celery Models
============================================
Custom admin interfaces for task management and monitoring.
"""

from django.contrib import admin
from django.utils.html import format_html
from app.models import TaskLog, Report, ScheduledTask


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    """Admin interface for TaskLog model."""
    
    list_display = [
        'task_id_short',
        'task_name',
        'status_badge',
        'created_at',
        'duration_display',
        'retry_count'
    ]
    list_filter = ['status', 'task_name', 'created_at']
    search_fields = ['task_id', 'task_name', 'result']
    readonly_fields = [
        'task_id',
        'task_name',
        'args',
        'kwargs',
        'created_at',
        'started_at',
        'completed_at',
        'duration_display'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def task_id_short(self, obj):
        """Display shortened task ID."""
        return obj.task_id[:8] + '...'
    task_id_short.short_description = 'Task ID'
    
    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'SUCCESS': 'green',
            'FAILURE': 'red',
            'PENDING': 'orange',
            'STARTED': 'blue',
            'RETRY': 'purple',
            'REVOKED': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.status
        )
    status_badge.short_description = 'Status'
    
    def duration_display(self, obj):
        """Display task duration in human-readable format."""
        duration = obj.duration
        if duration is not None:
            if duration < 1:
                return f'{duration * 1000:.0f}ms'
            elif duration < 60:
                return f'{duration:.2f}s'
            else:
                minutes = int(duration / 60)
                seconds = duration % 60
                return f'{minutes}m {seconds:.0f}s'
        return 'N/A'
    duration_display.short_description = 'Duration'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface for Report model."""
    
    list_display = [
        'id',
        'report_type',
        'title',
        'status_badge',
        'created_by',
        'created_at',
        'completed_at'
    ]
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['title', 'description', 'report_type']
    readonly_fields = ['created_at', 'completed_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_type', 'title', 'description')
        }),
        ('Status', {
            'fields': ('status', 'file_path')
        }),
        ('Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'completed_at')
        }),
    )
    
    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'COMPLETED': 'green',
            'FAILED': 'red',
            'PENDING': 'orange',
            'PROCESSING': 'blue'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.status
        )
    status_badge.short_description = 'Status'


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    """Admin interface for ScheduledTask model."""
    
    list_display = [
        'name',
        'task_name',
        'enabled_badge',
        'schedule_display',
        'last_run',
        'next_run'
    ]
    list_filter = ['enabled', 'created_at']
    search_fields = ['name', 'task_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('name', 'task_name', 'enabled')
        }),
        ('Schedule', {
            'fields': ('crontab_schedule', 'interval_seconds')
        }),
        ('Arguments', {
            'fields': ('args', 'kwargs'),
            'classes': ('collapse',)
        }),
        ('Execution Info', {
            'fields': ('last_run', 'next_run', 'created_at', 'updated_at')
        }),
    )
    
    def enabled_badge(self, obj):
        """Display enabled status with badge."""
        if obj.enabled:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; '
                'border-radius: 3px;">Enabled</span>'
            )
        else:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 10px; '
                'border-radius: 3px;">Disabled</span>'
            )
    enabled_badge.short_description = 'Status'
    
    def schedule_display(self, obj):
        """Display schedule information."""
        if obj.crontab_schedule:
            return f'Crontab: {obj.crontab_schedule}'
        elif obj.interval_seconds:
            if obj.interval_seconds < 60:
                return f'Every {obj.interval_seconds}s'
            elif obj.interval_seconds < 3600:
                return f'Every {obj.interval_seconds / 60:.0f}m'
            else:
                return f'Every {obj.interval_seconds / 3600:.1f}h'
        return 'No schedule'
    schedule_display.short_description = 'Schedule'
