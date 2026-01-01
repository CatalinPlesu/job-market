// API Configuration
const API_BASE = '/api';

// API Client
const api = {
    getJobsIndex: () => m.request({ url: `${API_BASE}/jobs/index.json` }),
    getJobsPage: (page) => m.request({ url: `${API_BASE}/jobs/page-${page}.json` }),
    getAnalysisIndex: () => m.request({ url: `${API_BASE}/analysis/index.json` }),
    getAnalysis: (filename) => m.request({ url: `${API_BASE}/analysis/${filename}` })
};

// State Management
const state = {
    jobsIndex: null,
    currentPage: 1,
    jobs: [],
    allLoadedJobs: [], // Cache of all jobs loaded so far
    loadedPages: new Set(), // Track which pages have been loaded
    filters: {
        salaryMin: null,
        salaryMax: null,
        experienceMin: null,
        experienceMax: null
    },
    loading: false,
    analysisIndex: null,
    selectedAnalysis: null,
    selectedAnalysisData: null,
    itemsPerPage: 20, // User-configurable items per page for display
    availablePageSizes: [10, 20, 50, 100]
};

// Utility Functions
const formatSalary = (salary) => {
    if (!salary || !salary.min) return 'Not specified';
    const min = salary.min.toLocaleString();
    const max = salary.max ? salary.max.toLocaleString() : '';
    return max ? `${min} - ${max} ${salary.currency}` : `${min} ${salary.currency}`;
};

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString();
};

// Components

// Header Component
const Header = {
    view: () => m('div', { class: 'navbar bg-base-100 shadow-lg' }, [
        m('div', { class: 'navbar-start' }, [
            m('a', { 
                class: 'btn btn-ghost text-xl', 
                href: '#!/',
                oncreate: m.route.link 
            }, 'Moldova Job Market')
        ]),
        m('div', { class: 'navbar-center hidden lg:flex' }, [
            m('ul', { class: 'menu menu-horizontal px-1' }, [
                m('li', m('a', { href: '#!/', oncreate: m.route.link }, 'Home')),
                m('li', m('a', { href: '#!/jobs', oncreate: m.route.link }, 'Jobs')),
                m('li', m('a', { href: '#!/analysis', oncreate: m.route.link }, 'Analysis'))
            ])
        ]),
        m('div', { class: 'navbar-end' }, [
            m('label', { class: 'swap swap-rotate btn btn-ghost btn-circle' }, [
                m('input', { 
                    type: 'checkbox',
                    onchange: (e) => {
                        const theme = e.target.checked ? 'dark' : 'light';
                        document.documentElement.setAttribute('data-theme', theme);
                    }
                }),
                m('svg', { class: 'swap-on fill-current w-6 h-6', xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24' }, 
                    m('path', { d: 'M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z' })),
                m('svg', { class: 'swap-off fill-current w-6 h-6', xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24' }, 
                    m('path', { d: 'M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z' }))
            ])
        ])
    ])
};

// Footer Component
const Footer = {
    view: () => m('footer', { class: 'footer footer-center p-4 bg-base-300 text-base-content mt-8' }, [
        m('div', [
            m('p', '© 2026 Moldova Job Market - Data updated regularly')
        ])
    ])
};

// Loading Component
const Loading = {
    view: () => m('div', { class: 'flex justify-center items-center h-64' }, [
        m('span', { class: 'loading loading-spinner loading-lg' })
    ])
};

// Home Page
const HomePage = {
    oninit: () => {
        api.getJobsIndex().then(data => {
            state.jobsIndex = data;
        });
    },
    view: () => m('div', { class: 'container mx-auto px-4 py-8' }, [
        m('div', { class: 'hero min-h-[50vh] bg-base-200 rounded-lg' }, [
            m('div', { class: 'hero-content text-center' }, [
                m('div', { class: 'max-w-md' }, [
                    m('h1', { class: 'text-5xl font-bold' }, 'Moldova Job Market'),
                    m('p', { class: 'py-6' }, 'Browse thousands of job opportunities across Moldova. Filter by location, salary, skills, and more.'),
                    state.jobsIndex ? [
                        m('div', { class: 'stats shadow mb-6' }, [
                            m('div', { class: 'stat' }, [
                                m('div', { class: 'stat-title' }, 'Total Jobs'),
                                m('div', { class: 'stat-value' }, state.jobsIndex.total_jobs.toLocaleString())
                            ])
                        ]),
                        m('a', { 
                            class: 'btn btn-primary', 
                            href: '#!/jobs',
                            oncreate: m.route.link 
                        }, 'Browse Jobs')
                    ] : m(Loading)
                ])
            ])
        ])
    ])
};

// Job List Item Component (Extra Slim - HN Style)
const JobListItem = {
    view: (vnode) => {
        const job = vnode.attrs.job;
        return m('div', { class: 'job-item px-2 py-1 border-b border-base-300' }, [
            m('div', { class: 'flex items-start gap-2' }, [
                m('span', { class: 'text-xs opacity-60 mt-1' }, `${vnode.attrs.index}.`),
                m('div', { class: 'flex-1' }, [
                    m('a', { 
                        href: `#!/jobs/${job.id}`,
                        class: 'job-title font-medium hover:underline text-base-content',
                        oncreate: m.route.link
                    }, job.title),
                    m('div', { class: 'job-meta flex flex-wrap gap-2 mt-1 text-sm opacity-70' }, [
                        job.company && m('span', { class: 'badge badge-outline badge-sm' }, job.company),
                        job.location && job.location.city && m('span', job.location.city),
                        job.salary && m('span', formatSalary(job.salary)),
                        job.posting_date && m('span', formatDate(job.posting_date))
                    ])
                ])
            ])
        ]);
    }
};

// Helper function to get field value from a job object
const getJobFieldValue = (job, fieldKey) => {
    switch (fieldKey) {
        case 'job_function': return job.job_function;
        case 'seniority_level': return job.seniority_level;
        case 'industry': return job.industry;
        case 'department': return job.department;
        case 'job_family': return job.job_family;
        case 'specialization': return job.specialization;
        case 'education_level': return job.requirements?.education;
        case 'languages': return job.requirements?.languages;
        case 'hard_skills': return job.requirements?.hard_skills;
        case 'soft_skills': return job.requirements?.soft_skills;
        case 'certifications': return job.requirements?.certifications;
        case 'licenses_required': return job.requirements?.licenses;
        case 'employment_type': return job.employment?.type;
        case 'contract_type': return job.employment?.contract_type;
        case 'work_schedule': return job.employment?.work_schedule;
        case 'shift_details': return job.employment?.shift_details;
        case 'remote_work': return job.employment?.remote_work;
        case 'travel_required': return job.employment?.travel_required;
        case 'city': return job.location?.city;
        case 'region': return job.location?.region;
        case 'country': return job.location?.country;
        case 'company_name': return job.company;
        case 'company_size': return job.company_size;
        case 'benefits': return job.benefits;
        case 'work_environment': return job.work_environment;
        case 'professional_development': return job.professional_development;
        case 'work_life_balance': return job.work_life_balance;
        case 'physical_requirements': return job.physical_requirements;
        case 'work_conditions': return job.work_conditions;
        case 'special_requirements': return job.special_requirements;
        default: return null;
    }
};

// Filter matching logic - ALL filters work as AND (combined)
const matchesFilters = (job, filters) => {
    for (const [key, value] of Object.entries(filters)) {
        if (value === null || value === undefined || value === '') continue;
        
        switch (key) {
            // Job Details
            case 'job_function':
                if (job.job_function !== value) return false;
                break;
            case 'seniority_level':
                if (job.seniority_level !== value) return false;
                break;
            case 'industry':
                if (job.industry !== value) return false;
                break;
            case 'department':
                if (job.department !== value) return false;
                break;
            case 'job_family':
                if (job.job_family !== value) return false;
                break;
            case 'specialization':
                if (job.specialization !== value) return false;
                break;
            
            // Requirements
            case 'education_level':
                if (job.requirements?.education !== value) return false;
                break;
            case 'languages':
                if (!job.requirements?.languages || !job.requirements.languages.includes(value)) return false;
                break;
            case 'hard_skills':
                if (!job.requirements?.hard_skills || !job.requirements.hard_skills.some(skill => skill.includes(value))) return false;
                break;
            case 'soft_skills':
                if (!job.requirements?.soft_skills || !job.requirements.soft_skills.some(skill => skill.includes(value))) return false;
                break;
            case 'certifications':
                if (!job.requirements?.certifications || !job.requirements.certifications.includes(value)) return false;
                break;
            case 'licenses_required':
                if (!job.requirements?.licenses || !job.requirements.licenses.includes(value)) return false;
                break;
            
            // Work Arrangement
            case 'employment_type':
                if (job.employment?.type !== value) return false;
                break;
            case 'contract_type':
                if (job.employment?.contract !== value) return false;
                break;
            case 'work_schedule':
                if (job.employment?.schedule !== value) return false;
                break;
            case 'shift_details':
                if (job.employment?.shift !== value) return false;
                break;
            case 'remote_work':
                if (job.location?.remote_work !== value) return false;
                break;
            case 'travel_required':
                if (job.requirements?.travel !== value) return false;
                break;
            
            // Location
            case 'city':
                if (job.location?.city !== value) return false;
                break;
            case 'region':
                if (job.location?.region !== value) return false;
                break;
            case 'country':
                if (job.location?.country !== value) return false;
                break;
            
            // Company
            case 'company':
                if (job.company !== value) return false;
                break;
            case 'company_size':
                if (job.company_size !== value) return false;
                break;
            
            // Benefits & Culture
            case 'benefits':
                if (!job.benefits || !job.benefits.includes(value)) return false;
                break;
            case 'work_environment':
                if (!job.work_environment || !job.work_environment.includes(value)) return false;
                break;
            case 'professional_development':
                if (!job.professional_development || !job.professional_development.includes(value)) return false;
                break;
            case 'work_life_balance':
                if (!job.work_life_balance || !job.work_life_balance.includes(value)) return false;
                break;
            
            // Conditions
            case 'physical_requirements':
                if (!job.requirements?.physical || !job.requirements.physical.includes(value)) return false;
                break;
            case 'work_conditions':
                if (!job.work_conditions || !job.work_conditions.includes(value)) return false;
                break;
            case 'special_requirements':
                if (!job.requirements?.special || !job.requirements.special.includes(value)) return false;
                break;
            
            // Numeric Filters
            case 'salaryMin':
                const jobMinSalary = job.salary?.min_mdl || job.salary?.min;
                if (!jobMinSalary) return false;
                if (jobMinSalary < value) return false;
                break;
            case 'salaryMax':
                const jobMaxSalary = job.salary?.max_mdl || job.salary?.max;
                if (!jobMaxSalary) return false;
                if (jobMaxSalary > value) return false;
                break;
            case 'experienceMin':
                const jobExpYears = job.requirements?.experience_years;
                if (jobExpYears === null || jobExpYears === undefined) return false;
                if (jobExpYears < value) return false;
                break;
            case 'experienceMax':
                const jobExpYearsMax = job.requirements?.experience_years;
                if (jobExpYearsMax === null || jobExpYearsMax === undefined) return false;
                if (jobExpYearsMax > value) return false;
                break;
        }
    }
    return true;
};

// Get available filter options based on current filters (hierarchical)
const getAvailableOptions = (jobs, filterKey) => {
    const options = new Set();
    jobs.forEach(job => {
        let value;
        switch (filterKey) {
            case 'job_function':
                value = job.job_function;
                break;
            case 'seniority_level':
                value = job.seniority_level;
                break;
            case 'city':
                value = job.location?.city;
                break;
            case 'remote_work':
                value = job.location?.remote_work;
                break;
            case 'industry':
                value = job.industry;
                break;
            case 'company':
                value = job.company;
                break;
            case 'employment_type':
                value = job.employment?.type;
                break;
            case 'contract_type':
                value = job.employment?.contract;
                break;
        }
        if (value) options.add(value);
    });
    return Array.from(options).sort();
};

// Filter Component with Hierarchical Filtering (Left Sidebar)
const FilterPanel = {
    showAdvanced: false,
    view: () => {
        if (!state.jobsIndex) return null;
        
        // Get filtered jobs based on current filters for hierarchical filtering
        const filteredJobs = state.allLoadedJobs.filter(job => matchesFilters(job, state.filters));
        
        // Calculate salary range from all jobs
        const salaryRange = { min: 0, max: 100000 };
        state.allLoadedJobs.forEach(job => {
            const minSalary = job.salary?.min_mdl || job.salary?.min;
            const maxSalary = job.salary?.max_mdl || job.salary?.max;
            if (minSalary && minSalary > 0) salaryRange.min = Math.min(salaryRange.min === 0 ? minSalary : salaryRange.min, minSalary);
            if (maxSalary) salaryRange.max = Math.max(salaryRange.max, maxSalary);
        });
        
        // All available filter fields - organized following schema order
        // Excludes non-filterable fields like contact info
        const filterFields = [
            // Job Details
            { key: 'seniority_level', label: 'Seniority Level', section: 'Job Details' },
            { key: 'industry', label: 'Industry', section: 'Job Details' },
            { key: 'department', label: 'Department', section: 'Job Details' },
            { key: 'job_family', label: 'Job Family', section: 'Job Details' },
            { key: 'specialization', label: 'Specialization', section: 'Job Details' },
            { key: 'job_function', label: 'Job Function', section: 'Job Details' },
            
            // Requirements
            { key: 'education_level', label: 'Required Education', section: 'Requirements' },
            { key: 'languages', label: 'Languages', section: 'Requirements' },
            { key: 'hard_skills', label: 'Hard Skills', section: 'Requirements' },
            { key: 'soft_skills', label: 'Soft Skills', section: 'Requirements' },
            { key: 'certifications', label: 'Certifications', section: 'Requirements' },
            { key: 'licenses_required', label: 'Licenses', section: 'Requirements' },
            
            // Work Arrangement
            { key: 'employment_type', label: 'Employment Type', section: 'Work Arrangement' },
            { key: 'contract_type', label: 'Contract Type', section: 'Work Arrangement' },
            { key: 'work_schedule', label: 'Work Schedule', section: 'Work Arrangement' },
            { key: 'shift_details', label: 'Shift Details', section: 'Work Arrangement' },
            { key: 'remote_work', label: 'Remote Work', section: 'Work Arrangement' },
            { key: 'travel_required', label: 'Travel Required', section: 'Work Arrangement' },
            
            // Location
            { key: 'city', label: 'City', section: 'Location' },
            { key: 'region', label: 'Region', section: 'Location' },
            { key: 'country', label: 'Country', section: 'Location' },
            
            // Company
            { key: 'company', label: 'Company Name', section: 'Company' },
            { key: 'company_size', label: 'Company Size', section: 'Company' },
            
            // Benefits & Culture
            { key: 'benefits', label: 'Benefits', section: 'Benefits & Culture' },
            { key: 'work_environment', label: 'Work Environment', section: 'Benefits & Culture' },
            { key: 'professional_development', label: 'Professional Development', section: 'Benefits & Culture' },
            { key: 'work_life_balance', label: 'Work Life Balance', section: 'Benefits & Culture' },
            
            // Conditions
            { key: 'physical_requirements', label: 'Physical Requirements', section: 'Conditions' },
            { key: 'work_conditions', label: 'Work Conditions', section: 'Conditions' },
            { key: 'special_requirements', label: 'Special Requirements', section: 'Conditions' }
        ];
        
        const handleFilterChange = () => {
            JobsPage.displayPage = 1;
            m.redraw();
        };
        
        return m('div', { class: 'bg-base-200 p-4' }, [
            m('div', { class: 'flex justify-between items-center mb-4' }, [
                m('h3', { class: 'font-bold text-lg' }, 'Filters'),
                m('button', { 
                    class: 'btn btn-xs btn-ghost',
                    onclick: () => {
                        // Clear all filters - both numeric and categorical
                        Object.keys(state.filters).forEach(key => {
                            state.filters[key] = null;
                        });
                        handleFilterChange();
                    }
                }, 'Clear All')
            ]),
            
            // Salary Range Filter
            m('div', { class: 'form-control mb-6' }, [
                m('label', { class: 'label' }, m('span', { class: 'label-text font-semibold' }, 'Salary Range (MDL)')),
                m('div', { class: 'space-y-2' }, [
                    m('input', { 
                        type: 'number',
                        class: `input input-bordered input-sm w-full ${state.filters.salaryMin ? 'input-info' : ''}`,
                        placeholder: 'Minimum',
                        value: state.filters.salaryMin || '',
                        oninput: (e) => {
                            state.filters.salaryMin = e.target.value ? parseInt(e.target.value) : null;
                            handleFilterChange();
                        }
                    }),
                    m('input', { 
                        type: 'number',
                        class: `input input-bordered input-sm w-full ${state.filters.salaryMax ? 'input-info' : ''}`,
                        placeholder: 'Maximum',
                        value: state.filters.salaryMax || '',
                        oninput: (e) => {
                            state.filters.salaryMax = e.target.value ? parseInt(e.target.value) : null;
                            handleFilterChange();
                        }
                    }),
                    (state.filters.salaryMin || state.filters.salaryMax) && m('div', { class: 'text-xs opacity-70' }, 
                        `${state.filters.salaryMin ? state.filters.salaryMin.toLocaleString() : '0'} - ${state.filters.salaryMax ? state.filters.salaryMax.toLocaleString() : '∞'} MDL`
                    )
                ])
            ]),
            
            // Experience Years Filter
            m('div', { class: 'form-control mb-6' }, [
                m('label', { class: 'label' }, m('span', { class: 'label-text font-semibold' }, 'Experience (Years)')),
                m('div', { class: 'space-y-2' }, [
                    m('input', { 
                        type: 'number',
                        class: `input input-bordered input-sm w-full ${state.filters.experienceMin !== null ? 'input-info' : ''}`,
                        placeholder: 'Minimum',
                        min: 0,
                        value: state.filters.experienceMin !== null ? state.filters.experienceMin : '',
                        oninput: (e) => {
                            state.filters.experienceMin = e.target.value ? parseInt(e.target.value) : null;
                            handleFilterChange();
                        }
                    }),
                    m('input', { 
                        type: 'number',
                        class: `input input-bordered input-sm w-full ${state.filters.experienceMax !== null ? 'input-info' : ''}`,
                        placeholder: 'Maximum',
                        min: 0,
                        value: state.filters.experienceMax !== null ? state.filters.experienceMax : '',
                        oninput: (e) => {
                            state.filters.experienceMax = e.target.value ? parseInt(e.target.value) : null;
                            handleFilterChange();
                        }
                    }),
                    (state.filters.experienceMin !== null || state.filters.experienceMax !== null) && 
                        m('div', { class: 'text-xs opacity-70' }, 
                            `${state.filters.experienceMin || 0} - ${state.filters.experienceMax || '∞'} years`
                        )
                ])
            ]),
            
            m('div', { class: 'divider' }),
            
            // All filters grouped by section
            m('div', { class: 'space-y-6' },
                // Group filters by section
                Object.entries(
                    filterFields.reduce((acc, field) => {
                        if (!acc[field.section]) acc[field.section] = [];
                        acc[field.section].push(field);
                        return acc;
                    }, {})
                ).map(([section, fields]) => 
                    m('div', { class: 'space-y-2' }, [
                        m('div', { class: 'text-xs font-semibold opacity-60 uppercase tracking-wide' }, section),
                        ...fields.map(field => {
                            // Define hierarchical field relationships
                            const hierarchyLevels = ['industry', 'department', 'job_family', 'specialization'];
                            const currentFieldIndex = hierarchyLevels.indexOf(field.key);
                            
                            // Determine which filters to use for calculating options
                            let filterForOptions;
                            
                            // If this field is part of the hierarchy, use special filtering logic
                            if (currentFieldIndex !== -1) {
                                // For hierarchy fields, ONLY use parent fields in the hierarchy
                                // Ignore all other filters (seniority, location, etc.) AND child fields
                                filterForOptions = {};
                                for (let i = 0; i < currentFieldIndex; i++) {
                                    const parentKey = hierarchyLevels[i];
                                    if (state.filters[parentKey]) {
                                        filterForOptions[parentKey] = state.filters[parentKey];
                                    }
                                }
                            } else {
                                // For non-hierarchical fields, exclude this field but include all others
                                filterForOptions = { ...state.filters };
                                delete filterForOptions[field.key];
                            }
                            
                            const baseFilteredJobs = state.allLoadedJobs.filter(job => matchesFilters(job, filterForOptions));
                            
                            // Extract unique values from filtered jobs for this field
                            const availableValuesSet = new Set();
                            baseFilteredJobs.forEach(job => {
                                const value = getJobFieldValue(job, field.key);
                                if (value !== null && value !== undefined && value !== '') {
                                    if (Array.isArray(value)) {
                                        value.forEach(v => availableValuesSet.add(v));
                                    } else {
                                        availableValuesSet.add(value);
                                    }
                                }
                            });
                            const availableOptions = Array.from(availableValuesSet).sort();
                            
                            // Calculate counts for each option
                            const optionCounts = {};
                            availableOptions.forEach(option => {
                                // Create temporary filter state with this option
                                const tempFilters = { ...state.filters, [field.key]: option };
                                // Count how many jobs match with this option
                                const count = state.allLoadedJobs.filter(job => matchesFilters(job, tempFilters)).length;
                                optionCounts[option] = count;
                            });
                            
                            return m('div', { class: 'form-control' }, [
                                m('label', { class: 'label py-1' }, [
                                    m('span', { class: 'label-text text-sm' }, field.label)
                                ]),
                                m('select', { 
                                    class: `select select-bordered select-sm w-full ${state.filters[field.key] ? 'select-info' : ''}`,
                                    value: state.filters[field.key] || '',
                                    onchange: (e) => {
                                        if (e.target.value) {
                                            state.filters[field.key] = e.target.value;
                                        } else {
                                            state.filters[field.key] = null;
                                        }
                                        handleFilterChange();
                                    }
                                }, [
                                    m('option', { value: '' }, 'All'),
                                    ...availableOptions
                                        .filter(f => (optionCounts[f] || 0) > 0)  // Only show options with at least 1 job
                                        .map(f => 
                                            m('option', { value: f }, `${f} (${optionCounts[f]})`)
                                        )
                                ])
                            ]);
                        })
                    ])
                )
            )
        ]);
    }
};

// Jobs Page
const JobsPage = {
    displayPage: 1, // Current display page for filtered results
    
    oninit: async () => {
        // Skip if data is already loaded
        if (state.allLoadedJobs && state.allLoadedJobs.length > 0) {
            return;
        }
        
        state.loading = true;
        try {
            // Load index first to know how many pages we need
            const index = await api.getJobsIndex();
            state.jobsIndex = index;
            state.loadedPages = new Set();
            
            // Automatically load ALL pages from the API
            const pagePromises = [];
            for (let i = 1; i <= index.total_pages; i++) {
                pagePromises.push(api.getJobsPage(i));
            }
            
            // Load all pages in parallel for speed
            const pages = await Promise.all(pagePromises);
            
            // Combine all jobs from all pages efficiently
            state.allLoadedJobs = pages.flatMap(page => page.jobs);
            pages.forEach((page, idx) => {
                state.loadedPages.add(idx + 1);
            });
            
            state.loading = false;
            m.redraw();
        } catch (err) {
            console.error('Error loading jobs:', err);
            state.loading = false;
            m.redraw();
        }
    },
    
    getDisplayedJobs: () => {
        const filtered = state.allLoadedJobs.filter(job => matchesFilters(job, state.filters));
        const start = (JobsPage.displayPage - 1) * state.itemsPerPage;
        const end = start + state.itemsPerPage;
        return {
            jobs: filtered.slice(start, end),
            total: filtered.length,
            totalPages: Math.ceil(filtered.length / state.itemsPerPage)
        };
    },
    
    navigateToPage: async (pageNumber) => {
        JobsPage.displayPage = pageNumber;
        window.scrollTo(0, 0);
        m.redraw();
    },
    
    renderPagination: (totalPages) => {
        if (totalPages <= 1) return null;
        
        const currentPage = JobsPage.displayPage;
        const pageButtons = [];
        
        // First page button
        pageButtons.push(
            m('button', {
                class: `btn btn-sm ${currentPage === 1 ? 'btn-disabled' : ''}`,
                disabled: currentPage === 1,
                onclick: () => JobsPage.navigateToPage(1)
            }, '« First')
        );
        
        // Previous button
        pageButtons.push(
            m('button', {
                class: `btn btn-sm ${currentPage === 1 ? 'btn-disabled' : ''}`,
                disabled: currentPage === 1,
                onclick: () => JobsPage.navigateToPage(currentPage - 1)
            }, '‹ Prev')
        );
        
        // Page number buttons: show current, -3 to +3
        const startPage = Math.max(1, currentPage - 3);
        const endPage = Math.min(totalPages, currentPage + 3);
        
        if (startPage > 1) {
            pageButtons.push(m('div', { class: 'px-2 py-1 text-sm text-gray-500' }, '...'));
        }
        
        for (let i = startPage; i <= endPage; i++) {
            pageButtons.push(
                m('button', {
                    class: `btn btn-sm ${i === currentPage ? 'btn-primary' : ''}`,
                    onclick: () => JobsPage.navigateToPage(i)
                }, i)
            );
        }
        
        if (endPage < totalPages) {
            pageButtons.push(m('div', { class: 'px-2 py-1 text-sm text-gray-500' }, '...'));
        }
        
        // Next button
        pageButtons.push(
            m('button', {
                class: `btn btn-sm ${currentPage === totalPages ? 'btn-disabled' : ''}`,
                disabled: currentPage === totalPages,
                onclick: () => JobsPage.navigateToPage(currentPage + 1)
            }, 'Next ›')
        );
        
        // Last page button
        pageButtons.push(
            m('button', {
                class: `btn btn-sm ${currentPage === totalPages ? 'btn-disabled' : ''}`,
                disabled: currentPage === totalPages,
                onclick: () => JobsPage.navigateToPage(totalPages)
            }, 'Last »')
        );
        
        return m('div', { class: 'flex justify-center gap-1 items-center flex-wrap' }, pageButtons);
    },
    
    view: () => {
        const { jobs, total, totalPages } = JobsPage.getDisplayedJobs();
        const hasActiveFilters = Object.keys(state.filters).some(k => state.filters[k] !== null && state.filters[k] !== undefined && state.filters[k] !== '');
        
        // Calculate accurate job counts
        const totalJobsInAPI = state.jobsIndex ? state.jobsIndex.total_jobs : 0;
        const loadedJobsCount = state.allLoadedJobs.length;
        
        return m('div', { class: 'flex min-h-0 flex-1' }, [
            // Left Sidebar - Filters
            state.jobsIndex && m('div', { class: 'w-80 border-r border-base-300 overflow-y-auto' }, [
                m(FilterPanel)
            ]),
            
            // Main Content Area
            m('div', { class: 'flex-1 overflow-y-auto min-h-0' }, [
                m('div', { class: 'container mx-auto px-4 py-8' }, [
                    m('h1', { class: 'text-3xl font-bold mb-6' }, 'Browse Jobs'),
                    
                    // Page size selector and status
                    state.jobsIndex && m('div', { class: 'flex flex-col md:flex-row justify-between items-start md:items-center gap-2 mb-4' }, [
                        m('div', { class: 'text-sm flex items-center gap-2' }, [
                            m('span', 'Items per page:'),
                            state.availablePageSizes.map(size =>
                                m('button', {
                                    class: `btn btn-xs ${state.itemsPerPage === size ? 'btn-primary' : 'btn-ghost'}`,
                                    onclick: () => {
                                        state.itemsPerPage = size;
                                        JobsPage.displayPage = 1;
                                        m.redraw();
                                    }
                                }, size)
                            )
                        ]),
                        m('div', { class: 'text-sm opacity-70' }, [
                            hasActiveFilters ? 
                                `Showing ${jobs.length} of ${total} filtered jobs` :
                                `Showing ${jobs.length} of ${totalJobsInAPI} jobs`
                        ])
                    ]),
                    
                    // Top pagination
                    state.jobsIndex && JobsPage.renderPagination(totalPages),
                    
                    state.loading ? m(Loading) : [
                        m('div', { class: 'bg-base-100 rounded-lg shadow my-4' }, [
                            jobs.length > 0 ? 
                                jobs.map((job, idx) => m(JobListItem, { 
                                    job, 
                                    index: ((JobsPage.displayPage - 1) * state.itemsPerPage) + idx + 1 
                                })) :
                                m('div', { class: 'text-center py-8 opacity-70' }, 
                                    hasActiveFilters ? 'No jobs match your filters. Try adjusting your criteria.' : 'No jobs found'
                                )
                        ]),
                        
                        // Bottom pagination
                        JobsPage.renderPagination(totalPages)
                    ]
                ])
            ])
        ]);
    }
};

// Job Detail Page
const JobDetailPage = {
    job: null,
    activeTab: 'parsed',
    oninit: (vnode) => {
        const jobId = parseInt(vnode.attrs.id);
        
        // Find job in already loaded pages or load the page containing this job
        // First check if job is in current state.jobs
        let foundJob = state.jobs.find(j => j.id === jobId);
        
        if (foundJob) {
            JobDetailPage.job = foundJob;
        } else {
            // Need to load pages to find the job
            // For now, try to find it across all pages
            // In production, index.json would tell us which page
            JobDetailPage.job = null;
            
            // Try loading pages until we find the job
            const loadPages = async () => {
                if (state.jobsIndex) {
                    for (let page = 1; page <= state.jobsIndex.total_pages; page++) {
                        try {
                            const pageData = await api.getJobsPage(page);
                            const job = pageData.jobs.find(j => j.id === jobId);
                            if (job) {
                                JobDetailPage.job = job;
                                m.redraw();
                                return;
                            }
                        } catch (err) {
                            console.error(`Error loading page ${page}:`, err);
                        }
                    }
                }
            };
            
            if (state.jobsIndex) {
                loadPages();
            } else {
                api.getJobsIndex().then(index => {
                    state.jobsIndex = index;
                    loadPages();
                });
            }
        }
    },
    view: () => {
        if (!JobDetailPage.job) return m('div', { class: 'container mx-auto px-4 py-8' }, [
            m('div', { class: 'mb-4' }, [
                m('a', { 
                    href: '#!/jobs',
                    class: 'btn btn-sm btn-ghost',
                    oncreate: m.route.link
                }, '← Back to Jobs')
            ]),
            m(Loading)
        ]);
        
        const job = JobDetailPage.job;
        
        return m('div', { class: 'container mx-auto px-4 py-8' }, [
            m('div', { class: 'mb-4' }, [
                m('a', { 
                    href: '#!/jobs',
                    class: 'btn btn-sm btn-ghost',
                    oncreate: m.route.link
                }, '← Back to Jobs')
            ]),
            
            m('div', { class: 'card bg-base-100 shadow-xl' }, [
                m('div', { class: 'card-body' }, [
                    m('h1', { class: 'card-title text-2xl' }, job.title),
                    m('div', { class: 'flex flex-wrap gap-2 mb-4' }, [
                        job.company && m('span', { class: 'badge badge-primary' }, job.company),
                        job.location?.city && m('span', { class: 'badge badge-secondary' }, job.location.city),
                        job.seniority_level && m('span', { class: 'badge badge-accent' }, job.seniority_level)
                    ]),
                    
                    // Tabs
                    m('div', { class: 'tabs tabs-boxed mb-4' }, [
                        m('a', { 
                            class: `tab ${JobDetailPage.activeTab === 'parsed' ? 'tab-active' : ''}`,
                            onclick: () => JobDetailPage.activeTab = 'parsed'
                        }, 'Job Details'),
                        m('a', { 
                            class: `tab ${JobDetailPage.activeTab === 'raw' ? 'tab-active' : ''}`,
                            onclick: () => JobDetailPage.activeTab = 'raw'
                        }, 'Source Info')
                    ]),
                    
                    // Tab Content
                    JobDetailPage.activeTab === 'parsed' ? [
                        // Job Details View
                        m('div', { class: 'space-y-4' }, [
                            // Salary
                            job.salary && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Salary'),
                                m('p', formatSalary(job.salary))
                            ]),
                            
                            // Location
                            job.location && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Location'),
                                m('p', [
                                    job.location.city && m('span', job.location.city),
                                    job.location.region && m('span', `, ${job.location.region}`),
                                    job.location.country && m('span', `, ${job.location.country}`)
                                ]),
                                job.location.remote_work && m('p', [
                                    m('strong', 'Remote: '),
                                    job.location.remote_work
                                ])
                            ]),
                            
                            // Employment
                            job.employment && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Employment'),
                                job.employment.type && m('p', [m('strong', 'Type: '), job.employment.type]),
                                job.employment.contract && m('p', [m('strong', 'Contract: '), job.employment.contract]),
                                job.employment.schedule && m('p', [m('strong', 'Schedule: '), job.employment.schedule])
                            ]),
                            
                            // Requirements
                            job.requirements && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Requirements'),
                                job.requirements.education && m('p', [
                                    m('strong', 'Education: '),
                                    job.requirements.education
                                ]),
                                job.requirements.experience_years && m('p', [
                                    m('strong', 'Experience: '),
                                    `${job.requirements.experience_years} years`
                                ]),
                                job.requirements.languages && job.requirements.languages.length > 0 && m('div', [
                                    m('strong', 'Languages: '),
                                    m('div', { class: 'flex flex-wrap gap-2 mt-2' },
                                        job.requirements.languages.map(lang => 
                                            m('span', { class: 'badge badge-outline' }, lang)
                                        )
                                    )
                                ]),
                                job.requirements.hard_skills && job.requirements.hard_skills.length > 0 && m('div', [
                                    m('strong', 'Skills: '),
                                    m('div', { class: 'flex flex-wrap gap-2 mt-2' },
                                        job.requirements.hard_skills.map(skill => 
                                            m('span', { class: 'badge badge-primary' }, skill)
                                        )
                                    )
                                ]),
                                job.requirements.soft_skills && job.requirements.soft_skills.length > 0 && m('div', [
                                    m('strong', 'Soft Skills: '),
                                    m('div', { class: 'flex flex-wrap gap-2 mt-2' },
                                        job.requirements.soft_skills.map(skill => 
                                            m('span', { class: 'badge badge-secondary' }, skill)
                                        )
                                    )
                                ])
                            ]),
                            
                            // Responsibilities
                            job.parsed_view?.responsibilities && job.parsed_view.responsibilities.length > 0 && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Responsibilities'),
                                m('ul', { class: 'list-disc list-inside space-y-1' },
                                    job.parsed_view.responsibilities.map(r => m('li', r))
                                )
                            ]),
                            
                            // Benefits
                            job.benefits && job.benefits.length > 0 && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Benefits'),
                                m('div', { class: 'flex flex-wrap gap-2' },
                                    job.benefits.map(b => m('span', { class: 'badge badge-success' }, b))
                                )
                            ])
                        ])
                    ] : [
                        // Source Info View - Show raw original job description
                        m('div', { class: 'space-y-4' }, [
                            m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Source Information'),
                                job.source?.site && m('p', [m('strong', 'Source: '), job.source.site]),
                                job.source?.url && m('div', { class: 'mt-2' }, [
                                    m('a', { 
                                        href: job.source.url, 
                                        target: '_blank',
                                        class: 'btn btn-primary btn-sm'
                                    }, 'View Original Posting →')
                                ]),
                                job.posting_date && m('p', { class: 'mt-2' }, [
                                    m('strong', 'Posted: '), 
                                    formatDate(job.posting_date)
                                ])
                            ]),
                            // Show raw original data
                            job.raw && m('div', { class: 'mt-4' }, [
                                m('h3', { class: 'font-bold mb-2' }, 'Original Job Posting'),
                                job.raw.original_title && m('div', { class: 'mb-2' }, [
                                    m('p', { class: 'text-sm text-gray-500' }, 'Original Title:'),
                                    m('p', { class: 'font-medium' }, job.raw.original_title)
                                ]),
                                job.raw.original_company && m('div', { class: 'mb-2' }, [
                                    m('p', { class: 'text-sm text-gray-500' }, 'Original Company:'),
                                    m('p', { class: 'font-medium' }, job.raw.original_company)
                                ]),
                                job.raw.original_description && m('div', { class: 'mt-4' }, [
                                    m('p', { class: 'text-sm text-gray-500 mb-2' }, 'Original Description:'),
                                    m('div', { class: 'bg-base-200 p-4 rounded-lg max-h-96 overflow-y-auto' }, [
                                        m('pre', { class: 'whitespace-pre-wrap text-sm' }, job.raw.original_description)
                                    ])
                                ])
                            ])
                        ])
                    ]
                ])
            ])
        ]);
    }
};

// Chart Helper Functions
const ChartHelpers = {
    createChart: (canvas, config) => {
        if (!canvas) return null;
        // Destroy existing chart if present
        if (canvas.chart) {
            canvas.chart.destroy();
        }
        canvas.chart = new Chart(canvas, config);
        return canvas.chart;
    },
    destroyChart: (canvas) => {
        if (canvas && canvas.chart) {
            canvas.chart.destroy();
            canvas.chart = null;
        }
    }
};

// Analysis Page
const AnalysisPage = {
    oninit: () => {
        api.getAnalysisIndex().then(data => {
            state.analysisIndex = data;
        }).catch(err => {
            console.error('Error loading analysis index:', err);
            state.analysisIndex = { error: true };
        });
    },
    renderDistributionChart: (data) => {
        if (!data || !data.distribution || data.distribution.length === 0) return null;
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body' }, [
                m('h3', { class: 'card-title' }, 'Distribution Chart'),
                m('div', { class: 'chart-container' }, [
                    m('canvas', {
                        oncreate: (vnode) => {
                            const labels = data.distribution.map(item => item.range || `${item.min}-${item.max}`);
                            const values = data.distribution.map(item => item.count);
                            
                            ChartHelpers.createChart(vnode.dom, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Number of Jobs',
                                        data: values,
                                        backgroundColor: 'rgba(99, 102, 241, 0.7)',
                                        borderColor: 'rgba(99, 102, 241, 1)',
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            ticks: {
                                                precision: 0
                                            }
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: false
                                        },
                                        tooltip: {
                                            callbacks: {
                                                afterLabel: (context) => {
                                                    const item = data.distribution[context.dataIndex];
                                                    return item.percentage ? `${item.percentage.toFixed(1)}% of total` : '';
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        },
                        onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                    })
                ])
            ])
        ]);
    },
    renderTimeSeriesChart: (data) => {
        if (!data || !data.time_series || data.time_series.length === 0) {
            if (!data || !data.trends || data.trends.length === 0) return null;
            // Use trends if time_series is not available
            const trends = data.trends;
            
            return m('div', { class: 'card bg-base-100 shadow-xl' }, [
                m('div', { class: 'card-body' }, [
                    m('h3', { class: 'card-title' }, 'Trend Over Time'),
                    m('div', { class: 'chart-container' }, [
                        m('canvas', {
                            oncreate: (vnode) => {
                                const labels = trends.map(item => item.date || item.period);
                                const newJobs = trends.map(item => item.new_jobs || item.count || 0);
                                const closedJobs = trends.map(item => item.closed_jobs || 0);
                                
                                const datasets = [{
                                    label: 'New Jobs',
                                    data: newJobs,
                                    borderColor: 'rgba(34, 197, 94, 1)',
                                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                                    fill: true,
                                    tension: 0.4
                                }];
                                
                                if (closedJobs.some(v => v > 0)) {
                                    datasets.push({
                                        label: 'Closed Jobs',
                                        data: closedJobs,
                                        borderColor: 'rgba(239, 68, 68, 1)',
                                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                        fill: true,
                                        tension: 0.4
                                    });
                                }
                                
                                ChartHelpers.createChart(vnode.dom, {
                                    type: 'line',
                                    data: {
                                        labels: labels,
                                        datasets: datasets
                                    },
                                    options: {
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        scales: {
                                            y: {
                                                beginAtZero: true,
                                                ticks: {
                                                    precision: 0
                                                }
                                            }
                                        },
                                        plugins: {
                                            legend: {
                                                display: datasets.length > 1
                                            }
                                        }
                                    }
                                });
                            },
                            onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                        })
                    ])
                ])
            ]);
        }
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body' }, [
                m('h3', { class: 'card-title' }, 'Trend Over Time'),
                m('div', { class: 'chart-container' }, [
                    m('canvas', {
                        oncreate: (vnode) => {
                            const labels = data.time_series.map(item => item.date || item.period);
                            const values = data.time_series.map(item => item.average || item.count || 0);
                            
                            ChartHelpers.createChart(vnode.dom, {
                                type: 'line',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Average',
                                        data: values,
                                        borderColor: 'rgba(99, 102, 241, 1)',
                                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                                        fill: true,
                                        tension: 0.4
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: false
                                        }
                                    }
                                }
                            });
                        },
                        onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                    })
                ])
            ])
        ]);
    },
    renderTopItemsChart: (data, key, title) => {
        const items = data[key];
        if (!items || items.length === 0) return null;
        
        const topItems = items.slice(0, 15); // Show top 15
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body' }, [
                m('h3', { class: 'card-title' }, title),
                m('div', { class: 'chart-container' }, [
                    m('canvas', {
                        oncreate: (vnode) => {
                            const labels = topItems.map(item => 
                                item.name || item.skill || item.company || item.function || 
                                item.seniority || item.location || item.benefit || 'Unknown'
                            );
                            const values = topItems.map(item => item.count);
                            
                            ChartHelpers.createChart(vnode.dom, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Count',
                                        data: values,
                                        backgroundColor: 'rgba(168, 85, 247, 0.7)',
                                        borderColor: 'rgba(168, 85, 247, 1)',
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    indexAxis: 'y', // Horizontal bars
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        x: {
                                            beginAtZero: true,
                                            ticks: {
                                                precision: 0
                                            }
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: false
                                        },
                                        tooltip: {
                                            callbacks: {
                                                afterLabel: (context) => {
                                                    const item = topItems[context.dataIndex];
                                                    return item.percentage ? `${item.percentage.toFixed(1)}% of total` : '';
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        },
                        onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                    })
                ])
            ])
        ]);
    },
    renderBreakdownChart: (data) => {
        // Check for various breakdown formats
        const breakdownKey = data.by_function ? 'by_function' : 
                            data.by_seniority ? 'by_seniority' : 
                            data.by_location ? 'by_location' : 
                            data.by_company_size ? 'by_company_size' : 
                            data.by_education ? 'by_education' : 
                            data.employment_types ? 'employment_types' :
                            data.remote_options ? 'remote_options' :
                            data.education_requirements ? 'education_requirements' :
                            data.top_benefits ? 'top_benefits' : null;
        
        if (!breakdownKey || !data[breakdownKey] || data[breakdownKey].length === 0) return null;
        
        const items = data[breakdownKey].slice(0, 10); // Top 10
        const title = breakdownKey.includes('by_') ? 
            breakdownKey.replace('by_', '').replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) :
            breakdownKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body' }, [
                m('h3', { class: 'card-title' }, `${title}`),
                m('div', { class: 'chart-container' }, [
                    m('canvas', {
                        oncreate: (vnode) => {
                            // Extract labels based on data structure
                            const labels = items.map(item => 
                                item.function || item.seniority || item.location || 
                                item.size || item.education || item.education_level ||
                                item.employment_type || item.remote_option || 
                                item.benefit || item.name || 'Unknown'
                            );
                            const values = items.map(item => item.count);
                            
                            // Generate colors
                            const backgroundColors = items.map((_, i) => {
                                const hue = (i * 360 / items.length);
                                return `hsla(${hue}, 70%, 60%, 0.7)`;
                            });
                            
                            ChartHelpers.createChart(vnode.dom, {
                                type: 'doughnut',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        data: values,
                                        backgroundColor: backgroundColors,
                                        borderWidth: 2,
                                        borderColor: '#fff'
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: {
                                        legend: {
                                            position: 'right',
                                            labels: {
                                                boxWidth: 12,
                                                font: {
                                                    size: 11
                                                }
                                            }
                                        },
                                        tooltip: {
                                            callbacks: {
                                                label: (context) => {
                                                    const item = items[context.dataIndex];
                                                    const label = context.label || '';
                                                    const count = item.count || 0;
                                                    const percentage = item.percentage ? ` (${item.percentage.toFixed(1)}%)` : '';
                                                    const avg = item.average ? ` (Avg: ${Math.round(item.average).toLocaleString()} MDL)` : '';
                                                    return `${label}: ${count}${percentage}${avg}`;
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        },
                        onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                    })
                ])
            ])
        ]);
    },
    renderAnalysisData: (data) => {
        if (!data) return m(Loading);
        if (data.error) return m('div', { class: 'alert alert-error' }, data.error);
        
        // Render based on analysis type - CHARTS FIRST, then tables as fallback
        return m('div', { class: 'space-y-6' }, [
            // Overall stats if present
            data.overall && m('div', { class: 'stats stats-vertical lg:stats-horizontal shadow w-full' }, [
                data.overall.count && m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Sample Size'),
                    m('div', { class: 'stat-value text-primary' }, data.overall.count.toLocaleString())
                ]),
                data.overall.average && m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Average'),
                    m('div', { class: 'stat-value' }, `${Math.round(data.overall.average).toLocaleString()} ${data.overall.currency || 'MDL'}`)
                ]),
                data.overall.median && m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Median'),
                    m('div', { class: 'stat-value' }, `${Math.round(data.overall.median).toLocaleString()} ${data.overall.currency || 'MDL'}`)
                ]),
                data.overall.min && m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Range'),
                    m('div', { class: 'stat-value text-sm' }, 
                        `${Math.round(data.overall.min).toLocaleString()} - ${Math.round(data.overall.max).toLocaleString()}`)
                ])
            ]),
            
            // === CHARTS FIRST (Primary Visualizations) ===
            
            // Distribution chart (if available)
            AnalysisPage.renderDistributionChart(data),
            
            // Time series chart (for temporal data)
            AnalysisPage.renderTimeSeriesChart(data),
            
            // Top items charts (skills, companies, etc.)
            data.top_skills && AnalysisPage.renderTopItemsChart(data, 'top_skills', 'Top In-Demand Skills'),
            data.top_companies && AnalysisPage.renderTopItemsChart(data, 'top_companies', 'Top Companies'),
            data.top_benefits && AnalysisPage.renderTopItemsChart(data, 'top_benefits', 'Most Common Benefits'),
            
            // Requirements charts
            data.education_requirements && AnalysisPage.renderBreakdownChart({ education_requirements: data.education_requirements }),
            data.experience_requirements && AnalysisPage.renderDistributionChart({ distribution: data.experience_requirements }),
            
            // Breakdown pie chart (general)
            AnalysisPage.renderBreakdownChart(data),
            
            // === TABLES AS FALLBACK (Collapsible for detail) ===
            
            // Distribution table (detailed view, collapsed by default)
            data.distribution && m('details', { class: 'collapse collapse-arrow bg-base-100 shadow-xl' }, [
                m('summary', { class: 'collapse-title font-bold text-lg' }, 'Distribution Table (Detailed)'),
                m('div', { class: 'collapse-content' }, [
                    m('div', { class: 'overflow-x-auto' }, [
                        m('table', { class: 'table table-zebra' }, [
                            m('thead', [
                                m('tr', [
                                    m('th', 'Range'),
                                    m('th', 'Count'),
                                    m('th', 'Percentage'),
                                    m('th', 'Visual')
                                ])
                            ]),
                            m('tbody', 
                                data.distribution.map(item => 
                                    m('tr', [
                                        m('td', item.range || `${item.min}-${item.max}`),
                                        m('td', item.count.toLocaleString()),
                                        m('td', `${item.percentage?.toFixed(1) || '0'}%`),
                                        m('td', [
                                            m('progress', { 
                                                class: 'progress progress-primary w-32', 
                                                value: item.percentage || 0, 
                                                max: 100 
                                            })
                                        ])
                                    ])
                                )
                            )
                        ])
                    ])
                ])
            ]),
            
            // Breakdown table (collapsed by default)
            (data.by_function || data.by_seniority || data.by_location || data.by_company_size || data.by_education) && 
            m('details', { class: 'collapse collapse-arrow bg-base-100 shadow-xl' }, [
                m('summary', { class: 'collapse-title font-bold text-lg' }, 'Breakdown Table (Detailed)'),
                m('div', { class: 'collapse-content' }, [
                    m('div', { class: 'overflow-x-auto' }, [
                        m('table', { class: 'table table-zebra' }, [
                            m('thead', [
                                m('tr', [
                                    m('th', 'Category'),
                                    m('th', 'Count'),
                                    m('th', 'Average'),
                                    m('th', 'Median')
                                ])
                            ]),
                            m('tbody', 
                                (data.by_function || data.by_seniority || data.by_location || data.by_company_size || data.by_education || []).map(item => 
                                    m('tr', [
                                        m('td', { class: 'font-medium' }, 
                                            item.function || item.seniority || item.location || item.size || item.education || item.name
                                        ),
                                        m('td', item.count?.toLocaleString() || 'N/A'),
                                        m('td', item.average ? `${Math.round(item.average).toLocaleString()} MDL` : 'N/A'),
                                        m('td', item.median ? `${Math.round(item.median).toLocaleString()} MDL` : 'N/A')
                                    ])
                                )
                            )
                        ])
                    ])
                ])
            ]),
            
            // Top skills/companies table (collapsed by default)
            (data.top_skills || data.top_companies) && m('details', { class: 'collapse collapse-arrow bg-base-100 shadow-xl' }, [
                m('summary', { class: 'collapse-title font-bold text-lg' }, data.top_skills ? 'Top Skills Table (Detailed)' : 'Top Companies Table (Detailed)'),
                m('div', { class: 'collapse-content' }, [
                    m('div', { class: 'overflow-x-auto' }, [
                        m('table', { class: 'table table-zebra' }, [
                            m('thead', [
                                m('tr', [
                                    m('th', '#'),
                                    m('th', 'Name'),
                                    m('th', 'Count'),
                                    m('th', 'Percentage')
                                ])
                            ]),
                            m('tbody', 
                                (data.top_skills || data.top_companies || []).slice(0, 20).map((item, idx) => 
                                    m('tr', [
                                        m('td', idx + 1),
                                        m('td', { class: 'font-medium' }, item.name || item.skill || item.company),
                                        m('td', item.count?.toLocaleString() || 'N/A'),
                                        m('td', [
                                            m('progress', { 
                                                class: 'progress progress-secondary w-24', 
                                                value: item.percentage || 0, 
                                                max: 100 
                                            }),
                                            m('span', { class: 'text-xs ml-2' }, `${item.percentage?.toFixed(1) || 0}%`)
                                        ])
                                    ])
                                )
                            )
                        ])
                    ])
                ])
            ]),
            
            // Time series table (collapsed by default)
            data.time_series && m('details', { class: 'collapse collapse-arrow bg-base-100 shadow-xl' }, [
                m('summary', { class: 'collapse-title font-bold text-lg' }, 'Time Series Table (Detailed)'),
                m('div', { class: 'collapse-content' }, [
                    m('div', { class: 'overflow-x-auto' }, [
                        m('table', { class: 'table table-sm' }, [
                            m('thead', [
                                m('tr', [
                                    m('th', 'Date'),
                                    m('th', 'Count'),
                                    m('th', 'Average'),
                                    m('th', 'Change')
                                ])
                            ]),
                            m('tbody', 
                                data.time_series.map((item, idx) => {
                                    const prevItem = idx > 0 ? data.time_series[idx - 1] : null;
                                    const change = prevItem && item.average && prevItem.average ? 
                                        ((item.average - prevItem.average) / prevItem.average * 100).toFixed(1) : null;
                                    return m('tr', [
                                        m('td', item.date || item.period),
                                        m('td', item.count?.toLocaleString() || 'N/A'),
                                        m('td', item.average ? Math.round(item.average).toLocaleString() : 'N/A'),
                                        m('td', change ? [
                                            m('span', { 
                                                class: change > 0 ? 'text-success' : 'text-error' 
                                            }, `${change > 0 ? '+' : ''}${change}%`)
                                        ] : '-')
                                    ]);
                                })
                            )
                        ])
                    ])
                ])
            ]),
            
            // Skill combinations table (if present)
            data.top_combinations && m('details', { class: 'collapse collapse-arrow bg-base-100 shadow-xl' }, [
                m('summary', { class: 'collapse-title font-bold text-lg' }, 'Skill Combinations (Detailed)'),
                m('div', { class: 'collapse-content' }, [
                    m('div', { class: 'overflow-x-auto' }, [
                        m('table', { class: 'table table-zebra' }, [
                            m('thead', [
                                m('tr', [
                                    m('th', 'Skill 1'),
                                    m('th', 'Skill 2'),
                                    m('th', 'Count')
                                ])
                            ]),
                            m('tbody', 
                                data.top_combinations.slice(0, 30).map(item => 
                                    m('tr', [
                                        m('td', { class: 'font-medium' }, item.skill1),
                                        m('td', { class: 'font-medium' }, item.skill2),
                                        m('td', item.count?.toLocaleString() || 'N/A')
                                    ])
                                )
                            )
                        ])
                    ])
                ])
            ]),
            
            // Raw JSON view (collapsible)
            m('details', { class: 'collapse collapse-arrow bg-base-200' }, [
                m('summary', { class: 'collapse-title font-medium' }, 'View Raw JSON'),
                m('div', { class: 'collapse-content' }, [
                    m('pre', { class: 'bg-base-300 p-4 rounded text-xs overflow-x-auto' }, 
                        JSON.stringify(data, null, 2)
                    )
                ])
            ])
        ]);
    },
    view: () => m('div', { class: 'container mx-auto px-4 py-8' }, [
        m('h1', { class: 'text-3xl font-bold mb-6' }, 'Job Market Analysis'),
        
        state.analysisIndex ? [
            !state.analysisIndex.error && state.analysisIndex.data_summary && m('div', { class: 'stats shadow mb-6 w-full' }, [
                m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Total Jobs Analyzed'),
                    m('div', { class: 'stat-value' }, state.analysisIndex.data_summary.total_jobs?.toLocaleString() || 'N/A')
                ]),
                m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Date Range'),
                    m('div', { class: 'stat-value text-2xl' }, 
                        state.analysisIndex.data_summary.date_range ? 
                            `${formatDate(state.analysisIndex.data_summary.date_range.start)} - ${formatDate(state.analysisIndex.data_summary.date_range.end)}` :
                            'N/A'
                    )
                ]),
                m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Jobs with Salary'),
                    m('div', { class: 'stat-value' }, state.analysisIndex.data_summary.jobs_with_salary?.toLocaleString() || 'N/A')
                ])
            ]),
            
            state.analysisIndex.error ? 
                m('div', { class: 'alert alert-warning mb-6' }, [
                    m('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', class: 'stroke-current shrink-0 w-6 h-6' }, [
                        m('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' })
                    ]),
                    m('span', 'Analysis data not yet generated. Run: python -m json_generator --output frontend/api')
                ]) :
                m('div', { class: 'alert alert-info mb-6' }, [
                    m('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', class: 'stroke-current shrink-0 w-6 h-6' }, [
                        m('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
                    ]),
                    m('span', `${state.analysisIndex.analyses?.length || 0} analyses available. Click "View" to see data visualizations.`)
                ]),
            
            state.analysisIndex.analyses && m('div', { class: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' },
                state.analysisIndex.analyses.map(analysis => 
                    m('div', { class: 'card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow' }, [
                        m('div', { class: 'card-body' }, [
                            m('h2', { class: 'card-title text-lg' }, analysis.title),
                            m('p', { class: 'text-xs text-gray-500' }, `${analysis.id}.json`),
                            analysis.temporal && m('span', { class: 'badge badge-secondary mt-2' }, 'Time Series'),
                            m('div', { class: 'card-actions justify-end mt-4' }, [
                                m('a', { 
                                    class: 'btn btn-primary btn-sm',
                                    href: `#!/analysis/${analysis.id}`,
                                    oncreate: m.route.link
                                }, 'View Analysis')
                            ])
                        ])
                    ])
                )
            )
        ] : m(Loading)
    ])
};

// Analysis Detail Page (Full Page View)
const AnalysisDetailPage = {
    oninit: (vnode) => {
        const analysisId = vnode.attrs.id;
        state.selectedAnalysisData = null;
        state.selectedAnalysis = null;
        
        // Load analysis index if not already loaded
        if (!state.analysisIndex) {
            api.getAnalysisIndex().then(data => {
                state.analysisIndex = data;
                // Find the analysis
                state.selectedAnalysis = data.analyses?.find(a => a.id === analysisId);
                m.redraw();
            });
        } else {
            state.selectedAnalysis = state.analysisIndex.analyses?.find(a => a.id === analysisId);
        }
        
        // Load analysis data
        const filename = `${analysisId}.json`;
        api.getAnalysis(filename).then(response => {
            state.selectedAnalysisData = response.data || response;
            m.redraw();
        }).catch(err => {
            console.error(`Error loading ${filename}:`, err);
            state.selectedAnalysisData = { error: `Failed to load ${filename}` };
            m.redraw();
        });
    },
    view: () => m('div', { class: 'container mx-auto px-4 py-8' }, [
        // Breadcrumb navigation
        m('div', { class: 'text-sm breadcrumbs mb-4' }, [
            m('ul', [
                m('li', m('a', { href: '#!/analysis', oncreate: m.route.link }, 'Analysis')),
                m('li', state.selectedAnalysis?.title || 'Loading...')
            ])
        ]),
        
        // Title
        state.selectedAnalysis && m('h1', { class: 'text-4xl font-bold mb-6' }, state.selectedAnalysis.title),
        
        // Analysis data
        state.selectedAnalysisData ? 
            AnalysisPage.renderAnalysisData(state.selectedAnalysisData) :
            m(Loading)
    ])
};

// Layout Component
const Layout = {
    view: (vnode) => m('div', { class: 'min-h-screen flex flex-col' }, [
        m(Header),
        m('main', { class: 'flex-1' }, vnode.children),
        m(Footer)
    ])
};

// Router Configuration
m.route(document.getElementById('app'), '/', {
    '/': {
        render: () => m(Layout, m(HomePage))
    },
    '/jobs': {
        render: () => m(Layout, m(JobsPage))
    },
    '/jobs/:id': {
        render: (vnode) => m(Layout, m(JobDetailPage, { id: vnode.attrs.id }))
    },
    '/analysis': {
        render: () => m(Layout, m(AnalysisPage))
    },
    '/analysis/:id': {
        render: (vnode) => m(Layout, m(AnalysisDetailPage, { id: vnode.attrs.id }))
    }
});
