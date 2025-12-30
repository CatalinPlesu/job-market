/**
 * API Module
 * Handles all API calls and data fetching
 */

export class JobMarketAPI {
    constructor() {
        this.baseURL = '';
    }

    async fetchMetadata() {
        try {
            const response = await fetch(`${this.baseURL}/api/jobs/index.json`);
            if (!response.ok) throw new Error('Failed to fetch metadata');
            return await response.json();
        } catch (err) {
            console.error('Error fetching metadata:', err);
            throw err;
        }
    }

    async fetchLookups() {
        try {
            const [
                industries, departments, jobFamilies, specializations, 
                cities, companies, skills, hardSkills, softSkills,
                certifications, licenses, benefits, workEnvironment,
                professionalDevelopment, workLifeBalance, physicalRequirements,
                workConditions, specialRequirements, jobFunctions,
                requiredEducation, employmentTypes, contractTypes,
                workSchedules, shiftDetails, remoteWorkOptions, travelRequired,
                countries, regions, companySizes, salaryCurrencies, salaryPeriods
            ] = await Promise.all([
                this.fetchJSON('/api/lookups/industries.json', 'industries'),
                this.fetchJSON('/api/lookups/departments.json', 'departments'),
                this.fetchJSON('/api/lookups/job_families.json', 'job_families'),
                this.fetchJSON('/api/lookups/specializations.json', 'specializations'),
                this.fetchJSON('/api/lookups/cities.json', 'cities'),
                this.fetchJSON('/api/lookups/companies.json', 'companies'),
                this.fetchJSON('/api/lookups/skills.json', 'skills'),
                this.fetchJSON('/api/lookups/hard_skills.json', 'hard_skills'),
                this.fetchJSON('/api/lookups/soft_skills.json', 'soft_skills'),
                this.fetchJSON('/api/lookups/certifications.json', 'certifications'),
                this.fetchJSON('/api/lookups/licenses.json', 'licenses'),
                this.fetchJSON('/api/lookups/benefits.json', 'benefits'),
                this.fetchJSON('/api/lookups/work_environment.json', 'work_environment'),
                this.fetchJSON('/api/lookups/professional_development.json', 'professional_development'),
                this.fetchJSON('/api/lookups/work_life_balance.json', 'work_life_balance'),
                this.fetchJSON('/api/lookups/physical_requirements.json', 'physical_requirements'),
                this.fetchJSON('/api/lookups/work_conditions.json', 'work_conditions'),
                this.fetchJSON('/api/lookups/special_requirements.json', 'special_requirements'),
                this.fetchJSON('/api/lookups/job_functions.json', 'job_functions'),
                this.fetchJSON('/api/lookups/required_education.json', 'required_education'),
                this.fetchJSON('/api/lookups/employment_types.json', 'employment_types'),
                this.fetchJSON('/api/lookups/contract_types.json', 'contract_types'),
                this.fetchJSON('/api/lookups/work_schedules.json', 'work_schedules'),
                this.fetchJSON('/api/lookups/shift_details.json', 'shift_details'),
                this.fetchJSON('/api/lookups/remote_work_options.json', 'remote_work_options'),
                this.fetchJSON('/api/lookups/travel_required.json', 'travel_required'),
                this.fetchJSON('/api/lookups/countries.json', 'countries'),
                this.fetchJSON('/api/lookups/regions.json', 'regions'),
                this.fetchJSON('/api/lookups/company_sizes.json', 'company_sizes'),
                this.fetchJSON('/api/lookups/salary_currencies.json', 'salary_currencies'),
                this.fetchJSON('/api/lookups/salary_periods.json', 'salary_periods')
            ]);

            return {
                industries: industries || [],
                departments: departments || [],
                job_families: jobFamilies || [],
                specializations: specializations || [],
                cities: cities || [],
                companies: companies || [],
                skills: skills || [],
                hard_skills: hardSkills || [],
                soft_skills: softSkills || [],
                certifications: certifications || [],
                licenses: licenses || [],
                benefits: benefits || [],
                work_environment: workEnvironment || [],
                professional_development: professionalDevelopment || [],
                work_life_balance: workLifeBalance || [],
                physical_requirements: physicalRequirements || [],
                work_conditions: workConditions || [],
                special_requirements: specialRequirements || [],
                job_functions: jobFunctions || [],
                required_education: requiredEducation || [],
                employment_types: employmentTypes || [],
                contract_types: contractTypes || [],
                work_schedules: workSchedules || [],
                shift_details: shiftDetails || [],
                remote_work: remoteWorkOptions || [],
                travel_required: travelRequired || [],
                countries: countries || [],
                regions: regions || [],
                company_sizes: companySizes || [],
                salary_currencies: salaryCurrencies || [],
                salary_periods: salaryPeriods || []
            };
        } catch (err) {
            console.error('Error fetching lookups:', err);
            throw err;
        }
    }

    async fetchJobs(page = 1) {
        try {
            const response = await fetch(`${this.baseURL}/api/jobs/page-${page}.json`);
            if (!response.ok) throw new Error('Failed to fetch jobs');
            
            const data = await response.json();
            return {
                jobs: data.jobs || [],
                page: data.page || page,
                totalPages: Math.ceil((data.total_jobs || 0) / 100)
            };
        } catch (err) {
            console.error('Error fetching jobs:', err);
            throw err;
        }
    }

    async fetchJSON(url, key) {
        try {
            const response = await fetch(this.baseURL + url);
            if (!response.ok) throw new Error(`Failed to fetch ${key}`);
            const data = await response.json();
            return data[key];
        } catch (err) {
            console.error(`Error fetching ${key}:`, err);
            return [];
        }
    }
}

// Create global API instance
window.JobMarketAPI = new JobMarketAPI();