"""
FastAPI application entry point.
Configures the FastAPI application with middleware, routes, and documentation.
Handles application initialization, configuration validation, and startup/shutdown events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys

# Import configuration first (will raise if .env is missing required vars)
try:
    from app.core.config import settings
except ValueError as e:
    print(f"\n{'='*70}")
    print("CRITICAL: Configuration Error During Startup")
    print(f"{'='*70}")
    print(str(e))
    print(f"{'='*70}\n")
    sys.exit(1)

# Import other modules
from app.core.database import init_db
from app.api import api_router
from app.utils import format_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events.
    
    Startup:
    - Initialize database tables
    - Log startup information
    - Continue even if database is unavailable
    
    Shutdown:
    - Cleanup resources
    """
    # Startup
    try:
        print(f"\n{'='*70}")
        print(f"Starting FitAI Backend v{settings.APP_VERSION}")
        print(f"{'='*70}")
        print(f"Environment: {settings.ENVIRONMENT}")
        print(f"Debug: {settings.DEBUG}")
        print(f"API Prefix: {settings.API_V1_PREFIX}")
        
        # Extract database info safely
        db_url = settings.DATABASE_URL
        if db_url.startswith("sqlite"):
            db_display = "SQLite (Local)"
        elif '@' in db_url:
            db_display = db_url.split('@')[1]
        else:
            db_display = db_url
        
        print(f"Database: {db_display}")
        print(f"CORS Origins: {len(settings.cors_origins_list)} configured")
        print(f"{'='*70}\n")
        
        # Initialize database (continues even if it fails)
        db_initialized = init_db()
        if db_initialized:
            print("[OK] Database initialized successfully\n")
        else:
            print("[WARNING] Database initialization had issues, continuing anyway...\n")
        
    except Exception as e:
        print(f"\n[WARNING] Startup Warning (non-fatal): {str(e)}\n")
        print("Application will continue but some features may be limited\n")
    
    yield
    
    # Shutdown
    print("\n[SHUTDOWN] Shutting down FitAI Backend...\n")


# Create FastAPI application with lifespan context manager
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Fitness Coach Application",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log CORS configuration in development
if settings.is_development:
    print(f"[OK] CORS configured for: {', '.join(settings.cors_origins_list)}")



@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
)
def root():
    """
    Root endpoint with API information.
    
    Returns information about the API and links to documentation.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "api": settings.API_V1_PREFIX,
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check endpoint",
)
@app.get(
    "/api/health",
    tags=["Health"],
    summary="Health check endpoint",
)
def health_check():
    """
    Health check endpoint for monitoring application health.
    
    Returns:
        Standard response with healthy status
    """
    return format_response(
        success=True,
        message="Application is healthy",
        data={"status": "healthy", "version": settings.APP_VERSION},
    )


# Include all API routes
app.include_router(api_router)


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.
    
    Logs the error and returns a standardized error response.
    
    Args:
        request: The HTTP request that caused the error
        exc: The exception that was raised
        
    Returns:
        JSONResponse with error details
    """
    error_message = "Internal server error"
    if settings.is_development:
        error_message = str(exc)
    
    return JSONResponse(
        status_code=500,
        content=format_response(
            success=False,
            message=error_message,
        ),
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run server with configuration
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info" if settings.is_development else "warning",
    )
