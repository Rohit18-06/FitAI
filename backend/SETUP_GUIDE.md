# FitAI Backend - Complete Setup Guide

Step-by-step guide to set up and run the FitAI backend application.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+**: [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 12+**: [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git**: [Download Git](https://git-scm.com/)
- **Pip**: Usually comes with Python

Verify installations:

```bash
python --version
psql --version
git --version
pip --version
```

## Step 1: Clone or Navigate to Project

```bash
# If cloning from repository
git clone <repository-url>
cd fitai/backend

# If already in the project
cd backend
```

## Step 2: Create Virtual Environment

### On Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### On macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

## Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- fastapi
- uvicorn
- sqlalchemy
- psycopg (PostgreSQL driver)
- pydantic
- python-jose (JWT)
- passlib (bcrypt)
- alembic
- python-dotenv

## Step 5: Create PostgreSQL Database

### Option A: Using psql (Command Line)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE fitai_db;

# Create user (optional)
CREATE USER fitai_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE fitai_db TO fitai_user;

# Exit psql
\q
```

### Option B: Using pgAdmin (GUI)

1. Open pgAdmin
2. Right-click on "Databases"
3. Click "Create" → "Database"
4. Name it `fitai_db`
5. Click "Save"

### Option C: Using Docker

```bash
docker run --name fitai-postgres \
  -e POSTGRES_DB=fitai_db \
  -e POSTGRES_USER=fitai_user \
  -e POSTGRES_PASSWORD=your_secure_password \
  -p 5432:5432 \
  -d postgres:15
```

## Step 6: Configure Environment Variables

Create `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database Configuration
# For local PostgreSQL without password:
DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/fitai_db

# For PostgreSQL with username and password:
DATABASE_URL=postgresql+psycopg://fitai_user:your_secure_password@localhost:5432/fitai_db

# For Docker PostgreSQL:
DATABASE_URL=postgresql+psycopg://fitai_user:your_secure_password@db:5432/fitai_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-at-least-32-characters-long-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Configuration
APP_NAME=FitAI
APP_VERSION=1.0.0
ENVIRONMENT=development

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8000

# API Documentation
API_V1_PREFIX=/api/v1
```

### Generate Secure SECRET_KEY

```python
# In Python interactive shell
import secrets
print(secrets.token_urlsafe(32))
```

## Step 7: Initialize Database

The application will automatically create tables on first run. You can also manually initialize:

### Automatic Initialization (First Run)

Just run the application (Step 8), and tables will be created automatically.

### Using Alembic (Recommended for Production)

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration - create all tables"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

## Step 8: Run the Application

### Development Mode (with auto-reload)

```bash
# Using Uvicorn directly
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the provided entry point
python main.py
```

### Production Mode

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Expected Output

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Step 9: Test the Application

### Access API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Test Health Endpoint

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "success": true,
  "message": "Application is healthy",
  "data": {"status": "healthy"}
}
```

### Test Registration

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "age": 30,
    "gender": "M",
    "height_cm": 180,
    "weight_kg": 75
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

### Test Login

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

### Test Protected Endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Replace `YOUR_ACCESS_TOKEN` with the token from login response.

## Troubleshooting

### Issue: "psycopg.OperationalError: could not connect to server"

**Solution:**
1. Verify PostgreSQL is running:
   ```bash
   # Windows
   Get-Service PostgreSQL*
   
   # macOS/Linux
   brew services list | grep postgres
   ```

2. Check DATABASE_URL in `.env`:
   ```bash
   # Test connection
   psql DATABASE_URL
   ```

3. Restart PostgreSQL service

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution:**
1. Verify you're in the correct directory:
   ```bash
   pwd  # Should end with /backend
   ```

2. Verify virtual environment is activated:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

### Issue: "Pydantic validation error"

**Solution:**
1. Check `.env` file has all required variables
2. Verify data types (DATABASE_URL should be a valid PostgreSQL URL)
3. Restart the application

### Issue: "JWT token invalid"

**Solution:**
1. Verify SECRET_KEY is set in `.env`
2. Ensure the same SECRET_KEY is used across requests
3. Token expiration: get a new token via login

### Issue: CORS errors in frontend

**Solution:**
Add frontend URL to CORS_ORIGINS in `.env`:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourdomain.com
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
python -m uvicorn app.main:app --port 8001

# Or kill the process using port 8000
# Windows: taskkill /PID <PID> /F
# macOS/Linux: lsof -ti:8000 | xargs kill -9
```

## Common Commands

### Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Deactivate Virtual Environment

```bash
deactivate
```

### Install/Update Requirements

```bash
pip install -r requirements.txt
pip install --upgrade -r requirements.txt
```

### Run Tests

```bash
pytest
pytest -v
pytest tests/test_auth.py
pytest --cov=app
```

### Database Commands

```bash
# Connect to database
psql -U postgres -d fitai_db

# List tables
\dt

# Exit
\q
```

### Alembic Commands

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View history
alembic history

# Current version
alembic current
```

## Development Workflow

1. **Start virtual environment**: `source venv/bin/activate` (or Windows equivalent)
2. **Start PostgreSQL**: Ensure service is running
3. **Run application**: `python main.py`
4. **Access API docs**: http://localhost:8000/api/docs
5. **Make changes** to code
6. **Test with Swagger UI** or curl commands
7. **Commit changes**: `git add . && git commit -m "message"`

## Next Steps

1. ✅ Backend foundation complete
2. ⏳ Phase 3: Frontend Foundation
3. ⏳ Phase 4: Fitness Trackers
4. ⏳ Phase 5: Analytics Dashboard
5. ⏳ Phase 6: AI Features
6. ⏳ Phase 7: Video Analysis
7. ⏳ Phase 8: Reporting

## Support

For issues:
1. Check this guide's troubleshooting section
2. Review API documentation at http://localhost:8000/api/docs
3. Check application logs in terminal
4. Verify environment configuration

## Production Deployment

See `DEPLOYMENT.md` for:
- Render deployment steps
- Environment configuration for production
- Database backup strategies
- Monitoring and logging
- Security checklist
