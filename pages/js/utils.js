/**
 * Utilities Module
 * Contains formatting functions, date utilities, and helper functions
 */

export class Utils {
    /**
     * Format a date string to locale date format
     * @param {string} dateString - ISO date string
     * @returns {string} Formatted date
     */
    static formatDate(dateString) {
        if (!dateString) return '';
        return new Date(dateString).toLocaleDateString();
    }

    /**
     * Format salary range display
     * @param {number|null} min - Minimum salary
     * @param {number|null} max - Maximum salary
     * @returns {string} Formatted salary range
     */
    static formatSalaryRange(min, max) {
        if (!min && !max) return 'Not specified';
        if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()}`;
        if (min) return `From ${min.toLocaleString()}`;
        if (max) return `Up to ${max.toLocaleString()}`;
        return 'Not specified';
    }

    /**
     * Calculate statistics from job data
     * @param {Array} jobs - Array of job objects
     * @param {Object} metadata - Metadata with total counts
     * @returns {Object} Calculated statistics
     */
    static calculateStats(jobs, metadata) {
        const total = metadata.total_jobs || 0;
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

    /**
     * Get visible page numbers for pagination
     * @param {number} currentPage - Current page number
     * @param {number} totalPages - Total number of pages
     * @returns {Array} Array of visible page numbers
     */
    static getVisiblePages(currentPage, totalPages) {
        const pages = [];
        const start = Math.max(1, currentPage - 2);
        const end = Math.min(totalPages, currentPage + 2);
        
        for (let i = start; i <= end; i++) {
            pages.push(i);
        }
        
        return pages;
    }

    /**
     * Debounce function to limit function calls
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @returns {Function} Debounced function
     */
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Check if a job matches all filter criteria
     * @param {Object} job - Job object to check
     * @param {Object} filters - Filter criteria
     * @returns {boolean} True if job matches all filters
     */
    static matchesFilters(job, filters) {
        // Text search
        if (filters.search) {
            const searchLower = filters.search.toLowerCase();
            const matchesText = job.title_display.toLowerCase().includes(searchLower) ||
                               job.company.toLowerCase().includes(searchLower) ||
                               (job.skills_preview && job.skills_preview.some(skill => 
                                   skill.toLowerCase().includes(searchLower)));
            if (!matchesText) return false;
        }

        // Job Classification
        if (filters.industry && job.industry !== filters.industry) return false;
        if (filters.department && job.department !== filters.department) return false;
        if (filters.job_family && job.job_family !== filters.job_family) return false;
        if (filters.specialization && job.specialization !== filters.specialization) return false;
        if (filters.job_function && job.job_function !== filters.job_function) return false;
        if (filters.seniority_level && job.seniority_level !== filters.seniority_level) return false;

        // Requirements
        if (filters.required_education && job.required_education !== filters.required_education) return false;
        if (filters.experience_min !== null && job.experience_years < filters.experience_min) return false;
        if (filters.experience_max !== null && job.experience_years > filters.experience_max) return false;

        // Skills
        if (filters.hard_skills.length > 0) {
            const jobSkills = job.skills_preview || [];
            const hasSkill = filters.hard_skills.some(skill => jobSkills.includes(skill));
            if (!hasSkill) return false;
        }
        if (filters.soft_skills.length > 0) {
            const jobSkills = job.skills_preview || [];
            const hasSkill = filters.soft_skills.some(skill => jobSkills.includes(skill));
            if (!hasSkill) return false;
        }

        // Work Arrangement
        if (filters.employment_type && job.employment_type !== filters.employment_type) return false;
        if (filters.contract_type && job.contract_type !== filters.contract_type) return false;
        if (filters.work_schedule && job.work_schedule !== filters.work_schedule) return false;
        if (filters.shift_details && job.shift_details !== filters.shift_details) return false;
        if (filters.remote_work && job.remote_work !== filters.remote_work) return false;
        if (filters.travel_required && job.travel_required !== filters.travel_required) return false;

        // Location
        if (filters.country && job.country !== filters.country) return false;
        if (filters.region && job.region !== filters.region) return false;
        if (filters.city && job.city !== filters.city) return false;

        // Company
        if (filters.company_size && job.company_size !== filters.company_size) return false;
        if (filters.companies.length > 0 && !filters.companies.includes(job.company)) return false;

        // Salary
        if (filters.has_salary && !job.min_salary_mdl && !job.max_salary_mdl) return false;
        if (filters.salary_min !== null && job.min_salary_mdl < filters.salary_min) return false;
        if (filters.salary_max !== null && job.max_salary_mdl > filters.salary_max) return false;
        if (filters.salary_currency && job.salary_currency !== filters.salary_currency) return false;
        if (filters.salary_period && job.salary_period !== filters.salary_period) return false;

        // Benefits & Perks
        if (filters.benefits.length > 0) {
            // Assuming benefits are in job description or separate field
            const jobBenefits = job.benefits || [];
            const hasBenefit = filters.benefits.some(benefit => jobBenefits.includes(benefit));
            if (!hasBenefit) return false;
        }

        return true;
    }

    /**
     * Sort jobs based on sort option
     * @param {Array} jobs - Array of job objects
     * @param {string} sortOption - Sort option
     * @returns {Array} Sorted jobs array
     */
    static sortJobs(jobs, sortOption) {
        const sorted = [...jobs];
        
        switch (sortOption) {
            case 'date_desc':
                return sorted.sort((a, b) => new Date(b.posting_date) - new Date(a.posting_date));
            case 'date_asc':
                return sorted.sort((a, b) => new Date(a.posting_date) - new Date(b.posting_date));
            case 'salary_desc':
                return sorted.sort((a, b) => (b.max_salary_mdl || 0) - (a.max_salary_mdl || 0));
            case 'salary_asc':
                return sorted.sort((a, b) => (a.min_salary_mdl || 0) - (b.min_salary_mdl || 0));
            case 'title_asc':
                return sorted.sort((a, b) => a.title_display.localeCompare(b.title_display));
            case 'company_asc':
                return sorted.sort((a, b) => a.company.localeCompare(b.company));
            default:
                return sorted;
        }
    }
}

// Create global utils instance
window.Utils = Utils;