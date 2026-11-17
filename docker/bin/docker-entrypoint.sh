#!/bin/bash
set -e

export MEDIA_ROOT="${MEDIA_ROOT:-/var/media}"
export STATIC_ROOT="${STATIC_ROOT:-/var/static}"

export REDIS_LOGLEVEL="${REDIS_LOGLEVEL:-warning}"
export REDIS_MAXMEMORY="${REDIS_MAXMEMORY:-100Mb}"
export REDIS_MAXMEMORY_POLICY="${REDIS_MAXMEMORY_POLICY:-volatile-ttl}"

export DOLLAR='$'

mkdir -p /var/run/celery "${MEDIA_ROOT}" "${STATIC_ROOT}"
chown -R hope:unicef /var/run/celery "${MEDIA_ROOT}" "${STATIC_ROOT}"
echo "created support dirs /var/run '${MEDIA_ROOT}' '${STATIC_ROOT}' "
echo "Startup command is: '$1'"

case "$1" in
    "run")
        gosu hope:unicef django-admin upgrade
        exec gosu hope:unicef uwsgi --ini /conf/uwsgi.ini
        ;;
    "dev")
        until pg_isready -h db -p 5432; do
            echo "waiting for database"
            sleep 2
        done
        gosu hope:unicef django-admin collectstatic --no-input
        gosu hope:unicef django-admin migrate
        gosu hope:unicef django-admin runserver 0.0.0.0:8000
        ;;
    "setup")
        until pg_isready -h db -p 5432; do
            echo "waiting for database"
            sleep 2
        done
        gosu hope:unicef django-admin upgrade
        ;;
    "worker")
        exec gosu hope:unicef celery -A hope_dashboard.config.celery worker \
            --concurrency="${CELERY_CONCURRENCY:-4}" \
            -E \
            -l "${CELERY_LOGLEVEL:-INFO}"
        ;;
    "beat")
        exec gosu hope:unicef celery -A hope_dashboard.config.celery beat \
            --schedule=/var/run/celery/celerybeat-schedule \
            -l "${CELERY_LOGLEVEL:-INFO}"
        ;;
    *)
        exec "$@"
        ;;
esac
