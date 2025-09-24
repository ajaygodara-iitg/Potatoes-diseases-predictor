from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./farmer_responses.db"  # Change to PostgreSQL later if needed

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)  # Needed for SQLite

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
