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

## API reference
All endpoints are mounted under `/api/`. Authentication is currently
`AllowAny` — every endpoint is publicly readable and writable in dev.
This is fine for a local school demo; turn it on before any real deploy.

### Plain CRUD
```
GET    /api/students/
GET    /api/students/{id}/
POST   /api/students/
PATCH  /api/students/{id}/
DELETE /api/students/{id}/

... same shape for /api/employees/, /api/categories/, /api/items/
```

### Items filter
```
GET /api/items/?available=true   # only items with available_stock > 0
```

### Borrowing requests
```
GET    /api/requests/                       list
POST   /api/requests/                       create (status forced to "pending")
GET    /api/requests/{id}/                  retrieve
PATCH  /api/requests/{id}/                  update (status fields are read-only)
DELETE /api/requests/{id}/                  delete
GET    /api/requests/mine/?borrower={id}    list a single borrower's requests
POST   /api/requests/{id}/approve/          pending → approved
POST   /api/requests/{id}/reject/           pending → rejected
POST   /api/requests/{id}/issue/            approved → issued  (decrement stock)
POST   /api/requests/{id}/return/           issued → returned  (increment stock)
```

`PATCH` cannot change `status` — the state machine can only be advanced
through the four `POST` actions above. Illegal transitions return HTTP 400.

## End-to-end curl walkthrough
```powershell
# 1. seed (creates admin, 2 categories, 5 items, 3 students, 2 employees and one Pending request)
python manage.py seed

# 2. initial state: item 1 has 5 / 5 in stock, request 1 is Pending.
curl http://127.0.0.1:8000/api/items/1/
curl http://127.0.0.1:8000/api/requests/1/

# 3. approve (no stock change) → request is now "approved".
curl -X POST -H "Content-Type: application/json" -d '{"actor":"admin"}' `
     http://127.0.0.1:8000/api/requests/1/approve/

# 4. issue (decrements stock by request.quantity).
curl -X POST -H "Content-Type: application/json" -d '{"actor":"admin"}' `
     http://127.0.0.1:8000/api/requests/1/issue/

curl http://127.0.0.1:8000/api/items/1/ # available_stock is now 4

# 5. return (increments stock).
curl -X POST -H "Content-Type: application/json" -d '{"actor":"admin"}' `
     http://127.0.0.1:8000/api/requests/1/return/

curl http://127.0.0.1:8000/api/items/1/ # available_stock is back to 5

# 6. illegal transition — already returned, can't issue again.
curl -X POST -H "Content-Type: application/json" -d '{"actor":"admin"}' `
     http://127.0.0.1:8000/api/requests/1/issue/
# HTTP 400  {"detail": "Illegal transition: returned -> issued. Allowed source states: ['approved']."}
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