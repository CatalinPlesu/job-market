/**
 * Filters Module
 * Handles filter logic, computed properties, and filter operations
 */

import { JobMarketAPI } from './api.js';

export class FilterManager {
    constructor() {
        this.api = JobMarketAPI;
        this.lookups = {};
        this.metadata = {};
        
        // Initialize default filters
        this.filters = {
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

    // Filter state management
    setFilter(key, value) {
        this.filters[key] = value;
        this.updateURL();
        return this.filters;
    }

    resetFilters() {
        Object.assign(this.filters, {
            search: '',
            industry: '',
            department: '',
            job_family: '',
            specialization: '',
            job_function: '',
            seniority_level: '',
            required_education: '',
            experience_min: null,
            experience_max: null,
            hard_skills: [],
            soft_skills: [],
            certifications: [],
            licenses: [],
            employment_type: '',
            contract_type: '',
            work_schedule: '',
            shift_details: '',
            remote_work: '',
            travel_required: '',
            country: '',
            region: '',
            city: '',
            company_size: '',
            companies: [],
            salary_min: null,
            salary_max: null,
            has_salary: false,
            salary_currency: '',
            salary_period: '',
            benefits: [],
            work_environment: [],
            professional_development: [],
            work_life_balance: [],
            physical_requirements: [],
            work_conditions: [],
            special_requirements: []
        });
        this.updateURL();
        return this.filters;
    }

    // Computed properties
    get filteredDepartments() {
        if (!this.filters.industry) return this.lookups.departments || [];
        const industryId = parseInt(this.filters.industry);
        return (this.lookups.departments || []).filter(d => 
            d.parent_industry === industryId
        );
    }

    get filteredJobFamilies() {
        if (!this.filters.department) return this.lookups.job_families || [];
        const departmentId = parseInt(this.filters.department);
        return (this.lookups.job_families || []).filter(f => 
            f.parent_department === departmentId
        );
    }

    get filteredSpecializations() {
        if (!this.filters.job_family) return this.lookups.specializations || [];
        const familyId = parseInt(this.filters.job_family);
        return (this.lookups.specializations || []).filter(s => 
            s.parent_job_family === familyId
        );
    }

    get filteredJobFunctions() {
        return this.sortByJobsCount(this.lookups.job_functions || []);
    }

    get filteredContractTypes() {
        return this.sortByJobsCount(this.lookups.contract_types || []);
    }

    get filteredWorkSchedules() {
        return this.sortByJobsCount(this.lookups.work_schedules || []);
    }

    get filteredShiftDetails() {
        return this.sortByJobsCount(this.lookups.shift_details || []);
    }

    get filteredRequiredEducation() {
        return this.sortByJobsCount(this.lookups.required_education || []);
    }

    get filteredCompanySizes() {
        return this.sortByJobsCount(this.lookups.company_sizes || []);
    }

    get filteredTravelRequired() {
        return this.sortByJobsCount(this.lookups.travel_required || []);
    }

    get filteredCountries() {
        return this.sortByJobsCount(this.lookups.countries || []);
    }

    get filteredRegions() {
        return this.sortByJobsCount(this.lookups.regions || []);
    }

    get filteredSalaryCurrencies() {
        return this.sortByJobsCount(this.lookups.salary_currencies || []);
    }

    get filteredSalaryPeriods() {
        return this.sortByJobsCount(this.lookups.salary_periods || []);
    }

    get filteredHardSkills() {
        return this.filterAndSortSkills(this.lookups.hard_skills || []);
    }

    get filteredSoftSkills() {
        return this.filterAndSortSkills(this.lookups.soft_skills || []);
    }

    get filteredCertifications() {
        return this.filterAndSortItems(this.lookups.certifications || []);
    }

    get filteredLicenses() {
        return this.filterAndSortItems(this.lookups.licenses || []);
    }

    get filteredBenefits() {
        return this.filterAndSortItems(this.lookups.benefits || []);
    }

    get filteredWorkEnvironment() {
        return this.filterAndSortItems(this.lookups.work_environment || []);
    }

    get filteredProfessionalDevelopment() {
        return this.filterAndSortItems(this.lookups.professional_development || []);
    }

    get filteredWorkLifeBalance() {
        return this.filterAndSortItems(this.lookups.work_life_balance || []);
    }

    get filteredPhysicalRequirements() {
        return this.filterAndSortItems(this.lookups.physical_requirements || []);
    }

    get filteredWorkConditions() {
        return this.filterAndSortItems(this.lookups.work_conditions || []);
    }

    get filteredSpecialRequirements() {
        return this.filterAndSortItems(this.lookups.special_requirements || []);
    }

    get filteredEmploymentTypes() {
        return this.sortByJobsCount(this.lookups.employment_types || []);
    }

    get filteredRemoteWork() {
        return this.sortByJobsCount(this.lookups.remote_work || []);
    }

    get filteredSeniorityLevels() {
        return this.metadata.filter_metadata?.seniority_levels ? 
            this.sortByJobsCount(Object.values(this.metadata.filter_metadata.seniority_levels).map(l => ({ 
                id: l.name, 
                name: l.name, 
                jobs_count: l.jobs_count 
            }))) : [];
    }

    // Utility methods
    sortByJobsCount(items) {
        return [...items].sort((a, b) => (b.jobs_count || 0) - (a.jobs_count || 0));
    }

    filterAndSortSkills(items) {
        return this.sortByJobsCount(items)
            .slice(0, 100);
    }

    filterAndSortItems(items) {
        return this.sortByJobsCount(items)
            .slice(0, 50);
    }

    updateURL() {
        const params = new URLSearchParams();
        
        // Add filters to URL
        Object.entries(this.filters).forEach(([key, value]) => {
            if (value !== '' && value !== null && value !== false && (Array.isArray(value) ? value.length > 0 : true)) {
                if (Array.isArray(value)) {
                    params.set(key, value.join(','));
                } else {
                    params.set(key, value.toString());
                }
            }
        });

        const newUrl = `${window.location.pathname}?${params.toString()}`;
        history.replaceState({}, '', newUrl);
    }

    parseURL() {
        const urlParams = new URLSearchParams(window.location.search);
        
        // Parse filters
        Object.keys(this.filters).forEach(key => {
            const value = urlParams.get(key);
            if (value) {
                if (Array.isArray(this.filters[key])) {
                    this.filters[key] = value.split(',');
                } else if (typeof this.filters[key] === 'number') {
                    this.filters[key] = parseInt(value);
                } else if (typeof this.filters[key] === 'boolean') {
                    this.filters[key] = value === 'true';
                } else {
                    this.filters[key] = value;
                }
            }
        });
    }
}

// Create global filter manager instance
window.FilterManager = new FilterManager();