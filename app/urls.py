"""
URL Configuration for Celery App
=================================
API endpoints for demonstrating various Celery patterns.
"""

from django.urls import path
from app import views

urlpatterns = [
    # API Documentation
    path('api/docs/', views.api_documentation, name='api_docs'),
    
    # Simple Tasks
    path('api/simple-task/', views.simple_task_example, name='simple_task'),
    
    # Advanced Patterns
    path('api/chain-tasks/', views.task_chain_example, name='chain_tasks'),
    path('api/group-tasks/', views.task_group_example, name='group_tasks'),
    path('api/chord-tasks/', views.task_chord_example, name='chord_tasks'),
    
    # Long-Running Tasks
    path('api/long-task/', views.long_task_example, name='long_task'),
    path('api/task-progress/<str:task_id>/', views.task_progress, name='task_progress'),
    
    # Retry Logic
    path('api/retry-task/', views.retry_task_example, name='retry_task'),
    
    # Database Operations
    path('api/create-users/', views.create_users_example, name='create_users'),
    
    # Reports
    path('api/generate-report/', views.generate_report_example, name='generate_report'),
    
    # Task Management
    path('api/task-status/<str:task_id>/', views.task_status, name='task_status'),
    path('api/revoke-task/<str:task_id>/', views.revoke_task, name='revoke_task'),
    
    # Monitoring
    path('api/health/', views.celery_health, name='celery_health'),
    path('api/task-overview/', views.task_overview, name='task_overview'),
]