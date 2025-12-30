/**
 * Filter Logic Module
 * Contains all filtering logic that can work in both Node.js and browser environments
 */

/**
 * Main Filter Manager Class
 * Handles all filtering operations with client-side logic
 */
export class FilterManager {
    constructor(api) {
        this.api = api;
        this.filters = this.createDefaultFilters();
        this.metadata = {};
        this.lookups = {};
        this.allJobs = [];
    }

    createDefaultFilters() {
        return {
            // Search
            search: '',
            
            // Job Classification
            industry: '',
            department: '',
            job_family: '',
            specialization: '',
            job_function: '',
            seniority_level: '',
            
            // Requirements
            required_education: '',
            experience_min: null,
            experience_max: null,
            
            // Skills (multi-select)
            hard_skills: [],
            soft_skills: [],
            certifications: [],
            licenses: [],
            
            // Work Arrangement
            employment_type: '',
            contract_type: '',
            work_schedule: '',
            shift_details: '',
            remote_work: '',
            travel_required: '',
            
            // Location
            country: '',
            region: '',
            city: '',
            
            // Company Information
            company_size: '',
            companies: [],
            
            // Salary
            salary_min: null,
            salary_max: null,
            has_salary: false,
            salary_currency: '',
            salary_period: '',
            
            // Benefits & Perks
            benefits: [],
            work_environment: [],
            professional_development: [],
            work_life_balance: [],
            
            // Work Conditions
            physical_requirements: [],
            work_conditions: [],
            special_requirements: []
        };
    }

    /**
     * Apply all filters to the jobs array
     */
    filterJobs(jobs, filters = this.filters) {
        return jobs.filter(job => {
            // Search filter (title, company, skills)
            if (filters.search) {
                const searchLower = filters.search.toLowerCase();
                const matchesSearch = 
                    (job.title || '').toLowerCase().includes(searchLower) ||
                    (job.company || '').toLowerCase().includes(searchLower) ||
                    (job.hard_skills || []).some(skill => skill.toLowerCase().includes(searchLower)) ||
                    (job.soft_skills || []).some(skill => skill.toLowerCase().includes(searchLower));
                if (!matchesSearch) return false;
            }

            // Hierarchical filters (industry -> department -> job_family -> specialization)
            if (filters.industry && job.industry_id !== parseInt(filters.industry)) return false;
            if (filters.department && job.department_id !== parseInt(filters.department)) return false;
            if (filters.job_family && job.job_family_id !== parseInt(filters.job_family)) return false;
            if (filters.specialization && job.specialization_id !== parseInt(filters.specialization)) return false;
            
            // Job function
            if (filters.job_function && job.job_function_id !== parseInt(filters.job_function)) return false;
            
            // Seniority level
            if (filters.seniority_level && job.seniority_level_id !== parseInt(filters.seniority_level)) return false;
            
            // Required education
            if (filters.required_education && job.required_education_id !== parseInt(filters.required_education)) return false;
            
            // Experience filters
            if (filters.experience_min !== null && job.experience_years_min < filters.experience_min) return false;
            if (filters.experience_max !== null && job.experience_years_max > filters.experience_max) return false;
            
            // Skills filters (multi-select)
            if (filters.hard_skills.length > 0) {
                const jobSkills = (job.hard_skills || []).map(s => s.toLowerCase());
                const hasRequiredSkill = filters.hard_skills.some(skill => 
                    jobSkills.includes(skill.toLowerCase())
                );
                if (!hasRequiredSkill) return false;
            }
            
            if (filters.soft_skills.length > 0) {
                const jobSkills = (job.soft_skills || []).map(s => s.toLowerCase());
                const hasRequiredSkill = filters.soft_skills.some(skill => 
                    jobSkills.includes(skill.toLowerCase())
                );
                if (!hasRequiredSkill) return false;
            }
            
            if (filters.certifications.length > 0) {
                const jobCerts = (job.certifications || []).map(c => c.toLowerCase());
                const hasRequiredCert = filters.certifications.some(cert => 
                    jobCerts.includes(cert.toLowerCase())
                );
                if (!hasRequiredCert) return false;
            }
            
            if (filters.licenses.length > 0) {
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
            if (filters.companies.length > 0 && !filters.companies.includes(job.company)) return false;
            
            // Salary filters
            if (filters.has_salary && (!job.min_salary_mdl && !job.max_salary_mdl)) return false;
            if (filters.salary_min !== null && job.min_salary_mdl && job.min_salary_mdl < filters.salary_min) return false;
            if (filters.salary_max !== null && job.max_salary_mdl && job.max_salary_mdl > filters.salary_max) return false;
            if (filters.salary_currency && job.salary_currency_id !== parseInt(filters.salary_currency)) return false;
            if (filters.salary_period && job.salary_period_id !== parseInt(filters.salary_period)) return false;
            
            // Benefits and perks filters
            if (filters.benefits.length > 0) {
                const jobBenefits = (job.benefits || []).map(b => b.toLowerCase());
                const hasRequiredBenefit = filters.benefits.some(benefit => 
                    jobBenefits.includes(benefit.toLowerCase())
                );
                if (!hasRequiredBenefit) return false;
            }
            
            if (filters.work_environment.length > 0) {
                const jobEnv = (job.work_environment || []).map(e => e.toLowerCase());
                const hasRequiredEnv = filters.work_environment.some(env => 
                    jobEnv.includes(env.toLowerCase())
                );
                if (!hasRequiredEnv) return false;
            }
            
            if (filters.professional_development.length > 0) {
                const jobDev = (job.professional_development || []).map(d => d.toLowerCase());
                const hasRequiredDev = filters.professional_development.some(dev => 
                    jobDev.includes(dev.toLowerCase())
                );
                if (!hasRequiredDev) return false;
            }
            
            if (filters.work_life_balance.length > 0) {
                const jobBalance = (job.work_life_balance || []).map(b => b.toLowerCase());
                const hasRequiredBalance = filters.work_life_balance.some(balance => 
                    jobBalance.includes(balance.toLowerCase())
                );
                if (!hasRequiredBalance) return false;
            }
            
            // Work conditions filters
            if (filters.physical_requirements.length > 0) {
                const jobPhysical = (job.physical_requirements || []).map(p => p.toLowerCase());
                const hasRequiredPhysical = filters.physical_requirements.some(physical => 
                    jobPhysical.includes(physical.toLowerCase())
                );
                if (!hasRequiredPhysical) return false;
            }
            
            if (filters.work_conditions.length > 0) {
                const jobConditions = (job.work_conditions || []).map(c => c.toLowerCase());
                const hasRequiredCondition = filters.work_conditions.some(condition => 
                    jobConditions.includes(condition.toLowerCase())
                );
                if (!hasRequiredCondition) return false;
            }
            
            if (filters.special_requirements.length > 0) {
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
     * Get paginated results from filtered jobs
     */
    paginateJobs(filteredJobs, page = 1, pageSize = 100) {
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        
        return {
            jobs: filteredJobs.slice(startIndex, endIndex),
            page: page,
            totalPages: Math.ceil(filteredJobs.length / pageSize),
            totalJobs: filteredJobs.length
        };
    }

    /**
     * Apply filters and pagination in one operation
     */
    filterAndPaginate(jobs, filters = this.filters, page = 1, pageSize = 100) {
        const filteredJobs = this.filterJobs(jobs, filters);
        return this.paginateJobs(filteredJobs, page, pageSize);
    }

    /**
     * Reset all filters to default state
     */
    resetFilters() {
        this.filters = this.createDefaultFilters();
    }

    /**
     * Update a specific filter
     */
    updateFilter(key, value) {
        if (key in this.filters) {
            this.filters[key] = value;
        }
    }

    /**
     * Get statistics for current filters
     */
    getFilterStats(jobs) {
        const filteredJobs = this.filterJobs(jobs);
        
        return {
            totalJobs: jobs.length,
            filteredJobs: filteredJobs.length,
            companies: new Set(filteredJobs.map(j => j.company)).size,
            cities: new Set(filteredJobs.map(j => j.city)).size
        };
    }

    /**
     * Get filter metadata for UI
     */
    getFilterMetadata(jobs) {
        const stats = {};
        
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
            stats[dim] = {};
            jobs.forEach(job => {
                const value = job[dim];
                if (value) {
                    stats[dim][value] = (stats[dim][value] || 0) + 1;
                }
            });
        });

        // Count skills
        stats.hard_skills = {};
        stats.soft_skills = {};
        stats.certifications = {};
        stats.licenses = {};
        stats.benefits = {};
        stats.work_environment = {};
        stats.professional_development = {};
        stats.work_life_balance = {};
        stats.physical_requirements = {};
        stats.work_conditions = {};
        stats.special_requirements = {};

        jobs.forEach(job => {
            ['hard_skills', 'soft_skills', 'certifications', 'licenses', 
             'benefits', 'work_environment', 'professional_development', 
             'work_life_balance', 'physical_requirements', 'work_conditions', 
             'special_requirements'].forEach(skillType => {
                (job[skillType] || []).forEach(item => {
                    if (item) {
                        stats[skillType][item.toLowerCase()] = (stats[skillType][item.toLowerCase()] || 0) + 1;
                    }
                });
            });
        });

        return stats;
    }
}

/**
 * Utility functions for filtering
 */
export const FilterUtils = {
    /**
     * Debounce function for search inputs
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Format salary range for display
     */
    formatSalaryRange(min, max) {
        if (!min && !max) return 'Not specified';
        if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()}`;
        if (min) return `From ${min.toLocaleString()}`;
        if (max) return `Up to ${max.toLocaleString()}`;
        return 'Not specified';
    },

    /**
     * Format date for display
     */
    formatDate(dateString) {
        if (!dateString) return '';
        return new Date(dateString).toLocaleDateString();
    },

    /**
     * Calculate pagination stats
     */
    getVisiblePages(currentPage, totalPages, maxVisible = 5) {
        const pages = [];
        const start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
        const end = Math.min(totalPages, start + maxVisible - 1);
        
        for (let i = start; i <= end; i++) {
            pages.push(i);
        }
        
        return pages;
    },

    /**
     * Calculate job statistics
     */
    calculateStats(jobs, metadata) {
        const total = metadata?.total_jobs || jobs.length;
        const filtered = jobs.length;
        const companies = new Set(jobs.map(j => j.company)).size;
        const cities = new Set(jobs.map(j => j.city)).size;
        
        // Calculate average salary
        let salarySum = 0;
        let salaryCount = 0;
        jobs.forEach(job => {
            if (job.min_salary_mdl) { salarySum += job.min_salary_mdl; salaryCount++; }
            if (job.max_salary_mdl) { salarySum += job.max_salary_mdl; salaryCount++; }
        });
        const avgSalary = salaryCount > 0 ? Math.round(salarySum / salaryCount) : 0;
        
        return {
            total_jobs: total,
            filtered_jobs: filtered,
            companies,
            cities,
            avg_salary: avgSalary.toLocaleString() + ' MDL'
        };
    }
};

// Export for both Node.js and browser environments
if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment
    module.exports = { FilterManager, FilterUtils };
} else {
    // Browser environment
    window.FilterManager = FilterManager;
    window.FilterUtils = FilterUtils;
}