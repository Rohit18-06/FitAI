#!/usr/bin/env python
"""
Entry point script for running the FitAI backend server.

Run with: python main.py
"""

import uvicorn
import sys
from app.core.config import settings


def main():
    """Run the FastAPI application."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
