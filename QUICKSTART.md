# Quick Start Guide

Get up and running with Django Celery Implementation in 5 minutes!

## Prerequisites

- Python 3.8+
- Redis server
- pip

## Installation

### 1. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
Download from [Redis Windows](https://github.com/microsoftarchive/redis/releases)

### 2. Clone and Setup Project

```bash
# Clone repository
git clone <repository-url>
cd celery-implementation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.sample .env

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create logs directory
mkdir logs
```

## Quick Start Methods

### Method 1: Using Startup Script (Linux/Mac)

```bash
# Make script executable
chmod +x start.sh

# Start all services
./start.sh

# To stop all services
./stop.sh
```

### Method 2: Manual Start

**Terminal 1 - Django:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A celerytest worker --loglevel=info
```

**Terminal 3 - Celery Beat (Optional):**
```bash
celery -A celerytest beat --loglevel=info
```

**Terminal 4 - Flower (Optional):**
```bash
celery -A celerytest flower
```

### Method 3: Using Docker

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Access the Application

Once started, access:

- **Django App:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **API Docs:** http://localhost:8000/api/docs/
- **Flower:** http://localhost:5555

## Test the Setup

### 1. Simple Task Test

```bash
curl -X POST http://localhost:8000/api/simple-task/ \
  -H "Content-Type: application/json" \
  -d '{"x": 5, "y": 3}'
```

Response:
```json
{
  "status": "success",
  "task_id": "abc123...",
  "message": "Task queued to add 5 + 3"
}
```

### 2. Check Task Status

```bash
curl http://localhost:8000/api/task-status/abc123.../
```

### 3. Create Users in Batch

```bash
curl -X POST http://localhost:8000/api/create-users/ \
  -H "Content-Type: application/json" \
  -d '{"count": 5, "prefix": "testuser"}'
```

### 4. Execute Task Chain

```bash
curl -X POST http://localhost:8000/api/chain-tasks/ \
  -H "Content-Type: application/json" \
  -d '{"initial_value": 10}'
```

## Common Patterns

### Execute a Simple Task
```python
from app.tasks import add

result = add.apply_async(args=[10, 5])
print(result.get())  # Output: 15
```

### Execute Tasks in Parallel (Group)
```python
from celery import group
from app.tasks import add

job = group([
    add.s(2, 2),
    add.s(4, 4),
    add.s(8, 8)
])
result = job.apply_async()
print(result.get())  # Output: [4, 8, 16]
```

### Execute Tasks Sequentially (Chain)
```python
from celery import chain
from app.tasks import workflow_step_1, workflow_step_2, workflow_step_3

workflow = chain(
    workflow_step_1.s(5),
    workflow_step_2.s(),
    workflow_step_3.s()
)
result = workflow.apply_async()
print(result.get())
```

### Execute with Callback (Chord)
```python
from celery import chord
from app.tasks import process_data_chunk, aggregate_results

workflow = chord([
    process_data_chunk.s(1, [1, 2, 3]),
    process_data_chunk.s(2, [4, 5, 6]),
])(aggregate_results.s())

result = workflow.get()
print(result)
```

## Monitoring

### View Task Logs in Admin
1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Navigate to "Task Logs"

### Monitor with Flower
1. Go to http://localhost:5555
2. View active tasks, workers, and statistics

### Check Celery Status
```bash
# Active tasks
celery -A celerytest inspect active

# Registered tasks
celery -A celerytest inspect registered

# Worker stats
celery -A celerytest inspect stats
```

## Troubleshooting

### Redis Connection Error
```bash
# Check Redis status
redis-cli ping
# Should return: PONG

# If not running, start it:
sudo systemctl start redis
```

### Celery Worker Not Starting
```bash
# Ensure you're in the project directory
cd /path/to/celery-implementation

# Activate virtual environment
source venv/bin/activate

# Start with verbose logging
celery -A celerytest worker --loglevel=debug
```

### Database Errors
```bash
# Re-run migrations
python manage.py migrate

# Reset database (CAUTION: deletes all data)
rm db.sqlite3
python manage.py migrate
```

## Next Steps

1. **Explore API Documentation**
   - Visit http://localhost:8000/api/docs/
   - Test different endpoints

2. **Read Full Documentation**
   - Check [README.md](README.md) for detailed information
   - Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines

3. **Try Different Patterns**
   - Chain tasks
   - Group tasks
   - Use chord pattern
   - Create periodic tasks

4. **Customize for Your Needs**
   - Add your own tasks in `app/tasks.py`
   - Create custom views in `app/views.py`
   - Modify settings in `.env`

## Support

- **Issues:** Report bugs or request features on GitHub
- **Documentation:** Check README.md for detailed info
- **Examples:** Review `app/tasks.py` for task examples

Happy coding! 🚀
