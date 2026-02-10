
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

## 🛠️ Tech Stack

- Django
- Django REST Framework
- Gunicorn
- PostgreSQL
- JWT or upstream auth proxy (user_id passed in request)