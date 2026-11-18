# Build and use the Docker image

After cloning the repo, make sure Redis and PostgreSQL are running.

```shell
    export ADMIN_EMAIL=admin@example.com
    export ADMIN_PASSWORD=password
    export DATABASE_URL=postgres://postgres:@127.0.0.1:5432/hope_dashboard
    export REDIS_CACHE_URL=redis://127.0.0.1:6379/0
    export REDIS_LOCK_URL="redis://127.0.0.1:6379/1?backend=django_redis.cache.RedisCache"
    export REDIS_TSDB_URL=redis://127.0.0.1:6379/2
    export REDIS_URL=redis://127.0.0.1:6379/3

    cd docker

    make build run
```

## Use the provided compose.yml

```shell
    docker compose up
```

The stack starts the web app, Celery worker, Celery beat, PostgreSQL, and Redis.

Navigate to <http://localhost:8000/some-unicorn/> and log in using
`admin@example.com` / `password`. The path is controlled by
`DJANGO_ADMIN_URL`.

The published image is available at:

```text
unicef/hope-public-dashboard
```
