# Fina

Fina is a financial assistant with a FastAPI backend, React frontend, PostgreSQL database, Redis, and Celery background jobs.

## Stack

- Backend: Python 3.11, FastAPI, Uvicorn
- Frontend: React, Vite, nginx
- Data: PostgreSQL and MOEX market data
- Background jobs: Celery with Redis
- Authentication: JWT and email confirmation

## Project structure

```text
.
├── main.py                 # FastAPI application entry point
├── backend/
│   ├── api/                # Settings, schemas, and HTTP routers
│   ├── auth/               # PostgreSQL access, password hashing, JWT
│   ├── finance/            # Deposits, securities, and MOEX synchronization
│   └── services/           # Celery app, tasks, and email integration
├── frontend/
│   ├── src/                # React application and pages
│   ├── nginx.conf          # Production SPA and API proxy configuration
│   └── Dockerfile
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## Configuration

Create `.env` in the project root. Do not commit this file or expose its values.

For Docker Compose, use these service names:

```env
DB_HOST=db
DB_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
```

Also configure `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`, email settings, `FRONTEND_URL`, and the LLM settings. `LLM_API_KEY` is required for chat responses.

## Run with Docker

```powershell
docker compose up --build -d
```

Open:

- Frontend: http://localhost:5173
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Stop the services:

```powershell
docker compose down
```

## Run locally

Install backend dependencies and activate the virtual environment:

```powershell
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Run the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Local backend execution requires PostgreSQL, Redis, and the environment variables above to be available.

## Checks

```powershell
python -m compileall -q main.py backend
cd frontend
npm run lint
npm run build
cd ..
python -m unittest discover -s tests -v
```

## Importing the bundled finance history

After the user has registered, import `finance_3_months.csv` by passing that
user's database ID. Each non-zero income and expense value becomes a separate
transaction owned by that user. The operation is idempotent, so it can be run
again without duplicating the imported data.

```powershell
python import_transactions.py --user-id 1
```

The imported May--July 2026 records are available on the Home page through the
month navigation controls. The API always filters them to the authenticated
user, so another account cannot retrieve them.

## API routes

- `POST /auth/register`, `POST /auth/login`, `GET /auth/confirm`
- `GET|PUT /users/profile`, `PUT /users/account`
- `GET|POST|DELETE /users/avatar`
- `GET /chat/history`, `POST /chat/send`, `DELETE /chat/messages/{message_id}`
