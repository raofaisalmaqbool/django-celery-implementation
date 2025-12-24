"""
Django Views for Celery Task Demonstration
==========================================
This module provides API endpoints to demonstrate various Celery patterns.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from celery import chain, group, chord
from celery.result import AsyncResult
import json

from app.tasks import (
    # Simple tasks
    add, multiply,
    # Long-running tasks
    long_running_task,
    # Retry tasks
    task_with_retry,
    # Time-limited tasks
    time_limited_task,
    # Database tasks
    create_users_batch, cleanup_old_users,
    # Email tasks
    send_email_task, send_bulk_emails,
    # Data processing
    process_data_chunk, aggregate_results,
    # Report generation
    generate_report,
    # Workflow tasks
    workflow_step_1, workflow_step_2, workflow_step_3,
    # Monitoring
    health_check, cleanup_task_logs
)


# ============================================================================
# SIMPLE TASK EXECUTION
# ============================================================================

@csrf_exempt
@require_http_methods(["POST", "GET"])
def simple_task_example(request):
    """
    Execute a simple Celery task.
    
    Example:
        POST /api/simple-task/
        {
            "x": 10,
            "y": 20
        }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            x = data.get('x', 5)
            y = data.get('y', 3)
            
            # Execute task asynchronously
            result = add.apply_async(args=[x, y])
            
            return JsonResponse({
                'status': 'success',
                'task_id': result.id,
                'message': f'Task queued to add {x} + {y}',
                'check_status_url': f'/api/task-status/{result.id}/'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'info': 'POST to this endpoint with x and y values to add them asynchronously'
    })


# ============================================================================
# TASK CHAINING PATTERN
# ============================================================================

@csrf_exempt
@require_http_methods(["POST", "GET"])
def task_chain_example(request):
    """
    Demonstrate task chaining - execute tasks sequentially.
    Each task receives the result of the previous task.
    
    Example:
        POST /api/chain-tasks/
        {
            "initial_value": 5
        }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            initial_value = data.get('initial_value', 5)
            
            # Create a chain: workflow_step_1 -> workflow_step_2 -> workflow_step_3
            task_chain = chain(
                workflow_step_1.s(initial_value),
                workflow_step_2.s(),
                workflow_step_3.s()
            )
            
            result = task_chain.apply_async()
            
            return JsonResponse({
                'status': 'success',
                'task_id': result.id,
                'message': f'Task chain started with initial value {initial_value}',
                'pattern': 'Chain',
                'description': 'Tasks will execute sequentially, each receiving the previous result'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'info': 'POST to execute a chain of tasks sequentially'
    })


# ============================================================================
# TASK GROUP PATTERN
# ============================================================================

@csrf_exempt
@require_http_methods(["POST", "GET"])
def task_group_example(request):
    """
    Demonstrate task grouping - execute multiple tasks in parallel.
    
    Example:
        POST /api/group-tasks/
        {
            "count": 5
        }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            count = data.get('count', 5)
            
            # Create a group of tasks to run in parallel
            task_group = group([
                add.s(i, i * 2) for i in range(count)
            ])
            
            result = task_group.apply_async()
            
            return JsonResponse({
                'status': 'success',
                'group_id': result.id,
                'message': f'Created group of {count} tasks running in parallel',
                'pattern': 'Group',
                'description': 'All tasks execute simultaneously'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'info': 'POST to execute multiple tasks in parallel'
    })


# ============================================================================
# CHORD PATTERN (GROUP + CALLBACK)
# ============================================================================

@csrf_exempt
@require_http_methods(["POST", "GET"])
def task_chord_example(request):
    """
    Demonstrate chord pattern - execute tasks in parallel then aggregate results.
    
    Example:
        POST /api/chord-tasks/
        {
            "chunks": 3,
            "items_per_chunk": 10
        }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            chunks = data.get('chunks', 3)
            items_per_chunk = data.get('items_per_chunk', 10)
            
            # Create data chunks
            chunk_data = [
                list(range(i * items_per_chunk, (i + 1) * items_per_chunk))
                for i in range(chunks)
            ]
            
            # Create a chord: process chunks in parallel, then aggregate
            task_chord = chord([
                process_data_chunk.s(i, chunk)
                for i, chunk in enumerate(chunk_data)
            ])(aggregate_results.s())
            
            return JsonResponse({
                'status': 'success',
                'task_id': task_chord.id,
                'message': f'Created chord with {chunks} parallel tasks + aggregation',
                'pattern': 'Chord',
                'description': 'Tasks run in parallel, results are aggregated by callback'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'info': 'POST to execute chord pattern (parallel tasks + aggregation)'
    })


# ============================================================================
# LONG-RUNNING TASK WITH PROGRESS
# ============================================================================

@csrf_exempt
@require_http_methods(["POST", "GET"])
def long_task_example(request):
    """
    Execute a long-running task with progress tracking.
    
    Example:
        POST /api/long-task/
        {
            "steps": 10
        }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            steps = data.get('steps', 10)
            
            result = long_running_task.apply_async(args=[steps])
            
            return JsonResponse({
                'status': 'success',
                'task_id': result.id,
                'message': f'Long-running task started with {steps} steps',
                'progress_url': f'/api/task-progress/{result.id}/'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'info': 'POST to start a long-running task with progress tracking'
    })


# ============================================================================
# TASK WITH RETRY LOGIC
# ============================================================================

@csrf_exempt
@require_http_methods(["POST", "GET"])
def retry_task_example(request):
    """
    Execute a task that may fail and retry automatically.
    
    Example:
        POST /api/retry-task/
        {
            "fail_probability": 0.7
        }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            fail_probability = data.get('fail_probability', 0.5)
            
            result = task_with_retry.apply_async(args=[fail_probability])
            
            return JsonResponse({
                'status': 'success',
                'task_id': result.id,
                'message': 'Task queued with automatic retry on failure',
                'fail_probability': fail_probability,
                'max_retries': 3
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'info': 'POST to execute a task with retry logic'
    })


# ============================================================================
# BULK USER CREATION
# ============================================================================

@csrf_exempt
@require_http_methods(["POST", "GET"])
def create_users_example(request):
    """
    Create multiple users asynchronously.
    
    Example:
        POST /api/create-users/
        {
            "count": 10,
            "prefix": "testuser"
        }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            count = data.get('count', 10)
            prefix = data.get('prefix', 'user')
            
            result = create_users_batch.apply_async(args=[count, prefix])
            
            return JsonResponse({
                'status': 'success',
                'task_id': result.id,
                'message': f'User creation task queued for {count} users'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'info': 'POST to create multiple users asynchronously'
    })


# ============================================================================
# REPORT GENERATION
# ============================================================================

@csrf_exempt
@require_http_methods(["POST", "GET"])
def generate_report_example(request):
    """
    Generate a report asynchronously.
    
    Example:
        POST /api/generate-report/
        {
            "report_type": "USER",
            "filters": {"active": true}
        }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else {}
            report_type = data.get('report_type', 'USER')
            filters = data.get('filters', {})
            
            result = generate_report.apply_async(args=[report_type, filters])
            
            return JsonResponse({
                'status': 'success',
                'task_id': result.id,
                'message': f'Report generation started for type: {report_type}'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'info': 'POST to generate a report asynchronously'
    })


# ============================================================================
# TASK STATUS AND MONITORING
# ============================================================================

@require_http_methods(["GET"])
def task_status(request, task_id):
    """
    Check the status of a Celery task.
    
    Args:
        task_id: Celery task ID
    """
    try:
        result = AsyncResult(task_id)
        
        response_data = {
            'task_id': task_id,
            'status': result.status,
            'ready': result.ready(),
            'successful': result.successful() if result.ready() else None,
        }
        
        if result.ready():
            if result.successful():
                response_data['result'] = result.result
            else:
                response_data['error'] = str(result.info)
        else:
            # For tasks with progress tracking
            if result.state == 'PROGRESS':
                response_data['progress'] = result.info
        
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@require_http_methods(["GET"])
def task_progress(request, task_id):
    """
    Get detailed progress information for a task.
    
    Args:
        task_id: Celery task ID
    """
    try:
        result = AsyncResult(task_id)
        
        if result.state == 'PROGRESS':
            return JsonResponse({
                'task_id': task_id,
                'status': 'PROGRESS',
                'info': result.info
            })
        elif result.ready():
            return JsonResponse({
                'task_id': task_id,
                'status': 'COMPLETED',
                'result': result.result if result.successful() else None,
                'error': str(result.info) if not result.successful() else None
            })
        else:
            return JsonResponse({
                'task_id': task_id,
                'status': result.state
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST", "GET"])
def revoke_task(request, task_id):
    """
    Revoke/cancel a running task.
    
    Args:
        task_id: Celery task ID
    """
    try:
        from celery import current_app
        
        terminate = request.GET.get('terminate', 'false').lower() == 'true'
        current_app.control.revoke(task_id, terminate=terminate)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Task {task_id} revoked',
            'terminated': terminate
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


# ============================================================================
# HEALTH CHECK AND MONITORING
# ============================================================================

@require_http_methods(["GET"])
def celery_health(request):
    """
    Check Celery system health.
    """
    try:
        result = health_check.apply_async()
        health_info = result.get(timeout=5)
        
        return JsonResponse({
            'status': 'healthy',
            'celery_info': health_info
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)


@require_http_methods(["GET"])
def task_overview(request):
    """
    Get an overview of task statistics.
    """
    from app.models import TaskLog
    from django.db.models import Count
    
    try:
        stats = TaskLog.objects.values('status').annotate(count=Count('id'))
        
        total_tasks = TaskLog.objects.count()
        recent_tasks = TaskLog.objects.order_by('-created_at')[:10]
        
        return JsonResponse({
            'total_tasks': total_tasks,
            'status_breakdown': list(stats),
            'recent_tasks': [
                {
                    'task_id': task.task_id,
                    'task_name': task.task_name,
                    'status': task.status,
                    'created_at': task.created_at.isoformat()
                }
                for task in recent_tasks
            ]
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


# ============================================================================
# API DOCUMENTATION
# ============================================================================

@require_http_methods(["GET"])
def api_documentation(request):
    """
    Provide API documentation for all available endpoints.
    """
    endpoints = {
        'Simple Tasks': {
            'POST /api/simple-task/': 'Execute a simple addition task',
        },
        'Advanced Patterns': {
            'POST /api/chain-tasks/': 'Execute tasks sequentially (Chain pattern)',
            'POST /api/group-tasks/': 'Execute tasks in parallel (Group pattern)',
            'POST /api/chord-tasks/': 'Execute tasks in parallel with aggregation (Chord pattern)',
        },
        'Long-Running Tasks': {
            'POST /api/long-task/': 'Execute a long-running task with progress tracking',
            'GET /api/task-progress/<task_id>/': 'Get progress of a running task',
        },
        'Retry Logic': {
            'POST /api/retry-task/': 'Execute a task with automatic retry on failure',
        },
        'Database Operations': {
            'POST /api/create-users/': 'Create multiple users asynchronously',
        },
        'Reports': {
            'POST /api/generate-report/': 'Generate reports asynchronously',
        },
        'Task Management': {
            'GET /api/task-status/<task_id>/': 'Check task status',
            'POST /api/revoke-task/<task_id>/': 'Cancel a running task',
        },
        'Monitoring': {
            'GET /api/health/': 'Check Celery system health',
            'GET /api/task-overview/': 'Get task statistics and overview',
        },
        'Documentation': {
            'GET /api/docs/': 'This documentation page',
        }
    }
    
    return JsonResponse({
        'project': 'Django Celery Implementation',
        'description': 'Comprehensive demonstration of various Celery patterns',
        'endpoints': endpoints,
        'patterns_demonstrated': [
            'Simple Tasks',
            'Task Chaining',
            'Task Groups (Parallel Execution)',
            'Chord (Group + Callback)',
            'Long-Running Tasks with Progress',
            'Automatic Retry Logic',
            'Time-Limited Tasks',
            'Database Operations',
            'Email Tasks',
            'Report Generation',
        ]
    }, json_dumps_params={'indent': 2})