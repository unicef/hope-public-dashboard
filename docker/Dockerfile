FROM python:3.14-slim-bookworm AS base_os

ARG GOSU_VERSION=1.17
ARG GOSU_SHA256=bbc4136d03ab138b1ad66fa4fc051bafc6cc7ffae632b069a53657279a450de3

RUN set -x \
    && runtimeDeps=" \
        curl \
        gettext \
        libldap-2.5-0 \
        libmagic1 \
        libxml2 \
        mime-support \
        postgresql-client \
    " \
    && buildDeps=" \
        wget \
    " \
    && apt-get update \
    && apt-get install -y --no-install-recommends ${buildDeps} ${runtimeDeps} \
    && rm -rf /var/lib/apt/lists/* \
    && wget --quiet -O /usr/local/bin/gosu \
        "https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-amd64" \
    && echo "${GOSU_SHA256} /usr/local/bin/gosu" | sha256sum --check --status \
    && chmod +x /usr/local/bin/gosu \
    && apt-get purge -y --auto-remove ${buildDeps}

RUN groupadd --gid 1024 unicef \
    && adduser --disabled-login --disabled-password --no-create-home --ingroup unicef -q hope


# ------- builder -------
FROM base_os AS builder

RUN set -x \
    && buildDeps=" \
        build-essential \
        cmake \
        curl \
        gcc \
        git \
        libfontconfig1 \
        libgconf-2-4 \
        libglib2.0-0 \
        libldap2-dev \
        libnss3 \
        libsasl2-dev \
        libssl-dev \
        libxml2-dev \
        libzbar-dev \
        python3-dev \
        zlib1g-dev \
    " \
    && apt-get update \
    && apt-get install -y --no-install-recommends ${buildDeps} \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uwsgi uv


# ------- production only deps -------
FROM builder AS production

ARG VERSION

ENV PATH=/venv/bin:/usr/local/bin:/usr/bin:/bin \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv \
    SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION:-0.0.0.dev0}

WORKDIR /app
COPY uv.lock README.md MANIFEST.in pyproject.toml /app/
COPY src /app/src/

RUN --mount=type=cache,target=/root/.uv-cache \
    uv sync --cache-dir=/root/.uv-cache \
        --python=/usr/local/bin/python \
        --python-preference=system \
        --frozen \
        --no-dev \
        --no-editable


# ------- dist -------
FROM base_os AS dist

ARG BUILD_DATE
ARG GIT_SHA
ARG VERSION

ENV PATH=/venv/bin:/usr/local/bin:/usr/bin:/bin \
    BUILD_DATE=$BUILD_DATE \
    GIT_SHA=$GIT_SHA \
    VERSION=$VERSION \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=hope_dashboard.config.settings \
    STATIC_URL=/static/ \
    STATIC_ROOT=/var/static \
    MEDIA_ROOT=/var/media \
    PGSSLCERT=/tmp/postgresql.crt \
    UV_PROJECT_ENVIRONMENT=/venv \
    VIRTUAL_ENV=/venv \
    UWSGI_PROCESSES=4

RUN mkdir -p /var/static /var/media /var/run \
    && chown -R hope:unicef /var/static /var/media /var/run

COPY docker/conf /conf/
COPY docker/bin/* /usr/local/bin/
COPY --from=production /venv /venv
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/

RUN chown -R hope:unicef /venv /conf

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["run"]

LABEL maintainer="hope@unicef.org"
LABEL org.opencontainers.image.authors="hope@unicef.org"
LABEL org.opencontainers.image.description="UNICEF HOPE Public Dashboard"
LABEL org.opencontainers.image.documentation="https://github.com/unicef/hope-public-dashboard/"
LABEL org.opencontainers.image.title="HOPE Public Dashboard"
LABEL org.opencontainers.image.licenses="https://github.com/unicef/hope-public-dashboard/blob/${GIT_SHA:-develop}/LICENSE"
LABEL org.opencontainers.image.revision=$GIT_SHA
LABEL org.opencontainers.image.source="https://github.com/unicef/hope-public-dashboard/tree/${GIT_SHA:-develop}/"
LABEL org.opencontainers.image.url="https://hub.docker.com/repository/docker/unicef/hope-public-dashboard/tags/"
LABEL org.opencontainers.image.vendor="UNICEF"
LABEL org.opencontainers.image.created="$BUILD_DATE"
LABEL org.opencontainers.image.version="$VERSION"
