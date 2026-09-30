# Quick Start Guide

## Prerequisites
- Python 3.12+
- pip (Python package manager)

## Setup (First Time)

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Setup
```bash
python verify_setup.py
```

---

## Running the Server

### Start Development Server
```bash
python main.py
```

**Expected Output:**
```
======================================================================
Starting FitAI Backend v1.0.0
======================================================================
Environment: development
Debug: True
API Prefix: /api/v1
Database: SQLite (Local)
CORS Origins: 3 configured
======================================================================

[OK] Database initialized successfully

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Test the Server

In a new terminal (with venv activated):

**Health Check:**
```bash
curl http://127.0.0.1:8000/api/health
```

**API Documentation:**
- Swagger UI: http://127.0.0.1:8000/api/docs
- ReDoc: http://127.0.0.1:8000/api/redoc

---

## Database

### Current Setup
- **Type:** SQLite (file-based)
- **Location:** `backend/fitai.db`
- **No Setup Required:** Database and tables created automatically

### Switch to PostgreSQL

1. Update `.env`:
   ```
   DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/fitai_db
   ```

2. Restart the server:
   ```bash
   python main.py
   ```

---

## Environment Variables

### Required
- `DATABASE_URL` - Database connection string (SQLite or PostgreSQL)
- `SECRET_KEY` - JWT signing key (min 32 characters)

### Optional (with defaults)
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry in minutes (default: 15)
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token expiry in days (default: 7)
- `DEBUG` - Enable debug mode (default: True for development)
- `ENVIRONMENT` - Environment type (default: development)

See `.env` file for all configuration options.

---

## Common Commands

### Run Tests (when test suite is ready)
```bash
pytest
```

### Format Code
```bash
black app/
```

### Check Code Style
```bash
flake8 app/
```

### Type Checking
```bash
mypy app/
```

---

## Troubleshooting

### "DATABASE_URL must start with..."
**Solution:** Ensure `.env` file exists with valid DATABASE_URL:
```bash
cp .env.example .env
```

### "SECRET_KEY must be at least 32 characters"
**Solution:** Generate new key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### "Address already in use"
**Solution:** Another process is using port 8000. Either:
- Stop the other process
- Change port in code (currently hardcoded to 8000)

### Server hangs on startup
**Solution:** Check that PostgreSQL is running if using PostgreSQL, or verify SQLite database permissions.

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/              # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── workouts.py
│   │   │   ├── calories.py
│   │   │   ├── water.py
│   │   │   ├── steps.py
│   │   │   └── __init__.py
│   │   ├── dependencies.py  # Shared dependencies
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py        # Configuration & settings
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── security.py      # JWT & auth utilities
│   │   └── __init__.py
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── fitness.py
│   │   └── __init__.py
│   ├── schemas/             # Pydantic request/response models
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── fitness.py
│   │   └── __init__.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   └── __init__.py
│   ├── utils/               # Helper functions
│   │   ├── helpers.py
│   │   ├── validators.py
│   │   └── __init__.py
│   ├── main.py              # FastAPI application
│   └── __init__.py
├── migrations/              # Alembic migrations
├── .env                     # Local environment (DO NOT COMMIT)
├── .env.example             # Example environment
├── requirements.txt         # Python dependencies
├── fitai.db                 # SQLite database (created on first run)
└── main.py                  # Entry point

```

---

## Next Steps

1. ✓ Server is running
2. Next: Implement API endpoints
3. Then: Add database migrations
4. Finally: Deploy to production

---

## Need Help?

- Check `.env` for configuration issues
- Read `SQLITE_MIGRATION_COMPLETE.md` for detailed setup info
- Check `API_DOCUMENTATION.md` for endpoint details
- View live docs at http://127.0.0.1:8000/api/docs (after starting server)

---

**Status:** Ready to develop! 🚀
