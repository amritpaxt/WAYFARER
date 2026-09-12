# WAYFARER

WAYFARER is a noir investigative Life RPG. Complete real-world cases to earn experience, rebuild Chief Rook's memory, and uncover a fixed seven-night mystery. Low Clarity changes the delivery of a story beat, never its underlying facts.

## Run the backend

```powershell
cd WAYFARER
python -m pip install -r requirements.txt
$env:JWT_SECRET="a-long-random-production-secret"
$env:DEMO_MODE="true" # optional; enables the in-world End shift control
python -m uvicorn app.main:app --reload --port 8000
```

Copy `.env.example` and set a long `JWT_SECRET` before deployment. `ALLOWED_ORIGINS` accepts a comma-separated frontend allowlist. `DATABASE_PATH` controls where SQLite is stored (or set a full `DATABASE_URL`). On startup the API safely adds the story-day column to older local databases and refreshes the seven seeded episodes.

## Run the frontend

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env` if the API is not on `http://localhost:8000`. The frontend stores only the JWT in localStorage; character, quests, story, shop, inventory, and demo progression are always reloaded from the FastAPI API. The generated-art directory is optional: every image has an in-app gradient or SVG fallback.

## Deploy

Deploy the backend to Render (or equivalent) with:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set `JWT_SECRET`, `DEMO_MODE`, `ALLOWED_ORIGINS`, and `DATABASE_PATH`. Attach a persistent disk and point `DATABASE_PATH` to it (for example `/var/data/wayfarer.db`); SQLite on an ephemeral filesystem loses players and progress on redeploy. Deploy the `frontend` folder to Vercel or Netlify using `npm run build`, and set `VITE_API_BASE_URL` to the public API URL.

## Notes

Calendar rollover advances a character's `day_index` by the number of elapsed days (capped at 7) and reduces clarity using the same service used by demo advancement. `POST /dev/advance-day` is unavailable unless `DEMO_MODE=true`. Shop cosmetics are single-purchase items, returning `409` if already owned and `402` when gold is insufficient.

## Verify

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
cd frontend
npm run build
```

The test suite exercises all seven episodes: each gets its three fragments at
2, 4, and 6 completed cases, its reveal at 8 cases, and the final-vow path on
night seven. The next episode opens after one calendar day; cases completed in
an earlier episode do not count toward the new one.
