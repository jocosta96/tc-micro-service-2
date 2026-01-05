"""
Shared SQLAlchemy Base class for all models.
This ensures all models are registered with the same metadata for Alembic migrations.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create a shared Base class that all models will use
Base = declarative_base() 