"""
Job Identification Module
Handles logic for identifying when a job should be treated as a new position vs. reactivating an old one.
"""
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from config.settings import Config
from src.scrape_database import Job, JobCheck


def get_latest_job(db: Session, site: str, job_title: str, company_name: str):
    """
    Get the most recently created job matching site, title, and company.
    
    Args:
        db: Database session
        site: Site name
        job_title: Job title
        company_name: Company name
    
    Returns:
        Job object or None if no match found
    """
    return db.query(Job).filter(
        and_(
            Job.site == site,
            Job.job_title == job_title,
            Job.company_name == company_name
        )
    ).order_by(desc(Job.created_at)).first()


def get_all_matching_jobs(db: Session, site: str, job_title: str, company_name: str):
    """
    Get all jobs matching site, title, and company, ordered by creation date (newest first).
    
    Args:
        db: Database session
        site: Site name
        job_title: Job title
        company_name: Company name
    
    Returns:
        List of Job objects
    """
    return db.query(Job).filter(
        and_(
            Job.site == site,
            Job.job_title == job_title,
            Job.company_name == company_name
        )
    ).order_by(desc(Job.created_at)).all()


def get_last_successful_check_date(db: Session, job: Job):
    """
    Get the date of the last successful (HTTP 200) check for a job.
    
    Args:
        db: Database session
        job: Job object
    
    Returns:
        date object or None if no successful check exists
    """
    last_check = db.query(JobCheck).filter(
        and_(
            JobCheck.job_id == job.id,
            JobCheck.http_status == 200
        )
    ).order_by(desc(JobCheck.check_date)).first()
    
    return last_check.check_date if last_check else None


def get_last_failed_check_date(db: Session, job: Job):
    """
    Get the date of the last failed (non-200) check for a job.
    
    Args:
        db: Database session
        job: Job object
    
    Returns:
        date object or None if no failed check exists
    """
    last_check = db.query(JobCheck).filter(
        and_(
            JobCheck.job_id == job.id,
            JobCheck.http_status != 200,
            JobCheck.http_status.isnot(None)
        )
    ).order_by(desc(JobCheck.check_date)).first()
    
    return last_check.check_date if last_check else None


def is_job_dead(db: Session, job: Job):
    """
    Determine if a job is considered "dead" (removed/expired).
    A job is dead if its last check with an HTTP status was not 200.
    
    Args:
        db: Database session
        job: Job object
    
    Returns:
        bool: True if job is dead, False otherwise
    """
    last_check = db.query(JobCheck).filter(
        and_(
            JobCheck.job_id == job.id,
            JobCheck.http_status.isnot(None)
        )
    ).order_by(desc(JobCheck.check_date)).first()
    
    return last_check.http_status != 200 if last_check else False


def days_since_last_alive(db: Session, job: Job):
    """
    Calculate how many days since the job was last confirmed alive (HTTP 200).
    
    Args:
        db: Database session
        job: Job object
    
    Returns:
        int: Number of days since last alive check, or None if never alive
    """
    last_alive_date = get_last_successful_check_date(db, job)
    if not last_alive_date:
        return None
    
    today = date.today()
    delta = today - last_alive_date
    return delta.days


def should_create_new_job(db: Session, site: str, job_title: str, company_name: str):
    """
    Determine if a new job entry should be created for a position.
    
    A new job entry should be created if:
    1. No existing job matches the (site, title, company), OR
    2. The latest existing job is "dead" AND has been dead for longer than the resurrection threshold
    
    Args:
        db: Database session
        site: Site name
        job_title: Job title
        company_name: Company name
    
    Returns:
        tuple: (should_create: bool, existing_job: Job or None)
            - should_create: True if a new job should be created
            - existing_job: The latest existing job, or None if no match
    """
    latest_job = get_latest_job(db, site, job_title, company_name)
    
    # No existing job - create new
    if not latest_job:
        return True, None
    
    # Check if the latest job is dead
    if not is_job_dead(db, latest_job):
        # Job is still alive - reuse it
        return False, latest_job
    
    # Job is dead - check how long it's been dead
    days_dead = days_since_last_alive(db, latest_job)
    
    if days_dead is None:
        # Job was never confirmed alive, treat as still valid
        return False, latest_job
    
    threshold = Config.job_resurrection_threshold_days
    
    if days_dead >= threshold:
        # Job has been dead longer than threshold - create new entry
        return True, latest_job
    else:
        # Job has been dead but not long enough - reuse it
        return False, latest_job
