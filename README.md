# WAYFARER

WAYFARER is a full-stack noir life-RPG that turns real-world tasks into cases. Players complete cases to earn XP and gold, develop character stats, buy cosmetics, and uncover a seven-night investigation. Story delivery changes with the player's Clarity, while the underlying mystery remains consistent.

## Submission deliverables

This repository contains the complete application source code:

- **Frontend:** React 19, TypeScript, Vite, Framer Motion, and Lucide icons.
- **Backend:** Python, FastAPI, SQLAlchemy, and JWT authentication.
- **Database:** SQLite for zero-configuration local development; its connection URL can be replaced through an environment variable.
- **Configuration templates:** [`.env.example`](.env.example) and [`frontend/.env.example`](frontend/.env.example).
- **Tests:** backend service tests in [`tests/test_services.py`](tests/test_services.py).

## Features

- Account registration and login with hashed passwords and JWT sessions
- Case board with categories, difficulty-based rewards, completion, and deletion
- XP, levels, gold, Clarity, and character-stat progression
- Seven fixed story episodes with fragments at 2, 4, and 6 completed cases and a reveal at 8
- Story-day progression and a final-vow ending on night seven
- Cosmetic shop and per-player inventory
- Responsive, animated noir interface with local visual fallbacks
- CORS allowlist and development-only story-day advancement control

## Project structure

```text
WAYFARER/
├── app/                    # FastAPI routes, models, security, services, seed data
├── frontend/               # React/Vite application
│   ├── src/                # UI, styles, and client-side assets
│   └── public/             # Static media
├── tests/                  # Pytest service tests
├── .env.example            # Backend environment-variable template
├── requirements.txt        # Production Python dependencies
└── requirements-dev.txt    # Test/development dependencies
```

## Prerequisites

- Python 3.11 or later
- Node.js 20 or later and npm
- Git

## Local setup

Clone the public GitHub repository and enter the project directory:

```bash
git clone <YOUR_PUBLIC_GITHUB_REPOSITORY_URL>
cd WAYFARER
```

### 1. Configure and run the API

Create the backend environment file from the template. Do not commit the resulting `.env` file.

```powershell
Copy-Item .env.example .env
```

Set a long, unique value for `JWT_SECRET` in `.env`. Then install dependencies and start FastAPI:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# PowerShell loads the values explicitly for local development.
$env:JWT_SECRET="replace-with-a-long-random-secret"
$env:DEMO_MODE="true"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`. Confirm it is running at `GET /health`, or use the interactive API documentation at `http://127.0.0.1:8000/docs`.

> Note: the API requires `JWT_SECRET` at startup. The project intentionally does not provide an insecure fallback secret. If you use a dotenv loader in your shell or deployment platform, the values in `.env` can be loaded automatically; otherwise export them as shown above.

### 2. Configure and run the frontend

Open a second terminal, then create the frontend environment file and start Vite:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`). Create an account to begin playing.

## Environment variables

### Backend — `.env`

| Variable | Required | Example | Purpose |
| --- | --- | --- | --- |
| `JWT_SECRET` | Yes | `a-long-random-production-secret` | Signs authentication tokens. Use a long, unique secret in every deployment. |
| `DEMO_MODE` | No | `false` | Enables `POST /dev/advance-day` and the in-app **End shift** control when `true`. Keep `false` in production. |
| `ALLOWED_ORIGINS` | No | `https://app.example.com` | Comma-separated browser origins allowed to call the API. |
| `DATABASE_PATH` | No | `/var/data/wayfarer.db` | SQLite file location. Use a persistent mounted volume in production. |
| `DATABASE_URL` | No | `postgresql://...` | Full SQLAlchemy database URL. Overrides the URL built from `DATABASE_PATH`. Ordinary `postgresql://` URLs are supported. |

### Frontend — `frontend/.env`

| Variable | Required | Example | Purpose |
| --- | --- | --- | --- |
| `VITE_API_BASE_URL` | No | `https://api.example.com` | Base URL for the FastAPI API. Defaults to `http://127.0.0.1:8000`. |

The committed `.env.example` files provide safe starting values only. Never commit real secrets or production database credentials.

## API overview

All routes except registration, login, health, and metadata require an `Authorization: Bearer <token>` header.

| Area | Endpoint | Description |
| --- | --- | --- |
| Health | `GET /health` | API health check. |
| Authentication | `POST /auth/signup`, `POST /auth/login` | Create an account or receive a JWT. |
| Character | `GET /character/me`, `POST /character/login-tick` | Read character data and apply elapsed-day effects. |
| Cases | `GET/POST /quests`, `PATCH /quests/{id}/complete`, `DELETE /quests/{id}` | Manage player cases. |
| Story | `GET /story/day/{day_number}` | Read the current episode, unlocked fragments, and finale state. |
| Shop | `GET /shop/items`, `POST /shop/purchase/{item_id}` | Browse and purchase cosmetics. |
| Inventory | `GET /inventory/me` | Read player-owned cosmetics. |
| Metadata | `GET /meta` | Read public runtime flags such as demo mode. |

FastAPI serves the full request and response schema at `/docs` while the server is running.

## Verification

Run backend tests from the repository root:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

Build the frontend to validate the TypeScript application:

```powershell
cd frontend
npm run build
```

The test suite checks all seven story episodes, including fragment thresholds, reveal progression, next-day behavior, and the final-vow path.

## Deployment

### API

Deploy the repository's backend to Render, Railway, Fly.io, or a comparable Python host using this start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set `JWT_SECRET`, `ALLOWED_ORIGINS`, `DATABASE_PATH` (or `DATABASE_URL`), and `DEMO_MODE=false` in the host's secret/environment-variable settings. Attach persistent storage and point `DATABASE_PATH` to that volume, such as `/var/data/wayfarer.db`; an ephemeral filesystem will erase player data on redeploy.

### Free Render + Supabase Postgres

To keep player data without paying for a disk, create a free Supabase project and copy its **Session pooler** connection string from **Connect**. In Render, set the copied value as `DATABASE_URL` and omit `DATABASE_PATH`. Include `sslmode=require` if Supabase did not include it in the copied URL. The app normalizes standard `postgresql://` connection strings for its PostgreSQL driver.

This arrangement keeps data in Supabase when Render’s free web service spins down. Render’s free service can take about a minute to wake after 15 idle minutes, and Supabase pauses a free database after one week of inactivity.

### Frontend

Deploy the `frontend` directory to Vercel, Netlify, or any static host:

- Build command: `npm run build`
- Publish directory: `dist`
- Environment variable: `VITE_API_BASE_URL=https://<your-api-domain>`

Add the exact public frontend origin to the API's `ALLOWED_ORIGINS` setting. For example:

```text
ALLOWED_ORIGINS=https://your-app.vercel.app
```

## Security and data notes

- Passwords are hashed with Passlib before persistence.
- JWT signing requires an explicit secret and tokens expire after seven days.
- Each protected API route scopes database reads and writes to the authenticated user.
- CORS is limited to the configured allowlist rather than accepting every origin.
- The frontend keeps only the JWT in browser local storage; character, cases, story, shop, and inventory data are read from the API.

## License

No license has been selected for this project. Add a license file before distributing, reusing, or accepting external contributions under a specific license.
