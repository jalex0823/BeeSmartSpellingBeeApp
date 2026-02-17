web: gunicorn --bind 0.0.0.0:${PORT:-5000} --timeout 600 --graceful-timeout 30 --workers 1 --worker-class sync --keep-alive 5 --log-level info --access-logfile - --error-logfile - AjaSpellBApp:app
