# AI-Powered Customer Query Management System

Django + Django REST Framework backend where users submit customer queries, manage them, and use an AI model (Google Gemini, with a rule-based fallback) to auto-categorise, prioritise and draft a reply.

## Features
- Registration / login (Django auth + Token authentication)
- Full CRUD for customer queries + status update (Pending / In Progress / Resolved)
- AI analysis: category, priority, suggested response
- **Bonus:** search (name/email), filters (category/priority/status), pagination, dashboard, unit tests, AI fallback
- Swagger API docs at `/api/docs/`

## Tech stack
Python 3.10+, Django, DRF, django-filter, drf-spectacular, SQLite, Gemini API (`requests`), python-dotenv

## Installation
```bash
git clone <your-repo-url> && cd query_management
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
# edit .env -> add GEMINI_API_KEY (free: https://aistudio.google.com/app/apikey)
python manage.py migrate
python manage.py createsuperuser   # optional (admin panel)
python manage.py runserver
```
- API base: `http://127.0.0.1:8000/api/`
- Swagger docs: `http://127.0.0.1:8000/api/docs/`
- Admin: `http://127.0.0.1:8000/admin/`

> If `GEMINI_API_KEY` is empty, the app still works using the rule-based fallback.

## Run tests
```bash
python manage.py test
```

## Project structure
```
config/     settings, root urls
accounts/   register + login APIs
queries/    models, serializers, viewset, ai_service.py, tests
```

## Endpoints
| Method | Endpoint | Function |
|---|---|---|
| POST | /api/register/ | User registration |
| POST | /api/login/ | Login (returns token) |
| POST | /api/queries/ | Create query |
| GET | /api/queries/ | List (search, filter, paginate) |
| GET | /api/queries/{id}/ | Details |
| PUT / PATCH | /api/queries/{id}/ | Update |
| DELETE | /api/queries/{id}/ | Delete |
| PATCH | /api/queries/{id}/status/ | Update status only |
| POST | /api/queries/{id}/analyze/ | AI analysis |
| GET | /api/queries/dashboard/ | Total / pending / in-progress / resolved |

Query params on list: `?search=rahul`, `?category=Billing`, `?priority=High`, `?status=Pending`, `?page=2`, `?ordering=-created_at`.
All `/api/queries/*` endpoints need header `Authorization: Token <token>`.

See **API_DOCS.md** for sample requests/responses and **EXPLANATION.md** for the AI integration write-up.

## Security notes
- API key and `SECRET_KEY` are read from environment variables; `.env` is git-ignored.
- Passwords validated with Django validators and stored hashed.
