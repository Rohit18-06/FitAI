# FitAI Backend - Phase 2 Foundation

Production-ready FastAPI backend for the FitAI AI-Powered Fitness Coach application.

## Overview

FitAI Backend provides a robust REST API for fitness tracking, user management, and AI-powered fitness coaching. Built with FastAPI, PostgreSQL, and SQLAlchemy, following clean architecture and SOLID principles.

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL + SQLAlchemy 2.0
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Server**: Uvicorn
- **Python**: 3.12+

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── users.py         # User profile endpoints
│   │   │   ├── workouts.py      # Workout tracking endpoints
│   │   │   ├── calories.py      # Calorie tracking endpoints
│   │   │   ├── water.py         # Water intake endpoints
│   │   │   ├── steps.py         # Step tracking endpoints
│   │   │   └── __init__.py
│   │   ├── dependencies.py      # FastAPI dependencies (JWT verification)
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database setup and session management
│   │   ├── security.py          # JWT and password utilities
│   │   └── __init__.py
│   ├── models/
│   │   ├── user.py              # User model
│   │   ├── fitness.py           # Fitness tracking models
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── auth.py              # Authentication schemas
│   │   ├── user.py              # User schemas
│   │   ├── fitness.py           # Fitness schemas
│   │   └── __init__.py
│   ├── services/
│   │   ├── auth_service.py      # Authentication business logic
│   │   ├── user_service.py      # User management business logic
│   │   └── __init__.py
│   ├── utils/
│   │   ├── validators.py        # Input validation utilities
│   │   ├── helpers.py           # Helper functions
│   │   └── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   └── __init__.py
├── migrations/
│   ├── env.py                   # Alembic environment configuration
│   ├── script.py.mako           # Alembic migration template
│   ├── versions/                # Migration files directory
│   └── __init__.py
├── tests/
│   ├── conftest.py              # Pytest configuration
│   ├── test_auth.py             # Authentication tests
│   ├── test_fitness.py          # Fitness tracking tests
│   └── __init__.py
├── .env.example                 # Environment variables template
├── .env                         # Environment variables (DO NOT COMMIT)
├── requirements.txt             # Python dependencies
├── alembic.ini                  # Alembic configuration
├── main.py                      # Entry point for running the server
└── README.md                    # This file
```

## Installation

### Prerequisites

- Python 3.12+
- PostgreSQL 12+
- pip or conda

### 1. Clone and Setup

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/fitai_db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_NAME=FitAI
APP_VERSION=1.0.0
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4. Database Setup

Create PostgreSQL database:

```bash
# Using psql
createdb fitai_db

# Or using PostgreSQL GUI tool
```

Run migrations:

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

Or use the manual initialization (for development):

```bash
# The app will auto-initialize tables on first run from models
```

## Running the Application

### Development Mode

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the provided entry point:

```bash
python main.py
```

### Production Mode

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## API Endpoints

### Authentication

```
POST   /api/v1/auth/register          Register new user
POST   /api/v1/auth/login             Login and get tokens
POST   /api/v1/auth/refresh           Refresh access token
GET    /api/v1/auth/me                Get current user
POST   /api/v1/auth/logout            Logout (client-side)
```

### Users

```
GET    /api/v1/users/me               Get current user profile
PUT    /api/v1/users/me               Update profile
GET    /api/v1/users/{user_id}        Get user by ID
```

### Fitness Tracking

```
POST   /api/v1/workouts               Log workout
GET    /api/v1/workouts               Get workouts

POST   /api/v1/calories               Log calories
GET    /api/v1/calories               Get calorie entries

POST   /api/v1/water                  Log water intake
GET    /api/v1/water                  Get water entries

POST   /api/v1/steps                  Log steps
GET    /api/v1/steps                  Get step entries
```

## Authentication

### Register

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

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

Response:
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

### Protected Endpoints

Use the access token in the Authorization header:

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

### Refresh Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your-refresh-token"
  }'
```

## Database Models

### User
- id, name, email, hashed_password, age, gender, height_cm, weight_kg
- fitness_goal, experience_level, is_active
- created_at, updated_at

### Workout
- id, user_id, exercise_name, sets, reps, weight_kg, duration_minutes, calories_burned, recorded_at

### CalorieLog
- id, user_id, food_name, calories, protein_g, carbs_g, fat_g, meal_type, recorded_at

### WaterLog
- id, user_id, amount_ml, recorded_at

### StepLog
- id, user_id, steps, recorded_at

### BMIHistory
- id, user_id, bmi, category, created_at

## Alembic Migrations

### Create Migration

```bash
alembic revision --autogenerate -m "Add new field"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision>

# Downgrade one version
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

## Security Features

✅ JWT Authentication with access and refresh tokens
✅ Password hashing with bcrypt
✅ Input validation with Pydantic v2
✅ CORS protection
✅ Secure database access with SQLAlchemy ORM
✅ Environment variables for secrets
✅ HTTP Bearer token scheme
✅ User account status verification

## Error Handling

All API responses follow a standardized format:

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {}
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description"
}
```

HTTP Status Codes:
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity (Validation Error)
- `500` - Internal Server Error

## Development Workflow

### 1. Create a New Endpoint

```python
# In app/api/v1/my_feature.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_active_user

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

@router.get("/")
def get_feature(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Your logic here
    pass
```

### 2. Add Model

```python
# In app/models/my_feature.py
from app.core.database import Base

class MyModel(Base):
    __tablename__ = "my_models"
    # Define fields
```

### 3. Add Schema

```python
# In app/schemas/my_feature.py
from pydantic import BaseModel

class MySchema(BaseModel):
    # Define fields
```

### 4. Create Service

```python
# In app/services/my_service.py
class MyService:
    @staticmethod
    def my_method(db: Session):
        # Business logic here
        pass
```

### 5. Register Router

```python
# In app/api/v1/__init__.py
from app.api.v1 import my_feature
router.include_router(my_feature.router)
```

## Testing

Run tests:

```bash
pytest tests/

# With coverage
pytest --cov=app tests/

# Specific test file
pytest tests/test_auth.py

# Specific test function
pytest tests/test_auth.py::test_register
```

## Environment Variables Reference

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| DATABASE_URL | str | - | PostgreSQL connection string |
| SECRET_KEY | str | - | JWT signing key |
| ALGORITHM | str | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | int | 15 | Access token expiration |
| REFRESH_TOKEN_EXPIRE_DAYS | int | 7 | Refresh token expiration |
| APP_NAME | str | FitAI | Application name |
| APP_VERSION | str | 1.0.0 | Application version |
| ENVIRONMENT | str | development | Environment mode |
| CORS_ORIGINS | str | - | Comma-separated CORS origins |

## Deployment

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t fitai-backend .
docker run -p 8000:8000 --env-file .env fitai-backend
```

### Environment Variables for Production

```env
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://user:pass@prod-db:5432/fitai
SECRET_KEY=<generate-secure-key>
CORS_ORIGINS=https://yourdomain.com
```

## Contributing

1. Create a feature branch
2. Follow SOLID principles
3. Write tests for new features
4. Ensure all tests pass
5. Submit pull request

## Troubleshooting

### Database Connection Error

```
psycopg.OperationalError: could not connect to server
```

Solution: Verify PostgreSQL is running and DATABASE_URL is correct.

### JWT Token Invalid

```
"Invalid or expired token"
```

Solution: Regenerate token or check SECRET_KEY consistency.

### CORS Error

```
Access to XMLHttpRequest blocked by CORS
```

Solution: Add frontend URL to CORS_ORIGINS in .env

## Next Steps

- Phase 3: Frontend Foundation (React + Vite)
- Phase 4: Fitness Trackers (BMI, Advanced Endpoints)
- Phase 5: Analytics Dashboard
- Phase 6: AI Features (Gemini Integration)
- Phase 7: Video Analysis
- Phase 8: PDF Reporting

## License

Proprietary - FitAI Team

## Support

For issues and questions, contact the development team.
