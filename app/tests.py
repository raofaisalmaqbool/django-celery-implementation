"""
Test Suite for Celery Tasks and Views
=====================================
Comprehensive tests for Celery task execution and API endpoints.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from celery.result import AsyncResult
import json
import time

from app.tasks import (
    add, multiply, create_users_batch, long_running_task,
    task_with_retry, generate_report
)
from app.models import TaskLog, Report, ScheduledTask


class CeleryTaskTests(TestCase):
    """Test cases for Celery tasks."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = Client()
    
    def test_simple_add_task(self):
        """Test simple addition task."""
        result = add.apply_async(args=[5, 3])
        # Get result with timeout
        task_result = result.get(timeout=10)
        self.assertEqual(task_result, 8)
    
    def test_multiply_task(self):
        """Test multiplication task."""
        result = multiply.apply_async(args=[4, 5])
        task_result = result.get(timeout=10)
        self.assertEqual(task_result, 20)
    
    def test_create_users_batch(self):
        """Test batch user creation."""
        initial_count = User.objects.count()
        result = create_users_batch.apply_async(args=[5, 'testuser'])
        task_result = result.get(timeout=30)
        
        self.assertEqual(task_result['status'], 'success')
        self.assertEqual(task_result['count'], 5)
        self.assertEqual(User.objects.count(), initial_count + 5)
    
    def test_task_log_creation(self):
        """Test that task logs are created."""
        result = add.apply_async(args=[10, 20])
        result.get(timeout=10)
        
        # Check if task log was created
        task_log = TaskLog.objects.filter(task_id=result.id).first()
        self.assertIsNotNone(task_log)
        self.assertEqual(task_log.status, 'SUCCESS')


class APIEndpointTests(TestCase):
    """Test cases for API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_api_documentation(self):
        """Test API documentation endpoint."""
        response = self.client.get('/api/docs/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('endpoints', data)
        self.assertIn('project', data)
    
    def test_simple_task_endpoint(self):
        """Test simple task API endpoint."""
        response = self.client.post(
            '/api/simple-task/',
            data=json.dumps({'x': 10, 'y': 5}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertIn('task_id', data)
    
    def test_task_status_endpoint(self):
        """Test task status checking endpoint."""
        # Create a task
        result = add.apply_async(args=[3, 7])
        task_id = result.id
        
        # Check status
        response = self.client.get(f'/api/task-status/{task_id}/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertIn('task_id', data)
    
    def test_create_users_endpoint(self):
        """Test user creation endpoint."""
        response = self.client.post(
            '/api/create-users/',
            data=json.dumps({'count': 3, 'prefix': 'apitest'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
    
    def test_health_check_endpoint(self):
        """Test Celery health check endpoint."""
        response = self.client.get('/api/health/')
        # May return 503 if Celery worker is not running in test environment
        self.assertIn(response.status_code, [200, 503])
    
    def test_task_overview_endpoint(self):
        """Test task overview endpoint."""
        # Create some task logs first
        TaskLog.objects.create(
            task_id='test-task-1',
            task_name='test.task',
            status='SUCCESS'
        )
        
        response = self.client.get('/api/task-overview/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('total_tasks', data)
        self.assertIn('status_breakdown', data)


class ModelTests(TestCase):
    """Test cases for Django models."""
    
    def test_task_log_creation(self):
        """Test TaskLog model creation."""
        task_log = TaskLog.objects.create(
            task_id='test-123',
            task_name='test.task',
            status='PENDING'
        )
        
        self.assertEqual(str(task_log), 'test.task - PENDING (test-123)')
        self.assertEqual(task_log.status, 'PENDING')
    
    def test_task_log_mark_success(self):
        """Test marking task log as successful."""
        task_log = TaskLog.objects.create(
            task_id='test-456',
            task_name='test.task',
            status='STARTED'
        )
        
        task_log.mark_success(result={'data': 'test'})
        task_log.refresh_from_db()
        
        self.assertEqual(task_log.status, 'SUCCESS')
        self.assertIsNotNone(task_log.completed_at)
    
    def test_task_log_mark_failure(self):
        """Test marking task log as failed."""
        task_log = TaskLog.objects.create(
            task_id='test-789',
            task_name='test.task',
            status='STARTED'
        )
        
        task_log.mark_failure(error='Test error')
        task_log.refresh_from_db()
        
        self.assertEqual(task_log.status, 'FAILURE')
        self.assertEqual(task_log.result, 'Test error')
    
    def test_report_creation(self):
        """Test Report model creation."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        report = Report.objects.create(
            report_type='USER',
            title='Test Report',
            created_by=user
        )
        
        self.assertEqual(report.status, 'PENDING')
        self.assertIsNotNone(report.created_at)
    
    def test_scheduled_task_creation(self):
        """Test ScheduledTask model creation."""
        scheduled_task = ScheduledTask.objects.create(
            name='test-scheduled-task',
            task_name='app.tasks.health_check',
            interval_seconds=300,
            enabled=True
        )
        
        self.assertTrue(scheduled_task.enabled)
        self.assertEqual(str(scheduled_task), 'test-scheduled-task (Enabled)')


class CeleryPatternTests(TestCase):
    """Test cases for different Celery patterns."""
    
    def test_chain_pattern_endpoint(self):
        """Test task chaining pattern."""
        response = self.client.post(
            '/api/chain-tasks/',
            data=json.dumps({'initial_value': 5}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['pattern'], 'Chain')
    
    def test_group_pattern_endpoint(self):
        """Test task grouping pattern."""
        response = self.client.post(
            '/api/group-tasks/',
            data=json.dumps({'count': 3}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['pattern'], 'Group')
    
    def test_chord_pattern_endpoint(self):
        """Test chord pattern."""
        response = self.client.post(
            '/api/chord-tasks/',
            data=json.dumps({'chunks': 2, 'items_per_chunk': 5}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['pattern'], 'Chord')
