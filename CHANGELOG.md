# Changelog

All notable changes to this project are documented here. The format follows Keep a Changelog principles.

## [Unreleased]
### Planned
- Team collaboration features (shared tasks and roles).
- Notification and reminder channels (email/Slack).
- Rich text task descriptions and attachment support.
- Vector search for semantic task discovery.
- Enhanced observability with metrics and structured logs.

## [2025-09-29] Backend reliability & lifecycle polish
### Added
- Added complete user CRUD surface in the service layer and API, including secure self-delete endpoint helpers.
- Added pytest utilities and scenarios that exercise nested task flows, user deletion, and authentication bootstrapping.
- Added linting/formatting config to keep the backend style consistent.

### Changed
- Reworked task CRUD to eagerly load full trees, offer shallow vs tree responses, and refresh cascades after updates.
- Updated access token model to embed user IDs and refactored verification helpers to rely on IDs instead of usernames.
- Hardened SQLAlchemy session pragmas and cascade handling for consistent SQLite/Postgres behaviour and developer hot reloads.
- Opened up CORS defaults to support external dashboard clients during development.

### Fixed
- Removed trailing slash mismatches from task endpoints and corrected `get_current_user` to validate by id.
- Ensured orphaned subtasks are purged by enabling foreign key enforcement in tests and double-checking cascaded deletes.

### Documentation
- Expanded FastAPI docstrings and README coverage for authentication, task endpoints, and local dev workflows.
- Polished OpenAPI metadata and backend README feature lists.

## [2025-09-27] Authenticated dashboard & UI system
### Added
- Bootstrapped a Next.js App Router frontend with marketing landing, dashboard segment, and route groups for `home`, `tasks`, `agent`, and `settings`.
- Implemented dedicated sign-in/sign-up pages powered by shared `AuthShell`, `PasswordField`, and `OAuthButtons` components plus validation hooks.
- Integrated shadcn/ui primitives, thin-scrollbar utilities, and a marketing logo cloud block for consistent theming.
- Added dashboard middleware, JWT client helpers, and API proxy route handlers to forward auth headers to the backend.
- Authored an `AGENTS.md` integration guide describing how to wire the AskBar to backend MCP endpoints.

### Infrastructure
- Added `vercel.json`, Dockerfiles for dev/prod, and `.env.local` scaffolding to support local/hosted frontend deployments.
- Updated metadata, navigation config, and marketing assets (icons, logos) for the new UI.

## [2025-09-02] CI/CD & deployment pipeline
### Added
- Introduced Render deployment blueprint updates and GitHub Actions jobs to build, cache, and push backend Docker images before deployment.
- Added Docker build caching and tag management to speed up container publishing.
- Added `.dockerignore` / `.docker` tweaks and context fixes so backend and frontend images build from the correct paths.
- Registered Vercel deployment configuration and telemetry settings for the Next.js app.

### Documentation
- Added frontend configuration docs and expanded README badges for deployment/test workflows.

## [2025-08-31] Database & ops enhancements
### Added
- Added Postgres service to `docker-compose.yml` with health checks plus `asyncpg` support in the backend.
- Added a global `.gitignore`, dev requirements fixes, and instructions for running GitHub Actions tests.
- Documented project structure and agent setup guidance for contributors.

### Changed
- Refined database engine initialization, path configuration, and README disclaimers to clarify setup steps.
- Updated workflow configuration to ensure backend paths trigger CI from the new `backend/` root.

## [2025-07-31] Testing & tooling expansion
### Added
- Added comprehensive pytest coverage spanning auth failures, nested task lifecycle, and integration flows.
- Added Postman collection, curl quickstart examples, and Docker instructions for running the API locally.
- Added architecture diagrams and metadata updates to aid onboarding.

### Fixed
- Ignored local SQLite data and other generated artefacts to keep repos clean.

## [2025-07-30] Initial API scaffold
### Added
- Bootstrapped the FastAPI application with configuration modules, routing skeleton, and OpenAPI metadata.
- Added SQLAlchemy models for users and tasks with status/priority/category enums and relationships.
- Implemented authentication utilities for password hashing, token creation/verification, and API key enforcement.
- Delivered initial user signup/login endpoints and task create/list routes backed by async database sessions.
- Added Docker configuration, environment files, and packaging metadata to support containerized development.
