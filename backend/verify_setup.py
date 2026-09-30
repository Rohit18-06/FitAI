#!/usr/bin/env python
"""
Verification script for FitAI backend setup.

This script checks:
1. Python version compatibility
2. Virtual environment activation
3. Required dependencies installation
4. .env file existence and configuration
5. Database connectivity
6. Configuration validity

Usage:
    python verify_setup.py
"""

import sys
import os
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{BLUE}{'='*70}")
    print(f"{title}")
    print(f"{'='*70}{RESET}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"{GREEN}[OK] {message}{RESET}")


def print_error(message: str):
    """Print an error message."""
    print(f"{RED}[FAIL] {message}{RESET}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{YELLOW}[WARN] {message}{RESET}")


def print_info(message: str):
    """Print an info message."""
    print(f"{BLUE}[INFO] {message}{RESET}")


def check_python_version():
    """Check Python version."""
    print_header("1. Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 12:
        print_success(f"Python {version_str} (Required: 3.12+)")
        return True
    else:
        print_error(f"Python {version_str} (Required: 3.12+)")
        return False


def check_virtual_environment():
    """Check if virtual environment is activated."""
    print_header("2. Virtual Environment Check")
    
    is_venv = bool(os.environ.get('VIRTUAL_ENV')) or (sys.prefix != getattr(sys, "base_prefix", sys.prefix))
    if is_venv:
        venv_path = os.environ.get('VIRTUAL_ENV', sys.prefix)
        print_success(f"Virtual environment active: {venv_path}")
        return True
    else:
        print_warning("Virtual environment not activated")
        print_info("Activate with: source venv/bin/activate (macOS/Linux)")
        print_info("Activate with: venv\\Scripts\\activate (Windows)")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print_header("3. Dependency Check")
    
    dependencies = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('sqlalchemy', 'sqlalchemy'),
        ('psycopg', 'psycopg'),
        ('pydantic', 'pydantic'),
        ('pydantic_settings', 'pydantic_settings'),
        ('passlib', 'passlib'),
        ('python-jose', 'jose'),
        ('alembic', 'alembic'),
        ('python-dotenv', 'dotenv'),
    ]
    
    missing = []
    installed = []
    
    for pkg_name, module_name in dependencies:
        try:
            __import__(module_name)
            installed.append(pkg_name)
        except ImportError:
            missing.append(pkg_name)
    
    print(f"Installed: {len(installed)}/{len(dependencies)}")
    
    for dep in installed:
        print_success(f"{dep}")
    
    if missing:
        print_error(f"Missing: {', '.join(missing)}")
        print_info("Install with: pip install -r requirements.txt")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists and has required variables."""
    print_header("4. Environment File Check")
    
    env_path = Path(".env")
    
    if not env_path.exists():
        print_error(".env file not found")
        print_info("Create with: cp .env.example .env")
        return False
    
    print_success(".env file exists")
    
    # Check for required variables
    with open(".env", "r") as f:
        content = f.read()
    
    required_vars = ["DATABASE_URL", "SECRET_KEY"]
    found_vars = []
    missing_vars = []
    
    for var in required_vars:
        if var in content and not content.split(var)[1].split('\n')[0].strip().endswith('='):
            found_vars.append(var)
        else:
            # Check if it has a value
            for line in content.split('\n'):
                if line.startswith(var + '=') and line != var + '=':
                    found_vars.append(var)
                    break
            else:
                missing_vars.append(var)
    
    for var in found_vars:
        print_success(f"{var} is set")
    
    if missing_vars:
        for var in missing_vars:
            print_error(f"{var} is missing")
        print_info("Edit .env and set the missing variables")
        return False
    
    return True


def check_database_connection():
    """Check database connection."""
    print_header("5. Database Connection Check")
    
    try:
        from app.core.config import settings
        from sqlalchemy import text
        from app.core.database import get_engine
        
        print_info(f"DATABASE_URL: {settings.DATABASE_URL[:50]}...")
        
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print_success("Database connection successful")
        return True
            
    except ValueError as e:
        print_error(f"Configuration error: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        print_info("Ensure database is accessible and DATABASE_URL is valid in .env")
        return False


def check_configuration():
    """Check if configuration loads successfully."""
    print_header("6. Configuration Validation Check")
    
    try:
        from app.core.config import settings
        
        print_success(f"App Name: {settings.APP_NAME}")
        print_success(f"Version: {settings.APP_VERSION}")
        print_success(f"Environment: {settings.ENVIRONMENT}")
        print_success(f"Debug: {settings.DEBUG}")
        print_success(f"API Prefix: {settings.API_V1_PREFIX}")
        print_success(f"CORS Origins: {len(settings.cors_origins_list)} configured")
        
        return True
        
    except ValueError as e:
        print_error(f"Configuration validation failed: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False


def main():
    """Run all checks."""
    print(f"{BLUE}")
    print(f"+{'='*68}+")
    print(f"|{'FitAI Backend Setup Verification'.center(68)}|")
    print(f"+{'='*68}+")
    print(f"{RESET}")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Configuration", check_configuration),
        ("Database Connection", check_database_connection),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Error during {name} check: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print(f"\n{GREEN}{'='*70}")
        print("All checks passed! You can now run the server.")
        print(f"{'='*70}{RESET}")
        print("\nRun the server with:")
        print("  python main.py")
        print("\nThen open:")
        print("  http://localhost:8000/api/docs")
        return 0
    else:
        print(f"\n{RED}{'='*70}")
        print("Some checks failed. Please fix the issues above.")
        print(f"{'='*70}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
