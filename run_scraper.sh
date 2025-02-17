#!/bin/bash

echo "Starting SEPTA Scraper..."

python -c "from septa.core.database import init_trip_updates_db, init_db; init_trip_updates_db(); init_db()"

echo "45 23,0-1 * * * python /septa-delay/septa/rrschedules.py" >> mycron
echo "*/10 4-23,0-1 * * * python /septa-delay/septa/train_view.py" >> mycron
echo "*/10 4-23,0-1 * * * python /septa-delay/septa/trip_updates.py" >> mycron

crontab mycron
cron -f
