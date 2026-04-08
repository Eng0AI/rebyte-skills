---
name: fastapi-fullstack
description: "Scaffolds and develops full-stack web applications with FastAPI backend, React frontend, PostgreSQL database, and Docker containerization. Configures SQLAlchemy models, Alembic migrations, and API endpoints. Use when the user wants to build a web app, create a REST API, set up a Python full-stack project, or mentions FastAPI with React and PostgreSQL."
---

# FastAPI Full Stack

Set up and develop a full-stack Python application using the FastAPI template with React frontend, PostgreSQL, and Docker.

## Setup

### 1. Clone the Template

```bash
git clone --depth 1 https://github.com/tiangolo/full-stack-fastapi-template.git .
```

If the directory is not empty:

```bash
git clone --depth 1 https://github.com/tiangolo/full-stack-fastapi-template.git _temp_template
mv _temp_template/* _temp_template/.* . 2>/dev/null || true
rm -rf _temp_template
```

### 2. Remove Git History (Optional)

```bash
rm -rf .git
git init
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env — set at minimum:
# POSTGRES_SERVER=localhost
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=changethis
# POSTGRES_DB=app
# SECRET_KEY=<generate-a-random-key>
# FIRST_SUPERUSER=admin@example.com
# FIRST_SUPERUSER_PASSWORD=changethis
```

### 4. Start with Docker (Recommended)

```bash
docker compose up -d
```

Verify containers are running:

```bash
docker compose ps
# All services should show "running"
```

### 5. Or Start Manually

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head        # Run database migrations
uvicorn app.main:app --reload
```

### 6. Verify Setup

- API docs: open `http://localhost:8000/docs` — Swagger UI should load
- Frontend: open `http://localhost:5173` if running the React dev server

## Development Workflow

**Add a new API endpoint:**

1. Define the SQLAlchemy model in `backend/app/models/`
2. Create an Alembic migration: `alembic revision --autogenerate -m "add <model>"`
3. Apply the migration: `alembic upgrade head`
4. Add the endpoint in `backend/app/api/routes/`
5. Register the router in `backend/app/api/main.py`

**Run tests:**

```bash
cd backend
pytest
```

**Rebuild after dependency changes:**

```bash
docker compose up -d --build
```
