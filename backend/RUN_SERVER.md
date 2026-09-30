# Running FitAI Backend - Complete Instructions

## The Problem (Now Fixed)

```
ValidationError: 2 validation errors for Settings
DATABASE_URL Field required
SECRET_KEY Field required
```

This error is **now resolved**. Follow these exact steps to run the server.

---

## Prerequisites Check

Before proceeding, verify you have:

```bash
# Python 3.12+
python --version
# Expected: Python 3.12.x or higher

# PostgreSQL running
pg_isready
# Expected: accepting connections

# Virtual environment setup
ls backend/venv
# Should exist
```

---

## Step 1: Navigate to Backend Directory

```bash
cd backend
```

Verify you're in the right place:
```bash
pwd
# Should end with: /path/to/fitai/backend
```

---

## Step 2: Activate Virtual Environment

### macOS/Linux
```bash
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal prompt.

### Windows (Command Prompt)
```bash
venv\Scripts\activate.bat
```

### Windows (PowerShell)
```bash
venv\Scripts\Activate.ps1
```

---

## Step 3: Verify .env File Exists and Is Configured

Check the file exists:
```bash
ls .env
# or on Windows:
dir .env
```

View its contents:
```bash
cat .env
# Should contain DATABASE_URL and SECRET_KEY with actual values
```

Expected output:
```env
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_db
SECRET_KEY=dev-secret-key-this-is-only-for-development-please-change-12345678
```

If DATABASE_URL or SECRET_KEY is empty or missing:
```bash
# Recreate from template
cp .env.example .env

# Edit .env to set your database connection:
nano .env  # or use your editor
```

---

## Step 4: Verify PostgreSQL is Running

```bash
pg_isready
# Expected: accepting connections on 127.0.0.1:5432? yes
```

If PostgreSQL is not running:

### macOS
```bash
brew services start postgresql
```

### Linux (Ubuntu/Debian)
```bash
sudo systemctl start postgresql
```

### Windows
- Open Services app
- Find PostgreSQL
- Right-click → Start

### Docker
```bash
docker start fitai-postgres
```

### Verify Database Exists
```bash
psql -l | grep fitai_db
# Should show: fitai_db | postgres | UTF8

# If not, create it:
createdb fitai_db
```

---

## Step 5: Run Verification Script (Recommended)

This checks everything before starting:

```bash
python verify_setup.py
```

Expected output:
```
======================================================================
FitAI Backend Setup Verification
======================================================================

✅ Python 3.12.0 (Required: 3.12+)
✅ Virtual environment activated: /path/to/venv
✅ Installed: 10/10
✅ .env file exists
✅ App Name: FitAI
✅ Version: 1.0.0
✅ Database connection successful

======================================================================
All checks passed! You can now run the server.
======================================================================

Run the server with:
  python main.py

Then open:
  http://localhost:8000/api/docs
```

If any checks fail, follow the troubleshooting in that section before proceeding.

---

## Step 6: Start the Server

```bash
python main.py
```

### Expected Startup Output

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

**If you see this output, the server is running successfully! ✅**

### What If It Still Fails?

See the **Troubleshooting** section below.

---

## Step 7: Test the Server is Working

In a **new terminal** (keep the server running in the original):

```bash
# Health check
curl http://localhost:8000/api/health

# Expected response:
# {"success":true,"message":"Application is healthy","data":{"status":"healthy","version":"1.0.0"}}
```

---

## Step 8: Access API Documentation

Open your browser:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

You should see the interactive API documentation.

---

## Step 9: Test an Endpoint (Optional)

### Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": 1,
    "email": "john@example.com",
    "name": "John Doe"
  }
}
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

Expected response:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

✅ **Server is working!**

---

## Stopping the Server

In the terminal where the server is running:

```bash
Ctrl+C
```

You should see:
```
^C
🛑 Shutting down FitAI Backend...
```

---

## Troubleshooting

### Error: "ValidationError: DATABASE_URL Field required"

**Cause**: DATABASE_URL not set in .env

**Solution**:
```bash
# Check .env exists
ls .env

# If missing:
cp .env.example .env

# Edit .env and set DATABASE_URL:
nano .env
# Add: DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_db

# Restart server:
python main.py
```

---

### Error: "ValidationError: SECRET_KEY Field required"

**Cause**: SECRET_KEY not set or too short (min 32 chars)

**Solution**:
```bash
# Generate new SECRET_KEY:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy the output, then edit .env:
nano .env

# Replace SECRET_KEY with generated value:
# SECRET_KEY=<paste_generated_key_here>

# Restart server:
python main.py
```

---

### Error: "psycopg.OperationalError: could not connect to server"

**Cause**: PostgreSQL not running or wrong connection string

**Solution**:
```bash
# Check if PostgreSQL is running:
pg_isready
# Expected: accepting connections on 127.0.0.1:5432? yes

# If not running, start it:
# macOS:
brew services start postgresql

# Linux:
sudo systemctl start postgresql

# Windows: Use Services app to start PostgreSQL

# Then verify DATABASE_URL in .env matches your setup:
cat .env | grep DATABASE_URL

# Common formats:
# Local (no password): postgresql+psycopg://postgres@localhost:5432/fitai_db
# Local (with password): postgresql+psycopg://postgres:password@localhost:5432/fitai_db
# Docker: postgresql+psycopg://postgres:postgres@localhost:5432/fitai_db

# Restart server:
python main.py
```

---

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Cause**: Dependencies not installed or wrong virtual environment

**Solution**:
```bash
# Verify virtual environment is activated:
which python
# Should show path to venv/bin/python

# If not, activate it:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt

# Restart server:
python main.py
```

---

### Error: "Address already in use"

**Cause**: Port 8000 already in use

**Solution**:
```bash
# Option 1: Use different port
python -m uvicorn app.main:app --port 8001

# Option 2: Kill process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Then restart:
python main.py
```

---

### Error: "Could not connect to server" when testing

**Cause**: Server not running or wrong URL

**Solution**:
```bash
# Check server is running:
# You should see "Uvicorn running on http://0.0.0.0:8000"

# If not, start it in terminal 1:
python main.py

# In terminal 2, test:
curl http://localhost:8000/api/health
```

---

## Configuration Summary

### Current .env Setup

```env
# Database - REQUIRED
# Format: postgresql+psycopg://[user]:[password]@[host]:[port]/[database]
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_db

# JWT - REQUIRED (min 32 characters)
SECRET_KEY=dev-secret-key-this-is-only-for-development-please-change-12345678

# JWT Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=FitAI
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True

# API
API_V1_PREFIX=/api/v1

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000
```

---

## Quick Reference Commands

```bash
# Setup
cd backend
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database info

# Verify
python verify_setup.py

# Run
python main.py

# Test (in new terminal)
curl http://localhost:8000/api/health

# Stop (Ctrl+C in running terminal)
```

---

## Environment Variables Explained

| Variable | Example | Required | Notes |
|----------|---------|----------|-------|
| DATABASE_URL | postgresql+psycopg://postgres@localhost:5432/fitai_db | Yes | PostgreSQL connection string |
| SECRET_KEY | dev-secret-key-... | Yes | Min 32 characters, use for JWT signing |
| ALGORITHM | HS256 | No | JWT algorithm (default: HS256) |
| ACCESS_TOKEN_EXPIRE_MINUTES | 15 | No | Token expiration (default: 15) |
| REFRESH_TOKEN_EXPIRE_DAYS | 7 | No | Refresh token expiration (default: 7) |
| ENVIRONMENT | development | No | Environment mode (default: development) |
| DEBUG | True | No | Debug mode (default: True for dev) |
| CORS_ORIGINS | http://localhost:5173 | No | Comma-separated CORS origins |

---

## API Endpoints Available

```
POST   /api/v1/auth/register              Register user
POST   /api/v1/auth/login                 Login user
POST   /api/v1/auth/refresh               Refresh token
GET    /api/v1/auth/me                    Get current user
POST   /api/v1/auth/logout                Logout

GET    /api/v1/users/me                   Get profile
PUT    /api/v1/users/me                   Update profile
GET    /api/v1/users/{id}                 Get user by ID

POST   /api/v1/workouts                   Log workout
GET    /api/v1/workouts                   Get workouts

POST   /api/v1/calories                   Log calories
GET    /api/v1/calories                   Get calorie entries

POST   /api/v1/water                      Log water
GET    /api/v1/water                      Get water entries

POST   /api/v1/steps                      Log steps
GET    /api/v1/steps                      Get step entries

GET    /                                  API info
GET    /api/health                        Health check
```

---

## Documentation Links

Once the server is running:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

---

## Success Indicators

✅ Server started without errors
✅ Startup shows configuration summary
✅ "Database initialized successfully" message
✅ "Uvicorn running on http://0.0.0.0:8000" message
✅ Health check returns `{"success": true, ...}`
✅ Swagger UI loads at http://localhost:8000/api/docs

---

## Complete Checklist

Before running server:
- [ ] In `backend/` directory
- [ ] Virtual environment activated
- [ ] `.env` file exists with `DATABASE_URL` and `SECRET_KEY`
- [ ] PostgreSQL running (`pg_isready`)
- [ ] Database created (`createdb fitai_db`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)

Running server:
- [ ] Execute `python main.py`
- [ ] See startup messages
- [ ] See "Database initialized successfully"
- [ ] See "Uvicorn running on http://0.0.0.0:8000"

Verification:
- [ ] `curl http://localhost:8000/api/health` returns success
- [ ] Open http://localhost:8000/api/docs in browser
- [ ] See Swagger UI with all endpoints

---

## What's Different After the Fix

### Configuration (app/core/config.py)
- ✅ Now uses `SettingsConfigDict` (Pydantic v2)
- ✅ Environment variables properly loaded from `.env`
- ✅ Better validation with helpful error messages
- ✅ Supports required fields with `default=...`

### Startup (app/main.py)
- ✅ Better error handling for configuration
- ✅ Clear startup messages
- ✅ Database initialization in lifespan context
- ✅ Graceful shutdown logging

### Documentation
- ✅ `.env.example` with complete documentation
- ✅ New `ENVIRONMENT_SETUP.md` guide
- ✅ New `verify_setup.py` verification script
- ✅ New `QUICKSTART.md` and this file

---

## Production Deployment

Before deploying to production:

```bash
# Generate new SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env.production
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql+psycopg://user:pass@prod.db:5432/fitai_prod
SECRET_KEY=<generated_key>
CORS_ORIGINS=https://yourdomain.com
```

---

## Support & Help

If you encounter issues:

1. **Run verification**: `python verify_setup.py`
2. **Check troubleshooting** above
3. **Review .env configuration**: `cat .env`
4. **Check PostgreSQL**: `pg_isready`
5. **Check error messages** - they're now helpful!

---

## Next Steps

1. ✅ Follow steps above to run the server
2. ✅ Test endpoints with Swagger UI
3. ✅ For frontend: Continue to Phase 3
4. ✅ For advanced features: See Phase 4+ documentation

---

**Status: ✅ READY TO RUN**

Execute: `python main.py`

The server will start and be ready for use!
