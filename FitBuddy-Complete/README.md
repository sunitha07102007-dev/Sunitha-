# FitBuddy — AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLite application based on the supplied FitBuddy project documentation. It supports 7-day workout generation, nutrition/recovery tips, feedback-based plan updates, persistence, API docs, and an admin dashboard.

## Architecture

- **Frontend:** HTML + Jinja2 + responsive CSS
- **Backend:** FastAPI + Uvicorn
- **AI:** Google GenAI Python SDK (`google-genai`)
- **Database:** SQLite + SQLAlchemy 2
- **Validation:** Pydantic 2
- **Testing:** Pytest + FastAPI TestClient

## Important model note

The supplied documentation names Gemini 1.5 Pro and Gemini Flash. The code uses configurable model names because model availability changes over time. Defaults are `gemini-2.5-pro` for workout planning and `gemini-2.5-flash` for nutrition. Change `WORKOUT_MODEL` and `NUTRITION_MODEL` in `.env` if your Google AI account exposes different current models.

## VS Code setup — Windows

1. Install Python 3.11+ and VS Code.
2. Open this folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

5. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

6. Copy `.env.example` to `.env`.
7. For a no-key demo, leave `DEMO_MODE=true`. The full UI/database/feedback flow works without an API key.
8. For live Gemini generation, put your Gemini key in `GEMINI_API_KEY` and set `DEMO_MODE=false`.
9. Start the server:

```powershell
uvicorn app.main:app --reload
```

10. Open http://127.0.0.1:8000
11. API documentation: http://127.0.0.1:8000/docs
12. Health check: http://127.0.0.1:8000/health

## macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Gemini configuration

Get a Gemini API key from Google AI Studio, then set:

```env
GEMINI_API_KEY=your_key_here
DEMO_MODE=false
WORKOUT_MODEL=gemini-2.5-pro
NUTRITION_MODEL=gemini-2.5-flash
```

Never commit `.env` or expose the API key in frontend JavaScript.

## Test

With the virtual environment active:

```bash
pytest -q
```

You can also test the API interactively at `/docs`.

## Main routes

- `GET /` — user form
- `POST /generate-workout` — create and store a plan
- `POST /submit-feedback` — revise the latest plan for a user
- `GET /view-all-users?token=...` — protected admin dashboard
- `GET /health` — application health/configuration status
- `GET /docs` — FastAPI Swagger UI

## Database

SQLite is created automatically at `data/fitbuddy.db` on first startup. Users and plans persist between restarts.

## Admin dashboard

Set `ADMIN_TOKEN` in `.env`, then open `/view-all-users` and enter that token. This is intentionally a simple project-level access mechanism, matching the supplied documentation. For production deployment, replace it with real authentication, authorization, HTTPS, CSRF protection, and secret management.

## Safety

FitBuddy is an educational wellness application, not a medical device. Generated plans should be reviewed for the user's circumstances. The application prompt explicitly discourages diagnosis, treatment claims, and unsafe rapid weight-loss advice.
