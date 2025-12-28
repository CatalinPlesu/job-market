
import os
import json
import math
from datetime import datetime
from sqlalchemy.orm import Session
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


class HtmlGenerator:
    def __init__(self):
        self.pages_dir = "pages"
        self.api_dir = os.path.join(self.pages_dir, "api")
        self.jobs_dir = os.path.join(self.api_dir, "jobs")
        
        # Ensure directories exist
        os.makedirs(self.pages_dir, exist_ok=True)
        os.makedirs(self.api_dir, exist_ok=True)
        os.makedirs(self.jobs_dir, exist_ok=True)
        
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
            
            # Group jobs by (site, title, company) to identify duplicates
            deduplicated_jobs = self._deduplicate_jobs(valid_jobs)
            
            # Generate pages
            page_size = 20
            total_jobs = len(deduplicated_jobs)
            total_pages = math.ceil(total_jobs / page_size)
            
            # Generate pages-list.json
            pages_list = {
                "total_pages": total_pages,
                "total_jobs": total_jobs,
                "page_size": page_size,
                "generated_at": datetime.now().isoformat(),
                "filters": {
                    "sites": self._get_unique_values(deduplicated_jobs, "sites"),
                    "titles": self._get_unique_values(deduplicated_jobs, "titles"),
                    "companies": self._get_unique_values(deduplicated_jobs, "companies"),
                    "cities": self._get_unique_values(deduplicated_jobs, "cities"),
                    "seniority_levels": self._get_unique_values(deduplicated_jobs, "seniority_levels"),
                    "industries": self._get_unique_values(deduplicated_jobs, "industries"),
                    "employment_types": self._get_unique_values(deduplicated_jobs, "employment_types")
                }
            }
            
            with open(os.path.join(self.jobs_dir, "pages-list.json"), "w", encoding="utf-8") as f:
                json.dump(pages_list, f, indent=2, ensure_ascii=False)
            
            # Generate individual page files
            for page_num in range(1, total_pages + 1):
                start_idx = (page_num - 1) * page_size
                end_idx = start_idx + page_size
                page_jobs = deduplicated_jobs[start_idx:end_idx]
                
                # Serialize jobs and filter out any that failed serialization
                serialized_jobs = []
                for job in page_jobs:
                    serialized_job = self._serialize_job(job)
                    if serialized_job:  # Only include successfully serialized jobs
                        serialized_jobs.append(serialized_job)
                
                page_data = {
                    "page": page_num,
                    "total_pages": total_pages,
                    "jobs": serialized_jobs
                }
                
                with open(os.path.join(self.jobs_dir, f"page-{page_num}.json"), "w", encoding="utf-8") as f:
                    json.dump(page_data, f, indent=2, ensure_ascii=False)
            
            print(f"Generated {total_pages} pages with {total_jobs} jobs")
    
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
    
    def _get_unique_values(self, jobs, field_type):
        """Extract unique values for filtering from processed jobs"""
        values = set()
        for job in jobs:
            # Only include jobs that have basic required fields
            if not job.job_title or not job.company_name:
                continue
                
            if field_type == "sites" and hasattr(job, "sites_found"):
                values.update(job.sites_found)
            elif field_type == "titles":
                # Check if job_title is a string or a related object
                if isinstance(job.job_title, str):
                    title = job.job_title
                else:
                    title = job.job_title.name if hasattr(job, 'job_title') and job.job_title else None
                if title:
                    values.add(title)
            elif field_type == "companies":
                # Check if company_name is a string or a related object
                if isinstance(job.company_name, str):
                    company = job.company_name
                else:
                    company = job.company_name.name if hasattr(job, 'company_name') and job.company_name else None
                if company:
                    values.add(company)
            elif field_type == "cities":
                city = job.city.name if hasattr(job, 'city') and job.city else None
                if city:
                    values.add(city)
            elif field_type == "seniority_levels":
                level = job.seniority_level.name if hasattr(job, 'seniority_level') and job.seniority_level else None
                if level:
                    values.add(level)
            elif field_type == "industries":
                industry = job.industry.name if hasattr(job, 'industry') and job.industry else None
                if industry:
                    values.add(industry)
            elif field_type == "employment_types":
                employment_type = job.employment_type.name if hasattr(job, 'employment_type') and job.employment_type else None
                if employment_type:
                    values.add(employment_type)
        
        return sorted(list(values))
    
    def _serialize_job(self, job):
        """Convert job object to serializable dict"""
        # Ensure this job has basic required fields from data.db
        if not job.job_title or not job.company_name:
            return None
            
        return {
            "id": job.id,
            "job_url": job.job_url,
            "site": job.site,
            "sites_found": getattr(job, "sites_found", [job.site]),
            "job_title": job.job_title,
            "company_name": job.company_name,
            # LLM-structured fields (may be null if LLM processing not completed)
            "title": job.title.name if hasattr(job, 'title') and job.title else None,
            "job_function": job.job_function.name if hasattr(job, 'job_function') and job.job_function else None,
            "seniority_level": job.seniority_level.name if hasattr(job, 'seniority_level') and job.seniority_level else None,
            "industry": job.industry.name if hasattr(job, 'industry') and job.industry else None,
            "department": job.department.name if hasattr(job, 'department') and job.department else None,
            "job_family": job.job_family.name if hasattr(job, 'job_family') and job.job_family else None,
            "specialization": job.specialization.name if hasattr(job, 'specialization') and job.specialization else None,
            "min_salary": float(job.min_salary) if job.min_salary else None,
            "max_salary": float(job.max_salary) if job.max_salary else None,
            "salary_currency": job.salary_currency.code if hasattr(job, 'salary_currency') and job.salary_currency else None,
            "salary_period": job.salary_period.name if hasattr(job, 'salary_period') and job.salary_period else None,
            "required_education": job.required_education.name if hasattr(job, 'required_education') and job.required_education else None,
            "experience_years": job.experience_years,
            "employment_type": job.employment_type.name if hasattr(job, 'employment_type') and job.employment_type else None,
            "contract_type": job.contract_type.name if hasattr(job, 'contract_type') and job.contract_type else None,
            "work_schedule": job.work_schedule.name if hasattr(job, 'work_schedule') and job.work_schedule else None,
            "shift_details": job.shift_details.name if hasattr(job, 'shift_details') and job.shift_details else None,
            "remote_work": job.remote_work.name if hasattr(job, 'remote_work') and job.remote_work else None,
            "travel_required": job.travel_required.name if hasattr(job, 'travel_required') and job.travel_required else None,
            "city": job.city.name if hasattr(job, 'city') and job.city else None,
            "region": job.region.name if hasattr(job, 'region') and job.region else None,
            "country": job.country.name if hasattr(job, 'country') and job.country else None,
            "full_address": job.full_address.address if hasattr(job, 'full_address') and job.full_address else None,
            "company_size": job.company_size.name if hasattr(job, 'company_size') and job.company_size else None,
            "contact_person": job.contact_person.name if hasattr(job, 'contact_person') and job.contact_person else None,
            "posting_date": job.posting_date.isoformat() if job.posting_date else None,
            "original_language": job.original_language,
            "processed_at": job.processed_at.isoformat(),
            "raw_data_per_site": getattr(job, "raw_data_per_site", [])
        }
    
    def generate_html_page(self):
        """Generate the main HTML page"""
        print("Generating HTML page...")
        
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moldova Job Market Dashboard</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <style>
        :root {
            --primary-color: #007bff;
            --secondary-color: #6c757d;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #333;
            --border-color: #dee2e6;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            color: var(--primary-color);
            margin-bottom: 10px;
        }
        
        .filters {
            background: var(--card-bg);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .filter-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
        }
        
        .filter-group label {
            font-size: 12px;
            color: var(--secondary-color);
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .filter-group select, .filter-group input {
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 14px;
        }
        
        .search-row {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .search-input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 14px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s;
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            color: white;
        }
        
        .btn-primary:hover {
            background-color: #0056b3;
        }
        
        .btn-secondary {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .btn-secondary:hover {
            background-color: #545b62;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }
        
        .pagination button {
            padding: 8px 16px;
            border: 1px solid var(--border-color);
            background: white;
            cursor: pointer;
            border-radius: 4px;
        }
        
        .pagination button.active {
            background-color: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }
        
        .pagination button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .jobs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .job-card {
            background: var(--card-bg);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid var(--border-color);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .job-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .job-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .job-title {
            font-size: 18px;
            font-weight: bold;
            color: var(--primary-color);
            margin: 0;
        }
        
        .job-meta {
            font-size: 12px;
            color: var(--secondary-color);
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .job-meta span {
            background: var(--bg-color);
            padding: 2px 8px;
            border-radius: 12px;
        }
        
        .company-name {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .salary {
            font-size: 18px;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 15px;
        }
        
        .job-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .detail-item {
            font-size: 14px;
            color: var(--secondary-color);
        }
        
        .detail-label {
            font-weight: bold;
            color: var(--text-color);
        }
        
        .sites-badge {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }
        
        .site-tag {
            background: var(--primary-color);
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
        }
        
        .tabs {
            display: flex;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 15px;
        }
        
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
        }
        
        .tab.active {
            border-bottom-color: var(--primary-color);
            color: var(--primary-color);
            font-weight: bold;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: var(--secondary-color);
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
            border: 1px solid #f5c6cb;
        }
        
        .hidden {
            display: none !important;
        }
        
        @media (max-width: 768px) {
            .jobs-grid {
                grid-template-columns: 1fr;
            }
            
            .filter-row {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="container">
            <header>
                <h1>Moldova Job Market Dashboard</h1>
                <p>Comprehensive job listings from multiple sources</p>
            </header>
            
            <div class="filters">
                <div class="filter-row">
                    <div class="filter-group">
                        <label>Site</label>
                        <select v-model="filters.site">
                            <option value="">All Sites</option>
                            <option v-for="site in filtersData.sites" :key="site">{{ site }}</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Title</label>
                        <select v-model="filters.title">
                            <option value="">All Titles</option>
                            <option v-for="title in filtersData.titles" :key="title">{{ title }}</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Company</label>
                        <select v-model="filters.company">
                            <option value="">All Companies</option>
                            <option v-for="company in filtersData.companies" :key="company">{{ company }}</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>City</label>
                        <select v-model="filters.city">
                            <option value="">All Cities</option>
                            <option v-for="city in filtersData.cities" :key="city">{{ city }}</option>
                        </select>
                    </div>
                </div>
                
                <div class="filter-row">
                    <div class="filter-group">
                        <label>Seniority</label>
                        <select v-model="filters.seniority">
                            <option value="">All Levels</option>
                            <option v-for="level in filtersData.seniority_levels" :key="level">{{ level }}</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Industry</label>
                        <select v-model="filters.industry">
                            <option value="">All Industries</option>
                            <option v-for="industry in filtersData.industries" :key="industry">{{ industry }}</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Employment Type</label>
                        <select v-model="filters.employmentType">
                            <option value="">All Types</option>
                            <option v-for="type in filtersData.employment_types" :key="type">{{ type }}</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Remote Work</label>
                        <select v-model="filters.remoteWork">
                            <option value="">All Options</option>
                            <option value="remote">Remote</option>
                            <option value="hybrid">Hybrid</option>
                            <option value="on-site">On-site</option>
                        </select>
                    </div>
                </div>
                
                <div class="search-row">
                    <input 
                        type="text" 
                        class="search-input" 
                        v-model="filters.search" 
                        placeholder="Search job titles, descriptions, skills..."
                    >
                    <button class="btn btn-primary" @click="searchJobs">Search</button>
                    <button class="btn btn-secondary" @click="resetFilters">Reset</button>
                </div>
            </div>
            
            <div v-if="loading" class="loading">
                Loading jobs...
            </div>
            
            <div v-if="error" class="error">
                {{ error }}
            </div>
            
            <div v-if="!loading && jobs.length > 0" class="jobs-grid">
                <div v-for="job in jobs" :key="job.id" class="job-card">
                    <div class="job-header">
                        <h3 class="job-title">{{ job.title || job.job_title }}</h3>
                        <div class="job-meta">
                            <span>{{ formatDate(job.posting_date) }}</span>
                            <span v-if="job.original_language">{{ job.original_language }}</span>
                        </div>
                    </div>
                    
                    <div class="company-name">{{ job.company_name }}</div>
                    
                    <div v-if="job.sites_found && job.sites_found.length > 1" class="sites-badge">
                        <span v-for="site in job.sites_found" :key="site" class="site-tag">{{ site }}</span>
                    </div>
                    
                    <div v-if="job.min_salary || job.max_salary" class="salary">
                        {{ formatSalary(job.min_salary, job.max_salary, job.salary_currency, job.salary_period) }}
                    </div>
                    
                    <div class="job-details">
                        <div v-if="job.city" class="detail-item">
                            <span class="detail-label">Location:</span> {{ job.city }}
                        </div>
                        <div v-if="job.seniority_level" class="detail-item">
                            <span class="detail-label">Level:</span> {{ job.seniority_level }}
                        </div>
                        <div v-if="job.employment_type" class="detail-item">
                            <span class="detail-label">Type:</span> {{ job.employment_type }}
                        </div>
                        <div v-if="job.industry" class="detail-item">
                            <span class="detail-label">Industry:</span> {{ job.industry }}
                        </div>
                        <div v-if="job.experience_years" class="detail-item">
                            <span class="detail-label">Experience:</span> {{ job.experience_years }} years
                        </div>
                        <div v-if="job.required_education" class="detail-item">
                            <span class="detail-label">Education:</span> {{ job.required_education }}
                        </div>
                    </div>
                    
                    <div class="tabs">
                        <div class="tab" :class="{ active: activeTab[job.id] === 'details' }" @click="setActiveTab(job.id, 'details')">
                            Structured Details
                        </div>
                        <div class="tab" :class="{ active: activeTab[job.id] === 'raw' }" @click="setActiveTab(job.id, 'raw')">
                            Raw Data
                        </div>
                    </div>
                    
                    <div class="tab-content" :class="{ active: activeTab[job.id] === 'details' }">
                        <div class="job-details">
                            <div v-if="job.job_function" class="detail-item">
                                <span class="detail-label">Function:</span> {{ job.job_function }}
                            </div>
                            <div v-if="job.department" class="detail-item">
                                <span class="detail-label">Department:</span> {{ job.department }}
                            </div>
                            <div v-if="job.job_family" class="detail-item">
                                <span class="detail-label">Family:</span> {{ job.job_family }}
                            </div>
                            <div v-if="job.specialization" class="detail-item">
                                <span class="detail-label">Specialization:</span> {{ job.specialization }}
                            </div>
                            <div v-if="job.contract_type" class="detail-item">
                                <span class="detail-label">Contract:</span> {{ job.contract_type }}
                            </div>
                            <div v-if="job.work_schedule" class="detail-item">
                                <span class="detail-label">Schedule:</span> {{ job.work_schedule }}
                            </div>
                            <div v-if="job.shift_details" class="detail-item">
                                <span class="detail-label">Shift:</span> {{ job.shift_details }}
                            </div>
                            <div v-if="job.travel_required" class="detail-item">
                                <span class="detail-label">Travel:</span> {{ job.travel_required }}
                            </div>
                            <div v-if="job.company_size" class="detail-item">
                                <span class="detail-label">Company Size:</span> {{ job.company_size }}
                            </div>
                            <div v-if="job.region" class="detail-item">
                                <span class="detail-label">Region:</span> {{ job.region }}
                            </div>
                            <div v-if="job.country" class="detail-item">
                                <span class="detail-label">Country:</span> {{ job.country }}
                            </div>
                            <div v-if="job.full_address" class="detail-item">
                                <span class="detail-label">Address:</span> {{ job.full_address }}
                            </div>
                            <div v-if="job.contact_person" class="detail-item">
                                <span class="detail-label">Contact:</span> {{ job.contact_person }}
                            </div>
                        </div>
                    </div>
                    
                    <div class="tab-content" :class="{ active: activeTab[job.id] === 'raw' }">
                        <div v-for="siteData in job.raw_data_per_site" :key="siteData.site" style="margin-bottom: 15px;">
                            <h4 style="color: var(--primary-color); margin-bottom: 5px;">{{ siteData.site }}</h4>
                            <div style="font-size: 12px; color: var(--secondary-color); margin-bottom: 5px;">{{ siteData.job_url }}</div>
                            <div style="font-size: 14px; line-height: 1.4;">{{ siteData.job_description }}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div v-if="!loading && jobs.length === 0 && !error" class="loading">
                No jobs found. Try adjusting your filters.
            </div>
            
            <div v-if="!loading && jobs.length > 0" class="pagination">
                <button :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">Previous</button>
                <button v-for="page in visiblePages" :key="page" 
                        :class="{ active: page === currentPage }"
                        @click="goToPage(page)">
                    {{ page }}
                </button>
                <button :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">Next</button>
            </div>
        </div>
        
        <script>
            const { createApp, ref, onMounted, computed, watch } = Vue;
            
            createApp({
                setup() {
                    const jobs = ref([]);
                    const filtersData = ref({});
                    const loading = ref(false);
                    const error = ref('');
                    const currentPage = ref(1);
                    const totalPages = ref(1);
                    const activeTab = ref({});
                    
                    // Filter state
                    const filters = ref({
                        site: '',
                        title: '',
                        company: '',
                        city: '',
                        seniority: '',
                        industry: '',
                        employmentType: '',
                        remoteWork: '',
                        search: ''
                    });
                    
                    const visiblePages = computed(() => {
                        const pages = [];
                        const start = Math.max(1, currentPage.value - 2);
                        const end = Math.min(totalPages.value, currentPage.value + 2);
                        
                        for (let i = start; i <= end; i++) {
                            pages.push(i);
                        }
                        
                        return pages;
                    });
                    
                    const formatDate = (dateString) => {
                        if (!dateString) return '';
                        const date = new Date(dateString);
                        return date.toLocaleDateString();
                    };
                    
                    const formatSalary = (min, max, currency, period) => {
                        if (!min && !max) return '';
                        
                        let result = '';
                        if (min && max) {
                            result = `${min} - ${max}`;
                        } else if (min) {
                            result = `From ${min}`;
                        } else if (max) {
                            result = `Up to ${max}`;
                        }
                        
                        if (currency) {
                            result += ` ${currency.toUpperCase()}`;
                        }
                        
                        if (period) {
                            result += ` / ${period}`;
                        }
                        
                        return result;
                    };
                    
                    const fetchFilters = async () => {
                        try {
                            const response = await axios.get('/api/jobs/pages-list.json');
                            filtersData.value = response.data.filters;
                        } catch (err) {
                            console.error('Error fetching filters:', err);
                        }
                    };
                    
                    const fetchJobs = async (page = 1) => {
                        loading.value = true;
                        error.value = '';
                        
                        try {
                            const response = await axios.get(`/api/jobs/page-${page}.json`);
                            const data = response.data;
                            
                            jobs.value = data.jobs;
                            currentPage.value = data.page;
                            totalPages.value = data.total_pages;
                            
                            // Initialize active tabs
                            jobs.value.forEach(job => {
                                if (!activeTab.value[job.id]) {
                                    activeTab.value[job.id] = 'details';
                                }
                            });
                        } catch (err) {
                            console.error('Error fetching jobs:', err);
                            error.value = 'Failed to load jobs. Please try again.';
                        } finally {
                            loading.value = false;
                        }
                    };
                    
                    const searchJobs = async () => {
                        // For now, just reload current page with filters applied
                        // In a real implementation, you'd want server-side filtering
                        await fetchJobs(currentPage.value);
                    };
                    
                    const resetFilters = () => {
                        filters.value = {
                            site: '',
                            title: '',
                            company: '',
                            city: '',
                            seniority: '',
                            industry: '',
                            employmentType: '',
                            remoteWork: '',
                            search: ''
                        };
                        fetchJobs(1);
                    };
                    
                    const goToPage = async (page) => {
                        if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
                            await fetchJobs(page);
                        }
                    };
                    
                    const setActiveTab = (jobId, tab) => {
                        activeTab.value[jobId] = tab;
                    };
                    
                    onMounted(async () => {
                        await fetchFilters();
                        await fetchJobs(1);
                    });
                    
                    return {
                        jobs,
                        filtersData,
                        loading,
                        error,
                        currentPage,
                        totalPages,
                        activeTab,
                        filters,
                        visiblePages,
                        formatDate,
                        formatSalary,
                        fetchJobs,
                        searchJobs,
                        resetFilters,
                        goToPage,
                        setActiveTab
                    };
                }
            }).mount('#app');
        </script>
    </div>
</body>
</html>"""
        
        with open(os.path.join(self.pages_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("Generated HTML page")
    
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
