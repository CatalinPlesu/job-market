"""
Repository for data.db operations.
Handles JobDetail and all related lookup tables.
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from .data_database import (
    JobDetail, Responsibility, JobLanguage, ContactEmail, ContactPhone,
    Titles, JobFunctions, SeniorityLevels, Industries, Departments, JobFamilies,
    Specializations, EducationLevels, EmploymentTypes, ContractTypes, WorkSchedules,
    ShiftDetails, RemoteWorkOptions, TravelRequirements, Currencies, SalaryPeriods,
    Cities, Regions, Countries, FullAddresses, Companies, CompanySizes, ContactPersons,
    HardSkills, SoftSkills, Certifications, Licenses, Benefits, WorkEnvironment,
    ProfessionalDevelopment, WorkLifeBalance, PhysicalRequirements, WorkConditions,
    SpecialRequirements, DataSessionLocal
)


class JobRepository:
    """Repository for job data operations in data.db"""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or DataSessionLocal()
        self._should_close = session is None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._should_close:
            self.session.close()
    
    # ============ PRIVATE HELPERS ============
    
    def _get_or_create_lookup(self, model, field_name: str, value: str):
        """Get existing lookup record or create new one"""
        if not value:
            return None
        
        instance = self.session.query(model).filter(
            getattr(model, field_name) == value
        ).first()
        
        if not instance:
            instance = model(**{field_name: value})
            self.session.add(instance)
            self.session.flush()
        
        return instance
    
    def _get_or_create_m2m_items(self, model, field_name: str, values: List[str]) -> List:
        """Get or create multiple many-to-many items"""
        items = []
        for value in values:
            if value:
                item = self._get_or_create_lookup(model, field_name, value)
                if item:
                    items.append(item)
        return items
    
    def _handle_fk_field(self, detail: JobDetail, json_data: Dict, 
                         json_key: str, model, field_name: str = 'name'):
        """Handle foreign key field lookup and assignment"""
        value = json_data.get(json_key)
        if value:
            instance = self._get_or_create_lookup(model, field_name, value)
            setattr(detail, f'{json_key}_id', instance.id)
    
    # ============ PUBLIC API ============
    
    def get_job_detail_by_url(self, job_url: str) -> Optional[JobDetail]:
        """Get JobDetail by job_url"""
        return self.session.query(JobDetail).filter(JobDetail.job_url == job_url).first()
    
    def get_job_as_dict(self, job_detail_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve job detail with all details as a dictionary with actual values (not IDs).
        
        Args:
            job_detail_id: ID of the job detail to retrieve
        
        Returns:
            Dictionary with complete job information, or None if not found
        """
        detail = self.session.query(JobDetail).filter(JobDetail.id == job_detail_id).first()
        if not detail:
            return None
        
        # Query related objects separately since relationships might not be loaded
        fk_lookups = {
            'title': detail.title_id,
            'job_function': detail.job_function_id,
            'seniority_level': detail.seniority_level_id,
            'industry': detail.industry_id,
            'department': detail.department_id,
            'job_family': detail.job_family_id,
            'specialization': detail.specialization_id,
            'required_education': detail.required_education_id,
            'employment_type': detail.employment_type_id,
            'contract_type': detail.contract_type_id,
            'work_schedule': detail.work_schedule_id,
            'shift_details': detail.shift_details_id,
            'remote_work': detail.remote_work_id,
            'travel_required': detail.travel_required_id,
            'salary_currency': detail.salary_currency_id,
            'salary_period': detail.salary_period_id,
            'city': detail.city_id,
            'region': detail.region_id,
            'country': detail.country_id,
            'company_name_extracted': detail.company_name_id,
            'company_size': detail.company_size_id,
            'contact_person': detail.contact_person_id,
            'full_address': detail.full_address_id,
        }
        
        related_data = {}
        for attr_name, id_val in fk_lookups.items():
            if id_val:
                # Determine which model to query based on attribute name
                model_class = {
                    'title': Titles,
                    'job_function': JobFunctions,
                    'seniority_level': SeniorityLevels,
                    'industry': Industries,
                    'department': Departments,
                    'job_family': JobFamilies,
                    'specialization': Specializations,
                    'required_education': EducationLevels,
                    'employment_type': EmploymentTypes,
                    'contract_type': ContractTypes,
                    'work_schedule': WorkSchedules,
                    'shift_details': ShiftDetails,
                    'remote_work': RemoteWorkOptions,
                    'travel_required': TravelRequirements,
                    'salary_currency': Currencies,
                    'salary_period': SalaryPeriods,
                    'city': Cities,
                    'region': Regions,
                    'country': Countries,
                    'company_name_extracted': Companies,
                    'company_size': CompanySizes,
                    'contact_person': ContactPersons,
                    'full_address': FullAddresses,
                }[attr_name]
                
                obj = self.session.query(model_class).filter(model_class.id == id_val).first()
                if obj:
                    # Determine the correct field name for each model
                    if attr_name == 'salary_currency':
                        field_name = 'code'
                    elif attr_name == 'full_address':
                        field_name = 'address'
                    elif attr_name in ['benefits', 'work_environment', 'professional_development', 
                                     'work_life_balance', 'physical_requirements', 'work_conditions', 
                                     'special_requirements']:
                        field_name = 'description'
                    else:
                        field_name = 'name'
                    
                    related_data[attr_name] = getattr(obj, field_name)
                else:
                    related_data[attr_name] = None
            else:
                related_data[attr_name] = None
        
        # Build result dictionary
        result = {
            # JobDetail data
            'id': detail.id,
            'job_url': detail.job_url,
            'site': detail.site,
            'job_title': detail.job_title,
            'company_name': detail.company_name,
            'job_description': detail.job_description,
            
            # Job classification
            'title': related_data['title'],
            'job_function': related_data['job_function'],
            'seniority_level': related_data['seniority_level'],
            'industry': related_data['industry'],
            'department': related_data['department'],
            'job_family': related_data['job_family'],
            'specialization': related_data['specialization'],
            
            # Compensation
            'min_salary': float(detail.min_salary) if detail.min_salary else None,
            'max_salary': float(detail.max_salary) if detail.max_salary else None,
            'salary_currency': related_data['salary_currency'],
            'salary_period': related_data['salary_period'],
            
            # Requirements
            'required_education': related_data['required_education'],
            'experience_years': detail.experience_years,
            
            # Work arrangement
            'employment_type': related_data['employment_type'],
            'contract_type': detail.contract_type,
            'work_schedule': related_data['work_schedule'],
            'shift_details': related_data['shift_details'],
            'remote_work': related_data['remote_work'],
            'travel_required': related_data['travel_required'],
            
            # Location
            'city': related_data['city'],
            'region': related_data['region'],
            'country': related_data['country'],
            'full_address': related_data['full_address'],
            
            # Company information
            'company_name_extracted': related_data['company_name_extracted'],
            'company_size': related_data['company_size'],
            'contact_person': related_data['contact_person'],
            
            # Lists - Responsibilities
            'responsibilities': [
                {'description': r.description, 'order': r.order} 
                for r in sorted(detail.responsibilities, key=lambda x: x.order)
            ],
            
            # Lists - Languages
            'languages': [
                {'language': l.language, 'proficiency': l.proficiency}
                for l in detail.languages
            ],
            
            # Lists - Contact info
            'contact_emails': [e.email for e in detail.contact_emails],
            'contact_phones': [p.phone for p in detail.contact_phones],
            
            # Lists - Many-to-many (skills, certifications, etc.)
            'hard_skills': [s.name for s in detail.hard_skills],
            'soft_skills': [s.name for s in detail.soft_skills],
            'certifications': [c.name for c in detail.certifications],
            'licenses': [l.name for l in detail.licenses],
            'benefits': [b.description for b in detail.benefits],
            'work_environment': [w.description for w in detail.work_environment],
            'professional_development': [p.description for p in detail.professional_development],
            'work_life_balance': [w.description for w in detail.work_life_balance],
            'physical_requirements': [p.description for p in detail.physical_requirements],
            'work_conditions': [w.description for w in detail.work_conditions],
            'special_requirements': [s.description for s in detail.special_requirements],
            
            # Metadata
            'posting_date': detail.posting_date.isoformat() if detail.posting_date else None,
            'original_language': detail.original_language,
            'processed_at': detail.processed_at.isoformat() if detail.processed_at else None,
        }
        
        return result
    
    def get_all_jobs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get multiple jobs as dictionaries"""
        details = self.session.query(JobDetail).limit(limit).offset(offset).all()
        return [self.get_job_as_dict(detail.id) for detail in details]
    
    def find_jobs_by_skill(self, skill_name: str) -> List[Dict[str, Any]]:
        """Find all jobs requiring a specific skill"""
        details = (
            self.session.query(JobDetail)
            .join(JobDetail.hard_skills)
            .filter(HardSkills.name == skill_name)
            .all()
        )
        return [self.get_job_as_dict(detail.id) for detail in details]
    
    def find_jobs_by_location(self, city: str = None, country: str = None) -> List[Dict[str, Any]]:
        """Find jobs by location"""
        query = self.session.query(JobDetail)
        
        if city:
            query = query.join(JobDetail.city).filter(Cities.name == city)
        if country:
            query = query.join(JobDetail.country).filter(Countries.name == country)
        
        details = query.all()
        return [self.get_job_as_dict(detail.id) for detail in details]
