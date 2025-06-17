# homeo_expert_ai/celery.py
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeo_expert_ai.settings')

app = Celery('homeo_expert_ai')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Optional: Configure Google AI here if needed for workers
# import google.generativeai as genai
# if settings.GEMINI_API_KEY:
#     try:
#        genai.configure(api_key=settings.GEMINI_API_KEY)
#        print("Celery worker: Generative AI configured.")
#     except Exception as e:
#        print(f"Celery worker: Error configuring Generative AI: {e}")
# else:
#     print("Celery worker: GEMINI_API_KEY not found for configuration.")


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')