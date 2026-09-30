"""API routes module."""

from fastapi import APIRouter
from app.api.v1 import router as v1_router

api_router = APIRouter()

# Include v1 routes under /api prefix
api_router.include_router(v1_router, prefix="/api")

__all__ = ["api_router"]
