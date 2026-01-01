import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy import func
from .data_database import (
    JobDetail, DataSessionLocal, Titles, JobFunctions, SeniorityLevels,
    Industries, Cities, Countries, Companies, EmploymentTypes, RemoteWorkOptions,
    HardSkills, SoftSkills, Benefits, Responsibility, JobLanguage,
    ContactEmail, ContactPhone, Certifications, Licenses,
    Currencies, SalaryPeriods, EducationLevels, ContractTypes, WorkSchedules,
    ShiftDetails, TravelRequirements, Regions, FullAddresses, CompanySizes,
    ContactPersons, Departments, JobFamilies, Specializations,
    WorkEnvironment, ProfessionalDevelopment, WorkLifeBalance,
    PhysicalRequirements, WorkConditions, SpecialRequirements,
    job_hard_skills, job_soft_skills, job_certifications, job_licenses,
    job_benefits, job_work_environment, job_professional_development,
    job_work_life_balance, job_physical_requirements, job_work_conditions,
    job_special_requirements
)


def generate_html_page():
    """Generate GitHub Pages HTML exporter with Vue.js SPA and JSON API"""
    print("\n" + "="*80)
    print("GENERATE HTML PAGES FOR GITHUB PAGES")
    print("="*80)
    print()
    
    # Create pages directory structure
    pages_dir = Path("pages")
    api_dir = pages_dir / "api" / "jobs"
    js_dir = pages_dir / "js"
    components_dir = js_dir / "components"
    services_dir = js_dir / "services"
    
    print("Creating directory structure...")
    for directory in [pages_dir, api_dir, js_dir, components_dir, services_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Generate JSON API data
    print("Generating JSON API data...")
    session = DataSessionLocal()
    try:
        # Get all jobs and normalize
        all_jobs = _get_all_jobs_normalized(session)
        print(f"Found {len(all_jobs)} jobs in database")
        
        # Identify duplicates (same title + company)
        deduplicated_jobs = _deduplicate_jobs(all_jobs)
        print(f"After deduplication: {len(deduplicated_jobs)} unique jobs")
        
        # Generate paginated API files
        _generate_job_pages(deduplicated_jobs, api_dir)
        
        # Generate lookup tables for filters
        _generate_lookup_tables(session, api_dir)
        
    finally:
        session.close()
    
    # Generate HTML and JS files
    print("Generating HTML and JavaScript files...")
    _generate_index_html(pages_dir)
    _generate_app_js(js_dir)
    _generate_api_service(services_dir)
    _generate_job_list_component(components_dir)
    _generate_job_detail_component(components_dir)
    _generate_filters_component(components_dir)
    
    print()
    print("✓ GitHub Pages generation complete!")
    print(f"  Output directory: {pages_dir.absolute()}")
    print(f"  API data: {api_dir.absolute()}")
    print(f"  JavaScript: {js_dir.absolute()}")
    print()


def _get_all_jobs_normalized(session) -> List[Dict[str, Any]]:
    """Get all jobs with normalized data structure"""
    jobs = []
    
    query = session.query(JobDetail).all()
    
    for detail in query:
        job_data = {
            'id': detail.id,
            'job_url': detail.job_url,
            'site': detail.site,
            'job_title': detail.job_title,
            'company_name': detail.company_name,
            'job_description': detail.job_description,
            'posting_date': detail.posting_date.isoformat() if detail.posting_date else None,
            'processed_at': detail.processed_at.isoformat() if detail.processed_at else None,
            
            # Use IDs for normalization - will be resolved using lookup tables
            'title_id': detail.title_id,
            'job_function_id': detail.job_function_id,
            'seniority_level_id': detail.seniority_level_id,
            'industry_id': detail.industry_id,
            'department_id': detail.department_id,
            'job_family_id': detail.job_family_id,
            'specialization_id': detail.specialization_id,
            'city_id': detail.city_id,
            'region_id': detail.region_id,
            'country_id': detail.country_id,
            'company_name_id': detail.company_name_id,
            'employment_type_id': detail.employment_type_id,
            'remote_work_id': detail.remote_work_id,
            'salary_currency_id': detail.salary_currency_id,
            'salary_period_id': detail.salary_period_id,
            'required_education_id': detail.required_education_id,
            'contract_type_id': detail.contract_type_id,
            'work_schedule_id': detail.work_schedule_id,
            'shift_details_id': detail.shift_details_id,
            'travel_required_id': detail.travel_required_id,
            'full_address_id': detail.full_address_id,
            'company_size_id': detail.company_size_id,
            'contact_person_id': detail.contact_person_id,
            
            # Numeric values
            'min_salary': float(detail.min_salary) if detail.min_salary else None,
            'max_salary': float(detail.max_salary) if detail.max_salary else None,
            'experience_years': detail.experience_years,
            'original_language': detail.original_language,
            
            # Collections (will be IDs for normalization)
            'hard_skill_ids': _get_m2m_ids(session, job_hard_skills, detail.id, 'hard_skills_id'),
            'soft_skill_ids': _get_m2m_ids(session, job_soft_skills, detail.id, 'soft_skills_id'),
            'certification_ids': _get_m2m_ids(session, job_certifications, detail.id, 'certifications_id'),
            'license_ids': _get_m2m_ids(session, job_licenses, detail.id, 'licenses_id'),
            'benefit_ids': _get_m2m_ids(session, job_benefits, detail.id, 'benefits_id'),
            'work_environment_ids': _get_m2m_ids(session, job_work_environment, detail.id, 'work_environment_id'),
            'professional_development_ids': _get_m2m_ids(session, job_professional_development, detail.id, 'professional_development_id'),
            'work_life_balance_ids': _get_m2m_ids(session, job_work_life_balance, detail.id, 'work_life_balance_id'),
            'physical_requirement_ids': _get_m2m_ids(session, job_physical_requirements, detail.id, 'physical_requirements_id'),
            'work_condition_ids': _get_m2m_ids(session, job_work_conditions, detail.id, 'work_conditions_id'),
            'special_requirement_ids': _get_m2m_ids(session, job_special_requirements, detail.id, 'special_requirements_id'),
            
            # One-to-many relations
            'responsibilities': [
                {'description': r.description, 'order': r.order}
                for r in session.query(Responsibility).filter(Responsibility.job_detail_id == detail.id).order_by(Responsibility.order).all()
            ],
            'languages': [
                {'language': l.language, 'proficiency': l.proficiency}
                for l in session.query(JobLanguage).filter(JobLanguage.job_detail_id == detail.id).all()
            ],
            'contact_emails': [
                e.email for e in session.query(ContactEmail).filter(ContactEmail.job_detail_id == detail.id).all()
            ],
            'contact_phones': [
                p.phone for p in session.query(ContactPhone).filter(ContactPhone.job_detail_id == detail.id).all()
            ],
        }
        
        jobs.append(job_data)
    
    return jobs


def _get_m2m_ids(session, association_table, job_detail_id: int, column_name: str) -> List[int]:
    """Get IDs from many-to-many association table"""
    result = session.execute(
        association_table.select().where(
            association_table.c.job_details_id == job_detail_id
        )
    ).fetchall()
    
    # The column name pattern is {table_name}_id
    return [row[1] for row in result]  # Second column is the related entity ID


def _deduplicate_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate jobs by title and company, merging sites"""
    # Group by (normalized title, normalized company)
    job_groups = defaultdict(list)
    
    for job in jobs:
        key = (
            job['job_title'].lower().strip() if job['job_title'] else '',
            job['company_name'].lower().strip() if job['company_name'] else ''
        )
        job_groups[key].append(job)
    
    deduplicated = []
    for group in job_groups.values():
        if len(group) == 1:
            deduplicated.append(group[0])
        else:
            # Merge jobs with same title and company
            merged = group[0].copy()
            merged['sites'] = list(set(job['site'] for job in group))
            merged['job_urls'] = [{'site': job['site'], 'url': job['job_url']} for job in group]
            deduplicated.append(merged)
    
    # Sort by posting date (newest first)
    deduplicated.sort(key=lambda x: x.get('posting_date') or '', reverse=True)
    
    return deduplicated


def _generate_job_pages(jobs: List[Dict[str, Any]], api_dir: Path):
    """Generate paginated job JSON files"""
    jobs_per_page = 50
    total_jobs = len(jobs)
    total_pages = (total_jobs + jobs_per_page - 1) // jobs_per_page
    
    print(f"Generating {total_pages} pages with {jobs_per_page} jobs per page...")
    
    # Generate pages-list.json with metadata
    pages_list = {
        'total_jobs': total_jobs,
        'total_pages': total_pages,
        'jobs_per_page': jobs_per_page,
        'generated_at': datetime.utcnow().isoformat(),
        'pages': []
    }
    
    # Generate individual page files
    for page_num in range(total_pages):
        start_idx = page_num * jobs_per_page
        end_idx = min(start_idx + jobs_per_page, total_jobs)
        page_jobs = jobs[start_idx:end_idx]
        
        # Create page metadata for pages-list
        page_meta = {
            'page': page_num + 1,
            'job_count': len(page_jobs),
            'first_posting_date': page_jobs[0].get('posting_date') if page_jobs else None,
            'last_posting_date': page_jobs[-1].get('posting_date') if page_jobs else None,
        }
        pages_list['pages'].append(page_meta)
        
        # Write page file
        page_file = api_dir / f"page-{page_num + 1}.json"
        with open(page_file, 'w', encoding='utf-8') as f:
            json.dump({'jobs': page_jobs}, f, ensure_ascii=False, indent=2)
    
    # Write pages-list.json
    with open(api_dir / "pages-list.json", 'w', encoding='utf-8') as f:
        json.dump(pages_list, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Generated pages-list.json and {total_pages} page files")


def _generate_lookup_tables(session, api_dir: Path):
    """Generate lookup tables for normalized data"""
    print("Generating lookup tables...")
    
    lookup_tables = {
        'titles': (Titles, 'name'),
        'job_functions': (JobFunctions, 'name'),
        'seniority_levels': (SeniorityLevels, 'name'),
        'industries': (Industries, 'name'),
        'departments': (Departments, 'name'),
        'job_families': (JobFamilies, 'name'),
        'specializations': (Specializations, 'name'),
        'cities': (Cities, 'name'),
        'regions': (Regions, 'name'),
        'countries': (Countries, 'name'),
        'companies': (Companies, 'name'),
        'employment_types': (EmploymentTypes, 'name'),
        'remote_work_options': (RemoteWorkOptions, 'name'),
        'currencies': (Currencies, 'code'),
        'salary_periods': (SalaryPeriods, 'name'),
        'education_levels': (EducationLevels, 'name'),
        'contract_types': (ContractTypes, 'name'),
        'work_schedules': (WorkSchedules, 'name'),
        'shift_details': (ShiftDetails, 'name'),
        'travel_requirements': (TravelRequirements, 'name'),
        'full_addresses': (FullAddresses, 'address'),
        'company_sizes': (CompanySizes, 'name'),
        'contact_persons': (ContactPersons, 'name'),
        'hard_skills': (HardSkills, 'name'),
        'soft_skills': (SoftSkills, 'name'),
        'certifications': (Certifications, 'name'),
        'licenses': (Licenses, 'name'),
        'benefits': (Benefits, 'description'),
        'work_environment': (WorkEnvironment, 'description'),
        'professional_development': (ProfessionalDevelopment, 'description'),
        'work_life_balance': (WorkLifeBalance, 'description'),
        'physical_requirements': (PhysicalRequirements, 'description'),
        'work_conditions': (WorkConditions, 'description'),
        'special_requirements': (SpecialRequirements, 'description'),
    }
    
    lookups = {}
    for table_name, (model, field_name) in lookup_tables.items():
        records = session.query(model).all()
        lookups[table_name] = {
            record.id: getattr(record, field_name)
            for record in records
        }
    
    # Write lookups.json
    lookups_file = api_dir / "lookups.json"
    with open(lookups_file, 'w', encoding='utf-8') as f:
        json.dump(lookups, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Generated lookups.json with {len(lookups)} tables")


def _generate_index_html(pages_dir: Path):
    """Generate main index.html for Vue.js SPA"""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Market - Moldova</title>
    <script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 0;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        header h1 {
            font-size: 2.5em;
            font-weight: 700;
        }
        
        header p {
            font-size: 1.2em;
            opacity: 0.9;
            margin-top: 10px;
        }
        
        .loading {
            text-align: center;
            padding: 60px 20px;
            font-size: 1.2em;
            color: #667eea;
        }
        
        .error {
            background: #fee;
            border: 1px solid #fcc;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            color: #c33;
        }
        
        @media (max-width: 768px) {
            header h1 {
                font-size: 1.8em;
            }
            
            header p {
                font-size: 1em;
            }
        }
    </style>
</head>
<body>
    <div id="app">
        <header>
            <div class="container">
                <h1>Job Market - Moldova</h1>
                <p>Explore job opportunities across Moldova</p>
            </div>
        </header>
        
        <div class="container">
            <div v-if="loading" class="loading">
                Loading job data...
            </div>
            
            <div v-else-if="error" class="error">
                {{ error }}
            </div>
            
            <template v-else>
                <filters-component 
                    :lookups="lookups"
                    :filters="filters"
                    @update-filters="updateFilters"
                ></filters-component>
                
                <job-list-component 
                    v-if="!selectedJob"
                    :jobs="currentPageJobs"
                    :current-page="currentPage"
                    :total-pages="totalPages"
                    :lookups="lookups"
                    @select-job="selectJob"
                    @change-page="changePage"
                ></job-list-component>
                
                <job-detail-component 
                    v-else
                    :job="selectedJob"
                    :lookups="lookups"
                    @back="selectedJob = null"
                ></job-detail-component>
            </template>
        </div>
    </div>
    
    <script type="module" src="js/app.js"></script>
</body>
</html>
'''
    
    with open(pages_dir / "index.html", 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✓ Generated index.html")


def _generate_app_js(js_dir: Path):
    """Generate main Vue.js app initialization"""
    js_code = '''import apiService from './services/api.js';
import JobListComponent from './components/job-list.js';
import JobDetailComponent from './components/job-detail.js';
import FiltersComponent from './components/filters.js';

const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            loading: true,
            error: null,
            lookups: {},
            allJobs: [],
            filteredJobs: [],
            currentPageJobs: [],
            selectedJob: null,
            currentPage: 1,
            totalPages: 1,
            filters: {
                search: '',
                city: null,
                remote_work: null,
                seniority_level: null,
                employment_type: null,
            }
        };
    },
    
    async mounted() {
        try {
            await this.loadData();
        } catch (err) {
            this.error = 'Failed to load job data: ' + err.message;
            console.error(err);
        } finally {
            this.loading = false;
        }
    },
    
    methods: {
        async loadData() {
            // Load lookups first
            this.lookups = await apiService.loadLookups();
            
            // Load pages list to determine pagination
            const pagesList = await apiService.loadPagesList();
            this.totalPages = pagesList.total_pages;
            
            // Load first page
            await this.loadPage(1);
        },
        
        async loadPage(pageNum) {
            this.loading = true;
            try {
                const pageData = await apiService.loadJobPage(pageNum);
                this.allJobs = pageData.jobs;
                this.applyFilters();
                this.currentPage = pageNum;
            } finally {
                this.loading = false;
            }
        },
        
        applyFilters() {
            let filtered = [...this.allJobs];
            
            // Search filter
            if (this.filters.search) {
                const search = this.filters.search.toLowerCase();
                filtered = filtered.filter(job => 
                    (job.job_title && job.job_title.toLowerCase().includes(search)) ||
                    (job.company_name && job.company_name.toLowerCase().includes(search))
                );
            }
            
            // City filter
            if (this.filters.city) {
                filtered = filtered.filter(job => job.city_id === parseInt(this.filters.city));
            }
            
            // Remote work filter
            if (this.filters.remote_work) {
                filtered = filtered.filter(job => job.remote_work_id === parseInt(this.filters.remote_work));
            }
            
            // Seniority filter
            if (this.filters.seniority_level) {
                filtered = filtered.filter(job => job.seniority_level_id === parseInt(this.filters.seniority_level));
            }
            
            // Employment type filter
            if (this.filters.employment_type) {
                filtered = filtered.filter(job => job.employment_type_id === parseInt(this.filters.employment_type));
            }
            
            this.filteredJobs = filtered;
            this.currentPageJobs = filtered;
        },
        
        updateFilters(newFilters) {
            this.filters = { ...this.filters, ...newFilters };
            this.applyFilters();
        },
        
        selectJob(job) {
            this.selectedJob = job;
            window.scrollTo(0, 0);
        },
        
        async changePage(pageNum) {
            await this.loadPage(pageNum);
            window.scrollTo(0, 0);
        }
    },
    
    components: {
        'job-list-component': JobListComponent,
        'job-detail-component': JobDetailComponent,
        'filters-component': FiltersComponent
    }
});

app.mount('#app');
'''
    
    with open(js_dir / "app.js", 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print("✓ Generated app.js")


def _generate_api_service(services_dir: Path):
    """Generate API service for loading JSON data"""
    js_code = '''const API_BASE = './api/jobs';

const apiService = {
    async loadLookups() {
        const response = await fetch(`${API_BASE}/lookups.json`);
        if (!response.ok) throw new Error('Failed to load lookups');
        return await response.json();
    },
    
    async loadPagesList() {
        const response = await fetch(`${API_BASE}/pages-list.json`);
        if (!response.ok) throw new Error('Failed to load pages list');
        return await response.json();
    },
    
    async loadJobPage(pageNum) {
        const response = await fetch(`${API_BASE}/page-${pageNum}.json`);
        if (!response.ok) throw new Error(`Failed to load page ${pageNum}`);
        return await response.json();
    }
};

export default apiService;
'''
    
    with open(services_dir / "api.js", 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print("✓ Generated api.js")


def _generate_job_list_component(components_dir: Path):
    """Generate job list component"""
    js_code = '''const JobListComponent = {
    props: ['jobs', 'currentPage', 'totalPages', 'lookups'],
    
    template: `
        <div class="job-list">
            <div class="job-stats">
                <p>Showing {{ jobs.length }} jobs (Page {{ currentPage }} of {{ totalPages }})</p>
            </div>
            
            <div v-if="jobs.length === 0" class="no-jobs">
                No jobs found matching your criteria.
            </div>
            
            <div v-else class="jobs-grid">
                <div v-for="job in jobs" :key="job.id" class="job-card" @click="$emit('select-job', job)">
                    <div class="job-header">
                        <h2 class="job-title">{{ job.job_title }}</h2>
                        <span v-if="job.sites" class="job-sites">{{ job.sites.length }} sites</span>
                    </div>
                    
                    <p class="company-name">{{ job.company_name }}</p>
                    
                    <div class="job-meta">
                        <span v-if="job.city_id" class="meta-item">
                            📍 {{ getLookup('cities', job.city_id) }}
                        </span>
                        <span v-if="job.remote_work_id" class="meta-item">
                            💼 {{ getLookup('remote_work_options', job.remote_work_id) }}
                        </span>
                        <span v-if="job.seniority_level_id" class="meta-item">
                            ⭐ {{ getLookup('seniority_levels', job.seniority_level_id) }}
                        </span>
                    </div>
                    
                    <div v-if="job.min_salary || job.max_salary" class="job-salary">
                        💰 {{ formatSalary(job) }}
                    </div>
                    
                    <div class="job-footer">
                        <span v-if="job.posting_date" class="posting-date">
                            Posted: {{ formatDate(job.posting_date) }}
                        </span>
                    </div>
                </div>
            </div>
            
            <div v-if="totalPages > 1" class="pagination">
                <button 
                    @click="$emit('change-page', currentPage - 1)"
                    :disabled="currentPage === 1"
                    class="btn-page"
                >
                    ← Previous
                </button>
                
                <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
                
                <button 
                    @click="$emit('change-page', currentPage + 1)"
                    :disabled="currentPage === totalPages"
                    class="btn-page"
                >
                    Next →
                </button>
            </div>
        </div>
    `,
    
    methods: {
        getLookup(table, id) {
            return this.lookups[table]?.[id] || 'N/A';
        },
        
        formatSalary(job) {
            const currency = this.getLookup('currencies', job.salary_currency_id);
            const period = this.getLookup('salary_periods', job.salary_period_id);
            
            if (job.min_salary && job.max_salary) {
                return `${job.min_salary} - ${job.max_salary} ${currency}/${period}`;
            } else if (job.min_salary) {
                return `From ${job.min_salary} ${currency}/${period}`;
            } else if (job.max_salary) {
                return `Up to ${job.max_salary} ${currency}/${period}`;
            }
            return 'Not specified';
        },
        
        formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
        }
    }
};

// Styles
const style = document.createElement('style');
style.textContent = `
    .job-list {
        margin-top: 20px;
    }
    
    .job-stats {
        background: white;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .job-stats p {
        color: #666;
        font-size: 0.95em;
    }
    
    .no-jobs {
        background: white;
        padding: 60px 20px;
        text-align: center;
        border-radius: 8px;
        color: #999;
        font-size: 1.1em;
    }
    
    .jobs-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .job-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .job-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .job-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 8px;
    }
    
    .job-title {
        font-size: 1.3em;
        font-weight: 600;
        color: #333;
        margin: 0;
        flex: 1;
    }
    
    .job-sites {
        background: #667eea;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 500;
        margin-left: 10px;
        white-space: nowrap;
    }
    
    .company-name {
        font-size: 1.1em;
        color: #666;
        margin: 8px 0 16px;
    }
    
    .job-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin: 16px 0;
    }
    
    .meta-item {
        background: #f0f0f0;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.9em;
        color: #555;
    }
    
    .job-salary {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 10px 12px;
        border-radius: 6px;
        margin: 12px 0;
        font-weight: 500;
    }
    
    .job-footer {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #eee;
    }
    
    .posting-date {
        font-size: 0.85em;
        color: #999;
    }
    
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        padding: 30px 0;
    }
    
    .btn-page {
        background: #667eea;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 1em;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .btn-page:hover:not(:disabled) {
        background: #5568d3;
        transform: translateY(-1px);
    }
    
    .btn-page:disabled {
        background: #ccc;
        cursor: not-allowed;
        opacity: 0.6;
    }
    
    .page-info {
        font-weight: 500;
        color: #666;
    }
    
    @media (max-width: 768px) {
        .jobs-grid {
            grid-template-columns: 1fr;
        }
        
        .job-title {
            font-size: 1.1em;
        }
        
        .pagination {
            flex-direction: column;
            gap: 10px;
        }
        
        .btn-page {
            width: 100%;
        }
    }
`;
document.head.appendChild(style);

export default JobListComponent;
'''
    
    with open(components_dir / "job-list.js", 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print("✓ Generated job-list.js")


def _generate_job_detail_component(components_dir: Path):
    """Generate job detail component with tabs"""
    js_code = '''const JobDetailComponent = {
    props: ['job', 'lookups'],
    
    data() {
        return {
            activeTab: 'structured'
        };
    },
    
    template: `
        <div class="job-detail">
            <button @click="$emit('back')" class="btn-back">← Back to List</button>
            
            <div class="detail-header">
                <h1>{{ job.job_title }}</h1>
                <h2>{{ job.company_name }}</h2>
                
                <div class="header-meta">
                    <span v-if="job.city_id">
                        📍 {{ getLookup('cities', job.city_id) }}
                        <span v-if="job.country_id">, {{ getLookup('countries', job.country_id) }}</span>
                    </span>
                    <span v-if="job.posting_date">Posted: {{ formatDate(job.posting_date) }}</span>
                </div>
                
                <div v-if="job.sites && job.sites.length > 1" class="found-on">
                    <strong>Found on {{ job.sites.length }} sites:</strong>
                    <div class="site-links">
                        <a v-for="link in job.job_urls" :key="link.url" 
                           :href="link.url" target="_blank" class="site-link">
                            {{ link.site }}
                        </a>
                    </div>
                </div>
                <a v-else :href="job.job_url" target="_blank" class="apply-link">
                    View Original Posting →
                </a>
            </div>
            
            <div class="tabs">
                <button 
                    @click="activeTab = 'structured'" 
                    :class="{ active: activeTab === 'structured' }"
                    class="tab-btn"
                >
                    Structured Details
                </button>
                <button 
                    @click="activeTab = 'raw'" 
                    :class="{ active: activeTab === 'raw' }"
                    class="tab-btn tab-debug"
                >
                    Raw Data (Debug)
                </button>
            </div>
            
            <div v-if="activeTab === 'structured'" class="structured-content">
                <section v-if="job.min_salary || job.max_salary" class="detail-section salary-section">
                    <h3>💰 Compensation</h3>
                    <p class="salary-amount">{{ formatSalary(job) }}</p>
                </section>
                
                <section class="detail-section">
                    <h3>📋 Job Information</h3>
                    <div class="info-grid">
                        <div v-if="job.seniority_level_id" class="info-item">
                            <label>Seniority Level:</label>
                            <span>{{ getLookup('seniority_levels', job.seniority_level_id) }}</span>
                        </div>
                        <div v-if="job.employment_type_id" class="info-item">
                            <label>Employment Type:</label>
                            <span>{{ getLookup('employment_types', job.employment_type_id) }}</span>
                        </div>
                        <div v-if="job.contract_type_id" class="info-item">
                            <label>Contract Type:</label>
                            <span>{{ getLookup('contract_types', job.contract_type_id) }}</span>
                        </div>
                        <div v-if="job.remote_work_id" class="info-item">
                            <label>Work Location:</label>
                            <span>{{ getLookup('remote_work_options', job.remote_work_id) }}</span>
                        </div>
                        <div v-if="job.experience_years" class="info-item">
                            <label>Experience Required:</label>
                            <span>{{ job.experience_years }} years</span>
                        </div>
                        <div v-if="job.required_education_id" class="info-item">
                            <label>Education:</label>
                            <span>{{ getLookup('education_levels', job.required_education_id) }}</span>
                        </div>
                    </div>
                </section>
                
                <section v-if="job.responsibilities && job.responsibilities.length" class="detail-section">
                    <h3>🎯 Responsibilities</h3>
                    <ul class="list-items">
                        <li v-for="resp in job.responsibilities" :key="resp.order">
                            {{ resp.description }}
                        </li>
                    </ul>
                </section>
                
                <section v-if="hasSkills()" class="detail-section">
                    <h3>🛠️ Required Skills</h3>
                    <div v-if="job.hard_skill_ids && job.hard_skill_ids.length" class="skills-section">
                        <h4>Technical Skills</h4>
                        <div class="skill-tags">
                            <span v-for="id in job.hard_skill_ids" :key="id" class="skill-tag">
                                {{ getLookup('hard_skills', id) }}
                            </span>
                        </div>
                    </div>
                    <div v-if="job.soft_skill_ids && job.soft_skill_ids.length" class="skills-section">
                        <h4>Soft Skills</h4>
                        <div class="skill-tags">
                            <span v-for="id in job.soft_skill_ids" :key="id" class="skill-tag soft">
                                {{ getLookup('soft_skills', id) }}
                            </span>
                        </div>
                    </div>
                </section>
                
                <section v-if="job.languages && job.languages.length" class="detail-section">
                    <h3>🌐 Languages</h3>
                    <div class="language-list">
                        <span v-for="lang in job.languages" :key="lang.language" class="language-item">
                            {{ lang.language }}
                            <span v-if="lang.proficiency" class="proficiency">({{ lang.proficiency }})</span>
                        </span>
                    </div>
                </section>
                
                <section v-if="job.benefit_ids && job.benefit_ids.length" class="detail-section">
                    <h3>✨ Benefits</h3>
                    <ul class="list-items">
                        <li v-for="id in job.benefit_ids" :key="id">
                            {{ getLookup('benefits', id) }}
                        </li>
                    </ul>
                </section>
                
                <section v-if="job.contact_emails && job.contact_emails.length" class="detail-section">
                    <h3>📧 Contact Information</h3>
                    <div class="contact-info">
                        <p v-for="email in job.contact_emails" :key="email">
                            Email: <a :href="'mailto:' + email">{{ email }}</a>
                        </p>
                        <p v-for="phone in job.contact_phones" :key="phone">
                            Phone: {{ phone }}
                        </p>
                    </div>
                </section>
            </div>
            
            <div v-else class="raw-content">
                <div class="debug-notice">
                    ⚠️ This is raw data for debugging purposes
                </div>
                <pre>{{ JSON.stringify(job, null, 2) }}</pre>
            </div>
        </div>
    `,
    
    methods: {
        getLookup(table, id) {
            return this.lookups[table]?.[id] || 'N/A';
        },
        
        formatSalary(job) {
            const currency = this.getLookup('currencies', job.salary_currency_id);
            const period = this.getLookup('salary_periods', job.salary_period_id);
            
            if (job.min_salary && job.max_salary) {
                return `${job.min_salary} - ${job.max_salary} ${currency}/${period}`;
            } else if (job.min_salary) {
                return `From ${job.min_salary} ${currency}/${period}`;
            } else if (job.max_salary) {
                return `Up to ${job.max_salary} ${currency}/${period}`;
            }
            return 'Not specified';
        },
        
        formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        },
        
        hasSkills() {
            return (this.job.hard_skill_ids && this.job.hard_skill_ids.length) ||
                   (this.job.soft_skill_ids && this.job.soft_skill_ids.length);
        }
    }
};

// Styles
const style = document.createElement('style');
style.textContent = `
    .job-detail {
        background: white;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .btn-back {
        background: #f0f0f0;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 1em;
        cursor: pointer;
        margin-bottom: 20px;
        transition: background 0.2s;
    }
    
    .btn-back:hover {
        background: #e0e0e0;
    }
    
    .detail-header {
        border-bottom: 2px solid #eee;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }
    
    .detail-header h1 {
        font-size: 2em;
        color: #333;
        margin-bottom: 10px;
    }
    
    .detail-header h2 {
        font-size: 1.4em;
        color: #667eea;
        font-weight: 500;
        margin-bottom: 15px;
    }
    
    .header-meta {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        color: #666;
        margin-bottom: 15px;
    }
    
    .found-on {
        margin-top: 15px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .site-links {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 10px;
    }
    
    .site-link {
        display: inline-block;
        padding: 8px 16px;
        background: #667eea;
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-size: 0.9em;
        transition: background 0.2s;
    }
    
    .site-link:hover {
        background: #5568d3;
    }
    
    .apply-link {
        display: inline-block;
        margin-top: 15px;
        padding: 12px 24px;
        background: #667eea;
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 500;
        transition: background 0.2s;
    }
    
    .apply-link:hover {
        background: #5568d3;
    }
    
    .tabs {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        border-bottom: 2px solid #eee;
    }
    
    .tab-btn {
        background: none;
        border: none;
        padding: 12px 24px;
        font-size: 1em;
        cursor: pointer;
        color: #666;
        border-bottom: 3px solid transparent;
        margin-bottom: -2px;
        transition: all 0.2s;
    }
    
    .tab-btn:hover {
        color: #667eea;
    }
    
    .tab-btn.active {
        color: #667eea;
        border-bottom-color: #667eea;
        font-weight: 600;
    }
    
    .tab-debug {
        margin-left: auto;
        font-size: 0.9em;
        opacity: 0.7;
    }
    
    .detail-section {
        margin-bottom: 30px;
    }
    
    .detail-section h3 {
        font-size: 1.4em;
        color: #333;
        margin-bottom: 15px;
    }
    
    .detail-section h4 {
        font-size: 1.1em;
        color: #555;
        margin: 15px 0 10px;
    }
    
    .salary-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
    }
    
    .salary-section h3 {
        color: white;
    }
    
    .salary-amount {
        font-size: 1.5em;
        font-weight: 600;
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
    }
    
    .info-item {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    
    .info-item label {
        font-weight: 600;
        color: #555;
        font-size: 0.9em;
    }
    
    .info-item span {
        color: #333;
        font-size: 1.05em;
    }
    
    .list-items {
        list-style: none;
        padding: 0;
    }
    
    .list-items li {
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
        line-height: 1.6;
    }
    
    .list-items li:last-child {
        border-bottom: none;
    }
    
    .skill-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    .skill-tag {
        background: #667eea;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: 500;
    }
    
    .skill-tag.soft {
        background: #764ba2;
    }
    
    .language-list {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
    }
    
    .language-item {
        background: #f0f0f0;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 1em;
    }
    
    .proficiency {
        color: #666;
        font-size: 0.9em;
        margin-left: 5px;
    }
    
    .contact-info {
        line-height: 1.8;
    }
    
    .contact-info a {
        color: #667eea;
        text-decoration: none;
    }
    
    .contact-info a:hover {
        text-decoration: underline;
    }
    
    .raw-content {
        margin-top: 20px;
    }
    
    .debug-notice {
        background: #fff3cd;
        border: 1px solid #ffc107;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #856404;
    }
    
    .raw-content pre {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        overflow-x: auto;
        font-size: 0.85em;
        line-height: 1.5;
        border: 1px solid #dee2e6;
    }
    
    @media (max-width: 768px) {
        .job-detail {
            padding: 20px;
        }
        
        .detail-header h1 {
            font-size: 1.5em;
        }
        
        .detail-header h2 {
            font-size: 1.2em;
        }
        
        .info-grid {
            grid-template-columns: 1fr;
        }
        
        .tabs {
            overflow-x: auto;
        }
    }
`;
document.head.appendChild(style);

export default JobDetailComponent;
'''
    
    with open(components_dir / "job-detail.js", 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print("✓ Generated job-detail.js")


def _generate_filters_component(components_dir: Path):
    """Generate filters component"""
    js_code = '''const FiltersComponent = {
    props: ['lookups', 'filters'],
    
    data() {
        return {
            showFilters: false
        };
    },
    
    template: `
        <div class="filters">
            <button @click="showFilters = !showFilters" class="btn-toggle-filters">
                {{ showFilters ? '✕ Hide' : '⚙ Show' }} Filters
            </button>
            
            <div v-show="showFilters" class="filters-panel">
                <div class="filter-group">
                    <label>Search</label>
                    <input 
                        type="text" 
                        v-model="localFilters.search"
                        @input="updateFilters"
                        placeholder="Job title or company..."
                        class="filter-input"
                    />
                </div>
                
                <div class="filter-group">
                    <label>City</label>
                    <select v-model="localFilters.city" @change="updateFilters" class="filter-select">
                        <option :value="null">All Cities</option>
                        <option v-for="(name, id) in lookups.cities" :key="id" :value="id">
                            {{ name }}
                        </option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Work Location</label>
                    <select v-model="localFilters.remote_work" @change="updateFilters" class="filter-select">
                        <option :value="null">All</option>
                        <option v-for="(name, id) in lookups.remote_work_options" :key="id" :value="id">
                            {{ name }}
                        </option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Seniority Level</label>
                    <select v-model="localFilters.seniority_level" @change="updateFilters" class="filter-select">
                        <option :value="null">All Levels</option>
                        <option v-for="(name, id) in lookups.seniority_levels" :key="id" :value="id">
                            {{ name }}
                        </option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Employment Type</label>
                    <select v-model="localFilters.employment_type" @change="updateFilters" class="filter-select">
                        <option :value="null">All Types</option>
                        <option v-for="(name, id) in lookups.employment_types" :key="id" :value="id">
                            {{ name }}
                        </option>
                    </select>
                </div>
                
                <button @click="clearFilters" class="btn-clear">Clear Filters</button>
            </div>
        </div>
    `,
    
    data() {
        return {
            showFilters: false,
            localFilters: { ...this.filters }
        };
    },
    
    watch: {
        filters: {
            handler(newFilters) {
                this.localFilters = { ...newFilters };
            },
            deep: true
        }
    },
    
    methods: {
        updateFilters() {
            this.$emit('update-filters', this.localFilters);
        },
        
        clearFilters() {
            this.localFilters = {
                search: '',
                city: null,
                remote_work: null,
                seniority_level: null,
                employment_type: null,
            };
            this.updateFilters();
        }
    }
};

// Styles
const style = document.createElement('style');
style.textContent = `
    .filters {
        margin-bottom: 20px;
    }
    
    .btn-toggle-filters {
        background: #667eea;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 1em;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s;
        width: 100%;
    }
    
    .btn-toggle-filters:hover {
        background: #5568d3;
    }
    
    .filters-panel {
        background: white;
        padding: 24px;
        border-radius: 12px;
        margin-top: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
    }
    
    .filter-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .filter-group label {
        font-weight: 600;
        color: #555;
        font-size: 0.9em;
    }
    
    .filter-input,
    .filter-select {
        padding: 10px 12px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-size: 1em;
        transition: border-color 0.2s;
    }
    
    .filter-input:focus,
    .filter-select:focus {
        outline: none;
        border-color: #667eea;
    }
    
    .btn-clear {
        grid-column: 1 / -1;
        background: #f0f0f0;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 0.95em;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .btn-clear:hover {
        background: #e0e0e0;
    }
    
    @media (max-width: 768px) {
        .filters-panel {
            grid-template-columns: 1fr;
        }
    }
`;
document.head.appendChild(style);

export default FiltersComponent;
'''
    
    with open(components_dir / "filters.js", 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print("✓ Generated filters.js")
