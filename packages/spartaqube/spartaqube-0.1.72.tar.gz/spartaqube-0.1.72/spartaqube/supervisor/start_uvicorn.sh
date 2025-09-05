#!/bin/bash

# Determine the max number of available CPU cores
# WORKERS=$(python3 -c "import multiprocessing; print(multiprocessing.cpu_count())")
# Use the environment variable 'workers' if defined, otherwise compute the CPU count
WORKERS="${workers:-$(python3 -c 'import multiprocessing; print(multiprocessing.cpu_count())')}"

echo "Number of workers: $WORKERS"

# Start Uvicorn with the calculated number of workers
if [ "$SQ_SILENT" == "TRUE" ]; then
    echo "Mode silent"
    exec uvicorn spartaqube_app.asgi:application --host 0.0.0.0 --port 8664 --loop uvloop --http httptools --log-level warning --access-log --workers $WORKERS
else
    echo "Mode verbose"
    exec uvicorn spartaqube_app.asgi:application --host 0.0.0.0 --port 8664 --loop uvloop --http httptools --log-level debug --access-log --workers $WORKERS
fi
