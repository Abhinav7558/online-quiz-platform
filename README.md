# online-quiz-platform

A RESTful API backend built with FastAPI for an online quiz platform. This project provides quizzes, questions, submissions, users (student/instructor/admin), and basic analytics.

This README covers design decisions, how to run locally and with Docker, API access, main features, and example calls.

## Design overview
- FastAPI for fast development and automatic OpenAPI schema generation.
- SQLAlchemy ORM for database models and Alembic for migrations.
- Pydantic models (schemas) for request/response validation.
- Celery (present in the project) for background tasks (e.g., score calculation).

Key design decisions
- Keep business logic in `app/crud/*` so routers stay thin.
- Use database aggregation for analytics to avoid loading large datasets into memory.
- Secure endpoints with JWT-based authentication and role-based dependencies (`admin`, `instructor`, `student`).

## Prerequisites
- Python 3.12
- Docker & Docker Compose (recommended for quick local setup)
- A running PostgreSQL database when running without Docker

## Development (without Docker)
1. Create a virtual environment and install dependencies:

```bash
python -m venv venv
\venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file at project root (copy `sample.env`) and set values. Example:

```
DATABASE_URL=postgresql+psycopg2://quiz_user:quiz_pass@localhost:5432/quiz_db
SECRET_KEY=some_secret
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=password
```

3. Run database migrations:

```bash
alembic upgrade head
```

4. Start the app:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Running Celery (without Docker)

To run background tasks (the project includes a Celery app), you'll need a Redis broker running locally.

1. Install Redis locally or via a binary (or use Docker for Redis):

```bash
docker run -d --name redis -p 6379:6379 redis:7
```


3. Start a Celery worker from the project root:

```bash
celery -A app.celery_app worker --loglevel=info
```


## Running with Docker
The repository includes a `Dockerfile` and `docker-compose.yml` that start Postgres and the web app.

1. Build and start services:

```bash
docker-compose up --build
```

2. The API will be at `http://localhost:8000`.

3. Logs and migrations
- The web container runs Alembic migrations automatically at startup (see `docker-entrypoint.sh`). You can view logs with:

```powershell
docker-compose logs -f web
```

If you need to run migrations manually:

```powershell
docker-compose run --rm web alembic upgrade head
```

## API documentation / testing
- FastAPI automatically exposes interactive docs at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.
- Use these UIs to explore endpoints, models, and to test requests.

## Main features implemented
- User management (roles: ADMIN, INSTRUCTOR, STUDENT)
- Quizzes, questions, options
- Submissions and grading

## Assumptions & limitations
- The app expects PostgreSQL (psycopg2) as the database backend.
- Instructors can only access analytics for quizzes they created.

## Example API calls
- Get quizzes analytics (requires admin/instructor auth):

```http
GET /analytics/quizzes/
Authorization: Bearer <access_token>
```

- Get an individual student's analytics:

```http
GET /analytics/students/16
Authorization: Bearer <access_token>
```

Use the interactive Swagger UI at `/docs` to try endpoints with example payloads.

