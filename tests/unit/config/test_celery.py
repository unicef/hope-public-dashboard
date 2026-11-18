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
    assert task.crontab.hour == "2"
    assert task.crontab.minute == "0"
    assert task.enabled is True
    assert ensure_default_periodic_task().pk == task.pk
