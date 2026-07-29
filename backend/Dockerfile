# syntax=docker/dockerfile:1

###############################################################################
# Dependency build stage
###############################################################################

FROM python:3.14.6-slim-trixie AS app-build

LABEL maintainer="Tyler Higgins <tylermaverickhiggins@gmail.com>"

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

COPY --from=ghcr.io/astral-sh/uv:0.11.32 \
    /uv \
    /uvx \
    /usr/local/bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

###############################################################################
# Application / development stage
###############################################################################

FROM python:3.14.6-slim-trixie AS app

LABEL maintainer="Tyler Higgins <tylermaverickhiggins@gmail.com>"

WORKDIR /app

ARG APP_UID=1000
ARG APP_GID=1000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    USER=python

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf \
    /var/lib/apt/lists/* \
    /usr/share/doc/* \
    /usr/share/man/* \
    && apt-get clean \
    && groupadd --gid "${APP_GID}" python \
    && useradd \
    --create-home \
    --no-log-init \
    --uid "${APP_UID}" \
    --gid "${APP_GID}" \
    python \
    && mkdir -p /app/src /app/bin \
    && chown -R python:python /app

COPY --from=app-build /opt/venv /opt/venv
COPY --from=app-build /usr/local/bin/uv /usr/local/bin/uv
COPY --from=app-build /usr/local/bin/uvx /usr/local/bin/uvx
COPY --chown=python:python pyproject.toml /app/pyproject.toml

COPY --chown=python:python bin/ /app/bin/
COPY --chown=python:python src/ /app/src/

RUN find /app/bin -type f -exec chmod 0755 {} \;

USER python

WORKDIR /app/src

EXPOSE 8000

CMD ["bash"]
