from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import config
import os

# Create engine with WAL mode for better concurrency
def create_database_engine():
    """Create SQLAlchemy engine with optimized settings"""
    
    # Ensure data directory exists
    os.makedirs(config.BASE_DIR / 'data', exist_ok=True)
    
    engine = create_engine(
        config.DATABASE_URL,
        connect_args={
            'check_same_thread': False,
            'timeout': 30  # 30 second timeout for locks
        },
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,    # Recycle connections every hour
        echo=config.DEBUG     # Log SQL in debug mode
    )
    
    # Enable WAL mode for better concurrency
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA busy_timeout=30000"))  # 30s timeout
        conn.execute(text("PRAGMA synchronous=NORMAL"))  # Faster writes
        conn.commit()
    
    return engine

# Initialize engine
engine = create_database_engine()

# Create session factory
SessionLocal = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
))

@contextmanager
def get_db_session():
    """
    Context manager for database sessions
    Automatically commits on success, rolls back on error
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def init_db():
    """Initialize database tables"""
    from application.models import Base
    Base.metadata.create_all(bind=engine)
