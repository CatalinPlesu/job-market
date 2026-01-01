"""Database connector for querying job data."""

from typing import List
from sqlalchemy.orm import Session, subqueryload
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
        Get all job details from database with optimized loading.
        
        Uses subqueryload for efficient batch loading of relationships
        to avoid N+1 queries while keeping memory usage reasonable.
        
        Returns:
            List of JobDetail objects with all relationships loaded.
        """
        if not self.session:
            raise RuntimeError("Database connector must be used as context manager")
        
        # Query jobs with optimized subquery loading for relationships
        # This loads relationships in separate queries, avoiding massive JOINs
        query = self.session.query(JobDetail)
        
        # Load one-to-one relationships
        query = query.options(
            subqueryload(JobDetail.title),
            subqueryload(JobDetail.job_function),
            subqueryload(JobDetail.seniority_level),
            subqueryload(JobDetail.industry),
            subqueryload(JobDetail.department),
            subqueryload(JobDetail.job_family),
            subqueryload(JobDetail.specialization),
            subqueryload(JobDetail.education_level),
            subqueryload(JobDetail.employment_type),
            subqueryload(JobDetail.contract_type),
            subqueryload(JobDetail.work_schedule),
            subqueryload(JobDetail.shift_details),
            subqueryload(JobDetail.remote_work),
            subqueryload(JobDetail.travel_requirements),
            subqueryload(JobDetail.salary_currency),
            subqueryload(JobDetail.salary_period),
            subqueryload(JobDetail.city),
            subqueryload(JobDetail.region),
            subqueryload(JobDetail.country),
            subqueryload(JobDetail.company),
            subqueryload(JobDetail.company_size),
        )
        
        # Load one-to-many relationships
        query = query.options(
            subqueryload(JobDetail.responsibilities),
            subqueryload(JobDetail.languages),
        )
        
        # Load many-to-many relationships
        query = query.options(
            subqueryload(JobDetail.hard_skills),
            subqueryload(JobDetail.soft_skills),
            subqueryload(JobDetail.certifications),
            subqueryload(JobDetail.licenses),
            subqueryload(JobDetail.benefits),
            subqueryload(JobDetail.work_environment),
            subqueryload(JobDetail.professional_development),
            subqueryload(JobDetail.work_life_balance),
            subqueryload(JobDetail.physical_requirements),
            subqueryload(JobDetail.work_conditions),
            subqueryload(JobDetail.special_requirements),
        )
        
        jobs = query.all()
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
