from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Index, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
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
    site = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    company_name = Column(String(200), nullable=False)
    job_url = Column(String(500), nullable=False)
    job_description = Column(Text)  # Initially null, populated in stage 2
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    checks = relationship("JobCheck", back_populates="job")
    
    __table_args__ = (
        Index('idx_job_unique', 'site', 'company_name', 'job_title', unique=True),
    )

class JobCheck(Base):
    """
    Table tracking when jobs were checked and their status
    """
    __tablename__ = 'job_checks'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)  # Link to Job table
    check_date = Column(Date, nullable=False)  # Date only, no time
    http_status = Column(Integer)  # HTTP status code
    
    job = relationship("Job", back_populates="checks")
    
    # Unique constraint: one check per job per day
    __table_args__ = (
        Index('idx_job_check_unique', 'job_id', 'check_date', unique=True),
    )

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

# Create all tables
Base.metadata.create_all(engine)
