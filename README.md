# BorrowBox
The Django project serves a static HTML frontend based on [this frontend source code](https://github.com/profrbazur/borrowBoxUIHTML.git) (admin and student views) with added Backend for adding CRUD functionality and exposes a JSON API for the workflow.

## Prerequisites and Stack used
- Python 3.13
- Django 6.0.7
- Django REST Framework 3.16
- django-cors-headers 4.x
- SQLite (file-based, no server needed)

## Quickstart
From the project root (`borrowbox/`, where `manage.py` lives):
```powershell
# Powershell
..\venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Then open:
- **Django API** — http://127.0.0.1:8000/api/
- **Admin panel** — http://127.0.0.1:8000/admin/ (login: `admin` / `admin12345`)
- **Frontend pages** — http://127.0.0.1:8000/index.html (auto-routes every
  `*.html` in `borrowbox/frontend/templates/`)

The seed command is **idempotent** meaning it's safe to re-run.

## Project layout
```
borrowbox/
├─ requirements.txt
├─ borrowbox/
│   ├─ manage.py
│   ├─ db.sqlite3                   # SQLite database (committed)
│   ├─ borrowbox/                   # Project package (settings, urls, wsgi, asgi)
│   │  ├─ settings.py              # DRF + CORS configured
│   │  └─ urls.py
│   └─ frontend/                    # The single Django app
│      ├─ models.py                # Student, Employee, Category, Item, # BorrowingRequest, UserProfile
│      ├─ serializers.py           # ModelSerializer per entity
│      ├─ api.py                   # ModelViewSets + workflow @action methods
│      ├─ urls.py                  # /api/ + auto-glob HTML routes
│      ├─ admin.py                 # Admin registrations
│      ├─ tests.py                 # 6 smoke tests
│      ├─ management/commands/
│      │  └─ seed.py              # Demo data
│      └─ templates/               # Git submodule — the static HTML
└─ venv/
```

## Common commands
```powershell
# Activate the venv (PowerShell)
..\venv\Scripts\Activate.ps1

# Dev server
python manage.py runserver              # http://127.0.0.1:8000

# Database
python manage.py makemigrations frontend
python manage.py migrate
python manage.py seed                   # idempotent demo data

# Tests
python manage.py test frontend          # 6 smoke tests
python manage.py test frontend.tests.WorkflowTests.test_full_lifecycle_changes_stock_correctly

# Admin
python manage.py createsuperuser
```

## Members
- Moritz Chester Saribay