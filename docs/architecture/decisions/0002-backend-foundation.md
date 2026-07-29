# ADR-0002: Establish the Django Backend Foundation

## Status

Accepted

## Date

2026-07-28

## Context

Eirdom Household requires a stable backend foundation before development
begins on household-specific domains such as assets, maintenance,
inventory, finances, rooms, and household membership.

The backend must support:

-   Local development using Docker Desktop
-   Reproducible dependency installation
-   PostgreSQL as the long-term database
-   A custom authentication model
-   Automated testing
-   Consistent linting and formatting
-   Future REST API support for React and React Native

## Decision

### Framework

-   Python 3.14
-   Django 6
-   Django REST Framework

### Dependency Management

The backend uses **uv** with:

-   `pyproject.toml`
-   `uv.lock`

### Containerized Development

Development is Docker-first using Docker Compose.

The backend image:

-   Uses a multi-stage Docker build
-   Installs dependencies with `uv sync --frozen`
-   Runs as a non-root user
-   Uses bind mounts during development

### Database

-   PostgreSQL 18
-   Docker Compose service
-   Named Docker volume
-   `pg_isready` health check

SQLite was used only during initial scaffolding.

### Configuration

Configuration is supplied through environment variables:

-   DJANGO_SECRET_KEY
-   DJANGO_DEBUG
-   DJANGO_ALLOWED_HOSTS
-   POSTGRES_DB
-   POSTGRES_USER
-   POSTGRES_PASSWORD
-   POSTGRES_HOST
-   POSTGRES_PORT

A `.env.example` is committed while `.env` is ignored.

### User Model

A custom user model is used from project inception:

``` python
AUTH_USER_MODEL = "accounts.User"
```

The model extends `AbstractUser`.

### Testing

Testing uses:

-   pytest
-   pytest-django

Validation commands:

``` bash
pytest
python manage.py check
python manage.py makemigrations --check
ruff check .
ruff format --check .
```

## Consequences

### Positive

-   Reproducible development environment
-   PostgreSQL-first development
-   Custom user model before first migration
-   Automated testing foundation
-   Consistent linting and formatting
-   Docker-based workflow

### Negative

-   Docker adds complexity
-   PostgreSQL uses more resources than SQLite
-   Developers must understand containers, images, bind mounts, and
    volumes

## Alternatives Considered

-   SQLite as the primary database --- Rejected
-   Host-installed Python/PostgreSQL --- Rejected
-   Django default user model --- Rejected
-   pip + requirements.txt --- Rejected in favor of uv

## Validation

Verified:

-   PostgreSQL starts and becomes healthy
-   Django connects successfully
-   Initial migrations apply
-   Django Admin login works
-   Custom User model functions
-   `pytest` passes
-   `ruff check` passes
-   `ruff format --check` passes
-   `python manage.py check` passes
-   `python manage.py makemigrations --check` passes

## Future Work

Future ADRs should document:

-   Household domain model
-   Authentication and authorization
-   REST API conventions
-   Redis and background processing
-   GitHub Actions
-   Production deployment
-   Backup and recovery
-   Actual Budget integration
