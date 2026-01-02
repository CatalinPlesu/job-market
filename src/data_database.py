"""
Data Database Module
Handles the data.db database for LLM-processed job data.
This database stores JobDetail records and all lookup tables.
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Text, 
    ForeignKey, Date, Numeric, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Type
from pathlib import Path
from config.settings import Config

# Ensure database directory exists
db_path = Path(Config.data_db_path)
db_path.parent.mkdir(parents=True, exist_ok=True)

# Create engine for data database
data_engine = create_engine('sqlite:///' + Config.data_db_path, echo=False)
DataBase = declarative_base()
DataSessionLocal = sessionmaker(bind=data_engine)


# ============ Factory Functions ============

def create_simple_lookup(table_name: str, field_name: str = 'name', 
                         field_length: int = 200) -> Type[DataBase]:
    """Create a simple lookup table class dynamically"""
    
    attrs = {
        '__tablename__': table_name,
        'id': Column(Integer, primary_key=True),
        field_name: Column(String(field_length), nullable=False, unique=True, index=True),
    }
    
    return type(table_name.title().replace('_', ''), (DataBase,), attrs)


def create_m2m_table(left_table: str, right_table: str) -> Table:
    """Create many-to-many association table"""
    table_name = f"{left_table}_{right_table}"
    
    return Table(
        table_name, DataBase.metadata,
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

class JobDetail(DataBase):
    """Processed/extracted job details - fully normalized"""
    __tablename__ = 'job_details'
    
    id = Column(Integer, primary_key=True)
    # Reference to job in scrape.db (stored as job_url for cross-database reference)
    job_url = Column(String(500), nullable=False, unique=True, index=True)
    
    # Original job data (copied from scrape.db for convenience)
    site = Column(String(200), nullable=False, index=True)
    job_title = Column(String(200), nullable=False)
    company_name = Column(String(200), nullable=False, index=True)
    job_description = Column(Text)
    
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
    llm_model = Column(String(200))
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships (One-to-One via Foreign Keys)
    # Using 'select' (lazy loading) to avoid massive JOIN queries that consume memory
    title = relationship("Titles", foreign_keys=[title_id], lazy='select')
    job_function = relationship("JobFunctions", foreign_keys=[job_function_id], lazy='select')
    seniority_level = relationship("SeniorityLevels", foreign_keys=[seniority_level_id], lazy='select')
    industry = relationship("Industries", foreign_keys=[industry_id], lazy='select')
    department = relationship("Departments", foreign_keys=[department_id], lazy='select')
    job_family = relationship("JobFamilies", foreign_keys=[job_family_id], lazy='select')
    specialization = relationship("Specializations", foreign_keys=[specialization_id], lazy='select')
    education_level = relationship("EducationLevels", foreign_keys=[required_education_id], lazy='select')
    employment_type = relationship("EmploymentTypes", foreign_keys=[employment_type_id], lazy='select')
    contract_type = relationship("ContractTypes", foreign_keys=[contract_type_id], lazy='select')
    work_schedule = relationship("WorkSchedules", foreign_keys=[work_schedule_id], lazy='select')
    shift_details = relationship("ShiftDetails", foreign_keys=[shift_details_id], lazy='select')
    remote_work = relationship("RemoteWorkOptions", foreign_keys=[remote_work_id], lazy='select')
    travel_requirements = relationship("TravelRequirements", foreign_keys=[travel_required_id], lazy='select')
    salary_currency = relationship("Currencies", foreign_keys=[salary_currency_id], lazy='select')
    salary_period = relationship("SalaryPeriods", foreign_keys=[salary_period_id], lazy='select')
    city = relationship("Cities", foreign_keys=[city_id], lazy='select')
    region = relationship("Regions", foreign_keys=[region_id], lazy='select')
    country = relationship("Countries", foreign_keys=[country_id], lazy='select')
    company = relationship("Companies", foreign_keys=[company_name_id], lazy='select')
    company_size = relationship("CompanySizes", foreign_keys=[company_size_id], lazy='select')
    
    # Relationships (One-to-Many)
    responsibilities = relationship("Responsibility", back_populates="job_detail", lazy='select')
    languages = relationship("JobLanguage", back_populates="job_detail", lazy='select')
    
    # Relationships (Many-to-Many)
    hard_skills = relationship("HardSkills", secondary=job_hard_skills, lazy='select')
    soft_skills = relationship("SoftSkills", secondary=job_soft_skills, lazy='select')
    certifications = relationship("Certifications", secondary=job_certifications, lazy='select')
    licenses = relationship("Licenses", secondary=job_licenses, lazy='select')
    benefits = relationship("Benefits", secondary=job_benefits, lazy='select')
    work_environment = relationship("WorkEnvironment", secondary=job_work_environment, lazy='select')
    professional_development = relationship("ProfessionalDevelopment", secondary=job_professional_development, lazy='select')
    work_life_balance = relationship("WorkLifeBalance", secondary=job_work_life_balance, lazy='select')
    physical_requirements = relationship("PhysicalRequirements", secondary=job_physical_requirements, lazy='select')
    work_conditions = relationship("WorkConditions", secondary=job_work_conditions, lazy='select')
    special_requirements = relationship("SpecialRequirements", secondary=job_special_requirements, lazy='select')


# ============ Child Tables (One-to-Many) ============

class Responsibility(DataBase):
    """Job responsibilities"""
    __tablename__ = 'responsibilities'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    order = Column(Integer, default=0)
    
    job_detail = relationship("JobDetail", back_populates="responsibilities")


class JobLanguage(DataBase):
    """Languages required for job with proficiency level"""
    __tablename__ = 'job_languages'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False, index=True)
    language = Column(String(100), nullable=False)
    proficiency = Column(String(50))
    
    job_detail = relationship("JobDetail", back_populates="languages")


class ContactEmail(DataBase):
    """Contact emails"""
    __tablename__ = 'contact_emails'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False, index=True)
    email = Column(String(200), nullable=False)


class ContactPhone(DataBase):
    """Contact phones"""
    __tablename__ = 'contact_phones'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False, index=True)
    phone = Column(String(50), nullable=False)


def get_data_db():
    """Get data database session"""
    db = DataSessionLocal()
    try:
        return db
    finally:
        pass


def migrate_schema():
    """Migrate the database schema to add any missing columns
    
    This function is called automatically when the module is loaded to ensure
    the database schema is up to date. It checks for missing columns and adds
    them if necessary.
    """
    from sqlalchemy import inspect, text
    import logging
    
    logger = logging.getLogger(__name__)
    
    inspector = inspect(data_engine)
    
    # Check if job_details table exists
    if 'job_details' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('job_details')]
        
        # Add llm_model column if it doesn't exist
        if 'llm_model' not in columns:
            with data_engine.begin() as conn:
                conn.execute(text('ALTER TABLE job_details ADD COLUMN llm_model VARCHAR(200)'))
            logger.info("Added llm_model column to job_details table")


# Create all tables in data database
DataBase.metadata.create_all(data_engine)

# Run migrations automatically to handle schema updates
# Note: This runs at module import time to ensure schema compatibility
try:
    migrate_schema()
except Exception as e:
    import logging
    logging.getLogger(__name__).error(f"Failed to run database migration: {e}")
