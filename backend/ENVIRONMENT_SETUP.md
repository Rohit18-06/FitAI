# FitAI Backend - Environment Setup & Configuration

## Problem: ValidationError on Startup

When you see this error:
```
ValidationError: 2 validation errors for Settings
DATABASE_URL Field required
SECRET_KEY Field required
```

This means the application cannot find the required configuration variables.

---

## Solution: Complete Setup Guide

### Step 1: Create .env File

The `.env` file stores sensitive configuration variables. It must be in the `backend/` directory.

```bash
cd backend
cp .env.example .env
```

### Step 2: Edit .env File

Open `backend/.env` and configure the required variables:

**REQUIRED VARIABLES:**

1. **DATABASE_URL** - PostgreSQL connection string
2. **SECRET_KEY** - JWT signing key (min 32 characters)

**Example .env file:**

```env
# Database - REQUIRED
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_db

# JWT Secret - REQUIRED  
SECRET_KEY=your-generated-secret-key-here-must-be-32-chars

# Other settings (optional - have defaults)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_NAME=FitAI
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True
API_V1_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## How to Configure Each Variable

### 1. DATABASE_URL (REQUIRED)

PostgreSQL connection string in format:
```
postgresql+psycopg://[username]:[password]@[host]:[port]/[database]
```

#### Local PostgreSQL (Linux/macOS)
```env
# Without password
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_db

# With password
DATABASE_URL=postgresql+psycopg://postgres:mypassword@localhost:5432/fitai_db
```

#### Windows PostgreSQL
```env
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/fitai_db
```

#### Docker PostgreSQL
```env
DATABASE_URL=postgresql+psycopg://fitai_user:fitai_password@db:5432/fitai_db
```

#### Remote Database
```env
DATABASE_URL=postgresql+psycopg://user:password@production.db.host:5432/fitai_prod
```

---

### 2. SECRET_KEY (REQUIRED)

JWT signing key - must be at least 32 characters long and cryptographically secure.

#### Generate a new SECRET_KEY:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Output example:
# G9_K2p-qL3m_8N5_vB7_xC2_dE4_fR6_sT8_uV9_wX0

# Copy the output and paste into .env
SECRET_KEY=G9_K2p-qL3m_8N5_vB7_xC2_dE4_fR6_sT8_uV9_wX0
```

**For development only**, you can use:
```env
SECRET_KEY=dev-secret-key-this-is-only-for-development-please-change-12345678
```

**For production**, always generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Database Setup

Before running the app, ensure PostgreSQL database exists:

### Option 1: Using psql (Command Line)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE fitai_db;

# Verify it was created
\l

# Exit
\q
```

### Option 2: Using pgAdmin (GUI)

1. Open pgAdmin
2. Right-click "Databases"
3. Click "Create" → "Database"
4. Name: `fitai_db`
5. Click "Save"

### Option 3: Using Docker

```bash
docker run --name fitai-postgres \
  -e POSTGRES_DB=fitai_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15
```

Then set in .env:
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/fitai_db
```

---

## Verify Configuration

### Check .env File Exists

```bash
# In backend directory
ls -la .env

# Should see:
# -rw-r--r-- 1 user group 850 Jan 15 10:30 .env
```

### Check Variables Are Set

```bash
# View DATABASE_URL
grep DATABASE_URL .env

# View SECRET_KEY
grep SECRET_KEY .env
```

### Test Database Connection

```bash
# Using psql
psql DATABASE_URL

# Should connect successfully and show:
# fitai_db=#
```

---

## Why This Error Occurs

The error occurs because:

1. **No .env file exists** - The application can't find environment variables
2. **Required variables missing** - DATABASE_URL or SECRET_KEY not set
3. **Invalid variable format** - Variables don't match expected format
4. **Wrong Pydantic configuration** - Settings not using ConfigDict for Pydantic v2

### What Was Fixed

The configuration was updated to use Pydantic v2's `SettingsConfigDict`:

```python
# OLD (Pydantic v1 style - BROKEN)
class Config:
    env_file = ".env"

# NEW (Pydantic v2 style - FIXED)
model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=True,
)
```

---

## Running the Server

Once .env is configured:

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

### Expected Output

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

### Verify Server is Running

Open in browser:
- http://localhost:8000/api/docs (Swagger UI)
- http://localhost:8000/api/redoc (ReDoc)
- http://localhost:8000/api/health (Health check)

---

## Troubleshooting

### Error: "psycopg.OperationalError: could not connect to server"

**Cause:** PostgreSQL is not running or DATABASE_URL is wrong

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# If not running, start it
# macOS:
brew services start postgresql

# Linux (Ubuntu):
sudo systemctl start postgresql

# Windows: Start PostgreSQL service in Services app

# Verify DATABASE_URL in .env
grep DATABASE_URL backend/.env
```

### Error: "Field 'DATABASE_URL' required"

**Cause:** DATABASE_URL not set in .env

**Solution:**
```bash
# Check if .env exists
ls -la backend/.env

# If not, create it
cd backend
cp .env.example .env

# Edit and set DATABASE_URL
nano .env  # or use your editor
```

### Error: "Field 'SECRET_KEY' required"

**Cause:** SECRET_KEY not set or too short

**Solution:**
```bash
# Generate a new SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
echo "SECRET_KEY=<generated_key>" >> backend/.env
```

### Error: "Validation error in SECRET_KEY"

**Cause:** SECRET_KEY is less than 32 characters

**Solution:**
Generate a new key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy to .env (replace the old one)

---

## Environment Variables Reference

| Variable | Type | Required | Default | Example |
|----------|------|----------|---------|---------|
| DATABASE_URL | string | Yes | - | postgresql+psycopg://postgres@localhost:5432/fitai_db |
| SECRET_KEY | string | Yes | - | G9_K2p-qL3m_8N5_vB7_xC2_dE4_fR6_sT8 |
| ALGORITHM | string | No | HS256 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | int | No | 15 | 15 |
| REFRESH_TOKEN_EXPIRE_DAYS | int | No | 7 | 7 |
| APP_NAME | string | No | FitAI | FitAI |
| APP_VERSION | string | No | 1.0.0 | 1.0.0 |
| ENVIRONMENT | string | No | development | development |
| DEBUG | bool | No | True | True |
| API_V1_PREFIX | string | No | /api/v1 | /api/v1 |
| CORS_ORIGINS | string | No | localhost | http://localhost:5173 |

---

## Multiple Environments

### Development (.env)
```env
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_dev
SECRET_KEY=dev-secret-key-...
```

### Staging (.env.staging)
```env
ENVIRONMENT=staging
DEBUG=False
DATABASE_URL=postgresql+psycopg://user:pass@staging.db:5432/fitai_staging
SECRET_KEY=<secure-key>
```

### Production (.env.production)
```env
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql+psycopg://user:pass@prod.db:5432/fitai_prod
SECRET_KEY=<secure-key>
CORS_ORIGINS=https://fitai.com,https://app.fitai.com
```

Load with:
```bash
# Load staging config
source .env.staging && python main.py
```

---

## Security Best Practices

✅ **DO:**
- Generate secure SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Use strong database passwords
- Never commit .env to git (it's in .gitignore)
- Use different keys for dev/staging/production
- Rotate keys periodically
- Use environment-specific configurations

❌ **DON'T:**
- Hardcode secrets in code
- Use weak SECRET_KEY (less than 32 chars)
- Commit .env file to version control
- Reuse production key in development
- Share SECRET_KEY in plaintext
- Use same password for all environments

---

## Next Steps

1. ✅ Create and configure .env file
2. ✅ Verify PostgreSQL is running
3. ✅ Run `python main.py`
4. ✅ Open http://localhost:8000/api/docs
5. ✅ Test endpoints

---

## Getting Help

If you're still having issues:

1. Check this file's troubleshooting section
2. Verify all variables in .env are set
3. Check PostgreSQL is running: `pg_isready`
4. Review startup output for specific error messages
5. Check that virtual environment is activated
6. Ensure you're in the `backend/` directory

---

## References

- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- PostgreSQL: https://www.postgresql.org/docs/
- FastAPI: https://fastapi.tiangolo.com/
- JWT: https://jwt.io/
