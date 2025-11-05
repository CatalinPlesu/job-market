from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any, Optional, List
from datetime import datetime, date

# Use relative import since both files are in src/
from .database import (
    JobDetail, Title, JobFunction, SeniorityLevel, Industry, Department,
    JobFamily, Specialization, EducationLevel, EmploymentType, ContractType,
    WorkSchedule, ShiftDetail, RemoteWork, TravelRequirement, Currency,
    SalaryPeriod, City, Region, Country, FullAddress, Company, CompanySize,
    ContactPerson, HardSkill, SoftSkill, Certification, License, Benefit,
    WorkEnvironment, ProfessionalDevelopment, WorkLifeBalance,
    PhysicalRequirement, WorkCondition, SpecialRequirement, Responsibility,
    JobLanguage, ContactEmail, ContactPhone, SessionLocal, Job
)


def get_or_create(db: Session, model, **kwargs):
    """
    Get existing record or create new one.
    Returns the record instance.
    """
    # Try to find existing
    instance = db.query(model).filter_by(**kwargs).first()
    
    if instance:
        return instance
    
    # Create new
    instance = model(**kwargs)
    db.add(instance)
    db.flush()  # Get the ID without committing
    return instance


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse date string to date object"""
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def insert_job_detail(db: Session, job_id: int, parsed_json: Dict[str, Any]) -> JobDetail:
    """
    Insert parsed job JSON into normalized database structure.
    
    Args:
        db: SQLAlchemy session
        job_id: ID of the raw Job record
        parsed_json: Dictionary from AI parsing (matching your JSON schema)
    
    Returns:
        JobDetail: The created JobDetail instance
    
    Raises:
        ValueError: If job_id doesn't exist or JobDetail already exists for this job
    """
    
    # Check if JobDetail already exists for this job
    existing = db.query(JobDetail).filter_by(job_id=job_id).first()
    if existing:
        raise ValueError(f"JobDetail already exists for job_id {job_id}")
    
    # Create JobDetail instance
    job_detail = JobDetail(job_id=job_id)
    
    # === Handle single-value normalized fields ===
    
    if parsed_json.get('title'):
        title = get_or_create(db, Title, name=parsed_json['title'])
        job_detail.title_id = title.id
    
    if parsed_json.get('job_function'):
        job_function = get_or_create(db, JobFunction, name=parsed_json['job_function'])
        job_detail.job_function_id = job_function.id
    
    if parsed_json.get('seniority_level'):
        seniority = get_or_create(db, SeniorityLevel, name=parsed_json['seniority_level'])
        job_detail.seniority_level_id = seniority.id
    
    if parsed_json.get('industry'):
        industry = get_or_create(db, Industry, name=parsed_json['industry'])
        job_detail.industry_id = industry.id
    
    if parsed_json.get('department'):
        department = get_or_create(db, Department, name=parsed_json['department'])
        job_detail.department_id = department.id
    
    if parsed_json.get('job_family'):
        job_family = get_or_create(db, JobFamily, name=parsed_json['job_family'])
        job_detail.job_family_id = job_family.id
    
    if parsed_json.get('specialization'):
        specialization = get_or_create(db, Specialization, name=parsed_json['specialization'])
        job_detail.specialization_id = specialization.id
    
    if parsed_json.get('required_education'):
        education = get_or_create(db, EducationLevel, name=parsed_json['required_education'])
        job_detail.required_education_id = education.id
    
    if parsed_json.get('employment_type'):
        employment = get_or_create(db, EmploymentType, name=parsed_json['employment_type'])
        job_detail.employment_type_id = employment.id
    
    if parsed_json.get('contract_type'):
        contract = get_or_create(db, ContractType, name=parsed_json['contract_type'])
        job_detail.contract_type_id = contract.id
    
    if parsed_json.get('work_schedule'):
        schedule = get_or_create(db, WorkSchedule, name=parsed_json['work_schedule'])
        job_detail.work_schedule_id = schedule.id
    
    if parsed_json.get('shift_details'):
        shift = get_or_create(db, ShiftDetail, name=parsed_json['shift_details'])
        job_detail.shift_details_id = shift.id
    
    if parsed_json.get('remote_work'):
        remote = get_or_create(db, RemoteWork, name=parsed_json['remote_work'])
        job_detail.remote_work_id = remote.id
    
    if parsed_json.get('travel_required'):
        travel = get_or_create(db, TravelRequirement, name=parsed_json['travel_required'])
        job_detail.travel_required_id = travel.id
    
    if parsed_json.get('salary_currency'):
        currency = get_or_create(db, Currency, code=parsed_json['salary_currency'])
        job_detail.salary_currency_id = currency.id
    
    if parsed_json.get('salary_period'):
        period = get_or_create(db, SalaryPeriod, name=parsed_json['salary_period'])
        job_detail.salary_period_id = period.id
    
    # Location fields
    if parsed_json.get('city'):
        city = get_or_create(db, City, name=parsed_json['city'])
        job_detail.city_id = city.id
    
    if parsed_json.get('region'):
        region = get_or_create(db, Region, name=parsed_json['region'])
        job_detail.region_id = region.id
    
    if parsed_json.get('country'):
        country = get_or_create(db, Country, name=parsed_json['country'])
        job_detail.country_id = country.id
    
    if parsed_json.get('full_address'):
        address = get_or_create(db, FullAddress, address=parsed_json['full_address'])
        job_detail.full_address_id = address.id
    
    # Company
    if parsed_json.get('company_name'):
        company = get_or_create(db, Company, name=parsed_json['company_name'])
        job_detail.company_name_id = company.id
    
    if parsed_json.get('company_size'):
        size = get_or_create(db, CompanySize, name=parsed_json['company_size'])
        job_detail.company_size_id = size.id
    
    if parsed_json.get('contact_person'):
        person = get_or_create(db, ContactPerson, name=parsed_json['contact_person'])
        job_detail.contact_person_id = person.id
    
    # === Direct numeric/scalar fields ===
    
    job_detail.min_salary = parsed_json.get('min_salary')
    job_detail.max_salary = parsed_json.get('max_salary')
    job_detail.experience_years = parsed_json.get('experience_years')
    job_detail.original_language = parsed_json.get('original_language')
    job_detail.posting_date = parse_date(parsed_json.get('posting_date'))
    job_detail.processed_at = datetime.utcnow()
    
    # Add to session
    db.add(job_detail)
    db.flush()  # Get job_detail.id
    
    # === Handle many-to-many relationships ===
    
    # Hard skills
    if parsed_json.get('hard_skills'):
        for skill_name in parsed_json['hard_skills']:
            skill = get_or_create(db, HardSkill, name=skill_name)
            job_detail.hard_skills.append(skill)
    
    # Soft skills
    if parsed_json.get('soft_skills'):
        for skill_name in parsed_json['soft_skills']:
            skill = get_or_create(db, SoftSkill, name=skill_name)
            job_detail.soft_skills.append(skill)
    
    # Certifications
    if parsed_json.get('certifications'):
        for cert_name in parsed_json['certifications']:
            cert = get_or_create(db, Certification, name=cert_name)
            job_detail.certifications.append(cert)
    
    # Licenses
    if parsed_json.get('licenses_required'):
        for license_name in parsed_json['licenses_required']:
            lic = get_or_create(db, License, name=license_name)
            job_detail.licenses.append(lic)
    
    # Benefits
    if parsed_json.get('benefits'):
        for benefit_desc in parsed_json['benefits']:
            benefit = get_or_create(db, Benefit, description=benefit_desc)
            job_detail.benefits.append(benefit)
    
    # Work environment
    if parsed_json.get('work_environment'):
        for env_desc in parsed_json['work_environment']:
            env = get_or_create(db, WorkEnvironment, description=env_desc)
            job_detail.work_environment.append(env)
    
    # Professional development
    if parsed_json.get('professional_development'):
        for dev_desc in parsed_json['professional_development']:
            dev = get_or_create(db, ProfessionalDevelopment, description=dev_desc)
            job_detail.professional_development.append(dev)
    
    # Work-life balance
    if parsed_json.get('work_life_balance'):
        for balance_desc in parsed_json['work_life_balance']:
            balance = get_or_create(db, WorkLifeBalance, description=balance_desc)
            job_detail.work_life_balance.append(balance)
    
    # Physical requirements
    if parsed_json.get('physical_requirements'):
        for req_desc in parsed_json['physical_requirements']:
            req = get_or_create(db, PhysicalRequirement, description=req_desc)
            job_detail.physical_requirements.append(req)
    
    # Work conditions
    if parsed_json.get('work_conditions'):
        for cond_desc in parsed_json['work_conditions']:
            cond = get_or_create(db, WorkCondition, description=cond_desc)
            job_detail.work_conditions.append(cond)
    
    # Special requirements
    if parsed_json.get('special_requirements'):
        for spec_desc in parsed_json['special_requirements']:
            spec = get_or_create(db, SpecialRequirement, description=spec_desc)
            job_detail.special_requirements.append(spec)
    
    # === Handle one-to-many relationships ===
    
    # Responsibilities
    if parsed_json.get('responsibilities'):
        for idx, resp_desc in enumerate(parsed_json['responsibilities']):
            responsibility = Responsibility(
                job_detail_id=job_detail.id,
                description=resp_desc,
                order=idx
            )
            db.add(responsibility)
    
    # Languages with proficiency
    if parsed_json.get('languages'):
        lang_proficiency = parsed_json.get('language_proficiency', {})
        for lang in parsed_json['languages']:
            job_lang = JobLanguage(
                job_detail_id=job_detail.id,
                language=lang,
                proficiency=lang_proficiency.get(lang)
            )
            db.add(job_lang)
    
    # Contact emails
    if parsed_json.get('contact_emails'):
        for email in parsed_json['contact_emails']:
            contact_email = ContactEmail(
                job_detail_id=job_detail.id,
                email=email
            )
            db.add(contact_email)
    
    # Contact phones
    if parsed_json.get('contact_phones'):
        for phone in parsed_json['contact_phones']:
            contact_phone = ContactPhone(
                job_detail_id=job_detail.id,
                phone=phone
            )
            db.add(contact_phone)
    
    # Commit all changes
    db.commit()
    db.refresh(job_detail)
    
    return job_detail

def job_detail_to_dict(db: Session, job_id: int) -> Optional[Dict[str, Any]]:
    """
    Reconstruct the parsed JSON object from a JobDetail record.
    
    Args:
        db: SQLAlchemy session
        job_id: ID of the Job record
    
    Returns:
        Dictionary matching the original JSON schema, or None if not found
    """
    
    # Fetch JobDetail with all relationships loaded
    job_detail = db.query(JobDetail).filter_by(job_id=job_id).first()
    
    if not job_detail:
        return None
    
    # Helper to convert date to string
    def date_to_str(d: Optional[date]) -> Optional[str]:
        return d.strftime('%Y-%m-%d') if d else None
    
    # Build the dictionary
    result = {
        # Basic info
        "title": job_detail.title.name if job_detail.title else None,
        "job_function": job_detail.job_function.name if job_detail.job_function else None,
        "seniority_level": job_detail.seniority_level.name if job_detail.seniority_level else None,
        "industry": job_detail.industry.name if job_detail.industry else None,
        "department": job_detail.department.name if job_detail.department else None,
        "job_family": job_detail.job_family.name if job_detail.job_family else None,
        "specialization": job_detail.specialization.name if job_detail.specialization else None,
        
        # Salary
        "min_salary": float(job_detail.min_salary) if job_detail.min_salary else None,
        "max_salary": float(job_detail.max_salary) if job_detail.max_salary else None,
        "salary_currency": job_detail.salary_currency.code if job_detail.salary_currency else None,
        "salary_period": job_detail.salary_period.name if job_detail.salary_period else None,
        
        # Requirements
        "required_education": job_detail.required_education.name if job_detail.required_education else None,
        "experience_years": job_detail.experience_years,
        
        # Languages - reconstruct list and proficiency dict
        "languages": [jl.language for jl in job_detail.languages] if job_detail.languages else None,
        "language_proficiency": {jl.language: jl.proficiency for jl in job_detail.languages if jl.proficiency} if job_detail.languages else None,
        
        # Skills (many-to-many)
        "hard_skills": [skill.name for skill in job_detail.hard_skills] if job_detail.hard_skills else None,
        "soft_skills": [skill.name for skill in job_detail.soft_skills] if job_detail.soft_skills else None,
        
        # Certifications and licenses
        "certifications": [cert.name for cert in job_detail.certifications] if job_detail.certifications else None,
        "licenses_required": [lic.name for lic in job_detail.licenses] if job_detail.licenses else None,
        
        # Responsibilities (ordered)
        "responsibilities": [resp.description for resp in sorted(job_detail.responsibilities, key=lambda r: r.order)] if job_detail.responsibilities else None,
        
        # Work arrangement
        "employment_type": job_detail.employment_type.name if job_detail.employment_type else None,
        "contract_type": job_detail.contract_type.name if job_detail.contract_type else None,
        "work_schedule": job_detail.work_schedule.name if job_detail.work_schedule else None,
        "shift_details": job_detail.shift_details.name if job_detail.shift_details else None,
        "remote_work": job_detail.remote_work.name if job_detail.remote_work else None,
        "travel_required": job_detail.travel_required.name if job_detail.travel_required else None,
        
        # Location
        "city": job_detail.city.name if job_detail.city else None,
        "region": job_detail.region.name if job_detail.region else None,
        "country": job_detail.country.name if job_detail.country else None,
        "full_address": job_detail.full_address.address if job_detail.full_address else None,
        
        # Company
        "company_name": job_detail.company_name.name if job_detail.company_name else None,
        "company_size": job_detail.company_size.name if job_detail.company_size else None,
        
        # Contact info
        "contact_emails": [email.email for email in job_detail.contact_emails] if job_detail.contact_emails else None,
        "contact_phones": [phone.phone for phone in job_detail.contact_phones] if job_detail.contact_phones else None,
        "contact_person": job_detail.contact_person.name if job_detail.contact_person else None,
        
        # Benefits and perks
        "benefits": [benefit.description for benefit in job_detail.benefits] if job_detail.benefits else None,
        "work_environment": [env.description for env in job_detail.work_environment] if job_detail.work_environment else None,
        "professional_development": [dev.description for dev in job_detail.professional_development] if job_detail.professional_development else None,
        "work_life_balance": [balance.description for balance in job_detail.work_life_balance] if job_detail.work_life_balance else None,
        
        # Requirements and conditions
        "physical_requirements": [req.description for req in job_detail.physical_requirements] if job_detail.physical_requirements else None,
        "work_conditions": [cond.description for cond in job_detail.work_conditions] if job_detail.work_conditions else None,
        "special_requirements": [spec.description for spec in job_detail.special_requirements] if job_detail.special_requirements else None,
        
        # Metadata
        "posting_date": date_to_str(job_detail.posting_date),
        "original_language": job_detail.original_language
    }
    
    return result


# === Usage example ===
if __name__ == "__main__":
    # Example parsed JSON from AI
    example_json = {
        "title": "Senior Python Developer",
        "job_function": "Software Development",
        "seniority_level": "senior",
        "industry": "Technology",
        "department": "Engineering",
        "job_family": "Software Engineering",
        "specialization": "Backend Development",
        "min_salary": 50000,
        "max_salary": 80000,
        "salary_currency": "eur",
        "salary_period": "year",
        "required_education": "bachelor",
        "experience_years": 5,
        "languages": ["English", "Romanian"],
        "language_proficiency": {"English": "fluent", "Romanian": "native"},
        "hard_skills": ["Python", "Django", "PostgreSQL", "Docker"],
        "soft_skills": ["Communication", "Teamwork", "Problem Solving"],
        "certifications": ["AWS Certified Developer"],
        "licenses_required": None,
        "responsibilities": [
            "Design and implement backend services",
            "Collaborate with frontend team",
            "Write technical documentation"
        ],
        "employment_type": "full-time",
        "contract_type": "permanent",
        "work_schedule": "flexible",
        "shift_details": None,
        "remote_work": "hybrid",
        "travel_required": "occasional",
        "city": "Chisinau",
        "region": "Chișinău Municipality",
        "country": "Moldova",
        "full_address": "123 Main St, Chisinau, Moldova",
        "company_name": "TechCorp SRL",
        "company_size": "medium",
        "contact_emails": ["hr@techcorp.md"],
        "contact_phones": ["+373 22 123456"],
        "contact_person": "John Doe",
        "benefits": ["Health insurance", "Meal tickets", "Training budget"],
        "work_environment": ["Modern office", "Collaborative team"],
        "professional_development": ["Conferences", "Online courses"],
        "work_life_balance": ["Flexible hours", "Remote work option"],
        "physical_requirements": None,
        "work_conditions": ["Office environment"],
        "special_requirements": ["Must have work permit"],
        "posting_date": "2025-11-05",
        "original_language": "ro"
    }
    
    db = SessionLocal()
    try:
        # Assuming job_id 1 exists in jobs table
        job_detail = insert_job_detail(db, job_id=1, parsed_json=example_json)
        print(f"Successfully created JobDetail with id: {job_detail.id}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()
