# HOPE Public Dashboard


[![Test](https://github.com/unicef/hope-public-dashboard/actions/workflows/test.yml/badge.svg)](https://github.com/unicef/hope-public-dashboard/actions/workflows/test.yml)
[![Lint](https://github.com/unicef/hope-public-dashboard/actions/workflows/lint.yml/badge.svg)](https://github.com/unicef/hope-public-dashboard/actions/workflows/lint.yml)
[![Documentation](https://github.com/unicef/hope-public-dashboard/actions/workflows/docs.yml/badge.svg)](https://unicef.github.io/hope-public-dashboard/)
[![Docker Pulls](https://img.shields.io/docker/pulls/unicef/hope-public-dashboard)](https://hub.docker.com/repository/docker/unicef/hope-public-dashboard/tags)


## Translations

You can contribute to the Portal translation at https://app.transifex.com/unicef-hope/hope-dashboard/dashboard/


## Contributing

### Requirements

- [uv](https://docs.astral.sh/uv/)
- [direnv](https://direnv.net/)

### Checkout and configure development environment

```shell

    git clone https://github.com/unicef/hope-public-dashboard.git
    cd hope-public-dashboard
    uv venv .venv
    uv sync

    ./manage.py env --develop > .envrc  # create initial development configuration
    direnv allow .  # enable enviroment
    createdb hope_dashboard  # create postgres database on localhost

```

### Docker

Build the public dashboard image:

```shell
    make -C docker build
```

Run it together with PostgreSQL, Redis, a Celery worker, and Celery beat:

```shell
    docker compose up
```

The published image is available at:

```text
unicef/hope-public-dashboard
```

Publishing is handled by `.github/workflows/docker-publish.yml`.
The repository needs these GitHub Actions secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Automatic Azure deployment is optional and is enabled only when
`AZURE_PIPELINE_ID_DEVELOP` is configured. It also needs `AZURE_PAT` and the
`AZURE_ORGANIZATION` / `AZURE_PROJECT` variables.
