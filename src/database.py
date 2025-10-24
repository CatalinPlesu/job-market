from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config.settings import Config

# Create engine
engine = create_engine('sqlite:///' + Config.db_path, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class Job(Base):
    """
    Single table combining job info and description
    """
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    job_title = Column(String(200), nullable=False)
    company_name = Column(String(200), nullable=False)
    job_url = Column(String(500), unique=True, nullable=False)
    job_description = Column(Text)  # Initially null, populated in stage 2
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)


class JobCheck(Base):
    """
    Table tracking when jobs were checked and their status
    """
    __tablename__ = 'job_checks'

    id = Column(Integer, primary_key=True)
    job_url = Column(String(500), nullable=False)  # Links to jobs table
    check_date = Column(DateTime, nullable=False)  # Date of check
    http_status = Column(Integer)  # HTTP status code
    checked_at = Column(DateTime, default=datetime.utcnow)


# Create composite unique index: same title + same company + same date created = same job
# This prevents exact duplicates while allowing new posts with same title
Index('idx_job_title_company_date', 'job_title',
      'company_name', 'created_at', unique=True)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass


# Create all tables
Base.metadata.create_all(engine)
