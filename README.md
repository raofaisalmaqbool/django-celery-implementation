# Django Celery Implementation

A comprehensive Django project demonstrating various Celery patterns and best practices for distributed task processing.

![Django](https://img.shields.io/badge/Django-5.0.6-green.svg)
![Celery](https://img.shields.io/badge/Celery-5.4.0-37814A.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Redis](https://img.shields.io/badge/Redis-Cache%20%26%20Broker-red.svg)

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Celery Patterns Implemented](#celery-patterns-implemented)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
- [Celery Tasks](#celery-tasks)
- [Monitoring](#monitoring)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## ✨ Features

- **Multiple Celery Patterns**: Chains, Groups, Chords, and Callbacks
- **Task Progress Tracking**: Real-time progress updates for long-running tasks
- **Automatic Retry Logic**: Configurable retry with exponential backoff
- **Time-Limited Tasks**: Soft and hard time limits to prevent hanging tasks
- **Periodic Tasks**: Scheduled tasks using Celery Beat
- **Task Monitoring**: Track task execution history and statistics
- **Signal Handlers**: Pre-run, post-run, and failure handlers
- **Result Backend**: Store results in Django database or Redis
- **RESTful API**: Comprehensive API for task management
- **Admin Interface**: Django admin integration for task monitoring
- **Environment-based Configuration**: Easy configuration management

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Django    │────▶│    Redis     │◀────│   Celery    │
│  Web App    │     │ (Broker)     │     │   Worker    │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                         │
       │            ┌──────────────┐            │
       └───────────▶│  PostgreSQL/ │◀───────────┘
                    │   SQLite     │
                    │  (Database)  │
                    └──────────────┘
                           │
                    ┌──────────────┐
                    │Celery Results│
                    └──────────────┘
```

## 🎯 Celery Patterns Implemented

### 1. **Simple Tasks**
Basic asynchronous task execution for operations like sending emails, processing data, etc.

### 2. **Task Chaining**
Sequential task execution where each task receives the result of the previous task.
```python
chain(task1.s(value) | task2.s() | task3.s())
```

### 3. **Task Groups**
Parallel execution of multiple independent tasks.
```python
group([task1.s(), task2.s(), task3.s()])
```

### 4. **Chords**
Execute tasks in parallel, then aggregate results with a callback.
```python
chord([task1.s(), task2.s(), task3.s()])(callback.s())
```

### 5. **Long-Running Tasks**
Tasks with progress tracking and state updates.

### 6. **Retry Logic**
Automatic retry on failure with exponential backoff and jitter.

### 7. **Time-Limited Tasks**
Tasks with soft and hard time limits to prevent infinite execution.

### 8. **Periodic Tasks**
Scheduled tasks using Celery Beat (cron-like scheduling).

### 9. **Callbacks**
Success and error callbacks for task completion handling.

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Redis server
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd celery-implementation
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Redis

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### On macOS:
```bash
brew install redis
brew services start redis
```

#### On Windows:
Download and install from [Redis Windows](https://github.com/microsoftarchive/redis/releases)

### Step 5: Environment Configuration

```bash
# Copy sample environment file
cp .env.sample .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

## ⚙️ Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Redis
REDIS_CACHE_URL=redis://127.0.0.1:6379/1

# Celery
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=django-db
```

### Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create logs directory
mkdir logs
```

## 🏃 Running the Project

### 1. Start Redis Server

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

### 2. Start Django Development Server

```bash
python manage.py runserver
```

### 3. Start Celery Worker

```bash
# In a new terminal window
celery -A celerytest worker --loglevel=info

# On Windows, use:
celery -A celerytest worker --loglevel=info --pool=solo
```

### 4. Start Celery Beat (for periodic tasks)

```bash
# In another terminal window
celery -A celerytest beat --loglevel=info
```

### 5. Start Flower (Optional - Web-based monitoring)

```bash
# In another terminal window
celery -A celerytest flower
# Access at: http://localhost:5555
```

## 📡 API Endpoints

### Documentation
- **GET** `/api/docs/` - Complete API documentation

### Simple Tasks
- **POST** `/api/simple-task/` - Execute simple addition task
  ```json
  {
    "x": 10,
    "y": 20
  }
  ```

### Advanced Patterns
- **POST** `/api/chain-tasks/` - Execute task chain
  ```json
  {
    "initial_value": 5
  }
  ```

- **POST** `/api/group-tasks/` - Execute tasks in parallel
  ```json
  {
    "count": 5
  }
  ```

- **POST** `/api/chord-tasks/` - Execute chord pattern
  ```json
  {
    "chunks": 3,
    "items_per_chunk": 10
  }
  ```

### Long-Running Tasks
- **POST** `/api/long-task/` - Start long-running task
  ```json
  {
    "steps": 10
  }
  ```

- **GET** `/api/task-progress/<task_id>/` - Get task progress

### Task Management
- **GET** `/api/task-status/<task_id>/` - Check task status
- **POST** `/api/revoke-task/<task_id>/` - Cancel running task

### Database Operations
- **POST** `/api/create-users/` - Create users in batch
  ```json
  {
    "count": 10,
    "prefix": "testuser"
  }
  ```

### Reports
- **POST** `/api/generate-report/` - Generate report asynchronously
  ```json
  {
    "report_type": "USER",
    "filters": {"active": true}
  }
  ```

### Monitoring
- **GET** `/api/health/` - Celery health check
- **GET** `/api/task-overview/` - Task statistics

## 📊 Celery Tasks

### Available Tasks

#### Simple Tasks
- `add(x, y)` - Addition operation
- `multiply(x, y)` - Multiplication operation

#### Database Tasks
- `create_users_batch(count, prefix)` - Create multiple users
- `cleanup_old_users(days)` - Clean up inactive users

#### Email Tasks
- `send_email_task(subject, message, recipients)` - Send email
- `send_bulk_emails(user_ids, subject, message)` - Send bulk emails

#### Data Processing
- `process_data_chunk(chunk_id, data)` - Process data chunk
- `aggregate_results(results)` - Aggregate results from multiple tasks

#### Long-Running Tasks
- `long_running_task(total_steps)` - Task with progress tracking
- `time_limited_task(duration)` - Task with time limits

#### Monitoring
- `health_check()` - System health check
- `cleanup_task_logs(days)` - Clean up old logs

#### Report Generation
- `generate_report(report_type, filters)` - Generate reports

## 📈 Monitoring

### Django Admin

Access the Django admin interface at `http://localhost:8000/admin/`

Features:
- View all task logs
- Monitor task execution history
- Manage scheduled tasks
- View reports

### Flower - Web-based Monitoring

Access Flower at `http://localhost:5555/`

Features:
- Real-time task monitoring
- Worker management
- Task statistics and graphs
- Task history and details

### Command Line Monitoring

```bash
# Inspect active tasks
celery -A celerytest inspect active

# Inspect scheduled tasks
celery -A celerytest inspect scheduled

# Inspect registered tasks
celery -A celerytest inspect registered

# Worker statistics
celery -A celerytest inspect stats
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run with pytest
pytest

# Run with coverage
coverage run -m pytest
coverage report
coverage html  # Generate HTML report
```

### Manual Testing

```bash
# Test simple task
curl -X POST http://localhost:8000/api/simple-task/ \
  -H "Content-Type: application/json" \
  -d '{"x": 5, "y": 3}'

# Check task status
curl http://localhost:8000/api/task-status/<task_id>/
```

## 🚀 Production Deployment

### 1. Environment Setup

```bash
# Set production environment variables
DEBUG=False
SECRET_KEY=<secure-random-key>
ALLOWED_HOSTS=yourdomain.com

# Use PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=celery_production
DB_USER=postgres
DB_PASSWORD=<secure-password>
```

### 2. Static Files

```bash
python manage.py collectstatic --noinput
```

### 3. Run with Gunicorn

```bash
gunicorn celerytest.wsgi:application --bind 0.0.0.0:8000
```

### 4. Celery Worker as Systemd Service

Create `/etc/systemd/system/celery.service`:

```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/celery -A celerytest worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start celery
sudo systemctl enable celery
```

### 5. Celery Beat as Systemd Service

Create `/etc/systemd/system/celerybeat.service`:

```ini
[Unit]
Description=Celery Beat Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/celery -A celerytest beat --loglevel=info

[Install]
WantedBy=multi-user.target
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Redis Connection Error
```
Error: [Errno 111] Connection refused
```
**Solution**: Ensure Redis server is running
```bash
sudo systemctl status redis
sudo systemctl start redis
```

#### 2. Celery Worker Not Starting
```
Error: No module named 'celerytest'
```
**Solution**: Ensure virtual environment is activated and in correct directory

#### 3. Tasks Not Executing
**Solution**: Check Celery worker is running and connected to broker
```bash
celery -A celerytest inspect active
```

#### 4. Import Errors
**Solution**: Run migrations and ensure all dependencies are installed
```bash
python manage.py migrate
pip install -r requirements.txt
```

### Debug Mode

Enable verbose logging:
```python
# In .env
CELERY_LOG_LEVEL=DEBUG
APP_LOG_LEVEL=DEBUG
```

## 📝 Project Structure

```
celery-implementation/
├── app/                        # Main Django app
│   ├── admin.py               # Admin configuration
│   ├── models.py              # Database models
│   ├── tasks.py               # Celery tasks
│   ├── views.py               # API views
│   └── urls.py                # URL routing
├── celerytest/                # Django project settings
│   ├── __init__.py           # Celery app initialization
│   ├── celery.py             # Celery configuration
│   ├── settings.py           # Django settings
│   └── urls.py               # Main URL configuration
├── logs/                      # Application logs
├── .env                       # Environment variables (git-ignored)
├── .env.sample               # Sample environment file
├── .gitignore                # Git ignore rules
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Rao Faisal Maqbool**

## 🙏 Acknowledgments

- Django Documentation
- Celery Documentation
- Redis Documentation
- Community contributors

## 📚 Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Documentation](https://flower.readthedocs.io/)

## 🔗 Related Projects

- [Django Celery Results](https://github.com/celery/django-celery-results)
- [Django Celery Beat](https://github.com/celery/django-celery-beat)
- [Flower](https://github.com/mher/flower)

---

**Happy Coding! 🎉**
