#!/bin/sh
# Railway startup script (POSIX sh compatible)

# Use Railway's PORT environment variable, default to 5000 if not set
PORT=${PORT:-5000}

echo "Starting BeeSmart Spelling Bee App"
echo "Port: $PORT"
# Avoid bash-only substring expansion; just indicate if DB is configured
if [ -n "$DATABASE_URL" ]; then
    echo "Database URL detected"
else
    echo "Database URL not set (using SQLite)"
fi

# Start gunicorn with the port
exec gunicorn --bind "0.0.0.0:$PORT" \
        --timeout 300 \
        --workers 1 \
        --log-level debug \
        --access-logfile - \
        --error-logfile - \
        AjaSpellBApp:app
