# Wayfarer API

Run locally:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

The SQLite database is created at `backend/wayfarer.db` and seeds Day 1 plus Days 2-7 teaser records on first startup.
