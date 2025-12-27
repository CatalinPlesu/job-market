"""
Scrape Database Module
Handles the scrape.db database for raw scraped job data.
This database stores Job records and JobCheck records.
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Text, 
    ForeignKey, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from pathlib import Path
from config.settings import Config

# Ensure database directory exists
db_path = Path(Config.scrape_db_path)
db_path.parent.mkdir(parents=True, exist_ok=True)

# Create engine for scrape database
scrape_engine = create_engine('sqlite:///' + Config.scrape_db_path, echo=False)
ScrapeBase = declarative_base()
ScrapeSessionLocal = sessionmaker(bind=scrape_engine)


class Job(ScrapeBase):
    """Original job posting (raw scraped data)"""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    site = Column(String(200), nullable=False, index=True)
    job_title = Column(String(200), nullable=False)
    company_name = Column(String(200), nullable=False, index=True)
    job_url = Column(String(500), nullable=False, unique=True)
    job_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    checks = relationship("JobCheck", back_populates="job", cascade="all, delete-orphan")


class JobCheck(ScrapeBase):
    """Track when jobs were checked and their status"""
    __tablename__ = 'job_checks'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False, index=True)
    check_date = Column(Date, nullable=False)
    http_status = Column(Integer)
    
    job = relationship("Job", back_populates="checks")


class SiteStatistics(ScrapeBase):
    """Track scraping statistics per site"""
    __tablename__ = 'site_statistics'
    
    id = Column(Integer, primary_key=True)
    site_name = Column(String(200), nullable=False, unique=True, index=True)
    total_runs = Column(Integer, default=0, nullable=False)
    total_pages = Column(Integer, default=0, nullable=False)
    average_pages = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_scrape_db():
    """Get scrape database session"""
    db = ScrapeSessionLocal()
    try:
        return db
    finally:
        pass


# Create all tables in scrape database
ScrapeBase.metadata.create_all(scrape_engine)
