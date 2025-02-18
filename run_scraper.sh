#!/bin/bash

echo "Starting SEPTA Scraper..."

python -c "from septa.core.database import init_trip_updates_db, init_db; init_trip_updates_db(); init_db()"

echo "45 23,0-1 * * * cd /septa-delay && python -m septa.rrschedules" >> mycron
echo "*/10 4-23,0-1 * * * cd /septa-delay && python -m septa.train_view" >> mycron
echo "*/10 4-23,0-1 * * * cd /septa-delay && python -m septa.trip_updates" >> mycron

crontab mycron
cron -f
