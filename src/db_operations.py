from src.database import get_db, Job, JobCheck
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
import logging


def insert_job(job_title, company_name, job_url):
    """Insert new job (stage 1) - handles duplicates automatically"""
    db = get_db()
    try:
        # Check if job already exists
        existing_job = db.query(Job).filter(Job.job_url == job_url).first()

        if not existing_job:
            job = Job(
                job_title=job_title,
                company_name=company_name,
                job_url=job_url
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            logging.info(f"New job added: {job_title} at {company_name}")
            return job
        else:
            logging.info(f"Job already exists: {job_title}")
            return existing_job
    except IntegrityError:
        db.rollback()
        logging.warning(f"Duplicate URL attempted: {job_url}")
        return None
    finally:
        db.close()


def update_job_description(job_url, job_description):
    """Update job description (stage 2) - only updates if description is null"""
    db = get_db()
    try:
        job = db.query(Job).filter(Job.job_url == job_url).first()

        if job and job.job_description is None:
            job.job_description = job_description
            job.updated_at = datetime.utcnow()
            db.commit()
            logging.info(f"Description updated for: {job.job_title}")
            return True
        elif job and job.job_description is not None:
            logging.info(f"Description already exists for: {job_url}")
            return False
        else:
            logging.warning(f"Job not found: {job_url}")
            return False
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating description for {job_url}: {e}")
        return False
    finally:
        db.close()


def check_job_status(job_url, http_status):
    """Record job status check"""
    db = get_db()
    try:
        from datetime import date
        today = datetime.combine(date.today(), datetime.min.time())

        # Check if already checked today
        existing_check = db.query(JobCheck).filter(
            JobCheck.job_url == job_url,
            JobCheck.check_date >= today,
            JobCheck.check_date < today.replace(day=today.day + 1)
        ).first()

        if not existing_check:
            check = JobCheck(
                job_url=job_url,
                check_date=today,
                http_status=http_status
            )
            db.add(check)
            db.commit()
            logging.info(f"Status recorded: {job_url} - {http_status}")
        else:
            # Update existing check if needed
            existing_check.http_status = http_status
            db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Error recording status for {job_url}: {e}")
    finally:
        db.close()


def get_jobs_without_description():
    """Get all jobs that need description (stage 2 targets)"""
    db = get_db()
    try:
        jobs = db.query(Job).filter(Job.job_description == None).all()
        return jobs
    finally:
        db.close()


def get_all_jobs():
    """Get all jobs"""
    db = get_db()
    try:
        jobs = db.query(Job).all()
        return jobs
    finally:
        db.close()
