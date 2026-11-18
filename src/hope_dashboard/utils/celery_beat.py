from django_celery_beat.models import CrontabSchedule, PeriodicTask

DEFAULT_TASK_NAME = "Sync daily aggregates"
DEFAULT_TASK_PATH = "hope_dashboard.analysis.tasks.schedule_sync_daily_aggregates"


def ensure_default_periodic_task() -> PeriodicTask:
    """Create the daily synchronization task if it does not exist."""
    crontab, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="2",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
        timezone="UTC",
    )
    task, _ = PeriodicTask.objects.get_or_create(
        name=DEFAULT_TASK_NAME,
        defaults={
            "task": DEFAULT_TASK_PATH,
            "crontab": crontab,
            "args": "[]",
            "kwargs": "{}",
            "enabled": True,
            "description": "Run the HOPE aggregate synchronization every day at 02:00 UTC.",
        },
    )
    return task
