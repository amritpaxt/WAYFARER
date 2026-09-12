# WAYFARER

WAYFARER is a Life-RPG framed as a noir detective mystery: a memory-wiped police chief rebuilds their life one completed case at a time. The interface uses near-black and slate panels, amber for momentum, teal for clarity, and muted blood-rust only when the story becomes unreliable. Playfair Display gives case files their pulp-noir voice while IBM Plex Sans keeps controls crisp and accessible.

## Run the backend

```powershell
cd C:\Users\Admin\Downloads\WAYFARER-main\WAYFARER-main
python -m pip install -r requirements.txt
$env:DEMO_MODE="true" # optional; enables the in-world Sleep control
python -m uvicorn app.main:app --reload --port 8000
```

Copy `.env.example` and set a long `JWT_SECRET` before deployment. The API persists its SQLite data in `wayfarer.db`. On startup it safely adds the story-day column to older local databases and refreshes the seven seeded episodes.

## Run the frontend

```powershell
cd C:\Users\Admin\Downloads\WAYFARER-main\WAYFARER-main\frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env` if the API is not on `http://localhost:8000`. The frontend stores only the JWT in localStorage; character, quests, story, shop, inventory, and demo progression are always reloaded from the FastAPI API.

## Notes

Calendar rollover advances a character's `day_index` by the number of elapsed days (capped at 7) and reduces clarity using the same service used by demo advancement. `POST /dev/advance-day` is unavailable unless `DEMO_MODE=true`. Shop cosmetics are single-purchase items, returning `409` if already owned and `402` when gold is insufficient.

Run backend checks with `python -m pytest` after installing `pytest`.
