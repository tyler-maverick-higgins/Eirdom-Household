# Application Architecture

## Context

Eirdom Household is the central platform designed to help manage every aspect of our home. The goal is to simplify daily life by bringing household management, finances, inventory, maintenance, meal planning, and future automation into a single self-hosted platform.

## Decision

The initial technology stack will consist of:

* Docker
* Django
* Python
* Node.js
* React
* React Native
* PostgreSQL
* Redis
* Actual Budget (integration)

## Initial Architecture

The platform will follow a modular, containerized architecture.

* **Django REST Framework** will expose a versioned HTTP API used by the React web application, React Native mobile application, and approved integrations.
* **React** serves as the web frontend.
* **React Native** powers the mobile application.
* **PostgreSQL** stores all persistent application data.
* **Redis** will initially support background-task messaging and may later be used for caching or other short-lived data where appropriate.
* **Celery** (planned) will process asynchronous and scheduled jobs.
* **Actual Budget** remains the authoritative system for bank-synced accounts, transactions, reconciliation, categories, and budgeting. Eirdom Household consumes selected financial data and adds household-specific context such as subscription tracking, project associations, maintenance expenses, and renewal workflows.
* **Authentik** is planned as the external identity provider using OpenID Connect. Django will remain responsible for authorization and
household-level permissions.

The Django backend will initially be implemented as a modular monolith. Business domains such as food, chores, maintenance, and finance will be separate Django applications within the same backend deployment rather than independent microservices.

## Why Django?

I have previous experience developing applications with Django and am comfortable with its architecture. Mature open-source projects such as NetBox demonstrate Django's ability to support large, feature-rich applications while remaining maintainable over the long term.

Its built-in ORM, authentication system, administrative interface, and mature ecosystem make it an excellent foundation for the Eirdom Household platform.

## Consequences

This architecture offers several advantages:

* Familiar technologies reduce development time.
* Docker provides consistent development and deployment environments.
* A modular design allows services to evolve independently.
* PostgreSQL offers a robust and reliable relational database.
* Redis enables high-performance caching and background processing.
* React and React Native allow a consistent user experience across web and mobile platforms.

This architecture also introduces several costs:

* Separate web and mobile clients increase frontend development and testing.
* Docker Compose introduces networking and configuration complexity during local development.
* Django and React require a clearly maintained API contract.
* Background tasks add operational dependencies on Redis and Celery.
* Integrating Actual Budget requires careful source-of-truth boundaries to avoid duplicated or conflicting financial records.
* The modular monolith must maintain strong internal boundaries to avoid becoming tightly coupled as features are added.

The initial infrastructure can run comfortably on existing hardware while leaving room for future expansion as the platform grows.
