# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django REST Framework backend for a dice rolling application. Provides APIs for rolling dice and managing per-user dice macros with JWT authentication via cookies.

## Commands

All commands run from the `project/` directory:

```bash
# Run dev server
python project/manage.py runserver

# Database migrations
python project/manage.py makemigrations
python project/manage.py migrate

# Run tests
python project/manage.py test dice

# Docker build & run
docker build -t dice .
docker run -p 8500:8500 dice
```

Production runs via Gunicorn on port 8500.

## Architecture

- **project/dice_backend/** — Django project settings and root URL config
- **project/dice/** — Single Django app containing all business logic

### Key files

- `dice/authentication.py` — Custom JWT auth (`DiceJWTAuthentication`) that reads `access_token` from cookies, verifies with HS256 using `SECRET_KEY` env var. Returns a `SimpleUser` with `id` and `permissions` from JWT payload.
- `dice/models.py` — `DiceMacro` model (user_id, name, num_dice, sides, modifier). Unique constraint on (user_id, name).
- `dice/serializers.py` — Validates roll requests (num_dice 1-100, sides 2-1000) and enforces max 10 macros per user.
- `dice/views.py` — `RollDiceView` (public, no auth) and `DiceMacroViewSet` (authenticated CRUD + roll action). All macro queries filtered by `request.user.id`.

### API Routes (all prefixed `/api/`)

- `POST /api/roll/` — Public dice roll
- `/api/macros/` — Authenticated CRUD (DefaultRouter) + custom `POST /api/macros/{id}/roll/`

## Environment Variables

- `SECRET_KEY` — Django secret key, also used for JWT verification
- `DB_DATABASE`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (default 5432) — PostgreSQL connection
- `DOMAIN` — Optional; sets ALLOWED_HOSTS to `[dice.{DOMAIN}, localhost, 127.0.0.1]`

## Deployment

AWS CodeBuild (`buildspec.yml`) builds a Docker image and pushes to ECR repo "dice" tagged with the git commit hash and `latest`.
