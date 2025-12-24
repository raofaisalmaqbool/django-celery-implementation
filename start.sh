#!/bin/bash

# ============================================================================
# Django Celery Project Startup Script
# ============================================================================
# This script starts all necessary services for the Django Celery project

echo "=========================================="
echo "Django Celery Implementation - Startup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python -m venv venv
    echo -e "${GREEN}Virtual environment created!${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update requirements
echo -e "${YELLOW}Installing/updating requirements...${NC}"
pip install -r requirements.txt

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    mkdir logs
    echo -e "${GREEN}Logs directory created!${NC}"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}.env file not found. Copying from .env.sample...${NC}"
    cp .env.sample .env
    echo -e "${RED}Please update .env file with your configuration!${NC}"
fi

# Check if Redis is running
echo -e "${YELLOW}Checking Redis connection...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}Redis is running!${NC}"
else
    echo -e "${RED}Redis is not running. Please start Redis first:${NC}"
    echo "  sudo systemctl start redis"
    echo "  or"
    echo "  redis-server"
    exit 1
fi

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py makemigrations
python manage.py migrate

# Create superuser if needed
echo ""
echo -e "${YELLOW}Do you want to create a superuser? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

# Start services
echo ""
echo -e "${GREEN}=========================================="
echo "Starting Services"
echo "==========================================${NC}"
echo ""

# Start Django development server
echo -e "${YELLOW}Starting Django development server...${NC}"
python manage.py runserver > logs/django.log 2>&1 &
DJANGO_PID=$!
echo -e "${GREEN}Django server started (PID: $DJANGO_PID)${NC}"
echo "  URL: http://localhost:8000"
echo "  Admin: http://localhost:8000/admin"
echo "  API Docs: http://localhost:8000/api/docs/"

# Start Celery worker
echo ""
echo -e "${YELLOW}Starting Celery worker...${NC}"
celery -A celerytest worker --loglevel=info > logs/celery_worker.log 2>&1 &
CELERY_PID=$!
echo -e "${GREEN}Celery worker started (PID: $CELERY_PID)${NC}"

# Start Celery beat
echo ""
echo -e "${YELLOW}Starting Celery beat...${NC}"
celery -A celerytest beat --loglevel=info > logs/celery_beat.log 2>&1 &
BEAT_PID=$!
echo -e "${GREEN}Celery beat started (PID: $BEAT_PID)${NC}"

# Start Flower
echo ""
echo -e "${YELLOW}Starting Flower (Celery monitoring)...${NC}"
celery -A celerytest flower > logs/flower.log 2>&1 &
FLOWER_PID=$!
echo -e "${GREEN}Flower started (PID: $FLOWER_PID)${NC}"
echo "  URL: http://localhost:5555"

# Save PIDs to file for stopping later
echo "$DJANGO_PID" > .pids
echo "$CELERY_PID" >> .pids
echo "$BEAT_PID" >> .pids
echo "$FLOWER_PID" >> .pids

echo ""
echo -e "${GREEN}=========================================="
echo "All services started successfully!"
echo "==========================================${NC}"
echo ""
echo "Services running:"
echo "  - Django:  http://localhost:8000"
echo "  - Flower:  http://localhost:5555"
echo ""
echo "To stop all services, run: ./stop.sh"
echo "Logs are available in the logs/ directory"
echo ""
echo -e "${YELLOW}Press Ctrl+C to view logs (services will continue running)${NC}"

# Wait for user interrupt
trap 'echo ""; echo "Services are still running. Use ./stop.sh to stop them."; exit 0' INT

# Tail all logs
tail -f logs/*.log
