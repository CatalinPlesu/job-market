"""Job serialization to JSON format."""

from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .currency_converter import CurrencyConverter

from src.data_database import JobDetail


def serialize_job(job: JobDetail, currency_converter: Optional['CurrencyConverter'] = None) -> Dict[str, Any]:
    """
    Convert JobDetail object to JSON-serializable dictionary.
    
    Args:
        job: JobDetail database object.
        currency_converter: Optional CurrencyConverter for salary conversion.
        
    Returns:
        Dictionary representation of job.
    """
    # Get salary info
    min_salary = float(job.min_salary) if job.min_salary else None
    max_salary = float(job.max_salary) if job.max_salary else None
    currency = job.salary_currency.code if job.salary_currency else None
    
    # Build salary dict with original values
    salary_dict = {
        'min': min_salary,
        'max': max_salary,
        'currency': currency,
        'period': job.salary_period.name if job.salary_period else None,
    }
    
    # Add MDL conversion if converter available
    if currency_converter and currency:
        converted = currency_converter.convert_salary_range(min_salary, max_salary, currency)
        salary_dict['min_mdl'] = converted['min_mdl']
        salary_dict['max_mdl'] = converted['max_mdl']
    
    result = {
        'id': job.id,
        'title': job.title.name if job.title else None,
        'job_function': job.job_function.name if job.job_function else None,
        'specialization': job.specialization.name if job.specialization else None,
        'seniority_level': job.seniority_level.name if job.seniority_level else None,
        'company': job.company.name if job.company else job.company_name,
        'company_size': job.company_size.name if job.company_size else None,
        'location': {
            'city': job.city.name if job.city else None,
            'region': job.region.name if job.region else None,
            'country': job.country.name if job.country else None,
            'remote_work': job.remote_work.name if job.remote_work else None,
        },
        'salary': salary_dict,
        'employment': {
            'type': job.employment_type.name if job.employment_type else None,
            'contract': job.contract_type.name if job.contract_type else None,
            'schedule': job.work_schedule.name if job.work_schedule else None,
        },
        'requirements': {
            'education': job.education_level.name if job.education_level else None,
            'experience_years': job.experience_years,
            'languages': [lang.language for lang in job.languages] if job.languages else [],
            'hard_skills': [skill.name for skill in job.hard_skills] if job.hard_skills else [],
            'soft_skills': [skill.name for skill in job.soft_skills] if job.soft_skills else [],
            'certifications': [cert.name for cert in job.certifications] if job.certifications else [],
        },
        'benefits': [benefit.description for benefit in job.benefits] if job.benefits else [],
        'posting_date': job.posting_date.isoformat() if job.posting_date else None,
        'source': {
            'site': job.site,
            'url': job.job_url,
        },
        'parsed_view': {
            'responsibilities': [resp.description for resp in job.responsibilities] if job.responsibilities else [],
            'work_environment': [env.description for env in job.work_environment] if job.work_environment else [],
            'professional_development': [pd.description for pd in job.professional_development] if job.professional_development else [],
        }
    }
    
    # Add optional fields
    if job.industry:
        result['industry'] = job.industry.name
    if job.department:
        result['department'] = job.department.name
    if job.job_family:
        result['job_family'] = job.job_family.name
    if job.shift_details:
        result['shift_details'] = job.shift_details.name
    if job.travel_requirements:
        result['travel_requirements'] = job.travel_requirements.name
    
    return result


def serialize_jobs(jobs: List[JobDetail], currency_converter: Optional['CurrencyConverter'] = None) -> List[Dict[str, Any]]:
    """
    Convert list of JobDetail objects to JSON-serializable list.
    
    Args:
        jobs: List of JobDetail database objects.
        currency_converter: Optional CurrencyConverter for salary conversion.
        
    Returns:
        List of dictionary representations.
    """
    return [serialize_job(job, currency_converter) for job in jobs]
