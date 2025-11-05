from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Text, Boolean, 
    Index, ForeignKey, Date, Numeric, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config.settings import Config

# Create engine
engine = create_engine('sqlite:///' + Config.db_path, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


# ============ Many-to-Many Association Tables ============

job_hard_skills = Table('job_hard_skills', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('hard_skill_id', Integer, ForeignKey('hard_skills.id'), primary_key=True)
)

job_soft_skills = Table('job_soft_skills', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('soft_skill_id', Integer, ForeignKey('soft_skills.id'), primary_key=True)
)

job_certifications = Table('job_certifications', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('certification_id', Integer, ForeignKey('certifications.id'), primary_key=True)
)

job_licenses = Table('job_licenses', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('license_id', Integer, ForeignKey('licenses.id'), primary_key=True)
)

job_benefits = Table('job_benefits', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('benefit_id', Integer, ForeignKey('benefits.id'), primary_key=True)
)

job_work_environment = Table('job_work_environment', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('work_environment_id', Integer, ForeignKey('work_environment.id'), primary_key=True)
)

job_professional_development = Table('job_professional_development', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('professional_development_id', Integer, ForeignKey('professional_development.id'), primary_key=True)
)

job_work_life_balance = Table('job_work_life_balance', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('work_life_balance_id', Integer, ForeignKey('work_life_balance.id'), primary_key=True)
)

job_physical_requirements = Table('job_physical_requirements', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('physical_requirement_id', Integer, ForeignKey('physical_requirements.id'), primary_key=True)
)

job_work_conditions = Table('job_work_conditions', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('work_condition_id', Integer, ForeignKey('work_conditions.id'), primary_key=True)
)

job_special_requirements = Table('job_special_requirements', Base.metadata,
    Column('job_detail_id', Integer, ForeignKey('job_details.id'), primary_key=True),
    Column('special_requirement_id', Integer, ForeignKey('special_requirements.id'), primary_key=True)
)


# ============ Normalized Lookup Tables - Each Field Separate ============

class Title(Base):
    """Job titles - normalized"""
    __tablename__ = 'titles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="title")

class JobFunction(Base):
    """Job functions - normalized"""
    __tablename__ = 'job_functions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="job_function")

class SeniorityLevel(Base):
    """Seniority levels - normalized"""
    __tablename__ = 'seniority_levels'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="seniority_level")

class Industry(Base):
    """Industries - normalized"""
    __tablename__ = 'industries'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="industry")

class Department(Base):
    """Departments - normalized"""
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="department")

class JobFamily(Base):
    """Job families - normalized"""
    __tablename__ = 'job_families'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="job_family")

class Specialization(Base):
    """Specializations - normalized"""
    __tablename__ = 'specializations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="specialization")

class EducationLevel(Base):
    """Education levels - normalized"""
    __tablename__ = 'education_levels'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="required_education")

class EmploymentType(Base):
    """Employment types - normalized"""
    __tablename__ = 'employment_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="employment_type")

class ContractType(Base):
    """Contract types - normalized"""
    __tablename__ = 'contract_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="contract_type")

class WorkSchedule(Base):
    """Work schedules - normalized"""
    __tablename__ = 'work_schedules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="work_schedule")

class ShiftDetail(Base):
    """Shift details - normalized"""
    __tablename__ = 'shift_details'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="shift_details")

class RemoteWork(Base):
    """Remote work options - normalized"""
    __tablename__ = 'remote_work_options'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="remote_work")

class TravelRequirement(Base):
    """Travel requirements - normalized"""
    __tablename__ = 'travel_requirements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="travel_required")

class Currency(Base):
    """Currencies - normalized"""
    __tablename__ = 'currencies'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="salary_currency")

class SalaryPeriod(Base):
    """Salary periods - normalized"""
    __tablename__ = 'salary_periods'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="salary_period")

class City(Base):
    """Cities - normalized"""
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="city")

class Region(Base):
    """Regions - normalized"""
    __tablename__ = 'regions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="region")

class Country(Base):
    """Countries - normalized"""
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="country")

class FullAddress(Base):
    """Full addresses - normalized"""
    __tablename__ = 'full_addresses'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(500), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="full_address")

class Company(Base):
    """Company names - normalized"""
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="company_name")

class CompanySize(Base):
    """Company sizes - normalized"""
    __tablename__ = 'company_sizes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="company_size")

class ContactPerson(Base):
    """Contact persons - normalized"""
    __tablename__ = 'contact_persons'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    job_details = relationship("JobDetail", back_populates="contact_person")

class HardSkill(Base):
    """Hard skills - normalized"""
    __tablename__ = 'hard_skills'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_hard_skills, back_populates="hard_skills")

class SoftSkill(Base):
    """Soft skills - normalized"""
    __tablename__ = 'soft_skills'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_soft_skills, back_populates="soft_skills")

class Certification(Base):
    """Certifications - normalized"""
    __tablename__ = 'certifications'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_certifications, back_populates="certifications")

class License(Base):
    """Licenses - normalized"""
    __tablename__ = 'licenses'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_licenses, back_populates="licenses")

class Benefit(Base):
    """Benefits - normalized"""
    __tablename__ = 'benefits'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_benefits, back_populates="benefits")

class WorkEnvironment(Base):
    """Work environment characteristics - normalized"""
    __tablename__ = 'work_environment'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_work_environment, back_populates="work_environment")

class ProfessionalDevelopment(Base):
    """Professional development opportunities - normalized"""
    __tablename__ = 'professional_development'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_professional_development, back_populates="professional_development")

class WorkLifeBalance(Base):
    """Work-life balance features - normalized"""
    __tablename__ = 'work_life_balance'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_work_life_balance, back_populates="work_life_balance")

class PhysicalRequirement(Base):
    """Physical requirements - normalized"""
    __tablename__ = 'physical_requirements'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_physical_requirements, back_populates="physical_requirements")

class WorkCondition(Base):
    """Work conditions - normalized"""
    __tablename__ = 'work_conditions'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_work_conditions, back_populates="work_conditions")

class SpecialRequirement(Base):
    """Special requirements - normalized"""
    __tablename__ = 'special_requirements'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False, unique=True)
    
    jobs = relationship("JobDetail", secondary=job_special_requirements, back_populates="special_requirements")


# ============ One-to-Many Relationships ============

class Responsibility(Base):
    """Job responsibilities - one-to-many"""
    __tablename__ = 'responsibilities'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False)
    description = Column(String(500), nullable=False)
    order = Column(Integer, default=0)
    
    job_detail = relationship("JobDetail", back_populates="responsibilities")

class JobLanguage(Base):
    """Languages required for job with proficiency - one-to-many"""
    __tablename__ = 'job_languages'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False)
    language = Column(String(100), nullable=False)
    proficiency = Column(String(50), nullable=True)
    
    job_detail = relationship("JobDetail", back_populates="languages")
    
    __table_args__ = (
        Index('idx_job_language_unique', 'job_detail_id', 'language', unique=True),
    )

class ContactEmail(Base):
    """Contact emails - one-to-many"""
    __tablename__ = 'contact_emails'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False)
    email = Column(String(200), nullable=False)
    
    job_detail = relationship("JobDetail", back_populates="contact_emails")

class ContactPhone(Base):
    """Contact phones - one-to-many"""
    __tablename__ = 'contact_phones'
    
    id = Column(Integer, primary_key=True)
    job_detail_id = Column(Integer, ForeignKey('job_details.id'), nullable=False)
    phone = Column(String(50), nullable=False)
    
    job_detail = relationship("JobDetail", back_populates="contact_phones")


# ============ Main Tables ============

class Job(Base):
    """
    Original job posting (your existing table)
    """
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    site = Column(String(200), nullable=False)
    job_title = Column(String(200), nullable=False)
    company_name = Column(String(200), nullable=False)
    job_url = Column(String(500), nullable=False)
    job_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    checks = relationship("JobCheck", back_populates="job")
    detail = relationship("JobDetail", back_populates="job", uselist=False)
    
    __table_args__ = (
        Index('idx_job_unique', 'site', 'company_name', 'job_title', unique=True),
    )

class JobDetail(Base):
    """
    Processed/extracted job details - all fields are foreign keys to normalized tables
    """
    __tablename__ = 'job_details'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False, unique=True)
    
    # All string fields now as foreign keys to normalized tables
    title_id = Column(Integer, ForeignKey('titles.id'), nullable=True)
    job_function_id = Column(Integer, ForeignKey('job_functions.id'), nullable=True)
    seniority_level_id = Column(Integer, ForeignKey('seniority_levels.id'), nullable=True)
    industry_id = Column(Integer, ForeignKey('industries.id'), nullable=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=True)
    job_family_id = Column(Integer, ForeignKey('job_families.id'), nullable=True)
    specialization_id = Column(Integer, ForeignKey('specializations.id'), nullable=True)
    
    # Salary (numeric values stay as is)
    min_salary = Column(Numeric(12, 2), nullable=True)
    max_salary = Column(Numeric(12, 2), nullable=True)
    salary_currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=True)
    salary_period_id = Column(Integer, ForeignKey('salary_periods.id'), nullable=True)
    
    # Requirements
    required_education_id = Column(Integer, ForeignKey('education_levels.id'), nullable=True)
    experience_years = Column(Integer, nullable=True)
    
    # Work arrangement
    employment_type_id = Column(Integer, ForeignKey('employment_types.id'), nullable=True)
    contract_type_id = Column(Integer, ForeignKey('contract_types.id'), nullable=True)
    work_schedule_id = Column(Integer, ForeignKey('work_schedules.id'), nullable=True)
    shift_details_id = Column(Integer, ForeignKey('shift_details.id'), nullable=True)
    remote_work_id = Column(Integer, ForeignKey('remote_work_options.id'), nullable=True)
    travel_required_id = Column(Integer, ForeignKey('travel_requirements.id'), nullable=True)
    
    # Location 
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=True)
    full_address_id = Column(Integer, ForeignKey('full_addresses.id'), nullable=True)
    
    # Company
    company_name_id = Column(Integer, ForeignKey('companies.id'), nullable=True)
    company_size_id = Column(Integer, ForeignKey('company_sizes.id'), nullable=True)
    
    # Contact
    contact_person_id = Column(Integer, ForeignKey('contact_persons.id'), nullable=True)
    
    # Metadata
    posting_date = Column(Date, nullable=True)
    original_language = Column(String(10), nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships to Job
    job = relationship("Job", back_populates="detail")
    
    # Relationships to normalized tables
    title = relationship("Title", back_populates="job_details")
    job_function = relationship("JobFunction", back_populates="job_details")
    seniority_level = relationship("SeniorityLevel", back_populates="job_details")
    industry = relationship("Industry", back_populates="job_details")
    department = relationship("Department", back_populates="job_details")
    job_family = relationship("JobFamily", back_populates="job_details")
    specialization = relationship("Specialization", back_populates="job_details")
    required_education = relationship("EducationLevel", back_populates="job_details")
    employment_type = relationship("EmploymentType", back_populates="job_details")
    contract_type = relationship("ContractType", back_populates="job_details")
    work_schedule = relationship("WorkSchedule", back_populates="job_details")
    shift_details = relationship("ShiftDetail", back_populates="job_details")
    remote_work = relationship("RemoteWork", back_populates="job_details")
    travel_required = relationship("TravelRequirement", back_populates="job_details")
    salary_currency = relationship("Currency", back_populates="job_details")
    salary_period = relationship("SalaryPeriod", back_populates="job_details")
    city = relationship("City", back_populates="job_details")
    region = relationship("Region", back_populates="job_details")
    country = relationship("Country", back_populates="job_details")
    full_address = relationship("FullAddress", back_populates="job_details")
    company_name = relationship("Company", back_populates="job_details")
    company_size = relationship("CompanySize", back_populates="job_details")
    contact_person = relationship("ContactPerson", back_populates="job_details")
    
    # One-to-many relationships
    responsibilities = relationship("Responsibility", back_populates="job_detail", cascade="all, delete-orphan")
    languages = relationship("JobLanguage", back_populates="job_detail", cascade="all, delete-orphan")
    contact_emails = relationship("ContactEmail", back_populates="job_detail", cascade="all, delete-orphan")
    contact_phones = relationship("ContactPhone", back_populates="job_detail", cascade="all, delete-orphan")
    
    # Many-to-many relationships
    hard_skills = relationship("HardSkill", secondary=job_hard_skills, back_populates="jobs")
    soft_skills = relationship("SoftSkill", secondary=job_soft_skills, back_populates="jobs")
    certifications = relationship("Certification", secondary=job_certifications, back_populates="jobs")
    licenses = relationship("License", secondary=job_licenses, back_populates="jobs")
    benefits = relationship("Benefit", secondary=job_benefits, back_populates="jobs")
    work_environment = relationship("WorkEnvironment", secondary=job_work_environment, back_populates="jobs")
    professional_development = relationship("ProfessionalDevelopment", secondary=job_professional_development, back_populates="jobs")
    work_life_balance = relationship("WorkLifeBalance", secondary=job_work_life_balance, back_populates="jobs")
    physical_requirements = relationship("PhysicalRequirement", secondary=job_physical_requirements, back_populates="jobs")
    work_conditions = relationship("WorkCondition", secondary=job_work_conditions, back_populates="jobs")
    special_requirements = relationship("SpecialRequirement", secondary=job_special_requirements, back_populates="jobs")

class JobCheck(Base):
    """
    Table tracking when jobs were checked and their status
    """
    __tablename__ = 'job_checks'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    check_date = Column(Date, nullable=False)
    http_status = Column(Integer)
    
    job = relationship("Job", back_populates="checks")
    
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
