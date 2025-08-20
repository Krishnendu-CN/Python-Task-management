# Flask Admin Advanced Demo

A production-style Flask app with:
- Role-based auth (Admin, Staff) via Flask-Login
- Postgres (Render) or SQLite (local) with SQLAlchemy
- Database migrations (Flask-Migrate)
- Tasks module with CRUD, search, sort, pagination
- HTMX-enhanced UI (inline actions) + Bootstrap + Alpine.js
- REST API with JWT (flask-jwt-extended)
- Environment-driven config
- Render deployment ready (Procfile, render.yaml)
- Basic tests (pytest)

## Quickstart (Local)

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# copy env
cp .env.example .env           # or set your own env vars

# init DB (SQLite by default)
flask db init
flask db migrate -m "init"
flask db upgrade

# create an admin user
flask create-admin --email admin@example.com --password admin123 --name "Admin"

# run
flask run
```
Visit http://127.0.0.1:5000/

## Deploy to Render

1. Push this repo to GitHub
2. In Render, create a **Web Service**
3. Set the following env vars:
   - `FLASK_ENV=production`
   - `SECRET_KEY=<random>`
   - `DATABASE_URL=postgresql+psycopg2://...` (Render Postgres)
   - `JWT_SECRET_KEY=<random>`
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn wsgi:app`

Or use `render.yaml` (Infrastructure as Code).

## API (JWT)
- `POST /api/login` → { access_token }
- `GET /api/tasks` (bearer) → list
- `POST /api/tasks` (bearer) → create
- `PATCH /api/tasks/<id>` (bearer) → update/complete
- `DELETE /api/tasks/<id>` (bearer) → delete

Use header: `Authorization: Bearer <token>`

## Tech
- Flask, SQLAlchemy, Flask-Login, Flask-Migrate, WTForms, JWT
- Bootstrap 5, HTMX, Alpine.js, Chart.js
```