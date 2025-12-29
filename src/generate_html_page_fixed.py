import os
import json
import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from src.data_database import (
    DataSessionLocal, JobDetail, Titles, JobFunctions, SeniorityLevels,
    Industries, Departments, JobFamilies, Specializations, EducationLevels,
    EmploymentTypes, ContractTypes, WorkSchedules, ShiftDetails, 
    RemoteWorkOptions, TravelRequirements, SalaryPeriods, Cities, 
    Regions, Countries, Companies, CompanySizes, ContactPersons,
    Responsibility, JobLanguage, ContactEmail, ContactPhone,
    HardSkills, SoftSkills, Certifications, Licenses, Benefits,
    WorkEnvironment, ProfessionalDevelopment, WorkLifeBalance,
    PhysicalRequirements, WorkConditions, SpecialRequirements
)
from src.scrape_database import ScrapeSessionLocal, Job, JobCheck


class HtmlGenerator:
    def __init__(self):
        self.pages_dir = "pages"
        self.api_dir = os.path.join(self.pages_dir, "api")
        self.jobs_dir = os.path.join(self.api_dir, "jobs")
        self.lookups_dir = os.path.join(self.api_dir, "lookups")
        self.analytics_dir = os.path.join(self.api_dir, "analytics")
        
        # Ensure directories exist
        os.makedirs(self.pages_dir, exist_ok=True)
        os.makedirs(self.api_dir, exist_ok=True)
        os.makedirs(self.jobs_dir, exist_ok=True)
        os.makedirs(self.lookups_dir, exist_ok=True)
        os.makedirs(self.analytics_dir, exist_ok=True)
        
        # Configuration from ui_requirements.md
        self.JOBS_PER_PAGE = 100
        self.ALIVE_THRESHOLD_DAYS = 7
        self.TARGET_CURRENCY = 'MDL'
        self.EXCHANGE_RATES = {
            'EUR': 19.5,
            'USD': 18.0,
            'GBP': 22.5,
            'MDL': 1.0,
            'RUB': 0.25,
            'UAH': 0.48
        }
    
    def get_alive_jobs(self):
        """Get alive jobs from scrape.db based on last check date"""
        with ScrapeSessionLocal() as db:
            # Get jobs that have been checked recently (alive)
            cutoff_date = datetime.now() - timedelta(days=self.ALIVE_THRESHOLD_DAYS)
            alive_jobs_query = db.query(Job).join(JobCheck).filter(
                JobCheck.check_date >= cutoff_date
            ).all()
            
            # Get job URLs of alive jobs for filtering
            alive_job_urls = {job.job_url for job in alive_jobs_query}
        
        return alive_job_urls
    
    def _deduplicate_jobs(self, jobs):
        """Identify and group jobs with same title and company across sites"""
        job_groups = {}
        
        for job in jobs:
            # Only process jobs that have basic required fields
            if not job.job_title or not job.company_name:
                continue
                
            key = (job.job_title, job.company_name)
            
            if key not in job_groups:
                job_groups[key] = {
                    "original_job": job,
                    "sites": set(),
                    "raw_data": []
                }
            
            job_groups[key]["sites"].add(job.site)
            job_groups[key]["raw_data"].append({
                "site": job.site,
                "job_url": job.job_url,
                "job_description": job.job_description
            })
        
        # Return deduplicated list with site information
        result = []
        for group_data in job_groups.values():
            job = group_data["original_job"]
            job.sites_found = list(group_data["sites"])
            job.raw_data_per_site = group_data["raw_data"]
            result.append(job)
        
        return result
    
    def _process_jobs(self, jobs):
        """Convert salaries to MDL and calculate days open for jobs"""
        processed_jobs = []
        for job in jobs:
            # Convert salaries to MDL - handle foreign key relationships
            if job.min_salary and job.salary_currency_id and hasattr(job, 'salary_currency') and job.salary_currency:
                currency_code = job.salary_currency.code.upper()
                rate = self.EXCHANGE_RATES.get(currency_code, 1.0)
                job.min_salary_mdl = float(job.min_salary) * rate
            else:
                job.min_salary_mdl = None
                
            if job.max_salary and job.salary_currency_id and hasattr(job, 'salary_currency') and job.salary_currency:
                currency_code = job.salary_currency.code.upper()
                rate = self.EXCHANGE_RATES.get(currency_code, 1.0)
                job.max_salary_mdl = float(job.max_salary) * rate
            else:
                job.max_salary_mdl = None
            
            # Calculate days open
            if job.posting_date:
                days_open = (datetime.now().date() - job.posting_date).days
                job.days_open = max(0, days_open)
            else:
                job.days_open = None
            
            processed_jobs.append(job)
        
        return processed_jobs
    
    def _generate_metadata(self, jobs, total_pages):
        """Generate metadata with filter metadata and combination index"""
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "total_jobs": len(jobs),
            "total_pages": total_pages,
            "jobs_per_page": self.JOBS_PER_PAGE,
            "filter_metadata": {},
            "combination_index": {}
        }
        
        # Generate filter metadata
        filter_metadata = metadata["filter_metadata"]
        
        # Industry metadata
        industries = self._get_industry_metadata(jobs)
        filter_metadata["industries"] = industries
        
        # Department metadata (hierarchical)
        departments = self._get_department_metadata(jobs, industries)
        filter_metadata["departments"] = departments
        
        # Job family metadata
        job_families = self._get_job_family_metadata(jobs, departments)
        filter_metadata["job_families"] = job_families
        
        # Specialization metadata
        specializations = self._get_specialization_metadata(jobs, job_families)
        filter_metadata["specializations"] = specializations
        
        # Location metadata
        cities = self._get_city_metadata(jobs)
        filter_metadata["cities"] = cities
        
        # Other filter dimensions
        filter_metadata["seniority_levels"] = self._get_seniority_metadata(jobs)
        filter_metadata["remote_work"] = self._get_remote_work_metadata(jobs)
        filter_metadata["employment_types"] = self._get_employment_type_metadata(jobs)
        filter_metadata["skills"] = self._get_skills_metadata(jobs)
        
        # Generate combination index for fast filtering
        metadata["combination_index"] = self._generate_combination_index(jobs)
        
        return metadata
    
    def _get_industry_metadata(self, jobs):
        """Generate industry metadata with hierarchical relationships"""
        industry_data = {}
        
        for job in jobs:
            if job.industry:
                industry_id = job.industry.id
                industry_name = job.industry.name
                
                if industry_id not in industry_data:
                    industry_data[industry_id] = {
                        "name": industry_name,
                        "jobs_count": 0,
                        "departments": set(),
                        "avg_salary_mdl": 0,
                        "salary_sum": 0,
                        "salary_count": 0
                    }
                
                industry_data[industry_id]["jobs_count"] += 1
                industry_data[industry_id]["departments"].add(job.department.id if job.department else None)
                
                # Calculate salary stats
                if job.min_salary_mdl:
                    industry_data[industry_id]["salary_sum"] += job.min_salary_mdl
                    industry_data[industry_id]["salary_count"] += 1
                if job.max_salary_mdl:
                    industry_data[industry_id]["salary_sum"] += job.max_salary_mdl
                    industry_data[industry_id]["salary_count"] += 1
        
        # Convert sets to lists and calculate averages
        for industry_id, data in industry_data.items():
            data["departments"] = [d for d in data["departments"] if d is not None]
            if data["salary_count"] > 0:
                data["avg_salary_mdl"] = data["salary_sum"] / data["salary_count"]
            else:
                data["avg_salary_mdl"] = 0
            del data["salary_sum"]
            del data["salary_count"]
        
        return industry_data
    
    def _get_department_metadata(self, jobs, industries):
        """Generate department metadata with parent relationships"""
        department_data = {}
        
        for job in jobs:
            if job.department:
                dept_id = job.department.id
                dept_name = job.department.name
                industry_id = job.industry.id if job.industry else None
                
                if dept_id not in department_data:
                    department_data[dept_id] = {
                        "name": dept_name,
                        "parent_industry": industry_id,
                        "jobs_count": 0,
                        "job_families": set(),
                        "avg_salary_mdl": 0,
                        "salary_sum": 0,
                        "salary_count": 0
                    }
                
                department_data[dept_id]["jobs_count"] += 1
                department_data[dept_id]["job_families"].add(job.job_family.id if job.job_family else None)
                
                # Calculate salary stats
                if job.min_salary_mdl:
                    department_data[dept_id]["salary_sum"] += job.min_salary_mdl
                    department_data[dept_id]["salary_count"] += 1
                if job.max_salary_mdl:
                    department_data[dept_id]["salary_sum"] += job.max_salary_mdl
                    department_data[dept_id]["salary_count"] += 1
        
        # Convert sets to lists and calculate averages
        for dept_id, data in department_data.items():
            data["job_families"] = [f for f in data["job_families"] if f is not None]
            if data["salary_count"] > 0:
                data["avg_salary_mdl"] = data["salary_sum"] / data["salary_count"]
            else:
                data["avg_salary_mdl"] = 0
            del data["salary_sum"]
            del data["salary_count"]
        
        return department_data
    
    def _get_job_family_metadata(self, jobs, departments):
        """Generate job family metadata with parent relationships"""
        family_data = {}
        
        for job in jobs:
            if job.job_family:
                family_id = job.job_family.id
                family_name = job.job_family.name
                dept_id = job.department.id if job.department else None
                
                if family_id not in family_data:
                    family_data[family_id] = {
                        "name": family_name,
                        "parent_department": dept_id,
                        "jobs_count": 0,
                        "specializations": set(),
                        "avg_salary_mdl": 0,
                        "salary_sum": 0,
                        "salary_count": 0
                    }
                
                family_data[family_id]["jobs_count"] += 1
                family_data[family_id]["specializations"].add(job.specialization.id if job.specialization else None)
                
                # Calculate salary stats
                if job.min_salary_mdl:
                    family_data[family_id]["salary_sum"] += job.min_salary_mdl
                    family_data[family_id]["salary_count"] += 1
                if job.max_salary_mdl:
                    family_data[family_id]["salary_sum"] += job.max_salary_mdl
                    family_data[family_id]["salary_count"] += 1
        
        # Convert sets to lists and calculate averages
        for family_id, data in family_data.items():
            data["specializations"] = [s for s in data["specializations"] if s is not None]
            if data["salary_count"] > 0:
                data["avg_salary_mdl"] = data["salary_sum"] / data["salary_count"]
            else:
                data["avg_salary_mdl"] = 0
            del data["salary_sum"]
            del data["salary_count"]
        
        return family_data
    
    def _get_specialization_metadata(self, jobs, job_families):
        """Generate specialization metadata with parent relationships"""
        specialization_data = {}
        
        for job in jobs:
            if job.specialization:
                spec_id = job.specialization.id
                spec_name = job.specialization.name
                family_id = job.job_family.id if job.job_family else None
                
                if spec_id not in specialization_data:
                    specialization_data[spec_id] = {
                        "name": spec_name,
                        "parent_job_family": family_id,
                        "jobs_count": 0,
                        "avg_salary_mdl": 0,
                        "salary_sum": 0,
                        "salary_count": 0
                    }
                
                specialization_data[spec_id]["jobs_count"] += 1
                
                # Calculate salary stats
                if job.min_salary_mdl:
                    specialization_data[spec_id]["salary_sum"] += job.min_salary_mdl
                    specialization_data[spec_id]["salary_count"] += 1
                if job.max_salary_mdl:
                    specialization_data[spec_id]["salary_sum"] += job.max_salary_mdl
                    specialization_data[spec_id]["salary_count"] += 1
        
        # Calculate averages
        for spec_id, data in specialization_data.items():
            if data["salary_count"] > 0:
                data["avg_salary_mdl"] = data["salary_sum"] / data["salary_count"]
            else:
                data["avg_salary_mdl"] = 0
            del data["salary_sum"]
            del data["salary_count"]
        
        return specialization_data
    
    def _get_city_metadata(self, jobs):
        """Generate city metadata"""
        city_data = {}
        
        for job in jobs:
            if job.city:
                city_id = job.city.id
                city_name = job.city.name
                
                if city_id not in city_data:
                    city_data[city_id] = {
                        "name": city_name,
                        "jobs_count": 0,
                        "avg_salary_mdl": 0,
                        "salary_sum": 0,
                        "salary_count": 0
                    }
                
                city_data[city_id]["jobs_count"] += 1
                
                # Calculate salary stats
                if job.min_salary_mdl:
                    city_data[city_id]["salary_sum"] += job.min_salary_mdl
                    city_data[city_id]["salary_count"] += 1
                if job.max_salary_mdl:
                    city_data[city_id]["salary_sum"] += job.max_salary_mdl
                    city_data[city_id]["salary_count"] += 1
        
        # Calculate averages
        for city_id, data in city_data.items():
            if data["salary_count"] > 0:
                data["avg_salary_mdl"] = data["salary_sum"] / data["salary_count"]
            else:
                data["avg_salary_mdl"] = 0
            del data["salary_sum"]
            del data["salary_count"]
        
        return city_data
    
    def _get_seniority_metadata(self, jobs):
        """Generate seniority level metadata"""
        seniority_data = {}
        
        for job in jobs:
            if job.seniority_level:
                level_id = job.seniority_level.id
                level_name = job.seniority_level.name
                
                if level_id not in seniority_data:
                    seniority_data[level_id] = {
                        "name": level_name,
                        "jobs_count": 0,
                        "avg_salary_mdl": 0,
                        "salary_sum": 0,
                        "salary_count": 0
                    }
                
                seniority_data[level_id]["jobs_count"] += 1
                
                # Calculate salary stats
                if job.min_salary_mdl:
                    seniority_data[level_id]["salary_sum"] += job.min_salary_mdl
                    seniority_data[level_id]["salary_count"] += 1
                if job.max_salary_mdl:
                    seniority_data[level_id]["salary_sum"] += job.max_salary_mdl
                    seniority_data[level_id]["salary_count"] += 1
        
        # Calculate averages
        for level_id, data in seniority_data.items():
            if data["salary_count"] > 0:
                data["avg_salary_mdl"] = data["salary_sum"] / data["salary_count"]
            else:
                data["avg_salary_mdl"] = 0
            del data["salary_sum"]
            del data["salary_count"]
        
        return seniority_data
    
    def _get_remote_work_metadata(self, jobs):
        """Generate remote work metadata"""
        remote_data = {}
        
        for job in jobs:
            if job.remote_work:
                remote_id = job.remote_work.id
                remote_name = job.remote_work.name
                
                if remote_id not in remote_data:
                    remote_data[remote_id] = {
                        "name": remote_name,
                        "jobs_count": 0,
                        "avg_salary_mdl": 0,
                        "salary_sum": 0,
                        "salary_count": 0
                    }
                
                remote_data[remote_id]["jobs_count"] += 1
                
                # Calculate salary stats
                if job.min_salary_mdl:
                    remote_data[remote_id]["salary_sum"] += job.min_salary_mdl
                    remote_data[remote_id]["salary_count"] += 1
                if job.max_salary_mdl:
                    remote_data[remote_id]["salary_sum"] += job.max_salary_mdl
                    remote_data[remote_id]["salary_count"] += 1
        
        # Calculate averages
        for remote_id, data in remote_data.items():
            if data["salary_count"] > 0:
                data["avg_salary_mdl"] = data["salary_sum"] / data["salary_count"]
            else:
                data["avg_salary_mdl"] = 0
            del data["salary_sum"]
            del data["salary_count"]
        
        return remote_data
    
    def _get_employment_type_metadata(self, jobs):
        """Generate employment type metadata"""
        employment_data = {}
        
        for job in jobs:
            if job.employment_type:
                type_id = job.employment_type.id
                type_name = job.employment_type.name
                
                if type_id not in employment_data:
                    employment_data[type_id] = {
                        "name": type_name,
                        "jobs_count": 0,
                        "avg_salary_mdl": 0,
                        "salary_sum": 0,
                        "salary_count": 0
                    }
                
                employment_data[type_id]["jobs_count"] += 1
                
                # Calculate salary stats
                if job.min_salary_mdl:
                    employment_data[type_id]["salary_sum"] += job.min_salary_mdl
                    employment_data[type_id]["salary_count"] += 1
                if job.max_salary_mdl:
                    employment_data[type_id]["salary_sum"] += job.max_salary_mdl
                    employment_data[type_id]["salary_count"] += 1
        
        # Calculate averages
        for type_id, data in employment_data.items():
            if data["salary_count"] > 0:
                data["avg_salary_mdl"] = data["salary_sum"] / data["salary_count"]
            else:
                data["avg_salary_mdl"] = 0
            del data["salary_sum"]
            del data["salary_count"]
        
        return employment_data
    
    def _get_skills_metadata(self, jobs):
        """Generate skills metadata"""
        skills_data = {}
        
        for job in jobs:
            # Get hard skills
            if hasattr(job, 'hard_skills') and job.hard_skills:
                for skill in job.hard_skills:
                    if skill.name:
                        skill_name = skill.name
                        
                        if skill_name not in skills_data:
                            skills_data[skill_name] = {
                                "jobs_count": 0,
                                "avg_salary_mdl": 0,
                                "salary_sum": 0,
                                "salary_count": 0
                            }
                        
                        skills_data[skill_name]["jobs_count"] += 1
                        
                        # Calculate salary stats
                        if job.min_salary_mdl:
                            skills_data[skill_name]["salary_sum"] += job.min_salary_mdl
                            skills_data[skill_name]["salary_count"] += 1
                        if job.max_salary_mdl:
                            skills_data[skill_name]["salary_sum"] += job.max_salary_mdl
                            skills_data[skill_name]["salary_count"] += 1
        
        # Calculate averages
        for skill_name, data in skills_data.items():
            if data["salary_count"] > 0:
                data["avg_salary_mdl"] = data["salary_sum"] / data["salary_count"]
            else:
                data["avg_salary_mdl"] = 0
            del data["salary_sum"]
            del data["salary_count"]
        
        return skills_data
    
    def _generate_combination_index(self, jobs):
        """Generate combination index for fast filtering"""
        combination_index = {}
        
        for job in jobs:
            # Create various filter combinations
            combinations = []
            
            # Industry + Department
            if job.industry and job.department:
                combinations.append(f"industry_{job.industry.id}:department_{job.department.id}")
            
            # Industry + City
            if job.industry and job.city:
                combinations.append(f"industry_{job.industry.id}:city_{job.city.id}")
            
            # Department + City
            if job.department and job.city:
                combinations.append(f"department_{job.department.id}:city_{job.city.id}")
            
            # Seniority + City
            if job.seniority_level and job.city:
                combinations.append(f"seniority_{job.seniority_level.id}:city_{job.city.id}")
            
            # Remote + City
            if job.remote_work and job.city:
                combinations.append(f"remote_{job.remote_work.id}:city_{job.city.id}")
            
            # Skills + City (top 3 skills)
            if job.city and hasattr(job, 'hard_skills') and job.hard_skills:
                for i, skill in enumerate(job.hard_skills[:3]):
                    if skill.name:
                        combinations.append(f"skill_{skill.name}:city_{job.city.id}")
            
            # Add job to each combination
            for combo in combinations:
                if combo not in combination_index:
                    combination_index[combo] = []
                combination_index[combo].append(job.id)
        
        return combination_index
    
    def _generate_lookup_files(self, jobs):
        """Generate lookup files for all filter dimensions"""
        
        # Industries lookup
        industries = {}
        for job in jobs:
            if job.industry:
                industries[job.industry.id] = {
                    "id": job.industry.id,
                    "name": job.industry.name,
                    "jobs_count": 0  # Will be calculated below
                }
        
        # Count jobs per industry
        for job in jobs:
            if job.industry and job.industry.id in industries:
                industries[job.industry.id]["jobs_count"] += 1
        
        with open(os.path.join(self.lookups_dir, "industries.json"), "w", encoding="utf-8") as f:
            json.dump({"industries": list(industries.values())}, f, indent=2, ensure_ascii=False)
        
        # Departments lookup
        departments = {}
        for job in jobs:
            if job.department:
                departments[job.department.id] = {
                    "id": job.department.id,
                    "name": job.department.name,
                    "parent_industry_id": job.industry.id if job.industry else None,
                    "jobs_count": 0
                }
        
        # Count jobs per department
        for job in jobs:
            if job.department and job.department.id in departments:
                departments[job.department.id]["jobs_count"] += 1
        
        with open(os.path.join(self.lookups_dir, "departments.json"), "w", encoding="utf-8") as f:
            json.dump({"departments": list(departments.values())}, f, indent=2, ensure_ascii=False)
        
        # Job families lookup
        job_families = {}
        for job in jobs:
            if job.job_family:
                job_families[job.job_family.id] = {
                    "id": job.job_family.id,
                    "name": job.job_family.name,
                    "parent_department_id": job.department.id if job.department else None,
                    "jobs_count": 0
                }
        
        # Count jobs per job family
        for job in jobs:
            if job.job_family and job.job_family.id in job_families:
                job_families[job.job_family.id]["jobs_count"] += 1
        
        with open(os.path.join(self.lookups_dir, "job_families.json"), "w", encoding="utf-8") as f:
            json.dump({"job_families": list(job_families.values())}, f, indent=2, ensure_ascii=False)
        
        # Specializations lookup
        specializations = {}
        for job in jobs:
            if job.specialization:
                specializations[job.specialization.id] = {
                    "id": job.specialization.id,
                    "name": job.specialization.name,
                    "parent_job_family_id": job.job_family.id if job.job_family else None,
                    "jobs_count": 0
                }
        
        # Count jobs per specialization
        for job in jobs:
            if job.specialization and job.specialization.id in specializations:
                specializations[job.specialization.id]["jobs_count"] += 1
        
        with open(os.path.join(self.lookups_dir, "specializations.json"), "w", encoding="utf-8") as f:
            json.dump({"specializations": list(specializations.values())}, f, indent=2, ensure_ascii=False)
        
        # Cities lookup
        cities = {}
        for job in jobs:
            if job.city:
                cities[job.city.id] = {
                    "id": job.city.id,
                    "name": job.city.name,
                    "jobs_count": 0,
                    "avg_salary_mdl": 0,
                    "salary_sum": 0,
                    "salary_count": 0
                }
        
        # Count jobs and calculate salary stats per city
        for job in jobs:
            if job.city and job.city.id in cities:
                cities[job.city.id]["jobs_count"] += 1
                if job.min_salary_mdl:
                    cities[job.city.id]["salary_sum"] += job.min_salary_mdl
                    cities[job.city.id]["salary_count"] += 1
                if job.max_salary_mdl:
                    cities[job.city.id]["salary_sum"] += job.max_salary_mdl
                    cities[job.city.id]["salary_count"] += 1
        
        # Calculate averages
        for city_data in cities.values():
            if city_data["salary_count"] > 0:
                city_data["avg_salary_mdl"] = city_data["salary_sum"] / city_data["salary_count"]
            else:
                city_data["avg_salary_mdl"] = 0
            del city_data["salary_sum"]
            del city_data["salary_count"]
        
        with open(os.path.join(self.lookups_dir, "cities.json"), "w", encoding="utf-8") as f:
            json.dump({"cities": list(cities.values())}, f, indent=2, ensure_ascii=False)
        
        # Companies lookup (company name is string field)
        companies = {}
        for job in jobs:
            if job.company_name:
                if job.company_name not in companies:
                    companies[job.company_name] = {
                        "name": job.company_name,
                        "jobs_count": 0,
                        "avg_salary_mdl": 0,
                        "salary_sum": 0,
                        "salary_count": 0
                    }
        
        # Count jobs and calculate salary stats per company
        for job in jobs:
            if job.company_name and job.company_name in companies:
                companies[job.company_name]["jobs_count"] += 1
                if job.min_salary_mdl:
                    companies[job.company_name]["salary_sum"] += job.min_salary_mdl
                    companies[job.company_name]["salary_count"] += 1
                if job.max_salary_mdl:
                    companies[job.company_name]["salary_sum"] += job.max_salary_mdl
                    companies[job.company_name]["salary_count"] += 1
        
        # Calculate averages
        for company_data in companies.values():
            if company_data["salary_count"] > 0:
                company_data["avg_salary_mdl"] = company_data["salary_sum"] / company_data["salary_count"]
            else:
                company_data["avg_salary_mdl"] = 0
            del company_data["salary_sum"]
            del company_data["salary_count"]
        
        with open(os.path.join(self.lookups_dir, "companies.json"), "w", encoding="utf-8") as f:
            json.dump({"companies": list(companies.values())}, f, indent=2, ensure_ascii=False)
        
        # Skills lookup
        skills = {}
        for job in jobs:
            if hasattr(job, 'hard_skills') and job.hard_skills:
                for skill in job.hard_skills:
                    if skill.name:
                        skill_name = skill.name
                        if skill_name not in skills:
                            skills[skill_name] = {
                                "name": skill_name,
                                "jobs_count": 0,
                                "avg_salary_mdl": 0,
                                "salary_sum": 0,
                                "salary_count": 0
                            }
                        
                        skills[skill_name]["jobs_count"] += 1
                        if job.min_salary_mdl:
                            skills[skill_name]["salary_sum"] += job.min_salary_mdl
                            skills[skill_name]["salary_count"] += 1
                        if job.max_salary_mdl:
                            skills[skill_name]["salary_sum"] += job.max_salary_mdl
                            skills[skill_name]["salary_count"] += 1
        
        # Calculate averages
        for skill_data in skills.values():
            if skill_data["salary_count"] > 0:
                skill_data["avg_salary_mdl"] = skill_data["salary_sum"] / skill_data["salary_count"]
            else:
                skill_data["avg_salary_mdl"] = 0
            del skill_data["salary_sum"]
            del skill_data["salary_count"]
        
        with open(os.path.join(self.lookups_dir, "skills.json"), "w", encoding="utf-8") as f:
            json.dump({"skills": list(skills.values())}, f, indent=2, ensure_ascii=False)
        
        # Seniority levels lookup
        seniority_levels = {}
        for job in jobs:
            if job.seniority_level:
                seniority_levels[job.seniority_level.id] = {
                    "id": job.seniority_level.id,
                    "name": job.seniority_level.name,
                    "jobs_count": 0,
                    "avg_salary_mdl": 0,
                    "salary_sum": 0,
                    "salary_count": 0
                }
        
        # Count jobs and calculate salary stats per seniority level
        for job in jobs:
            if job.seniority_level and job.seniority_level.id in seniority_levels:
                seniority_levels[job.seniority_level.id]["jobs_count"] += 1
                if job.min_salary_mdl:
                    seniority_levels[job.seniority_level.id]["salary_sum"] += job.min_salary_mdl
                    seniority_levels[job.seniority_level.id]["salary_count"] += 1
                if job.max_salary_mdl:
                    seniority_levels[job.seniority_level.id]["salary_sum"] += job.max_salary_mdl
                    seniority_levels[job.seniority_level.id]["salary_count"] += 1
        
        # Calculate averages
        for level_data in seniority_levels.values():
            if level_data["salary_count"] > 0:
                level_data["avg_salary_mdl"] = level_data["salary_sum"] / level_data["salary_count"]
            else:
                level_data["avg_salary_mdl"] = 0
            del level_data["salary_sum"]
            del level_data["salary_count"]
        
        with open(os.path.join(self.lookups_dir, "seniority_levels.json"), "w", encoding="utf-8") as f:
            json.dump({"seniority_levels": list(seniority_levels.values())}, f, indent=2, ensure_ascii=False)
        
        # Employment types lookup
        employment_types = {}
        for job in jobs:
            if job.employment_type:
                employment_types[job.employment_type.id] = {
                    "id": job.employment_type.id,
                    "name": job.employment_type.name,
                    "jobs_count": 0,
                    "avg_salary_mdl": 0,
                    "salary_sum": 0,
                    "salary_count": 0
                }
        
        # Count jobs and calculate salary stats per employment type
        for job in jobs:
            if job.employment_type and job.employment_type.id in employment_types:
                employment_types[job.employment_type.id]["jobs_count"] += 1
                if job.min_salary_mdl:
                    employment_types[job.employment_type.id]["salary_sum"] += job.min_salary_mdl
                    employment_types[job.employment_type.id]["salary_count"] += 1
                if job.max_salary_mdl:
                    employment_types[job.employment_type.id]["salary_sum"] += job.max_salary_mdl
                    employment_types[job.employment_type.id]["salary_count"] += 1
        
        # Calculate averages
        for type_data in employment_types.values():
            if type_data["salary_count"] > 0:
                type_data["avg_salary_mdl"] = type_data["salary_sum"] / type_data["salary_count"]
            else:
                type_data["avg_salary_mdl"] = 0
            del type_data["salary_sum"]
            del type_data["salary_count"]
        
        with open(os.path.join(self.lookups_dir, "employment_types.json"), "w", encoding="utf-8") as f:
            json.dump({"employment_types": list(employment_types.values())}, f, indent=2, ensure_ascii=False)
        
        # Remote work options lookup
        remote_work_options = {}
        for job in jobs:
            if job.remote_work:
                remote_work_options[job.remote_work.id] = {
                    "id": job.remote_work.id,
                    "name": job.remote_work.name,
                    "jobs_count": 0,
                    "avg_salary_mdl": 0,
                    "salary_sum": 0,
                    "salary_count": 0
                }
        
        # Count jobs and calculate salary stats per remote work option
        for job in jobs:
            if job.remote_work and job.remote_work.id in remote_work_options:
                remote_work_options[job.remote_work.id]["jobs_count"] += 1
                if job.min_salary_mdl:
                    remote_work_options[job.remote_work.id]["salary_sum"] += job.min_salary_mdl
                    remote_work_options[job.remote_work.id]["salary_count"] += 1
                if job.max_salary_mdl:
                    remote_work_options[job.remote_work.id]["salary_sum"] += job.max_salary_mdl
                    remote_work_options[job.remote_work.id]["salary_count"] += 1
        
        # Calculate averages
        for remote_data in remote_work_options.values():
            if remote_data["salary_count"] > 0:
                remote_data["avg_salary_mdl"] = remote_data["salary_sum"] / remote_data["salary_count"]
            else:
                remote_data["avg_salary_mdl"] = 0
            del remote_data["salary_sum"]
            del remote_data["salary_count"]
        
        with open(os.path.join(self.lookups_dir, "remote_work_options.json"), "w", encoding="utf-8") as f:
            json.dump({"remote_work_options": list(remote_work_options.values())}, f, indent=2, ensure_ascii=False)
        
        print(f"Generated lookup files with {len(industries)} industries, {len(departments)} departments, {len(cities)} cities")
    
    def _generate_analytics(self, jobs):
        """Generate analytics files"""
        
        # Summary analytics
        summary = {
            "total_jobs": len(jobs),
            "sites": {},
            "salary_stats": {
                "min": float('inf'),
                "max": float('-inf'),
                "avg": 0,
                "count": 0
            },
            "top_industries": {},
            "top_cities": {},
            "salary_by_city": {},
            "salary_by_industry": {},
            "salary_by_seniority": {},
            "salary_by_employment_type": {}
        }
        
        # Calculate summary stats
        for job in jobs:
            # Sites
            if job.site:
                summary["sites"][job.site] = summary["sites"].get(job.site, 0) + 1
            
            # Salary stats
            if job.min_salary_mdl:
                summary["salary_stats"]["min"] = min(summary["salary_stats"]["min"], job.min_salary_mdl)
                summary["salary_stats"]["max"] = max(summary["salary_stats"]["max"], job.min_salary_mdl)
                summary["salary_stats"]["avg"] += job.min_salary_mdl
                summary["salary_stats"]["count"] += 1
            if job.max_salary_mdl:
                summary["salary_stats"]["min"] = min(summary["salary_stats"]["min"], job.max_salary_mdl)
                summary["salary_stats"]["max"] = max(summary["salary_stats"]["max"], job.max_salary_mdl)
                summary["salary_stats"]["avg"] += job.max_salary_mdl
                summary["salary_stats"]["count"] += 1
            
            # Industries
            if job.industry:
                industry_name = job.industry.name
                summary["top_industries"][industry_name] = summary["top_industries"].get(industry_name, 0) + 1
                
                # Salary by industry
                if industry_name not in summary["salary_by_industry"]:
                    summary["salary_by_industry"][industry_name] = {
                        "total": 0,
                        "count": 0,
                        "avg": 0
                    }
                if job.min_salary_mdl:
                    summary["salary_by_industry"][industry_name]["total"] += job.min_salary_mdl
                    summary["salary_by_industry"][industry_name]["count"] += 1
                if job.max_salary_mdl:
                    summary["salary_by_industry"][industry_name]["total"] += job.max_salary_mdl
                    summary["salary_by_industry"][industry_name]["count"] += 1
            
            # Cities
            if job.city:
                city_name = job.city.name
                summary["top_cities"][city_name] = summary["top_cities"].get(city_name, 0) + 1
                
                # Salary by city
                if city_name not in summary["salary_by_city"]:
                    summary["salary_by_city"][city_name] = {
                        "total": 0,
                        "count": 0,
                        "avg": 0
                    }
                if job.min_salary_mdl:
                    summary["salary_by_city"][city_name]["total"] += job.min_salary_mdl
                    summary["salary_by_city"][city_name]["count"] += 1
                if job.max_salary_mdl:
                    summary["salary_by_city"][city_name]["total"] += job.max_salary_mdl
                    summary["salary_by_city"][city_name]["count"] += 1
            
            # Seniority levels
            if job.seniority_level:
                level_name = job.seniority_level.name
                if level_name not in summary["salary_by_seniority"]:
                    summary["salary_by_seniority"][level_name] = {
                        "total": 0,
                        "count": 0,
                        "avg": 0
                    }
                if job.min_salary_mdl:
                    summary["salary_by_seniority"][level_name]["total"] += job.min_salary_mdl
                    summary["salary_by_seniority"][level_name]["count"] += 1
                if job.max_salary_mdl:
                    summary["salary_by_seniority"][level_name]["total"] += job.max_salary_mdl
                    summary["salary_by_seniority"][level_name]["count"] += 1
            
            # Employment types
            if job.employment_type:
                type_name = job.employment_type.name
                if type_name not in summary["salary_by_employment_type"]:
                    summary["salary_by_employment_type"][type_name] = {
                        "total": 0,
                        "count": 0,
                        "avg": 0
                    }
                if job.min_salary_mdl:
                    summary["salary_by_employment_type"][type_name]["total"] += job.min_salary_mdl
                    summary["salary_by_employment_type"][type_name]["count"] += 1
                if job.max_salary_mdl:
                    summary["salary_by_employment_type"][type_name]["total"] += job.max_salary_mdl
                    summary["salary_by_employment_type"][type_name]["count"] += 1
        
        # Calculate averages
        if summary["salary_stats"]["count"] > 0:
            summary["salary_stats"]["avg"] = summary["salary_stats"]["avg"] / summary["salary_stats"]["count"]
        else:
            summary["salary_stats"]["avg"] = 0
        
        # Calculate industry averages
        for industry_name, data in summary["salary_by_industry"].items():
            if data["count"] > 0:
                data["avg"] = data["total"] / data["count"]
        
        # Calculate city averages
        for city_name, data in summary["salary_by_city"].items():
            if data["count"] > 0:
                data["avg"] = data["total"] / data["count"]
        
        # Calculate seniority averages
        for level_name, data in summary["salary_by_seniority"].items():
            if data["count"] > 0:
                data["avg"] = data["total"] / data["count"]
        
        # Calculate employment type averages
        for type_name, data in summary["salary_by_employment_type"].items():
            if data["count"] > 0:
                data["avg"] = data["total"] / data["count"]
        
        # Convert counters to sorted lists
        summary["top_industries"] = sorted(
            [{"name": k, "count": v} for k, v in summary["top_industries"].items()],
            key=lambda x: x["count"], reverse=True
        )[:10]
        
        summary["top_cities"] = sorted(
            [{"name": k, "count": v} for k, v in summary["top_cities"].items()],
            key=lambda x: x["count"], reverse=True
        )[:10]
        
        with open(os.path.join(self.analytics_dir, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Generated analytics with summary of {len(jobs)} jobs")
    
    def _serialize_job(self, job):
        """Convert job object to serializable dict"""
        # Ensure this job has basic required fields from data.db
        if not job.job_title or not job.company_name:
            return None
            
        # Get skills for this job
        skills_preview = []
        total_skills = 0
        if hasattr(job, 'hard_skills') and job.hard_skills:
            skills_preview = [skill.name for skill in job.hard_skills[:3] if skill.name]
            total_skills = len([skill for skill in job.hard_skills if skill.name])
        
        # Get languages for this job
        languages_required = []
        if hasattr(job, 'job_languages') and job.job_languages:
            languages_required = [lang.language for lang in job.job_languages if lang.language]
        
        # Get benefits
        has_benefits = False
        if hasattr(job, 'benefits') and job.benefits:
            has_benefits = len([b for b in job.benefits if b.description]) > 0
        
        # Get certifications
        has_certifications = False
        if hasattr(job, 'certifications') and job.certifications:
            has_certifications = len([c for c in job.certifications if c.name]) > 0
        
        return {
            "id": job.id,
            "title_display": job.title.name if hasattr(job, 'title') and job.title else job.job_title,
            "title": job.title.name if hasattr(job, 'title') and job.title else job.job_title,
            "company": job.company_name,
            "company_id": job.company.id if hasattr(job, 'company') and job.company else None,
            
            "sites": getattr(job, "sites_found", [job.site]),
            "urls": {job.site: job.job_url} if job.job_url else {},
            
            "days_open": job.days_open,
            "posting_date": job.posting_date.isoformat() if job.posting_date else None,
            
            # All filter IDs (for filtering logic)
            "industry_id": job.industry.id if hasattr(job, 'industry') and job.industry else None,
            "department_id": job.department.id if hasattr(job, 'department') and job.department else None,
            "job_family_id": job.job_family.id if hasattr(job, 'job_family') and job.job_family else None,
            "specialization_id": job.specialization.id if hasattr(job, 'specialization') and job.specialization else None,
            "seniority_level_id": job.seniority_level.id if hasattr(job, 'seniority_level') and job.seniority_level else None,
            "city_id": job.city.id if hasattr(job, 'city') and job.city else None,
            "region_id": job.region.id if hasattr(job, 'region') and job.region else None,
            "country_id": job.country.id if hasattr(job, 'country') and job.country else None,
            "remote_work_id": job.remote_work.id if hasattr(job, 'remote_work') and job.remote_work else None,
            "employment_type_id": job.employment_type.id if hasattr(job, 'employment_type') and job.employment_type else None,
            "contract_type_id": job.contract_type.id if hasattr(job, 'contract_type') and job.contract_type else None,
            "work_schedule_id": job.work_schedule.id if hasattr(job, 'work_schedule') and job.work_schedule else None,
            "required_education_id": job.required_education.id if hasattr(job, 'required_education') and job.required_education else None,
            "company_size_id": job.company_size.id if hasattr(job, 'company_size') and job.company_size else None,
            "travel_required_id": job.travel_required.id if hasattr(job, 'travel_required') and job.travel_required else None,
            "shift_details_id": job.shift_details.id if hasattr(job, 'shift_details') and job.shift_details else None,
            
            # Display values (from processed data.db)
            "city": job.city.name if hasattr(job, 'city') and job.city else None,
            "region": job.region.name if hasattr(job, 'region') and job.region else None,
            "country": job.country.name if hasattr(job, 'country') and job.country else None,
            "seniority_level": job.seniority_level.name if hasattr(job, 'seniority_level') and job.seniority_level else None,
            "remote_work": job.remote_work.name if hasattr(job, 'remote_work') and job.remote_work else None,
            "employment_type": job.employment_type.name if hasattr(job, 'employment_type') and job.employment_type else None,
            
            # Salary (normalized to MDL)
            "min_salary_mdl": float(job.min_salary_mdl) if job.min_salary_mdl else None,
            "max_salary_mdl": float(job.max_salary_mdl) if job.max_salary_mdl else None,
            "salary_period": job.salary_period.name if hasattr(job, 'salary_period') and job.salary_period else None,
            "has_salary": bool(job.min_salary_mdl or job.max_salary_mdl),
            "original_currency": job.salary_currency.code if job.salary_currency_id and hasattr(job, 'salary_currency') and job.salary_currency else None,
            "original_min_salary": float(job.min_salary) if job.min_salary else None,
            "original_max_salary": float(job.max_salary) if job.max_salary else None,
            
            # Requirements preview
            "experience_years": int(job.experience_years) if job.experience_years else None,
            "required_education": job.required_education.name if hasattr(job, 'required_education') and job.required_education else None,
            "skills_preview": skills_preview,
            "total_skills": total_skills,
            "languages_required": languages_required,
            
            # Quick indicators
            "has_certifications": has_certifications,
            "has_benefits": has_benefits,
            
            # Raw data for debug tab
            "raw_data": {
                "sites": {
                    job.site: {
                        "url": job.job_url,
                        "job_title": job.job_title,
                        "company_name": job.company_name,
                        "job_description": job.job_description,
                        "scraped_at": job.processed_at.isoformat()
                    }
                }
            }
        }
    
    def generate_api_data(self):
        """Generate API JSON files for frontend from data.db (LLM-processed jobs)"""
        print("Generating API data from data.db (LLM-processed jobs)...")
        
        # Get all jobs from data.db - these are jobs that have been processed
        # through the scraping pipeline and stored in the normalized database
        with DataSessionLocal() as db:
            # Query jobs from JobDetail table in data.db
            # These are jobs that have been scraped and stored for LLM processing
            jobs_query = db.query(JobDetail).filter(
                JobDetail.job_title.isnot(None),  # Basic scraped field
                JobDetail.company_name.isnot(None)  # Basic scraped field
            ).order_by(JobDetail.processed_at.desc())
            
            jobs = jobs_query.all()
            
            print(f"Found {len(jobs)} jobs in data.db")
            print("Note: These jobs may have original scraped data and/or LLM-structured data")
            
            # Filter jobs that have the basic required fields for display
            valid_jobs = []
            for job in jobs:
                if job.job_title and job.company_name:
                    valid_jobs.append(job)
            
            print(f"Filtered to {len(valid_jobs)} jobs with basic data for display")
            
            # Get alive jobs from scrape.db to filter by alive status
            alive_job_urls = self.get_alive_jobs()
            print(f"Found {len(alive_job_urls)} alive job URLs in scrape.db")
            
            # Filter valid jobs to only include alive ones
            alive_valid_jobs = [job for job in valid_jobs if job.job_url in alive_job_urls]
            
            print(f"Filtered to {len(alive_valid_jobs)} jobs that are both valid and alive")
            
            # Group jobs by (site, title, company) to identify duplicates
            deduplicated_jobs = self._deduplicate_jobs(alive_valid_jobs)
            
            # Convert salaries to MDL and calculate days open
            processed_jobs = self._process_jobs(deduplicated_jobs)
            
            # Generate pages
            total_jobs = len(processed_jobs)
            total_pages = math.ceil(total_jobs / self.JOBS_PER_PAGE)
            
            # Generate metadata with filter metadata and combination index
            metadata = self._generate_metadata(processed_jobs, total_pages)
            
            # Write main metadata file
            with open(os.path.join(self.jobs_dir, "index.json"), "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Generate individual page files
            for page_num in range(1, total_pages + 1):
                start_idx = (page_num - 1) * self.JOBS_PER_PAGE
                end_idx = start_idx + self.JOBS_PER_PAGE
                page_jobs = processed_jobs[start_idx:end_idx]
                
                # Serialize jobs and filter out any that failed serialization
                serialized_jobs = []
                for job in page_jobs:
                    serialized_job = self._serialize_job(job)
                    if serialized_job:  # Only include successfully serialized jobs
                        serialized_jobs.append(serialized_job)
                
                page_data = {
                    "page": page_num,
                    "jobs": serialized_jobs
                }
                
                with open(os.path.join(self.jobs_dir, f"page-{page_num}.json"), "w", encoding="utf-8") as f:
                    json.dump(page_data, f, indent=2, ensure_ascii=False)
            
            # Generate lookup files
            self._generate_lookup_files(processed_jobs)
            
            # Generate analytics
            self._generate_analytics(processed_jobs)
            
            print(f"Generated {total_pages} pages with {total_jobs} jobs")
            print(f"Metadata: {len(metadata['filter_metadata'])} filter dimensions")
            print(f"Combination index: {len(metadata['combination_index'])} combinations")
    
    def generate_html_page(self):
        """Generate the main HTML page"""
        print("HTML page template available at: pages/index.html")
    
    def run(self):
        """Main execution method"""
        try:
            print("Starting HTML page generation...")
            self.generate_api_data()
            self.generate_html_page()
            print("HTML page generation completed successfully!")
            print(f"Files generated in: {os.path.abspath(self.pages_dir)}")
        except Exception as e:
            print(f"Error generating HTML page: {e}")
            raise


def generate_html_page():
    """Main function called from CLI"""
    generator = HtmlGenerator()
    generator.run()