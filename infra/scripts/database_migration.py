#!/usr/bin/env python3
"""
Database migration script for Clean Architecture.
This script handles database schema migrations using Alembic.
"""

import os
import sys
import shlex
import subprocess # nosec
from pathlib import Path

# Add the project root directory to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))



def run_alembic_command(command):
    """Run an Alembic command"""
    try:
        # Change to the project root directory
        project_root = Path(__file__).parent.parent.parent
        os.chdir(project_root)

        # Set Alembic config path if not already set
        if 'ALEMBIC_CONFIG' not in os.environ:
            os.environ['ALEMBIC_CONFIG'] = str(project_root / 'alembic.ini')

        # Check if we're running in Kubernetes with persistent volume
        if Path("/migrations").exists():
            print("Running in Kubernetes environment with persistent volume")

        print(f"Running Alembic command: {' '.join(command)}")
        print(f"Working directory: {os.getcwd()}")
        print(f"ALEMBIC_CONFIG: {os.environ.get('ALEMBIC_CONFIG', 'Not set')}")

        # Static command mapping - all commands are fully static with no external input
        # This approach satisfies static analysis security requirements
        # Using shlex.quote for additional sanitization layer
        static_commands = {
            "current": [shlex.quote("alembic"), shlex.quote("current")],
            "initial_migration": [shlex.quote("alembic"), shlex.quote("revision"), shlex.quote("--autogenerate"), shlex.quote("-m"), shlex.quote("Initial migration")],
            "create_migration": [shlex.quote("alembic"), shlex.quote("revision"), shlex.quote("--autogenerate"), shlex.quote("-m"), shlex.quote("Create new migration")],
            "upgrade": [shlex.quote("alembic"), shlex.quote("upgrade"), shlex.quote("head")],
            "history": [shlex.quote("alembic"), shlex.quote("history")]
        }

        # Convert command list to lookup key
        command_key = None
        if command == ["current"]:
            command_key = "current"
        elif command == ["revision", "--autogenerate", "-m", "Initial migration"]:
            command_key = "initial_migration"
        elif command == ["revision", "--autogenerate", "-m", "Create new migration"]:
            command_key = "create_migration"
        elif command == ["upgrade", "head"]:
            command_key = "upgrade"
        elif command == ["history"]:
            command_key = "history"

        # Execute only if command is in static whitelist
        if command_key and command_key in static_commands:
            # Safe subprocess usage: fully static commands with shlex.quote() sanitization
            # No external input, shell=False, all arguments properly escaped
            # pylint: disable=subprocess-run-check
            result = subprocess.run(  # nosec B603
                static_commands[command_key],
                capture_output=True,
                text=True,
                check=True,
                env=os.environ.copy(),
                shell=False
            )
            print(f"Alembic command {' '.join(command)} executed successfully:")
            print(result.stdout)
            return True
        else:
            print("Rejected alembic command: only static, pre-approved commands are allowed.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error running Alembic command {' '.join(command)}:")
        print(f"Return code: {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: Alembic not found. Please install Alembic: pip install alembic")
        return False


def init_database():
    """Initialize the database with Alembic"""
    print("Initializing database with Alembic...")
    
    # Ensure migration files exist
    project_root = Path(__file__).parent.parent.parent
    migrations_source = project_root / "src" / "config" / "migrations"
    
    # Ensure versions directory exists (required for migration file generation)
    versions_dir = migrations_source / "versions"
    if not versions_dir.exists():
        print(f"Creating versions directory at {versions_dir}...")
        versions_dir.mkdir(parents=True, exist_ok=True)
        print("Versions directory created successfully")
    
    # If we're running in Kubernetes, copy migration files to persistent volume
    if Path("/migrations").exists():
        import shutil
        
        # Copy env.py (essential for Alembic)
        env_source = migrations_source / "env.py"
        env_dest = Path("/migrations/env.py")
        print(f"Checking env.py: source={env_source} (exists={env_source.exists()}), dest={env_dest} (exists={env_dest.exists()})")
        if not env_dest.exists() and env_source.exists():
            print("Copying env.py to persistent volume...")
            shutil.copy2(env_source, env_dest)
            print(f"env.py copied successfully to {env_dest}")
        elif env_dest.exists():
            print("env.py already exists in persistent volume")
        else:
            print(f"ERROR: env.py source not found at {env_source}")
        
        # Copy script.py.mako template
        template_source = migrations_source / "script.py.mako"
        template_dest = Path("/migrations/script.py.mako")
        print(f"Checking script.py.mako: source={template_source} (exists={template_source.exists()}), dest={template_dest} (exists={template_dest.exists()})")
        if not template_dest.exists() and template_source.exists():
            print("Copying script.py.mako template to persistent volume...")
            shutil.copy2(template_source, template_dest)
            print(f"script.py.mako copied successfully to {template_dest}")
        elif template_dest.exists():
            print("script.py.mako already exists in persistent volume")
        else:
            print(f"ERROR: script.py.mako source not found at {template_source}")
        
        # Create versions directory if it doesn't exist
        versions_dest = Path("/migrations/versions")
        if not versions_dest.exists():
            print("Creating versions directory in persistent volume...")
            versions_dest.mkdir(parents=True, exist_ok=True)
    
    # Check if alembic_version table exists (if not, this is a fresh database)
    if not run_alembic_command(["current"]):
        print("Database not initialized. Creating initial migration...")
        
        # Create initial migration
        if not run_alembic_command(["revision", "--autogenerate", "-m", "Initial migration"]):
            print("Failed to create initial migration")
            return False
        
        # Apply the migration
        if not run_alembic_command(["upgrade", "head"]):
            print("Failed to apply initial migration")
            return False
    else:
        print("Database already initialized. Checking for pending migrations...")
        
        # Check if there are any migration files
        versions_dir = project_root / "src" / "config" / "migrations" / "versions"
        
        # If we're running in Kubernetes, check /migrations/versions/
        if Path("/migrations/versions").exists():
            versions_dir = Path("/migrations/versions")
        
        if not versions_dir.exists() or not list(versions_dir.glob("*.py")):
            print("No migration files found. Creating initial migration...")
            
            # Create initial migration
            if not run_alembic_command(["revision", "--autogenerate", "-m", "Initial migration"]):
                print("Failed to create initial migration")
                return False
            
            # Apply the migration
            if not run_alembic_command(["upgrade", "head"]):
                print("Failed to apply initial migration")
                return False
        else:
            # Check for pending migrations
            if not run_alembic_command(["upgrade", "head"]):
                print("Failed to apply pending migrations")
                return False
    
    print("Database initialization completed successfully!")
    return True


def create_migration():
    """Create a new migration"""    
    if not run_alembic_command(["revision", "--autogenerate", "-m", "Create new migration"]):
        print("Failed to create migration")
        return False
    print("Migration created successfully!")
    return True


def apply_migrations():
    """Apply all pending migrations"""
    print("Applying pending migrations...")
    
    if not run_alembic_command(["upgrade", "head"]):
        print("Failed to apply migrations")
        return False
    
    print("Migrations applied successfully!")
    return True


def show_migration_status():
    """Show current migration status"""
    print("Current migration status:")
    run_alembic_command(["current"])
    print("\nMigration history:")
    run_alembic_command(["history"])


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python database_migration.py init          - Initialize database")
        print("  python database_migration.py migrate       - Apply pending migrations")
        print("  python database_migration.py create <msg>  - Create new migration")
        print("  python database_migration.py status        - Show migration status")
        return
    
    command = sys.argv[1]
    
    if command == "init":
        init_database()
    elif command == "migrate":
        apply_migrations()
    elif command == "create":
        create_migration()
    elif command == "status":
        show_migration_status()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: init, migrate, create, status")


if __name__ == "__main__":
    main()
