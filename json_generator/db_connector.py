"""Database connector for querying job data."""

from typing import List
from sqlalchemy.orm import Session
from src.data_database import JobDetail, DataSessionLocal, get_data_db


class DatabaseConnector:
    """Handles database queries for job data."""
    
    def __init__(self):
        """Initialize database connection."""
        self.session = None
    
    def __enter__(self):
        """Context manager entry."""
        self.session = DataSessionLocal()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            self.session.close()
    
    def get_all_jobs(self) -> List[JobDetail]:
        """
        Get all job details from database.
        
        Returns:
            List of JobDetail objects with all relationships loaded.
        """
        if not self.session:
            raise RuntimeError("Database connector must be used as context manager")
        
        # Query all jobs with eager loading of relationships
        jobs = self.session.query(JobDetail).all()
        return jobs
    
    def get_jobs_count(self) -> int:
        """
        Get total count of jobs in database.
        
        Returns:
            Total number of jobs.
        """
        if not self.session:
            raise RuntimeError("Database connector must be used as context manager")
        
        return self.session.query(JobDetail).count()
