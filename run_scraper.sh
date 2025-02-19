#!/bin/bash

echo "🚀 Starting SEPTA Scraper..."

# Get the correct Python path dynamically
PYTHON_PATH=$(which python3)

# Write cron jobs to a file using the correct Python path
echo "45 23,0-1 * * * cd /septa-delay && $PYTHON_PATH -m septa.rrschedules >> /septa-delay/logs/rrschedules_cron.log 2>&1" > mycron
echo "*/10 4-23,0-1 * * * cd /septa-delay && $PYTHON_PATH -m septa.train_view >> /septa-delay/logs/train_view_cron.log 2>&1" >> mycron
echo "*/10 4-23,0-1 * * * cd /septa-delay && $PYTHON_PATH -m septa.trip_updates >> /septa-delay/logs/trip_updates_cron.log 2>&1" >> mycron

# Install the cron jobs
crontab mycron

# Start cron
service cron start

echo "✅ Cron jobs installed with Python path: $PYTHON_PATH"