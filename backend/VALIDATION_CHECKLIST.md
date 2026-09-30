# FitAI Backend - Complete Validation Checklist

## Pre-Startup Validation

Use this checklist to verify everything is ready before running the server.

---

## 1. File Structure Validation

### Core Configuration Files
```bash
# Check these files exist and are updated
ls -la app/core/config.py
ls -la app/main.py
ls -la .env
ls -la .env.example
```

**Expected:**
- ✅ `app/core/config.py` - Contains `model_config = SettingsConfigDict(...)`
- ✅ `app/main.py` - Contains `lifespan` context manager
- ✅ `.env` - Contains `DATABASE_URL` and `SECRET_KEY`
- ✅ `.env.example` - Contains documentation

### Verification Files
```bash
ls -la verify_setup.py
```

**Expected:**
- ✅ `verify_setup.py` exists (automation script)

### Documentation Files
```bash
ls -la ENVIRONMENT_SETUP.md
ls -la QUICKSTART.md
ls -la RUN_SERVER.md
ls -la FIX_SUMMARY.md
```

**Expected:**
- ✅ All documentation files present

---

## 2. Environment Configuration Validation

### Check .env File Content
```bash
# View .env file
cat .env
```

**Expected Output:**
```env
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_db
SECRET_KEY=dev-secret-key-...
ALGORITHM=HS256
ENVIRONMENT=development
DEBUG=True
```

**Validation:**
- ✅ DATABASE_URL is not empty
- ✅ SECRET_KEY is not empty
- ✅ SECRET_KEY is at least 32 characters
- ✅ ALGORITHM is set to HS256
- ✅ ENVIRONMENT is set to development
- ✅ DEBUG is True

### Check .env.example
```bash
grep -c "DATABASE_URL" .env.example
```

**Expected:**
- ✅ Contains DATABASE_URL with example
- ✅ Contains SECRET_KEY with instructions
- ✅ Contains 60+ lines of documentation

---

## 3. Configuration File Validation

### Check config.py Uses Pydantic v2
```bash
grep "SettingsConfigDict" app/core/config.py
```

**Expected:**
```
model_config = SettingsConfigDict(
```

✅ Shows Pydantic v2 syntax is being used

### Check No Old Pydantic v1 Syntax
```bash
grep -A 3 "class Config:" app/core/config.py
```

**Expected:**
- ✅ No `class Config:` with `env_file` in config.py
- ✅ SettingsConfigDict is used instead

### Check Field Validation
```bash
grep "default=\.\.\." app/core/config.py | head -2
```

**Expected:**
- ✅ DATABASE_URL and SECRET_KEY marked as required
- ✅ Using `Field(default=...)` syntax

---

## 4. Database Validation

### Check PostgreSQL Running
```bash
pg_isready
```

**Expected Output:**
```
accepting connections on 127.0.0.1:5432? yes
```

✅ PostgreSQL is running

### Check Database Exists
```bash
psql -l | grep fitai_db
```

**Expected:**
```
 fitai_db | postgres | UTF8 | ...
```

✅ Database exists

### Check Connection String Format
```bash
grep "DATABASE_URL=" .env
```

**Expected Formats:**
```
postgresql+psycopg://postgres@localhost:5432/fitai_db          (no password)
postgresql+psycopg://user:password@localhost:5432/fitai_db     (with password)
postgresql+psycopg://postgres:postgres@localhost:5432/fitai_db (docker)
```

✅ DATABASE_URL matches one of the valid formats

---

## 5. Dependencies Validation

### Check Python Version
```bash
python --version
```

**Expected:**
```
Python 3.12.0 (or higher)
```

✅ Python 3.12+ installed

### Check Virtual Environment Activated
```bash
which python
```

**Expected:**
```
/path/to/venv/bin/python
```

✅ Virtual environment is active

### Check Required Packages
```bash
python -c "import fastapi, pydantic_settings, sqlalchemy, psycopg; print('All imports successful')"
```

**Expected:**
```
All imports successful
```

✅ All dependencies installed

### List Installed Packages
```bash
pip list | grep -E "fastapi|pydantic|sqlalchemy|psycopg"
```

**Expected:**
- ✅ fastapi 0.104.1 or higher
- ✅ pydantic 2.5.0 or higher
- ✅ pydantic-settings 2.1.0 or higher
- ✅ sqlalchemy 2.0.23 or higher
- ✅ psycopg 3.17.0 or higher

---

## 6. Startup Simulation Validation

### Run Verification Script
```bash
python verify_setup.py
```

**Expected Output:**
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
```

✅ All checks pass

### Test Configuration Loading
```bash
python -c "from app.core.config import settings; print(f'✅ Config loaded: {settings.APP_NAME} v{settings.APP_VERSION}')"
```

**Expected:**
```
✅ Config loaded: FitAI v1.0.0
```

✅ Configuration loads successfully

---

## 7. API Startup Validation

### Start Server
```bash
python main.py &
sleep 5
```

**Expected Output:**
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

✅ Server starts without errors

### Test Health Endpoint
```bash
curl http://localhost:8000/api/health
```

**Expected:**
```json
{
  "success": true,
  "message": "Application is healthy",
  "data": {
    "status": "healthy",
    "version": "1.0.0"
  }
}
```

✅ API is responding

### Test Root Endpoint
```bash
curl http://localhost:8000/
```

**Expected:**
```json
{
  "app": "FitAI",
  "version": "1.0.0",
  "environment": "development",
  "status": "running",
  "docs": "/api/docs",
  "redoc": "/api/redoc",
  "api": "/api/v1"
}
```

✅ API provides information

---

## 8. Documentation Validation

### Check All Documentation Files
```bash
for file in ENVIRONMENT_SETUP.md QUICKSTART.md RUN_SERVER.md FIX_SUMMARY.md; do
  if [ -f "$file" ]; then
    echo "✅ $file exists"
  else
    echo "❌ $file missing"
  fi
done
```

**Expected:**
```
✅ ENVIRONMENT_SETUP.md exists
✅ QUICKSTART.md exists
✅ RUN_SERVER.md exists
✅ FIX_SUMMARY.md exists
```

### Verify Documentation Content
```bash
grep -l "DATABASE_URL" ENVIRONMENT_SETUP.md QUICKSTART.md RUN_SERVER.md
```

**Expected:**
- ✅ Documentation files contain setup instructions
- ✅ DATABASE_URL examples provided
- ✅ Troubleshooting sections included

---

## 9. Error Handling Validation

### Test Invalid Configuration
```bash
# Temporarily rename .env
mv .env .env.bak

# Try to load config
python -c "from app.core.config import settings" 2>&1 | head -5

# Restore .env
mv .env.bak .env
```

**Expected:**
- ✅ Clear error message about DATABASE_URL being required
- ✅ Helpful troubleshooting steps shown
- ✅ No cryptic validation errors

### Test Validation Messages
```bash
grep -A 5 "def validate_database_url" app/core/config.py
```

**Expected:**
- ✅ Custom validation for DATABASE_URL
- ✅ Helpful error messages
- ✅ Format examples provided

---

## 10. Security Validation

### Check SECRET_KEY Length
```bash
grep "SECRET_KEY=" .env | awk -F'=' '{print length($2)}'
```

**Expected:**
```
80 (or higher)
```

✅ SECRET_KEY is at least 32 characters (min for security)

### Check No Hardcoded Secrets
```bash
grep -r "SECRET_KEY\|DATABASE_URL" app/ | grep -v "Field\|description\|env_file" | head -5
```

**Expected:**
- ✅ No hardcoded database URLs
- ✅ No hardcoded secret keys
- ✅ All secrets from environment variables

### Check .gitignore
```bash
cat .gitignore | grep ".env"
```

**Expected:**
```
.env
```

✅ .env file is in gitignore

---

## 11. API Endpoints Validation

### Register Endpoint
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123!"
  }' 2>/dev/null | jq '.success'
```

**Expected:**
```
true
```

✅ Register endpoint works

### Login Endpoint
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }' 2>/dev/null | jq '.data.access_token' | wc -c
```

**Expected:**
```
> 100  (JWT token is long)
```

✅ Login endpoint returns token

---

## 12. Complete Validation Summary

Create a validation report:

```bash
#!/bin/bash
echo "=== FitAI Backend Validation Report ==="
echo "Date: $(date)"
echo ""

echo "1. Files:"
[ -f app/core/config.py ] && echo "✅ config.py" || echo "❌ config.py"
[ -f app/main.py ] && echo "✅ main.py" || echo "❌ main.py"
[ -f .env ] && echo "✅ .env" || echo "❌ .env"
[ -f verify_setup.py ] && echo "✅ verify_setup.py" || echo "❌ verify_setup.py"

echo ""
echo "2. Configuration:"
grep -q "SettingsConfigDict" app/core/config.py && echo "✅ Pydantic v2" || echo "❌ Pydantic v1"
grep -q "DATABASE_URL" .env && echo "✅ DATABASE_URL set" || echo "❌ DATABASE_URL missing"
grep -q "SECRET_KEY" .env && echo "✅ SECRET_KEY set" || echo "❌ SECRET_KEY missing"

echo ""
echo "3. Database:"
pg_isready -q && echo "✅ PostgreSQL running" || echo "❌ PostgreSQL not running"

echo ""
echo "4. Python:"
python --version | grep -q "3.12" && echo "✅ Python 3.12+" || echo "❌ Python < 3.12"

echo ""
echo "5. Verification:"
python verify_setup.py 2>&1 | grep -q "All checks passed" && echo "✅ All checks passed" || echo "❌ Some checks failed"
```

Save as `validate.sh` and run:
```bash
chmod +x validate.sh
./validate.sh
```

---

## Quick Validation Commands

Copy and paste to validate everything:

```bash
# Quick validation
echo "1. Checking files..."
ls -q app/core/config.py app/main.py .env verify_setup.py >/dev/null && echo "✅ All files present" || echo "❌ Missing files"

echo "2. Checking configuration..."
grep -q "SettingsConfigDict" app/core/config.py && echo "✅ Pydantic v2 config" || echo "❌ Wrong config"

echo "3. Checking database..."
pg_isready -q && echo "✅ PostgreSQL running" || echo "❌ PostgreSQL down"

echo "4. Checking Python..."
python --version | grep -q "3.12" && echo "✅ Python 3.12+" || echo "❌ Wrong Python"

echo "5. Running verification..."
python verify_setup.py 2>&1 | tail -3
```

---

## Validation Pass/Fail Criteria

### PASS (Ready to Run) ✅
- ✅ All files present and updated
- ✅ Configuration uses Pydantic v2
- ✅ .env file has DATABASE_URL and SECRET_KEY
- ✅ PostgreSQL running and database exists
- ✅ Python 3.12+ with all dependencies
- ✅ `python verify_setup.py` shows all checks passed
- ✅ Server starts without errors
- ✅ Health endpoint returns success

### FAIL (Not Ready) ❌
- ❌ Missing configuration files
- ❌ Using old Pydantic v1 syntax
- ❌ .env missing or incomplete
- ❌ PostgreSQL not running
- ❌ Wrong Python version
- ❌ Verification script fails
- ❌ Server won't start
- ❌ Endpoints not responding

---

## Post-Validation Steps

If all validations PASS:

1. ✅ Start server: `python main.py`
2. ✅ Open API docs: http://localhost:8000/api/docs
3. ✅ Test endpoints with Swagger UI
4. ✅ Proceed to Phase 3 (Frontend)

If any validation FAILS:

1. ❌ Check error messages carefully
2. ❌ Review troubleshooting sections
3. ❌ Run `python verify_setup.py` for diagnostics
4. ❌ Check relevant documentation file
5. ❌ Fix the issue and re-validate

---

## Validation Automation Script

For CI/CD pipelines, use `verify_setup.py`:

```bash
cd backend
python verify_setup.py
# Exit code 0 = all checks passed
# Exit code 1 = some checks failed
```

---

## Expected Validation Output

When everything is valid:

```
======================================================================
FitAI Backend Setup Verification
======================================================================

✅ Python 3.12.0 (Required: 3.12+)
✅ Virtual environment activated: /Users/you/fitai/backend/venv
✅ Installed: 10/10
  ✅ fastapi
  ✅ uvicorn
  ✅ sqlalchemy
  ✅ psycopg
  ✅ pydantic
  ✅ pydantic_settings
  ✅ passlib
  ✅ python_jose
  ✅ alembic
  ✅ python_dotenv
✅ .env file exists
✅ DATABASE_URL is set
✅ SECRET_KEY is set
✅ App Name: FitAI
✅ Version: 1.0.0
✅ Environment: development
✅ Debug: True
✅ Database connection successful

======================================================================
All 6/6 checks passed! You can now run the server.
======================================================================

Run the server with:
  python main.py

Then open:
  http://localhost:8000/api/docs
```

---

## Troubleshooting Validation Failures

| Check | If Failed | Solution |
|-------|-----------|----------|
| Files | Missing | Run: `git checkout` or copy from backup |
| Config | Pydantic v1 | Run: `git checkout app/core/config.py` |
| .env | Missing | Run: `cp .env.example .env` |
| Database | Not running | Start PostgreSQL service |
| Python | < 3.12 | Install Python 3.12+ |
| Imports | Failed | Run: `pip install -r requirements.txt` |
| Connection | Failed | Check DATABASE_URL in .env |
| Verification | Failed | Read error message and fix |

---

## Validation Checklist (Printable)

```
Pre-Startup Validation Checklist
=================================
Date: _______________
Validator: _______________

File Validation
- [ ] app/core/config.py exists
- [ ] app/main.py exists
- [ ] .env exists
- [ ] verify_setup.py exists

Configuration Validation
- [ ] config.py uses SettingsConfigDict
- [ ] .env has DATABASE_URL
- [ ] .env has SECRET_KEY (32+ chars)
- [ ] No old Pydantic v1 syntax

Database Validation
- [ ] PostgreSQL running (pg_isready)
- [ ] Database exists (psql -l)
- [ ] Connection string valid

Dependencies Validation
- [ ] Python 3.12+
- [ ] Virtual environment active
- [ ] All packages installed

Startup Validation
- [ ] python verify_setup.py passes
- [ ] Configuration loads successfully
- [ ] Server starts without errors
- [ ] Health endpoint responds

Ready to Run
- [ ] All checks above passed
- [ ] No warnings or errors
- [ ] Documentation reviewed

Status: ☐ PASS  ☐ FAIL
```

---

## Sign-Off

When all validation checks pass, the backend is ready to run:

```
✅ Configuration: VALID
✅ Database: READY
✅ Dependencies: INSTALLED
✅ Startup: SUCCESS
✅ API: RESPONDING

STATUS: READY TO DEPLOY
```

---

**Validation Complete** - Backend is production-ready!

Execute: `python main.py`
