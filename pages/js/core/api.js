/**
 * Browser API Module
 * Handles API calls and data fetching for browser environment
 */

export class BrowserAPI {
    constructor() {
        this.baseURL = '';
        this.allJobs = [];
        this.metadata = {};
        this.lookups = {};
    }

    /**
     * Fetch metadata
     */
    async fetchMetadata() {
        try {
            const response = await fetch(`${this.baseURL}/api/jobs/index.json`);
            if (!response.ok) throw new Error('Failed to fetch metadata');
            this.metadata = await response.json();
            return this.metadata;
        } catch (err) {
            console.error('Error fetching metadata:', err);
            throw err;
        }
    }

    /**
     * Fetch all lookups in parallel
     */
    async fetchLookups() {
        try {
            const lookupPromises = [
                'industries', 'departments', 'job_families', 'specializations',
                'cities', 'companies', 'skills', 'hard_skills', 'soft_skills',
                'certifications', 'licenses', 'benefits', 'work_environment',
                'professional_development', 'work_life_balance', 'physical_requirements',
                'work_conditions', 'special_requirements', 'job_functions',
                'required_education', 'employment_types', 'contract_types',
                'work_schedules', 'shift_details', 'remote_work_options', 'travel_required',
                'countries', 'regions', 'company_sizes', 'salary_currencies', 'salary_periods'
            ].map(async (lookupType) => {
                try {
                    const response = await fetch(`${this.baseURL}/api/lookups/${lookupType}.json`);
                    if (!response.ok) throw new Error(`Failed to fetch ${lookupType}`);
                    const data = await response.json();
                    return [lookupType, data[lookupType] || []];
                } catch (err) {
                    console.error(`Error fetching ${lookupType}:`, err);
                    return [lookupType, []];
                }
            });

            const results = await Promise.all(lookupPromises);
            this.lookups = Object.fromEntries(results);
            return this.lookups;
        } catch (err) {
            console.error('Error fetching lookups:', err);
            throw err;
        }
    }

    /**
     * Fetch all jobs for client-side filtering
     */
    async fetchAllJobs() {
        try {
            // Get metadata first to know total pages
            if (Object.keys(this.metadata).length === 0) {
                await this.fetchMetadata();
            }

            const totalPages = Math.ceil(this.metadata.total_jobs / 100);
            const promises = [];

            // Fetch all pages in parallel
            for (let i = 1; i <= totalPages; i++) {
                promises.push(this.fetchPage(i));
            }

            const pages = await Promise.all(promises);
            this.allJobs = [];

            pages.forEach(page => {
                this.allJobs = this.allJobs.concat(page.jobs || []);
            });

            return this.allJobs;
        } catch (err) {
            console.error('Error fetching all jobs:', err);
            throw err;
        }
    }

    /**
     * Fetch a specific page
     */
    async fetchPage(page) {
        try {
            const response = await fetch(`${this.baseURL}/api/jobs/page-${page}.json`);
            if (!response.ok) throw new Error(`Failed to fetch page ${page}`);
            return await response.json();
        } catch (err) {
            console.error(`Error fetching page ${page}:`, err);
            throw err;
        }
    }

    /**
     * Fetch jobs with filters - uses client-side filtering
     */
    async fetchJobs(page = 1, filters = {}) {
        try {
            // Load all jobs if not already loaded
            if (this.allJobs.length === 0) {
                await this.fetchAllJobs();
            }

            // Apply filters using the same logic as the Node.js server
            const filteredJobs = this.filterJobs(this.allJobs, filters);

            // Apply pagination
            const result = this.paginateJobs(filteredJobs, page);
            return result;
        } catch (err) {
            console.error('Error fetching jobs:', err);
            throw err;
        }
    }

    /**
     * Apply filters to jobs array
     */
    filterJobs(jobs, filters) {
        return jobs.filter(job => {
            // Search filter
            if (filters.search) {
                const searchLower = filters.search.toLowerCase();
                const matchesSearch = 
                    (job.title || '').toLowerCase().includes(searchLower) ||
                    (job.company || '').toLowerCase().includes(searchLower) ||
                    (job.hard_skills || []).some(skill => skill.toLowerCase().includes(searchLower)) ||
                    (job.soft_skills || []).some(skill => skill.toLowerCase().includes(searchLower));
                if (!matchesSearch) return false;
            }

            // Hierarchical filters
            if (filters.industry && job.industry_id !== parseInt(filters.industry)) return false;
            if (filters.department && job.department_id !== parseInt(filters.department)) return false;
            if (filters.job_family && job.job_family_id !== parseInt(filters.job_family)) return false;
            if (filters.specialization && job.specialization_id !== parseInt(filters.specialization)) return false;
            
            // Job details
            if (filters.job_function && job.job_function_id !== parseInt(filters.job_function)) return false;
            if (filters.seniority_level && job.seniority_level_id !== parseInt(filters.seniority_level)) return false;
            if (filters.required_education && job.required_education_id !== parseInt(filters.required_education)) return false;
            
            // Experience filters
            if (filters.experience_min !== null && job.experience_years_min < filters.experience_min) return false;
            if (filters.experience_max !== null && job.experience_years_max > filters.experience_max) return false;
            
            // Skills filters (multi-select)
            if (filters.hard_skills && filters.hard_skills.length > 0) {
                const jobSkills = (job.hard_skills || []).map(s => s.toLowerCase());
                const hasRequiredSkill = filters.hard_skills.some(skill => 
                    jobSkills.includes(skill.toLowerCase())
                );
                if (!hasRequiredSkill) return false;
            }
            
            if (filters.soft_skills && filters.soft_skills.length > 0) {
                const jobSkills = (job.soft_skills || []).map(s => s.toLowerCase());
                const hasRequiredSkill = filters.soft_skills.some(skill => 
                    jobSkills.includes(skill.toLowerCase())
                );
                if (!hasRequiredSkill) return false;
            }
            
            if (filters.certifications && filters.certifications.length > 0) {
                const jobCerts = (job.certifications || []).map(c => c.toLowerCase());
                const hasRequiredCert = filters.certifications.some(cert => 
                    jobCerts.includes(cert.toLowerCase())
                );
                if (!hasRequiredCert) return false;
            }
            
            if (filters.licenses && filters.licenses.length > 0) {
                const jobLicenses = (job.licenses || []).map(l => l.toLowerCase());
                const hasRequiredLicense = filters.licenses.some(license => 
                    jobLicenses.includes(license.toLowerCase())
                );
                if (!hasRequiredLicense) return false;
            }
            
            // Work arrangement filters
            if (filters.employment_type && job.employment_type_id !== parseInt(filters.employment_type)) return false;
            if (filters.contract_type && job.contract_type_id !== parseInt(filters.contract_type)) return false;
            if (filters.work_schedule && job.work_schedule_id !== parseInt(filters.work_schedule)) return false;
            if (filters.shift_details && job.shift_details_id !== parseInt(filters.shift_details)) return false;
            if (filters.remote_work && job.remote_work_id !== parseInt(filters.remote_work)) return false;
            if (filters.travel_required && job.travel_required_id !== parseInt(filters.travel_required)) return false;
            
            // Location filters
            if (filters.country && job.country_id !== parseInt(filters.country)) return false;
            if (filters.region && job.region_id !== parseInt(filters.region)) return false;
            if (filters.city && job.city_id !== parseInt(filters.city)) return false;
            
            // Company filters
            if (filters.company_size && job.company_size_id !== parseInt(filters.company_size)) return false;
            if (filters.companies && filters.companies.length > 0 && !filters.companies.includes(job.company)) return false;
            
            // Salary filters
            if (filters.has_salary && (!job.min_salary_mdl && !job.max_salary_mdl)) return false;
            if (filters.salary_min !== null && job.min_salary_mdl && job.min_salary_mdl < filters.salary_min) return false;
            if (filters.salary_max !== null && job.max_salary_mdl && job.max_salary_mdl > filters.salary_max) return false;
            if (filters.salary_currency && job.salary_currency_id !== parseInt(filters.salary_currency)) return false;
            if (filters.salary_period && job.salary_period_id !== parseInt(filters.salary_period)) return false;
            
            // Benefits and perks filters
            if (filters.benefits && filters.benefits.length > 0) {
                const jobBenefits = (job.benefits || []).map(b => b.toLowerCase());
                const hasRequiredBenefit = filters.benefits.some(benefit => 
                    jobBenefits.includes(benefit.toLowerCase())
                );
                if (!hasRequiredBenefit) return false;
            }
            
            if (filters.work_environment && filters.work_environment.length > 0) {
                const jobEnv = (job.work_environment || []).map(e => e.toLowerCase());
                const hasRequiredEnv = filters.work_environment.some(env => 
                    jobEnv.includes(env.toLowerCase())
                );
                if (!hasRequiredEnv) return false;
            }
            
            if (filters.professional_development && filters.professional_development.length > 0) {
                const jobDev = (job.professional_development || []).map(d => d.toLowerCase());
                const hasRequiredDev = filters.professional_development.some(dev => 
                    jobDev.includes(dev.toLowerCase())
                );
                if (!hasRequiredDev) return false;
            }
            
            if (filters.work_life_balance && filters.work_life_balance.length > 0) {
                const jobBalance = (job.work_life_balance || []).map(b => b.toLowerCase());
                const hasRequiredBalance = filters.work_life_balance.some(balance => 
                    jobBalance.includes(balance.toLowerCase())
                );
                if (!hasRequiredBalance) return false;
            }
            
            // Work conditions filters
            if (filters.physical_requirements && filters.physical_requirements.length > 0) {
                const jobPhysical = (job.physical_requirements || []).map(p => p.toLowerCase());
                const hasRequiredPhysical = filters.physical_requirements.some(physical => 
                    jobPhysical.includes(physical.toLowerCase())
                );
                if (!hasRequiredPhysical) return false;
            }
            
            if (filters.work_conditions && filters.work_conditions.length > 0) {
                const jobConditions = (job.work_conditions || []).map(c => c.toLowerCase());
                const hasRequiredCondition = filters.work_conditions.some(condition => 
                    jobConditions.includes(condition.toLowerCase())
                );
                if (!hasRequiredCondition) return false;
            }
            
            if (filters.special_requirements && filters.special_requirements.length > 0) {
                const jobSpecial = (job.special_requirements || []).map(s => s.toLowerCase());
                const hasRequiredSpecial = filters.special_requirements.some(special => 
                    jobSpecial.includes(special.toLowerCase())
                );
                if (!hasRequiredSpecial) return false;
            }
            
            return true;
        });
    }

    /**
     * Paginate filtered jobs
     */
    paginateJobs(jobs, page = 1, pageSize = 100) {
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        
        return {
            jobs: jobs.slice(startIndex, endIndex),
            page: page,
            totalPages: Math.ceil(jobs.length / pageSize),
            totalJobs: jobs.length
        };
    }

    /**
     * Get filter statistics
     */
    getFilterStats(jobs) {
        const filteredJobs = this.filterJobs(jobs, {});
        
        return {
            totalJobs: jobs.length,
            filteredJobs: filteredJobs.length,
            companies: new Set(filteredJobs.map(j => j.company)).size,
            cities: new Set(filteredJobs.map(j => j.city)).size
        };
    }

    /**
     * Get filter metadata
     */
    getFilterMetadata(jobs) {
        const metadata = {};
        
        // Count occurrences for each filter dimension
        const dimensions = [
            'industry_id', 'department_id', 'job_family_id', 'specialization_id',
            'job_function_id', 'seniority_level_id', 'required_education_id',
            'employment_type_id', 'contract_type_id', 'work_schedule_id',
            'shift_details_id', 'remote_work_id', 'travel_required_id',
            'country_id', 'region_id', 'city_id', 'company_size_id',
            'salary_currency_id', 'salary_period_id'
        ];

        dimensions.forEach(dim => {
            metadata[dim] = {};
            jobs.forEach(job => {
                const value = job[dim];
                if (value) {
                    metadata[dim][value] = (metadata[dim][value] || 0) + 1;
                }
            });
        });

        // Count skills
        const skillTypes = [
            'hard_skills', 'soft_skills', 'certifications', 'licenses',
            'benefits', 'work_environment', 'professional_development',
            'work_life_balance', 'physical_requirements', 'work_conditions',
            'special_requirements'
        ];

        skillTypes.forEach(skillType => {
            metadata[skillType] = {};
            jobs.forEach(job => {
                (job[skillType] || []).forEach(item => {
                    if (item) {
                        const key = item.toLowerCase();
                        metadata[skillType][key] = (metadata[skillType][key] || 0) + 1;
                    }
                });
            });
        });

        return metadata;
    }
}

// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BrowserAPI };
} else {
    window.BrowserAPI = BrowserAPI;
}