from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Adjust your PostgreSQL connection URL here
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost:5432/agromart"

# Create the engine without additional connection args
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a sessionmaker using the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base class to be used by ORM models
Base = declarative_base()

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
