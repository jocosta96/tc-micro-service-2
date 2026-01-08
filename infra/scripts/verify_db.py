#!/usr/bin/env python3
"""
Database verification script.
This script verifies that database tables exist and re-initializes if needed.
"""

import sys
import subprocess  # nosec
from pathlib import Path

# Add the project root directory to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.adapters.di.container import container  # noqa: E402


def verify_database_tables():
    """Verify that database tables exist and re-initialize if needed"""
    try:
        print("Verifying database tables exist...")

        # Try to access a table to verify it exists
        container.customer_repository.get_anonymous_customer()
        print("Tables verified successfully")
        return True

    except Exception as e:
        print(f"Table verification failed: {e}")
        print("Forcing database re-initialization...")

        try:
            # Force re-initialization
            # Safe: All arguments are static and passed as a list, not a string
            subprocess.run(
                ["python", "infra/scripts/database_migration.py", "init"],
                check=True,
                shell=False,
            )  # nosec
            subprocess.run(
                ["python", "infra/scripts/init_db.py", "--sample-data"],
                check=True,
                shell=False,
            )  # nosec
            print("Database re-initialization completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Database re-initialization failed: {e}")
            return False


def force_initial_migration():
    """Force creation of initial migration if none exists"""
    try:
        print("Checking if migration files exist...")

        # Check if there are any migration files in the versions directory
        project_root = Path(__file__).parent.parent.parent
        versions_dir = project_root / "src" / "config" / "migrations" / "versions"

        # If we're running in Kubernetes, check /migrations/versions/
        if Path("/migrations/versions").exists():
            versions_dir = Path("/migrations/versions")

        if not versions_dir.exists() or not list(versions_dir.glob("*.py")):
            print("No migration files found. Creating initial migration...")
            # Safe: All arguments are static and passed as a list, not a string
            subprocess.run(
                ["python", "infra/scripts/database_migration.py", "init"],
                check=True,
                shell=False,
            )  # nosec
            return True
        else:
            print("Migration files exist")
            return True

    except subprocess.CalledProcessError as e:
        print(f"Failed to create initial migration: {e}")
        return False


if __name__ == "__main__":
    # First, try to force create initial migration if needed
    if not force_initial_migration():
        sys.exit(1)

    # Then verify tables exist
    success = verify_database_tables()
    sys.exit(0 if success else 1)
