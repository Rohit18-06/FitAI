# FitAI Backend - Quick Start (After Fix)

## 30-Second Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create environment file
cp .env.example .env

# 3. Edit .env - set your PostgreSQL database
# (Already has a working development config - just verify DATABASE_URL is correct)

# 4. Verify setup
python verify_setup.py

# 5. Run server
python main.py

# 6. Test it
curl http://localhost:8000/api/health
```

---

## Detailed Steps

### Step 1: Create .env File

```bash
cd backend
cp .env.example .env
```

File is now created at `backend/.env`

### Step 2: Configure Database

**Option A: Local PostgreSQL (Default)**

If you have PostgreSQL running locally on port 5432 with default `postgres` user:

```bash
# Already set in .env:
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_db
```

Just create the database:
```bash
createdb fitai_db
```

**Option B: PostgreSQL with Password**

Edit `.env`:
```env
DATABASE_URL=postgresql+psycopg://postgres:yourpassword@localhost:5432/fitai_db
```

**Option C: Docker PostgreSQL**

Start PostgreSQL:
```bash
docker run --name fitai-postgres \
  -e POSTGRES_DB=fitai_db \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15
```

Edit `.env`:
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/fitai_db
```

### Step 3: Set SECRET_KEY

The `.env` has a development SECRET_KEY already. For production, generate a new one:

```bash
# Generate new SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy the output and update .env
SECRET_KEY=<paste_here>
```

### Step 4: Verify Setup

Run the verification script:

```bash
python verify_setup.py
```

You should see:
```
✅ Python 3.12+ 
✅ Virtual environment activated
✅ All dependencies installed
✅ .env file exists
✅ Configuration loaded
✅ Database connection successful
```

### Step 5: Run Server

```bash
python main.py
```

You should see:
```
======================================================================
Starting FitAI Backend v1.0.0
======================================================================
Environment: development
Debug: True
API Prefix: /api/v1
Database: localhost:5432/fitai_db
CORS Origins: 3 configured
======================================================================

✅ Database initialized successfully

INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 6: Test the API

```bash
# Health check
curl http://localhost:8000/api/health

# Expected response:
# {"success":true,"message":"Application is healthy","data":{"status":"healthy","version":"1.0.0"}}
```

### Step 7: Access Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## Complete .env Template

```env
# ============================================================================
# REQUIRED - Must be set
# ============================================================================

# PostgreSQL database URL
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_db

# JWT secret key (min 32 characters)
SECRET_KEY=dev-secret-key-this-is-only-for-development-please-change-12345678

# ============================================================================
# OPTIONAL - Have sensible defaults
# ============================================================================

# JWT settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application settings
APP_NAME=FitAI
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True

# API settings
API_V1_PREFIX=/api/v1

# CORS settings (comma-separated origins)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000
```

---

## File Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # ✅ FIXED: Pydantic v2 configuration
│   │   ├── database.py
│   │   ├── security.py
│   │   └── __init__.py
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── main.py                # ✅ FIXED: Better startup/error handling
│   └── __init__.py
├── migrations/
├── .env                       # ✅ NEW: Development configuration
├── .env.example               # ✅ UPDATED: Better documentation
├── verify_setup.py            # ✅ NEW: Setup verification
├── requirements.txt
├── alembic.ini
├── main.py
├── README.md
├── SETUP_GUIDE.md
├── ENVIRONMENT_SETUP.md       # ✅ NEW: Detailed env guide
├── FIX_SUMMARY.md             # ✅ NEW: Fix explanation
├── QUICKSTART.md              # ✅ NEW: This file
└── .gitignore
```

---

## What Was Fixed

### ✅ Configuration Loading
- `app/core/config.py` now uses `SettingsConfigDict` (Pydantic v2)
- `.env` file is properly loaded
- Environment variables are correctly parsed

### ✅ Better Error Messages
- Helpful startup messages
- Clear validation errors
- Troubleshooting steps included

### ✅ Startup Improvements
- `app/main.py` has better error handling
- Database initialization in lifespan context
- Clear startup logging

### ✅ Documentation
- `.env.example` has complete documentation
- New `ENVIRONMENT_SETUP.md` guide
- New `verify_setup.py` verification script
- This quick start guide

---

## Common Issues

### "DATABASE_URL not found"
```bash
# Check .env exists
ls backend/.env

# Check DATABASE_URL is set
grep DATABASE_URL backend/.env

# If not, edit .env and add:
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_db
```

### "Connection refused" 
```bash
# PostgreSQL not running. Start it:

# macOS:
brew services start postgresql

# Linux (Ubuntu):
sudo systemctl start postgresql

# Windows: Start PostgreSQL service in Services app

# Docker:
docker start fitai-postgres
```

### "SECRET_KEY too short"
```bash
# Generate a new one:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy to .env:
SECRET_KEY=<paste_here>
```

### "Module not found"
```bash
# Install dependencies:
pip install -r requirements.txt

# Verify:
python verify_setup.py
```

---

## Testing Endpoints

### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### Get Current User
```bash
# Replace TOKEN with access_token from login response
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer TOKEN"
```

---

## Verification Checklist

Before running the server:

- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] In backend directory: `pwd` should end with `/backend`
- [ ] .env file exists: `ls .env`
- [ ] DATABASE_URL is set: `grep DATABASE_URL .env`
- [ ] SECRET_KEY is set: `grep SECRET_KEY .env`
- [ ] PostgreSQL running: `pg_isready`
- [ ] Database exists: `psql -l | grep fitai_db`
- [ ] Dependencies installed: `python -c "import fastapi"`

---

## Commands Reference

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env

# Verify
python verify_setup.py

# Run
python main.py

# Test
curl http://localhost:8000/api/health

# View logs
# Output appears in the terminal running python main.py

# Stop
# Press Ctrl+C in terminal running python main.py
```

---

## Next Steps

1. ✅ Setup .env file
2. ✅ Run `python verify_setup.py`
3. ✅ Run `python main.py`
4. ✅ Open http://localhost:8000/api/docs
5. ✅ Test the API with Swagger UI

---

## Documentation

- **Full Setup Guide**: `SETUP_GUIDE.md`
- **Environment Guide**: `ENVIRONMENT_SETUP.md`
- **Fix Details**: `FIX_SUMMARY.md`
- **API Reference**: `API_DOCUMENTATION.md`
- **Project Info**: `README.md`

---

## Support

If you encounter issues:

1. Run `python verify_setup.py` to diagnose
2. Check `ENVIRONMENT_SETUP.md` troubleshooting
3. Review error message - they're helpful now!
4. Verify `.env` configuration
5. Check PostgreSQL is running

---

## Status

✅ **Backend is now fully configured and ready to run!**

Start the server with: `python main.py`

Access API at: http://localhost:8000/api/docs
