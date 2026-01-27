from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Create SQLAlchemy engine for Supabase connection pooler (transaction mode)
# Using NullPool to let Supabase's server-side pooler handle all connection management
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,  # Disable app-side pooling
    echo=settings.DEBUG,
    connect_args={
        "options": "-c statement_timeout=60000"  # 60 second timeout
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
