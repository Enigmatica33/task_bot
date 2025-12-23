import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_bot.settings")
app = Celery("task_bot")
app.conf.timezone = os.getenv("TIME_ZONE", "Europe/Moscow")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
