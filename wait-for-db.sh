#!/bin/bash

set -e

# Maximum number of attempts
max_attempts=30
# Delay between attempts in seconds
delay=2

echo "Waiting for MySQL database to be ready..."
for i in $(seq 1 $max_attempts); do
  echo "Attempt $i/$max_attempts"
  
  # Try to connect to the database
  if python -c "
import sys
import pymysql
import os

try:
    pymysql.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )
    print('Database connection successful!')
    sys.exit(0)
except Exception as e:
    print(f'Database connection error: {e}')
    sys.exit(1)
" 2>/dev/null; then
    # Connection successful
    echo "MySQL database is ready!"
    break
  else
    # Connection failed, wait and retry
    echo "MySQL not ready yet, waiting ${delay} seconds..."
    sleep $delay
    
    # If we've reached the maximum number of attempts, exit with error
    if [ $i -eq $max_attempts ]; then
      echo "Could not connect to MySQL database after $max_attempts attempts!"
      exit 1
    fi
  fi
done

# Now run the command
echo "Running: $@"
exec "$@"
