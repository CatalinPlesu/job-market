from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Text, 
    ForeignKey, Date, Numeric, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Type
from config.settings import Config

# Create engine with configurable database path
engine = create_engine('sqlite:///' + Config.db_path, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


# ============ Factory Functions ============

def create_simple_lookup(table_name: str, field_name: str = 'name', 
                         field_length: int = 200) -> Type[Base]:
    """Create a simple lookup table class dynamically"""
    
    attrs = {
        '__tablename__': table_name,
        'id': Column(Integer, primary_key=True),
        field_name: Column(String(field_length), nullable=False, unique=True, index=True),
    }
    
    return type(table_name.title().replace('_', ''), (Base,), attrs)


def create_m2m_table(left_table: str, right_table: str) -> Table:
    """Create many-to-many association table"""
    table_name = f"{left_table}_{right_table}"
    
    return Table(
        table_name, Base.metadata,
        Column(f'{left_table}_id', Integer, ForeignKey(f'{left_table}.id'), primary_key=True),
        Column(f'{right_table}_id', Integer, ForeignKey(f'{right_table}.id'), primary_key=True)
    )


# ============ Lookup Tables - Simple String Lookups ============

Titles = create_simple_lookup('titles')
JobFunctions = create_simple_lookup('job_functions')
SeniorityLevels = create_simple_lookup('seniority_levels')
Industries = create_simple_lookup('industries')
Departments = create_simple_lookup('departments')
JobFamilies = create_simple_lookup('job_families')
Specializations = create_simple_lookup('specializations')
EducationLevels = create_simple_lookup('education_levels')
EmploymentTypes = create_simple_lookup('employment_types')
ContractTypes = create_simple_lookup('contract_types')
WorkSchedules = create_simple_lookup('work_schedules')
ShiftDetails = create_simple_lookup('shift_details')
RemoteWorkOptions = create_simple_lookup('remote_work_options')
TravelRequirements = create_simple_lookup('travel_requirements')
SalaryPeriods = create_simple_lookup('salary_periods')
Cities = create_simple_lookup('cities')
Regions = create_simple_lookup('regions')
Countries = create_simple_lookup('countries')
Companies = create_simple_lookup('companies')
CompanySizes = create_simple_lookup('company_sizes')
ContactPersons = create_simple_lookup('contact_persons')

# Special lookups with different field names/lengths
Currencies = create_simple_lookup('currencies', 'code', 10)
FullAddresses = create_simple_lookup('full_addresses', 'address', 500)


# ============ Lookup Tables - Many-to-Many ============

HardSkills = create_simple_lookup('hard_skills', 'name', 200)
SoftSkills = create_simple_lookup('soft_skills', 'name', 200)
Certifications = create_simple_lookup('certifications', 'name', 200)
Licenses = create_simple_lookup('licenses', 'name', 200)
Benefits = create_simple_lookup('benefits', 'description', 500)
WorkEnvironment = create_simple_lookup('work_environment', 'description', 500)
ProfessionalDevelopment = create_simple_lookup('professional_development', 'description', 500)
WorkLifeBalance = create_simple_lookup('work_life_balance', 'description', 500)
PhysicalRequirements = create_simple_lookup('physical_requirements', 'description', 500)
WorkConditions = create_simple_lookup('work_conditions', 'description', 500)
SpecialRequirements = create_simple_lookup('special_requirements', 'description', 500)


# ============ Association Tables (Many-to-Many) ============

job_hard_skills = create_m2m_table('job_details', 'hard_skills')
job_soft_skills = create_m2m_table('job_details', 'soft_skills')
job_certifications = create_m2m_table('job_details', 'certifications')
job_licenses = create_m2m_table('job_details', 'licenses')
job_benefits = create_m2m_table('job_details', 'benefits')
job_work_environment = create_m2m_table('job_details', 'work_environment')
job_professional_development = create_m2m_table('job_details', 'professional_development')
job_work_life_balance = create_m2m_table('job_details', 'work_life_balance')
job_physical_requirements = create_m2m_table('job_details', 'physical_requirements')
job_work_conditions = create_m2m_table('job_details', 'work_conditions')
job_special_requirements = create_m2m_table('job_details', 'special_requirements')


# ============ Main Tables ============

class Job(Base):
    """Original job posting"""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    site = Column(String(200), nullable=False, index=True)
    job_title = Column(String(200), nullable=False)
    company_name = Column(String(200), nullable=False, index=True)
    job_url = Column(String(500), nullable=False, unique=True)
    job_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    detail = relationship("JobDetail", back_populates="job", uselist=False, cascade="all, delete-orphan", lazy="select")
    checks = relationship("JobCheck", back_populates="job", cascade="all, delete-orphan")


class JobDetail(Base):
    """Processed/extracted job details - fully normalized"""
    __tablename__ = 'job_details'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False, unique=True, index=True)
    
    # Job classification
    title_id = Column(Integer, ForeignKey('titles.id'))
    job_function_id = Column(Integer, ForeignKey('job_functions.id'))
    seniority_level_id = Column(Integer, ForeignKey('seniority_levels.id'))
    industry_id = Column(Integer, ForeignKey('industries.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    job_family_id = Column(Integer, ForeignKey('job_families.id'))
    specialization_id = Column(Integer, ForeignKey('specializations.id'))
    
    # Compensation
    min_salary = Column(Numeric(12, 2))
    max_salary = Column(Numeric(12, 2))
    salary_currency_id = Column(Integer, ForeignKey('currencies.id'))
    salary_period_id = Column(Integer, ForeignKey('salary_periods.id'))
    
    # Requirements
    required_education_id = Column(Integer, ForeignKey('education_levels.id'))
    experience_years = Column(Integer)
    
    # Work arrangement
    employment_type_id = Column(Integer, ForeignKey('employment_types.id'))
    contract_type_id = Column(Integer, ForeignKey('contract_types.id'))
    work_schedule_id = Column(Integer, ForeignKey('work_schedules.id'))
    shift_details_id = Column(Integer, ForeignKey('shift_details.id'))
    remote_work_id = Column(Integer, ForeignKey('remote_work_options.id'))
    travel_required_id = Column(Integer, ForeignKey('travel_requirements.id'))
    
    # Location
    city_id = Column(Integer, ForeignKey('cities.id'))
    region_id = Column(Integer, ForeignKey('regions.id'))
    country_id = Column(Integer, ForeignKey('countries.id'))
    full_address_id = Column(Integer, ForeignKey('full_addresses.id'))
    
    # Company information
    company_name_id = Column(Integer, ForeignKey('companies.id'))
    company_size_id = Column(Integer, ForeignKey('company_sizes.id'))
    contact_person_id = Column(Integer, ForeignKey('contact_persons.id'))
    
    # Metadata
    posting_date = Column(Date)
    original_language = Column(String(10))
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships - Parent
    job = relationship("Job", back_populates="detail")
    
    # Relationships - Foreign Key Lookups
    title = relationship("Titles", foreign_keys=[title_id])
    job_function = relationship("JobFunctions", foreign_keys=[job_function_id])
    seniority_level = relationship("SeniorityLevels", foreign_keys=[seniority_level_id])
    industry = relationship("Industries", foreign_keys=[industry_id])
    department = relationship("Departments", foreign_keys=[department_id])
    job_family = relationship("JobFamilies", foreign_keys=[job_family_id])
    specialization = relationship("Specializations", foreign_keys=[specialization_id])
    required_education = relationship("EducationLevels", foreign_keys=[required_education_id])
    employment_type = relationship("EmploymentTypes", foreign_keys=[employment_type_id])
    contract_type = relationship("ContractTypes", foreign_keys=[contract_type_id])
    work_schedule = relationship("WorkSchedules", foreign_keys=[work_schedule_id])
    shift_details = relationship("ShiftDetails", foreign_keys=[shift_details_id])
    remote_work = relationship("RemoteWorkOptions", foreign_keys=[remote_work_id])
    travel_required = relationship("TravelRequirements", foreign_keys=[travel_required_id])
    salary_currency = relationship("Currencies", foreign_keys=[salary_currency_id])
    salary_period = relationship("SalaryPeriods", foreign_keys=[salary_period_id])
    city = relationship("Cities", foreign_keys=[city_id])
    region = relationship("Regions", foreign_keys=[region_id])
    country = relationship("Countries", foreign_keys=[country_id])
    full_address = relationship("FullAddresses", foreign_keys=[full_address_id])
    company_name = relationship("Companies", foreign_keys=[company_name_id])
    company_size = relationship("CompanySizes", foreign_keys=[company_size_id])
    contact_person = relationship("ContactPersons", foreign_keys=[contact_person_id])
    
    # Relationships - One-to-Many (children)
    responsibilities = relationship("Responsibility", back_populates="job_detail", cascade="all, delete-orphan")
    languages = relationship("JobLanguage", back_populates="job_detail", cascade="all, delete-orphan")
    contact_emails = relationship("ContactEmail", back_populates="job_detail", cascade="all, delete-orphan")
    contact_phones = relationship("ContactPhone", back_populates="job_detail", cascade="all, delete-orphan")
    
    # Relationships - Many-to-Many
    hard_skills = relationship("HardSkills", secondary=job_hard_skills)
    soft_skills = relationship("SoftSkills", secondary=job_soft_skills)
    certifications = relationship("Certifications", secondary=job_certifications)
    licenses = relationship("Licenses", secondary=job_licenses)
    benefits = relationship("Benefits", secondary=job_benefits)
    work_environment = relationship("WorkEnvironment", secondary=job_work_environment)
    professional_development = relationship("ProfessionalDevelopment", secondary=job_professional_development)
    work_life_balance = relationship("WorkLifeBalance", secondary=job_work_life_balance)
    physical_requirements = relationship("PhysicalRequirements", secondary=job_physical_requirements)
    work_conditions = relationship("WorkConditions", secondary=job_work_conditions)
    special_requirements = relationship("SpecialRequirements", secondary=job_special_requirements)


# ============ Child Tables (One-to-Many) ============

class Responsibility(Base):
    """Job responsibilities"""
    __tablename__ = 'responsibilities'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    order = Column(Integer, default=0)
    
    job_detail = relationship("JobDetail", back_populates="responsibilities")


class JobLanguage(Base):
    """Languages required for job with proficiency level"""
    __tablename__ = 'job_languages'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False, index=True)
    language = Column(String(100), nullable=False)
    proficiency = Column(String(50))
    
    job_detail = relationship("JobDetail", back_populates="languages")


class ContactEmail(Base):
    """Contact emails"""
    __tablename__ = 'contact_emails'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False, index=True)
    email = Column(String(200), nullable=False)
    
    job_detail = relationship("JobDetail", back_populates="contact_emails")


class ContactPhone(Base):
    """Contact phones"""
    __tablename__ = 'contact_phones'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    
    job_detail = relationship("JobDetail", back_populates="contact_phones")


class JobCheck(Base):
    """Track when jobs were checked and their status"""
    __tablename__ = 'job_checks'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False, index=True)
    check_date = Column(Date, nullable=False)
    http_status = Column(Integer)
    
    job = relationship("Job", back_populates="checks")


# ============ Database Initialization ============

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass


# Create all tables
Base.metadata.create_all(engine)
