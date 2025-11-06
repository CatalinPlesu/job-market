from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from .database import (
    Job, JobDetail, Responsibility, JobLanguage, ContactEmail, ContactPhone,
    Titles, JobFunctions, SeniorityLevels, Industries, Departments, JobFamilies,
    Specializations, EducationLevels, EmploymentTypes, ContractTypes, WorkSchedules,
    ShiftDetails, RemoteWorkOptions, TravelRequirements, Currencies, SalaryPeriods,
    Cities, Regions, Countries, FullAddresses, Companies, CompanySizes, ContactPersons,
    HardSkills, SoftSkills, Certifications, Licenses, Benefits, WorkEnvironment,
    ProfessionalDevelopment, WorkLifeBalance, PhysicalRequirements, WorkConditions,
    SpecialRequirements, SessionLocal
)


class JobRepository:
    """Repository for job data operations"""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or SessionLocal()
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
    
    def save_job_from_json(self, job_data: Dict, extracted_data: Dict) -> Job:
        """
        Save job posting with extracted details from JSON.
        
        Args:
            job_data: Basic job info (site, job_title, company_name, job_url, job_description)
            extracted_data: Extracted/processed job details (as per your JSON schema)
        
        Returns:
            Job object with all relationships loaded
        """
        
        # Create Job record
        job = Job(**job_data)
        self.session.add(job)
        self.session.flush()
        
        # Create JobDetail record
        detail = JobDetail(job_id=job.id)
        
        # Handle simple foreign key fields
        fk_mappings = [
            ('title', Titles, 'name'),
            ('job_function', JobFunctions, 'name'),
            ('seniority_level', SeniorityLevels, 'name'),
            ('industry', Industries, 'name'),
            ('department', Departments, 'name'),
            ('job_family', JobFamilies, 'name'),
            ('specialization', Specializations, 'name'),
            ('required_education', EducationLevels, 'name'),
            ('employment_type', EmploymentTypes, 'name'),
            ('contract_type', ContractTypes, 'name'),
            ('work_schedule', WorkSchedules, 'name'),
            ('shift_details', ShiftDetails, 'name'),
            ('remote_work', RemoteWorkOptions, 'name'),
            ('travel_required', TravelRequirements, 'name'),
            ('salary_currency', Currencies, 'code'),
            ('salary_period', SalaryPeriods, 'name'),
            ('city', Cities, 'name'),
            ('region', Regions, 'name'),
            ('country', Countries, 'name'),
            ('company_name', Companies, 'name'),
            ('company_size', CompanySizes, 'name'),
            ('contact_person', ContactPersons, 'name'),
        ]
        
        for json_key, model, field_name in fk_mappings:
            self._handle_fk_field(detail, extracted_data, json_key, model, field_name)
        
        # Handle full address separately
        if extracted_data.get('full_address'):
            addr = self._get_or_create_lookup(FullAddresses, 'address', extracted_data['full_address'])
            detail.full_address_id = addr.id
        
        # Handle direct numeric/date fields
        for field in ['min_salary', 'max_salary', 'experience_years', 'original_language']:
            if field in extracted_data and extracted_data[field] is not None:
                setattr(detail, field, extracted_data[field])
        
        # Handle posting_date (convert string to date if needed)
        if extracted_data.get('posting_date'):
            posting_date = extracted_data['posting_date']
            if isinstance(posting_date, str):
                posting_date = datetime.strptime(posting_date, '%Y-%m-%d').date()
            detail.posting_date = posting_date
        
        self.session.add(detail)
        self.session.flush()
        
        # Handle many-to-many relationships
        m2m_mappings = [
            ('hard_skills', HardSkills, 'name', 'hard_skills'),
            ('soft_skills', SoftSkills, 'name', 'soft_skills'),
            ('certifications', Certifications, 'name', 'certifications'),
            ('licenses_required', Licenses, 'name', 'licenses'),
            ('benefits', Benefits, 'description', 'benefits'),
            ('work_environment', WorkEnvironment, 'description', 'work_environment'),
            ('professional_development', ProfessionalDevelopment, 'description', 'professional_development'),
            ('work_life_balance', WorkLifeBalance, 'description', 'work_life_balance'),
            ('physical_requirements', PhysicalRequirements, 'description', 'physical_requirements'),
            ('work_conditions', WorkConditions, 'description', 'work_conditions'),
            ('special_requirements', SpecialRequirements, 'description', 'special_requirements'),
        ]
        
        for json_key, model, field_name, relationship_name in m2m_mappings:
            items = extracted_data.get(json_key)
            # FIX: Check if items is not None before processing
            if items:
                m2m_items = self._get_or_create_m2m_items(model, field_name, items)
                setattr(detail, relationship_name, m2m_items)
        
        # Handle responsibilities
        responsibilities = extracted_data.get('responsibilities')
        # FIX: Check if responsibilities is not None
        if responsibilities:
            for i, resp in enumerate(responsibilities):
                if resp:
                    self.session.add(Responsibility(
                        job_detail_id=detail.id,
                        description=resp,
                        order=i
                    ))
        
        # Handle languages
        languages = extracted_data.get('languages')
        proficiencies = extracted_data.get('language_proficiency')
        
        # FIX: Check if languages is not None before iterating
        if languages:
            for lang in languages:
                if lang:
                    # FIX: Safely get proficiency, handle None case
                    proficiency = None
                    if proficiencies and isinstance(proficiencies, dict):
                        proficiency = proficiencies.get(lang)
                    
                    self.session.add(JobLanguage(
                        job_detail_id=detail.id,
                        language=lang,
                        proficiency=proficiency
                    ))
        
        # Handle contact emails
        contact_emails = extracted_data.get('contact_emails')
        # FIX: Check if contact_emails is not None
        if contact_emails:
            for email in contact_emails:
                if email:
                    self.session.add(ContactEmail(
                        job_detail_id=detail.id,
                        email=email
                    ))
        
        # Handle contact phones
        contact_phones = extracted_data.get('contact_phones')
        # FIX: Check if contact_phones is not None
        if contact_phones:
            for phone in contact_phones:
                if phone:
                    self.session.add(ContactPhone(
                        job_detail_id=detail.id,
                        phone=phone
                    ))
        
        self.session.commit()
        return job
    
    def get_job_as_dict(self, job_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve job with all details as a dictionary with actual values (not IDs).
        
        Args:
            job_id: ID of the job to retrieve
        
        Returns:
            Dictionary with complete job information, or None if not found
        
        Example:
            job_dict = repo.get_job_as_dict(1)
            print(job_dict['title'])  # "Senior Python Developer" (not an ID)
            print(job_dict['hard_skills'])  # ["Python", "Django", "PostgreSQL"]
        """
        
        job = self.session.query(Job).filter(Job.id == job_id).first()
        if not job or not job.detail:
            return None
        
        detail = job.detail
        
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
            # Original job data
            'id': job.id,
            'site': job.site,
            'job_title': job.job_title,
            'company_name': job.company_name,
            'job_url': job.job_url,
            'job_description': job.job_description,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
            
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
        jobs = self.session.query(Job).limit(limit).offset(offset).all()
        return [self.get_job_as_dict(job.id) for job in jobs if job.detail]
    
    def find_jobs_by_skill(self, skill_name: str) -> List[Dict[str, Any]]:
        """Find all jobs requiring a specific skill"""
        jobs = (
            self.session.query(Job)
            .join(JobDetail)
            .join(JobDetail.hard_skills)
            .filter(HardSkills.name == skill_name)
            .all()
        )
        return [self.get_job_as_dict(job.id) for job in jobs]
    
    def find_jobs_by_location(self, city: str = None, country: str = None) -> List[Dict[str, Any]]:
        """Find jobs by location"""
        query = self.session.query(Job).join(JobDetail)
        
        if city:
            query = query.join(JobDetail.city).filter(Cities.name == city)
        if country:
            query = query.join(JobDetail.country).filter(Countries.name == country)
        
        jobs = query.all()
        return [self.get_job_as_dict(job.id) for job in jobs]


# ============ USAGE EXAMPLES ============

if __name__ == '__main__':
    # Example 1: Save a job
    job_data = {
        'site': 'rabota.md',
        'job_title': 'Senior Python Developer',
        'company_name': 'TechCorp SRL',
        'job_url': 'https://rabota.md/job/12345  ',
        'job_description': 'We are looking for...'
    }
    
    extracted_data = {
        'title': 'Senior Python Developer',
        'seniority_level': 'senior',
        'hard_skills': ['Python', 'Django', 'PostgreSQL', 'Docker'],
        'soft_skills': ['Communication', 'Teamwork', 'Problem Solving'],
        'min_salary': 50000,
        'max_salary': 70000,
        'salary_currency': 'usd',
        'salary_period': 'year',
        'required_education': 'bachelor',
        'experience_years': 5,
        'employment_type': 'full-time',
        'remote_work': 'hybrid',
        'city': 'Chisinau',
        'country': 'Moldova',
        'languages': ['English', 'Romanian'],
        'language_proficiency': {'English': 'fluent', 'Romanian': 'native'},
        'responsibilities': [
            'Design and implement scalable web applications',
            'Mentor junior developers',
            'Participate in code reviews'
        ],
        'benefits': ['Health insurance', 'Flexible schedule', 'Remote work'],
        'posting_date': '2025-11-05',
        'original_language': 'ro'
    }
    
    with JobRepository() as repo:
        # Save job
        job = repo.save_job_from_json(job_data, extracted_data)
        print(f"Saved job with ID: {job.id}")
        
        # Retrieve job as dictionary
        job_dict = repo.get_job_as_dict(job.id)
        print(f"\nJob title: {job_dict['title']}")
        print(f"Skills: {', '.join(job_dict['hard_skills'])}")
        print(f"Location: {job_dict['city']}, {job_dict['country']}")
        
        # Find jobs by skill
        python_jobs = repo.find_jobs_by_skill('Python')
        print(f"\nFound {len(python_jobs)} jobs requiring Python")
