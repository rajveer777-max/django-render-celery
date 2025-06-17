web: gunicorn homeo_expert_ai.wsgi --bind 0.0.0.0:$PORT --workers 3
worker: celery -A homeo_expert_ai worker --loglevel=info