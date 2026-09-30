"""
Database configuration and session management.
Implements SQLAlchemy 2.0 with lazy connection initialization.
Supports both SQLite (development) and PostgreSQL (production).
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool, QueuePool
from typing import Generator
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

# Global engine and session factory (initialized lazily)
engine = None
SessionLocal = None


def get_engine():
    """
    Get or create the SQLAlchemy engine.
    
    Uses lazy initialization to avoid connection attempts on import.
    Configures different pool strategies for SQLite vs PostgreSQL.
    
    Returns:
        SQLAlchemy Engine instance
    """
    global engine
    
    if engine is not None:
        return engine
    
    # Determine if using SQLite or PostgreSQL
    is_sqlite = settings.DATABASE_URL.startswith("sqlite://")
    
    logger.info(f"Initializing database: {settings.DATABASE_URL}")
    
    if is_sqlite:
        # SQLite configuration
        # StaticPool: keeps one connection open (good for SQLite)
        # timeout: prevents hanging on connection attempts
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.ENVIRONMENT == "development",
            connect_args={"timeout": 5},  # 5 second timeout
            poolclass=StaticPool,  # Single persistent connection
        )
        logger.info("SQLite database configured")
    else:
        # PostgreSQL configuration
        # QueuePool: connection pooling for multi-threaded access
        # pool_pre_ping: verify connections before using them
        # connect_timeout: prevent hanging on database unavailability
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.ENVIRONMENT == "development",
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args={"connect_timeout": 5},
        )
        logger.info("PostgreSQL database configured")
    
    return engine


def get_session_factory():
    """
    Get or create the SQLAlchemy session factory.
    
    Uses lazy initialization to avoid connection attempts on import.
    
    Returns:
        SQLAlchemy sessionmaker instance
    """
    global SessionLocal
    
    if SessionLocal is not None:
        return SessionLocal
    
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=get_engine(),
    )
    
    return SessionLocal


def get_db() -> Generator:
    """
    Dependency injection function for database sessions.
    
    Yields a database session and ensures it's properly closed after use.
    Use this as a dependency in FastAPI route handlers.
    
    Example:
        @router.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
            
    Yields:
        SQLAlchemy Session
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    
    Safe initialization with error handling. If database is unavailable,
    logs a warning but doesn't crash the application.
    
    This should be called during application startup in the lifespan handler.
    """
    try:
        logger.info("Creating database tables...")
        engine = get_engine()
        
        # Create all tables from models
        Base.metadata.create_all(bind=engine)
        
        logger.info("[OK] Database tables created successfully")
        return True
        
    except Exception as e:
        logger.warning(f"[WARNING] Database initialization warning: {str(e)}")
        logger.warning("Application will continue but database functionality may be limited")
        # Don't raise - let the app start anyway
        return False
