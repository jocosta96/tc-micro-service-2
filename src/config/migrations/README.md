# Database Migrations

This directory contains the database migration configuration for the Clean Architecture project.

## Overview

The project uses Alembic for database schema management. Migrations are stored in a persistent volume that is shared between Kubernetes jobs.

## Structure

- `env.py` - Alembic environment configuration
- `versions/` - Directory containing migration files (created automatically)

## Migration Files

Migration files are automatically generated and stored in the persistent volume `/migrations/versions/` when running in Kubernetes.

## Usage

### Local Development

1. **Create a new migration:**
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migrations:**
   ```bash
   python src/scripts/database_migration.py migrate
   ```

3. **Check migration status:**
   ```bash
   python src/scripts/database_migration.py status
   ```

### Kubernetes Deployment

The migrations are handled automatically by Kubernetes jobs:

1. **Initial database setup:**
   ```bash
   kubectl apply -f infra/maintenance/job_db_init.yaml
   ```

2. **Apply pending migrations:**
   ```bash
   kubectl apply -f infra/maintenance/job_dbupdate.yaml
   ```

## Persistent Volume

Migrations are stored in a persistent volume (`pvc-migrations`) that is shared between:
- `job_db_init.yaml` - Initial database setup
- `job_dbupdate.yaml` - Database updates

## Important Notes

- **Never modify migration files after they have been applied to production**
- **Always test migrations in a development environment first**
- **Backup your database before applying migrations**
- **Migration files are stored in the persistent volume, not in the source code**

## Troubleshooting

### Migration fails to apply
1. Check the job logs: `kubectl logs job/db-init-job`
2. Verify the persistent volume is properly mounted
3. Ensure the database connection is working

### Migration files not found
1. Check if the persistent volume claim exists: `kubectl get pvc pvc-migrations`
2. Verify the volume is properly mounted in the job
3. Check if the migration files were copied to the persistent volume

### Schema changes not detected
1. Ensure all SQLAlchemy models are imported in `env.py`
2. Check that the models are properly registered with `Base.metadata`
3. Verify the database connection string is correct 