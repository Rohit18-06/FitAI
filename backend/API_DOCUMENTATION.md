# FitAI API Documentation - Phase 2

Complete REST API documentation for FitAI Backend Foundation.

## Base URL

```
http://localhost:8000
Development: http://localhost:8000/api/v1
Production: https://api.fitai.com/api/v1
```

## API Endpoints Summary

### Authentication (5 endpoints)
- POST `/api/v1/auth/register` - Register new user
- POST `/api/v1/auth/login` - Login user
- POST `/api/v1/auth/refresh` - Refresh access token
- GET `/api/v1/auth/me` - Get current user
- POST `/api/v1/auth/logout` - Logout (client-side)

### Users (3 endpoints)
- GET `/api/v1/users/me` - Get current user profile
- PUT `/api/v1/users/me` - Update current user profile
- GET `/api/v1/users/{user_id}` - Get user by ID

### Workouts (2 endpoints)
- POST `/api/v1/workouts` - Create workout
- GET `/api/v1/workouts` - Get workouts

### Calories (2 endpoints)
- POST `/api/v1/calories` - Log calories
- GET `/api/v1/calories` - Get calorie entries

### Water (2 endpoints)
- POST `/api/v1/water` - Log water
- GET `/api/v1/water` - Get water entries

### Steps (2 endpoints)
- POST `/api/v1/steps` - Log steps
- GET `/api/v1/steps` - Get step entries

### Health (2 endpoints)
- GET `/` - Root endpoint
- GET `/api/health` - Health check

---

## Authentication Endpoints

### 1. Register User

Register a new user account.

**Endpoint**
```
POST /api/v1/auth/register
```

**Request**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "age": 30,
  "gender": "M",
  "height_cm": 180,
  "weight_kg": 75
}
```

**Request Body Schema**

| Field | Type | Required | Constraints |
|-------|------|----------|------------|
| name | string | Yes | Min 2, Max 255 characters |
| email | string (email) | Yes | Valid email format |
| password | string | Yes | Min 8 characters |
| age | integer | No | Between 13 and 120 |
| gender | string | No | M, F, Other |
| height_cm | number | No | Greater than 0 |
| weight_kg | number | No | Greater than 0 |

**Response (201 Created)**
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

**Error Response (400)**
```json
{
  "success": false,
  "message": "Email already registered"
}
```

---

### 2. Login User

Authenticate user and receive JWT tokens.

**Endpoint**
```
POST /api/v1/auth/login
```

**Request**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcwMjAyMTYwMH0.abc123...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcwMjYyNjQwMH0.xyz789...",
    "token_type": "bearer"
  }
}
```

**Token Details**
- **access_token**: Valid for 15 minutes (configured in settings)
- **refresh_token**: Valid for 7 days (configured in settings)
- **token_type**: Always "bearer"

**Error Response (401)**
```json
{
  "success": false,
  "message": "Invalid email or password"
}
```

---

### 3. Refresh Token

Get a new access token using a refresh token.

**Endpoint**
```
POST /api/v1/auth/refresh
```

**Request**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcwMjYyNjQwMH0.xyz789..."
}
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcwMjAyMTYwMH0.new123...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcwMjYyNjQwMH0.xyz789...",
    "token_type": "bearer"
  }
}
```

**Error Response (401)**
```json
{
  "success": false,
  "message": "Invalid or expired refresh token"
}
```

---

### 4. Get Current User

Get authenticated user's profile (requires access token).

**Endpoint**
```
GET /api/v1/auth/me
```

**Headers**
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "User profile retrieved",
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "gender": "M",
    "height_cm": 180,
    "weight_kg": 75,
    "fitness_goal": "general_fitness",
    "experience_level": "beginner",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

**Error Response (401)**
```json
{
  "success": false,
  "message": "Invalid authentication credentials"
}
```

---

### 5. Logout

Logout endpoint (JWT tokens are stateless, actual logout happens on client).

**Endpoint**
```
POST /api/v1/auth/logout
```

**Headers**
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

## User Endpoints

### 1. Get User Profile

Get current user's profile.

**Endpoint**
```
GET /api/v1/users/me
```

**Headers**
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "User profile retrieved",
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "gender": "M",
    "height_cm": 180,
    "weight_kg": 75,
    "fitness_goal": "general_fitness",
    "experience_level": "beginner",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

---

### 2. Update User Profile

Update current user's profile information.

**Endpoint**
```
PUT /api/v1/users/me
```

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request (all fields optional)**
```json
{
  "name": "Jane Doe",
  "age": 28,
  "gender": "F",
  "height_cm": 170,
  "weight_kg": 65,
  "fitness_goal": "muscle_gain",
  "experience_level": "intermediate"
}
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "User profile updated successfully",
  "data": {
    "id": 1,
    "name": "Jane Doe",
    "email": "john@example.com",
    "age": 28,
    "gender": "F",
    "height_cm": 170,
    "weight_kg": 65,
    "fitness_goal": "muscle_gain",
    "experience_level": "intermediate",
    "is_active": true,
    "updated_at": "2024-01-15T10:35:00"
  }
}
```

---

### 3. Get User by ID

Get another user's profile (requires authentication).

**Endpoint**
```
GET /api/v1/users/{user_id}
```

**Parameters**
| Param | Type | Description |
|-------|------|-------------|
| user_id | integer | The user ID |

**Headers**
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "User profile retrieved",
  "data": {
    "id": 2,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "age": 28,
    "gender": "F",
    "height_cm": 170,
    "weight_kg": 65,
    "fitness_goal": "muscle_gain",
    "experience_level": "intermediate",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

---

## Workout Endpoints

### 1. Create Workout

Log a new workout entry.

**Endpoint**
```
POST /api/v1/workouts
```

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request**
```json
{
  "exercise_name": "Bench Press",
  "sets": 4,
  "reps": 8,
  "weight_kg": 100,
  "duration_minutes": 45,
  "calories_burned": 250
}
```

**Request Body Schema**

| Field | Type | Required | Constraints |
|-------|------|----------|------------|
| exercise_name | string | Yes | Min 2, Max 255 characters |
| sets | integer | Yes | Min 1, Max 100 |
| reps | integer | Yes | Min 1, Max 1000 |
| weight_kg | number | No | Min 0 (default: 0) |
| duration_minutes | integer | Yes | Min 1, Max 480 |
| calories_burned | number | Yes | Min 0 |

**Response (201 Created)**
```json
{
  "success": true,
  "message": "Workout logged successfully",
  "data": {
    "id": 1,
    "exercise_name": "Bench Press",
    "sets": 4,
    "reps": 8,
    "weight_kg": 100,
    "duration_minutes": 45,
    "calories_burned": 250,
    "recorded_at": "2024-01-15T10:30:00"
  }
}
```

---

### 2. Get Workouts

Get all workouts for current user (paginated).

**Endpoint**
```
GET /api/v1/workouts
```

**Query Parameters**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| skip | integer | 0 | Number of records to skip |
| limit | integer | 10 | Max records to return |

**Headers**
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "Workouts retrieved successfully",
  "data": {
    "total": 5,
    "workouts": [
      {
        "id": 1,
        "exercise_name": "Bench Press",
        "sets": 4,
        "reps": 8,
        "weight_kg": 100,
        "duration_minutes": 45,
        "calories_burned": 250,
        "recorded_at": "2024-01-15T10:30:00"
      }
    ]
  }
}
```

---

## Calorie Endpoints

### 1. Log Calories

Log a food entry with calorie information.

**Endpoint**
```
POST /api/v1/calories
```

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request**
```json
{
  "food_name": "Grilled Chicken Breast",
  "calories": 165,
  "protein_g": 31,
  "carbs_g": 0,
  "fat_g": 3.6,
  "meal_type": "lunch"
}
```

**Request Body Schema**

| Field | Type | Required | Constraints |
|-------|------|----------|------------|
| food_name | string | Yes | Min 2, Max 255 characters |
| calories | number | Yes | Min 0 |
| protein_g | number | Yes | Min 0 |
| carbs_g | number | Yes | Min 0 |
| fat_g | number | Yes | Min 0 |
| meal_type | string | Yes | breakfast, lunch, dinner, snack |

**Response (201 Created)**
```json
{
  "success": true,
  "message": "Calorie entry logged successfully",
  "data": {
    "id": 1,
    "food_name": "Grilled Chicken Breast",
    "calories": 165,
    "protein_g": 31,
    "carbs_g": 0,
    "fat_g": 3.6,
    "meal_type": "lunch",
    "recorded_at": "2024-01-15T12:30:00"
  }
}
```

---

### 2. Get Calorie Entries

Get all calorie entries for current user with summary.

**Endpoint**
```
GET /api/v1/calories
```

**Query Parameters**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| skip | integer | 0 | Number of records to skip |
| limit | integer | 10 | Max records to return |

**Response (200 OK)**
```json
{
  "success": true,
  "message": "Calorie entries retrieved successfully",
  "data": {
    "total": 3,
    "summary": {
      "total_calories": 2100,
      "total_protein_g": 150,
      "total_carbs_g": 250,
      "total_fat_g": 50
    },
    "entries": [
      {
        "id": 1,
        "food_name": "Grilled Chicken Breast",
        "calories": 165,
        "protein_g": 31,
        "carbs_g": 0,
        "fat_g": 3.6,
        "meal_type": "lunch",
        "recorded_at": "2024-01-15T12:30:00"
      }
    ]
  }
}
```

---

## Water Endpoints

### 1. Log Water Intake

Log water consumption.

**Endpoint**
```
POST /api/v1/water
```

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request**
```json
{
  "amount_ml": 500
}
```

**Response (201 Created)**
```json
{
  "success": true,
  "message": "Water intake logged successfully",
  "data": {
    "id": 1,
    "amount_ml": 500,
    "recorded_at": "2024-01-15T10:30:00"
  }
}
```

---

### 2. Get Water Entries

Get all water intake entries.

**Endpoint**
```
GET /api/v1/water
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "Water intake entries retrieved successfully",
  "data": {
    "total": 8,
    "total_water_ml": 4000,
    "entries": [
      {
        "id": 1,
        "amount_ml": 500,
        "recorded_at": "2024-01-15T10:30:00"
      }
    ]
  }
}
```

---

## Steps Endpoints

### 1. Log Steps

Log step count.

**Endpoint**
```
POST /api/v1/steps
```

**Request**
```json
{
  "steps": 8500
}
```

**Response (201 Created)**
```json
{
  "success": true,
  "message": "Steps logged successfully",
  "data": {
    "id": 1,
    "steps": 8500,
    "recorded_at": "2024-01-15T10:30:00"
  }
}
```

---

### 2. Get Step Entries

Get all step entries with statistics.

**Endpoint**
```
GET /api/v1/steps
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "Step entries retrieved successfully",
  "data": {
    "total": 7,
    "total_steps": 60000,
    "average_steps": 8571.43,
    "entries": [
      {
        "id": 1,
        "steps": 8500,
        "recorded_at": "2024-01-15T10:30:00"
      }
    ]
  }
}
```

---

## Health Endpoints

### 1. Root Endpoint

Get API information.

**Endpoint**
```
GET /
```

**Response (200 OK)**
```json
{
  "app": "FitAI",
  "version": "1.0.0",
  "environment": "development",
  "status": "running",
  "docs": "/api/docs",
  "redoc": "/api/redoc"
}
```

---

### 2. Health Check

Check if API is healthy.

**Endpoint**
```
GET /api/health
```

**Response (200 OK)**
```json
{
  "success": true,
  "message": "Application is healthy",
  "data": {
    "status": "healthy"
  }
}
```

---

## Authentication

All protected endpoints require JWT token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Bearer Token Scheme

The API uses HTTP Bearer authentication scheme. Include the token in the request header as shown above.

### Token Expiration

- **Access Token**: 15 minutes (configurable)
- **Refresh Token**: 7 days (configurable)

When access token expires, use the refresh token to obtain a new access token via `/api/v1/auth/refresh`.

---

## Error Handling

### Standard Error Response

```json
{
  "success": false,
  "message": "Error description"
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST request creating resource |
| 400 | Bad Request | Invalid request body or parameters |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | User account inactive |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error in request data |
| 500 | Internal Server Error | Server error |

### Common Errors

**Validation Error (422)**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error"
    }
  ]
}
```

**Unauthorized (401)**
```json
{
  "success": false,
  "message": "Invalid authentication credentials"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. This will be added in future phases.

---

## Response Format

All successful API responses follow this format:

```json
{
  "success": true,
  "message": "Description of the operation",
  "data": {
    // Response payload specific to endpoint
  }
}
```

---

## Example Usage

### Complete Flow: Register → Login → Get Profile

```bash
# 1. Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# 2. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
# Response includes access_token

# 3. Get Profile (use access_token from login)
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token_from_login>"

# 4. Log Workout
curl -X POST "http://localhost:8000/api/v1/workouts" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_name": "Bench Press",
    "sets": 4,
    "reps": 8,
    "weight_kg": 100,
    "duration_minutes": 45,
    "calories_burned": 250
  }'
```

---

## API Testing Tools

Recommended tools for testing the API:

- **Swagger UI**: http://localhost:8000/api/docs (Built-in)
- **Postman**: https://www.postman.com/
- **Insomnia**: https://insomnia.rest/
- **curl**: Command line tool
- **VS Code REST Client**: Extension for VS Code

---

## Next Phase

See `API_DOCUMENTATION_PHASE3.md` for endpoints added in Phase 3:
- AI Diet Planner
- AI Workout Planner
- AI Fitness Coach Chat
- Video Analysis
- Analytics Dashboard
- Reporting
