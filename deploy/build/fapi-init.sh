#!/bin/bash

# Automatically export all variables in /app-env if it exists
if [ -f "/app-env" ]; then
  echo "Loading environment variables from /app-env"
  set -o allexport
  source /app-env
  set +o allexport
else
  echo "/app-env not found, skipping..."
fi


DEFAULT_COMMAND="fastapi run app/main.py --port 80"


if [ $# -eq 0 ]; then
    exec $DEFAULT_COMMAND
else
    # Log the command to be executed
    exec "$@"
fi

