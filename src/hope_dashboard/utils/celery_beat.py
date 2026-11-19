from django_celery_beat.models import CrontabSchedule, PeriodicTask

DEFAULT_TASK_NAME = "Sync daily aggregates"
DEFAULT_TASK_PATH = "hope_dashboard.analysis.tasks.schedule_sync_daily_aggregates"


def ensure_default_periodic_task() -> PeriodicTask:
    """Create or update the three-hourly synchronization task."""
    crontab, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="*/3",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
        timezone="UTC",
    )
    task, _ = PeriodicTask.objects.update_or_create(
        name=DEFAULT_TASK_NAME,
        defaults={
            "task": DEFAULT_TASK_PATH,
            "crontab": crontab,
            "args": "[]",
            "kwargs": "{}",
            "enabled": True,
            "description": "Run the HOPE aggregate synchronization every 3 hours.",
        },
    )
    return task
