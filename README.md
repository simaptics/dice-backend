
---

# 🐍 dice-backend — Django REST API

```md
# 🐍 Dice Backend

A Django + Django REST Framework backend for a dice rolling app.
Provides APIs for saving, updating, deleting, and listing dice macros per user, with per-user limits and validation.

## ✨ Features

- 🔐 User-aware macros (user ID from JWT)
- 📦 CRUD API for dice macros
- 🚫 Per-user macro limit enforced
- 🔁 Upsert behavior (update if name exists, otherwise create)
- 🧾 Validation with friendly error messages
- 🗃️ PostgreSQL
- ✅ Test suite (31 tests) using SQLite in-memory DB

## 🛠️ Tech Stack

- Django
- Django REST Framework
- Gunicorn
- PostgreSQL
- JWT or upstream auth proxy (user_id passed in request)

## 🧪 Testing

Tests use an in-memory SQLite database so no PostgreSQL instance is needed.

```bash
cd project
python manage.py test dice --settings=dice_backend.test_settings
```

Test coverage includes:
- **Model** — field storage, `__str__`, unique constraints
- **Authentication** — valid/expired/invalid JWT tokens, missing cookies, payload validation
- **Public roll endpoint** — successful rolls, default modifier, input validation, response structure
- **Macro CRUD** — create, list, retrieve, update, delete, per-user isolation, 10-macro limit
- **Macro roll action** — rolling via saved macro, value range checks, cross-user protection
