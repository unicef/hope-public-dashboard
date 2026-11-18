from .. import env


CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 360 * 60
CELERY_TASK_REVOKED_QUEUE = "queue_hope_revoked"
CELERY_TASK_DEFAULT_QUEUE = "default"

# Periodic tasks are managed in Django admin through django_celery_beat.
