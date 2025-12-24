#!/bin/bash

# ============================================================================
# Django Celery Project Stop Script
# ============================================================================
# This script stops all services started by start.sh

echo "=========================================="
echo "Django Celery Implementation - Shutdown"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if PIDs file exists
if [ ! -f ".pids" ]; then
    echo -e "${YELLOW}No .pids file found. Attempting to find processes...${NC}"
    
    # Kill Django
    pkill -f "manage.py runserver"
    
    # Kill Celery worker
    pkill -f "celery.*worker"
    
    # Kill Celery beat
    pkill -f "celery.*beat"
    
    # Kill Flower
    pkill -f "celery.*flower"
    
    echo -e "${GREEN}All processes stopped!${NC}"
    exit 0
fi

# Read PIDs from file
PIDS=($(cat .pids))

# Stop each service
echo -e "${YELLOW}Stopping services...${NC}"

for PID in "${PIDS[@]}"; do
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping process $PID..."
        kill $PID
    fi
done

# Wait a moment for graceful shutdown
sleep 2

# Force kill if still running
for PID in "${PIDS[@]}"; do
    if ps -p $PID > /dev/null 2>&1; then
        echo "Force stopping process $PID..."
        kill -9 $PID
    fi
done

# Remove PIDs file
rm .pids

echo ""
echo -e "${GREEN}All services stopped successfully!${NC}"
echo ""

# Clean up Celery artifacts
if [ -f "celerybeat-schedule.db" ]; then
    echo "Cleaning up Celery artifacts..."
    rm -f celerybeat-schedule.db
    rm -f celerybeat.pid
fi

echo "Shutdown complete!"
