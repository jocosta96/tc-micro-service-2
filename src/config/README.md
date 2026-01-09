# Database Configuration

This directory contains the database configuration for the Clean Architecture application.

## Environment Variables

Set the following environment variables for PostgreSQL configuration:

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fastfood
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password123
DRIVER_NAME=postgresql

# API Configuration
API_USER=admin
API_PWD=admin123

# Application Configuration
DEBUG=true
LOG_LEVEL=INFO
```

## Database Setup

1. **Install PostgreSQL** (if not already installed)
2. **Create Database**:
   ```sql
   CREATE DATABASE fastfood;
   CREATE USER postgres WITH PASSWORD 'password123';
   GRANT ALL PRIVILEGES ON DATABASE fastfood TO postgres;
   ```

3. **Initialize Database**:
   ```bash
   cd src
   python scripts/init_db.py
   ```

4. **Create Sample Data** (optional):
   ```bash
   python scripts/init_db.py --sample-data
   ```

## Database Migrations

To run database migrations:

```bash
cd src/config
alembic upgrade head
```

To create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

## Clean Architecture Integration

The database configuration follows Clean Architecture principles:

- **Entities**: Pure business objects, no database dependencies
- **Use Cases**: Business logic, depend on repository interfaces
- **Interface Adapters**: Repository implementations, handle database specifics
- **Frameworks & Drivers**: Configuration, environment variables

The `DatabaseConfig` class in `database.py` provides a clean interface for database connection settings. 