import pytest


def test_celery() -> None:
    try:
        from hope_dashboard.config.celery import app

        assert app.clock
    except ImportError as e:
        pytest.fail(getattr(e, "message", "unknown error"))


def test_init_celery() -> None:
    try:
        from hope_dashboard.config.celery import init_sentry

        init_sentry()
    except ImportError as e:
        pytest.fail(getattr(e, "message", "unknown error"))


def test_celery_beat_uses_database_scheduler() -> None:
    from django.conf import settings

    assert "django_celery_beat" in settings.INSTALLED_APPS
    assert settings.CELERY_BEAT_SCHEDULER == "django_celery_beat.schedulers:DatabaseScheduler"


@pytest.mark.django_db
def test_ensure_default_periodic_task() -> None:
    from hope_dashboard.utils.celery_beat import DEFAULT_TASK_PATH, ensure_default_periodic_task

    task = ensure_default_periodic_task()

    assert task.task == DEFAULT_TASK_PATH
    assert task.crontab.hour == "*/3"
    assert task.crontab.minute == "0"
    assert task.enabled is True
    assert ensure_default_periodic_task().pk == task.pk


@pytest.mark.django_db
def test_ensure_default_periodic_task_updates_existing_schedule() -> None:
    from django_celery_beat.models import CrontabSchedule, PeriodicTask

    from hope_dashboard.utils.celery_beat import (
        DEFAULT_TASK_NAME,
        DEFAULT_TASK_PATH,
        ensure_default_periodic_task,
    )

    old_crontab = CrontabSchedule.objects.create(
        minute="0",
        hour="2",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
        timezone="UTC",
    )
    PeriodicTask.objects.create(
        name=DEFAULT_TASK_NAME,
        task=DEFAULT_TASK_PATH,
        crontab=old_crontab,
        enabled=False,
    )

    task = ensure_default_periodic_task()

    assert task.crontab.hour == "*/3"
    assert task.enabled is True
