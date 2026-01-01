// API Configuration
const API_BASE = '/api';

// API Client
const api = {
    getJobsIndex: () => m.request({ url: `${API_BASE}/jobs/index.json` }),
    getJobsPage: (page) => m.request({ url: `${API_BASE}/jobs/page-${page}.json` }),
    getJobDetail: (jobId) => m.request({ url: `${API_BASE}/jobs/${jobId}/detail.json` }),
    getAnalysisIndex: () => m.request({ url: `${API_BASE}/analysis/index.json` }),
    getAnalysis: (endpoint) => m.request({ url: `${API_BASE}${endpoint}` })
};

// State Management
const state = {
    jobsIndex: null,
    currentPage: 1,
    jobs: [],
    filters: {},
    loading: false,
    analysisIndex: null,
    selectedAnalysis: null
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
        return m('div', { class: 'job-item px-2' }, [
            m('div', { class: 'flex items-start gap-2' }, [
                m('span', { class: 'text-xs text-gray-500 mt-1' }, `${vnode.attrs.index}.`),
                m('div', { class: 'flex-1' }, [
                    m('a', { 
                        href: `#!/jobs/${job.id}`,
                        class: 'job-title font-medium hover:underline',
                        oncreate: m.route.link
                    }, job.title),
                    m('div', { class: 'job-meta flex flex-wrap gap-2 mt-1' }, [
                        job.company && m('span', { class: 'badge badge-ghost badge-sm' }, job.company),
                        job.location && job.location.city && m('span', job.location.city),
                        job.salary && m('span', formatSalary(job.salary)),
                        job.posting_date && m('span', formatDate(job.posting_date))
                    ])
                ])
            ])
        ]);
    }
};

// Filter matching logic
const matchesFilters = (job, filters) => {
    for (const [key, value] of Object.entries(filters)) {
        if (!value) continue;
        
        switch (key) {
            case 'job_function':
                if (job.job_function !== value) return false;
                break;
            case 'seniority_level':
                if (job.seniority_level !== value) return false;
                break;
            case 'city':
                if (job.location && job.location.city !== value) return false;
                break;
            case 'remote_work':
                if (job.location && job.location.remote_work !== value) return false;
                break;
            case 'industry':
                if (job.industry !== value) return false;
                break;
            case 'company':
                if (job.company !== value) return false;
                break;
            case 'employment_type':
                if (job.employment && job.employment.type !== value) return false;
                break;
            case 'contract_type':
                if (job.employment && job.employment.contract !== value) return false;
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

// Filter Component with Hierarchical Filtering
const FilterPanel = {
    showAdvanced: false,
    view: () => {
        if (!state.jobsIndex) return null;
        
        // Get filtered jobs based on current filters for hierarchical filtering
        const filteredJobs = state.jobs.filter(job => matchesFilters(job, state.filters));
        
        // All available filter fields
        const filterFields = [
            { key: 'job_function', label: 'Job Function', basic: true },
            { key: 'seniority_level', label: 'Seniority', basic: true },
            { key: 'city', label: 'City', basic: true },
            { key: 'remote_work', label: 'Remote Work', basic: true },
            { key: 'industry', label: 'Industry', basic: true },
            { key: 'company', label: 'Company', basic: true },
            { key: 'employment_type', label: 'Employment Type', basic: false },
            { key: 'contract_type', label: 'Contract Type', basic: false },
            { key: 'department', label: 'Department', basic: false },
            { key: 'specialization', label: 'Specialization', basic: false },
            { key: 'education_level', label: 'Education', basic: false },
            { key: 'company_size', label: 'Company Size', basic: false }
        ];
        
        const basicFilters = filterFields.filter(f => f.basic);
        const advancedFilters = filterFields.filter(f => !f.basic);
        
        return m('div', { class: 'bg-base-200 p-4 rounded-lg mb-4' }, [
            m('div', { class: 'flex justify-between items-center mb-4' }, [
                m('h3', { class: 'font-bold' }, 'Filters'),
                m('div', { class: 'flex gap-2' }, [
                    m('button', { 
                        class: 'btn btn-xs btn-ghost',
                        onclick: () => FilterPanel.showAdvanced = !FilterPanel.showAdvanced
                    }, FilterPanel.showAdvanced ? 'Show Less' : 'Show More'),
                    m('button', { 
                        class: 'btn btn-xs btn-ghost',
                        onclick: () => {
                            state.filters = {};
                            state.currentPage = 1;
                            m.redraw();
                        }
                    }, 'Clear All')
                ])
            ]),
            
            // Active filters badges
            Object.keys(state.filters).length > 0 && m('div', { class: 'flex flex-wrap gap-2 mb-4' },
                Object.entries(state.filters).map(([key, value]) => 
                    value && m('span', { class: 'badge badge-primary gap-2' }, [
                        `${key.replace(/_/g, ' ')}: ${value}`,
                        m('button', { 
                            class: 'btn btn-xs btn-circle btn-ghost',
                            onclick: () => {
                                delete state.filters[key];
                                m.redraw();
                            }
                        }, '×')
                    ])
                )
            ),
            
            // Basic filters
            m('div', { class: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4' },
                basicFilters.map(field => 
                    m('div', { class: 'form-control' }, [
                        m('label', { class: 'label' }, [
                            m('span', { class: 'label-text' }, field.label),
                            filteredJobs.length > 0 && state.filters[field.key] && 
                                m('span', { class: 'label-text-alt text-xs' }, 
                                    `(${getAvailableOptions(filteredJobs, field.key).length} options)`
                                )
                        ]),
                        m('select', { 
                            class: 'select select-bordered select-sm',
                            value: state.filters[field.key] || '',
                            onchange: (e) => {
                                if (e.target.value) {
                                    state.filters[field.key] = e.target.value;
                                } else {
                                    delete state.filters[field.key];
                                }
                                state.currentPage = 1;
                                m.redraw();
                            }
                        }, [
                            m('option', { value: '' }, 'All'),
                            ...(state.jobsIndex.filters[field.key] || []).map(f => 
                                m('option', { value: f }, f)
                            )
                        ])
                    ])
                )
            ),
            
            // Advanced filters (collapsible)
            FilterPanel.showAdvanced && m('div', { class: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' },
                advancedFilters.map(field => 
                    m('div', { class: 'form-control' }, [
                        m('label', { class: 'label' }, m('span', { class: 'label-text' }, field.label)),
                        m('select', { 
                            class: 'select select-bordered select-sm',
                            value: state.filters[field.key] || '',
                            onchange: (e) => {
                                if (e.target.value) {
                                    state.filters[field.key] = e.target.value;
                                } else {
                                    delete state.filters[field.key];
                                }
                                state.currentPage = 1;
                                m.redraw();
                            }
                        }, [
                            m('option', { value: '' }, 'All'),
                            ...(state.jobsIndex.filters[field.key] || []).map(f => 
                                m('option', { value: f }, f)
                            )
                        ])
                    ])
                )
            )
        ]);
    }
};

// Jobs Page
const JobsPage = {
    oninit: () => {
        state.loading = true;
        Promise.all([
            api.getJobsIndex(),
            api.getJobsPage(state.currentPage)
        ]).then(([index, page]) => {
            state.jobsIndex = index;
            state.jobs = page.jobs;
            state.loading = false;
        });
    },
    view: () => {
        // Apply client-side filtering
        const filteredJobs = state.jobs.filter(job => matchesFilters(job, state.filters));
        const hasActiveFilters = Object.keys(state.filters).some(k => state.filters[k]);
        
        return m('div', { class: 'container mx-auto px-4 py-8' }, [
            m('h1', { class: 'text-3xl font-bold mb-6' }, 'Browse Jobs'),
            
            state.jobsIndex && m(FilterPanel),
            
            state.loading ? m(Loading) : [
                m('div', { class: 'bg-base-100 rounded-lg shadow mb-4 p-4' }, [
                    m('div', { class: 'text-sm text-gray-600 mb-2' }, [
                        hasActiveFilters ? 
                            `Showing ${filteredJobs.length} filtered jobs (${state.jobs.length} total on page ${state.currentPage})` :
                            `Showing ${state.jobs.length} jobs (Page ${state.currentPage} of ${state.jobsIndex ? state.jobsIndex.total_pages : '?'})`
                    ]),
                    filteredJobs.length > 0 ? 
                        filteredJobs.map((job, idx) => m(JobListItem, { job, index: idx + 1 })) :
                        m('div', { class: 'text-center py-8 text-gray-500' }, 
                            hasActiveFilters ? 'No jobs match your filters' : 'No jobs found'
                        )
                ]),
                
                // Pagination
                state.jobsIndex && m('div', { class: 'flex justify-center gap-2' }, [
                    m('button', { 
                        class: 'btn btn-sm',
                        disabled: state.currentPage === 1,
                        onclick: () => {
                            state.currentPage--;
                            state.loading = true;
                            api.getJobsPage(state.currentPage).then(page => {
                                state.jobs = page.jobs;
                                state.loading = false;
                                window.scrollTo(0, 0);
                            });
                        }
                    }, 'Previous'),
                    m('span', { class: 'btn btn-sm btn-ghost' }, `Page ${state.currentPage} of ${state.jobsIndex.total_pages}`),
                    m('button', { 
                        class: 'btn btn-sm',
                        disabled: state.currentPage === state.jobsIndex.total_pages,
                        onclick: () => {
                            state.currentPage++;
                            state.loading = true;
                            api.getJobsPage(state.currentPage).then(page => {
                                state.jobs = page.jobs;
                                state.loading = false;
                                window.scrollTo(0, 0);
                            });
                        }
                    }, 'Next')
                ])
            ]
        ]);
    }
};

// Job Detail Page
const JobDetailPage = {
    job: null,
    activeTab: 'parsed',
    oninit: (vnode) => {
        const jobId = vnode.attrs.id;
        api.getJobDetail(jobId).then(data => {
            JobDetailPage.job = data.job;
        }).catch(err => {
            console.error('Error loading job:', err);
        });
    },
    view: () => {
        if (!JobDetailPage.job) return m(Loading);
        
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
                    m('h1', { class: 'card-title text-2xl' }, job.title || job.parsed?.title),
                    m('div', { class: 'flex flex-wrap gap-2 mb-4' }, [
                        job.company && m('span', { class: 'badge badge-primary' }, job.company),
                        job.parsed?.location?.city && m('span', { class: 'badge badge-secondary' }, job.parsed.location.city),
                        job.parsed?.seniority_level && m('span', { class: 'badge badge-accent' }, job.parsed.seniority_level)
                    ]),
                    
                    // Tabs
                    m('div', { class: 'tabs tabs-boxed mb-4' }, [
                        m('a', { 
                            class: `tab ${JobDetailPage.activeTab === 'parsed' ? 'tab-active' : ''}`,
                            onclick: () => JobDetailPage.activeTab = 'parsed'
                        }, 'Parsed View'),
                        m('a', { 
                            class: `tab ${JobDetailPage.activeTab === 'raw' ? 'tab-active' : ''}`,
                            onclick: () => JobDetailPage.activeTab = 'raw'
                        }, 'Raw View')
                    ]),
                    
                    // Tab Content
                    JobDetailPage.activeTab === 'parsed' ? [
                        // Parsed View
                        job.parsed && m('div', { class: 'space-y-4' }, [
                            // Salary
                            job.parsed.salary && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Salary'),
                                m('p', formatSalary(job.parsed.salary))
                            ]),
                            
                            // Requirements
                            job.parsed.requirements && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Requirements'),
                                job.parsed.requirements.education && m('p', [
                                    m('strong', 'Education: '),
                                    job.parsed.requirements.education
                                ]),
                                job.parsed.requirements.experience_years && m('p', [
                                    m('strong', 'Experience: '),
                                    `${job.parsed.requirements.experience_years} years`
                                ]),
                                job.parsed.requirements.languages && job.parsed.requirements.languages.length > 0 && m('div', [
                                    m('strong', 'Languages: '),
                                    m('div', { class: 'flex flex-wrap gap-2 mt-2' },
                                        job.parsed.requirements.languages.map(lang => 
                                            m('span', { class: 'badge badge-outline' }, lang)
                                        )
                                    )
                                ]),
                                job.parsed.requirements.hard_skills && job.parsed.requirements.hard_skills.length > 0 && m('div', [
                                    m('strong', 'Skills: '),
                                    m('div', { class: 'flex flex-wrap gap-2 mt-2' },
                                        job.parsed.requirements.hard_skills.map(skill => 
                                            m('span', { class: 'badge badge-primary' }, skill)
                                        )
                                    )
                                ])
                            ]),
                            
                            // Responsibilities
                            job.parsed.responsibilities && job.parsed.responsibilities.length > 0 && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Responsibilities'),
                                m('ul', { class: 'list-disc list-inside space-y-1' },
                                    job.parsed.responsibilities.map(r => m('li', r))
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
                        // Raw View
                        job.raw && m('div', { class: 'space-y-4' }, [
                            m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Original Information'),
                                m('p', [m('strong', 'Title: '), job.raw.original_title]),
                                m('p', [m('strong', 'Company: '), job.raw.original_company]),
                                m('p', [m('strong', 'Language: '), job.raw.original_language]),
                                m('p', [m('strong', 'Source: '), job.raw.source_site]),
                                m('p', [m('strong', 'Scraped At: '), formatDate(job.raw.scraped_at)])
                            ]),
                            m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Original Description'),
                                m('pre', { class: 'whitespace-pre-wrap bg-base-200 p-4 rounded' }, 
                                    job.raw.original_description
                                )
                            ]),
                            job.raw.source_url && m('div', [
                                m('a', { 
                                    href: job.raw.source_url, 
                                    target: '_blank',
                                    class: 'btn btn-primary'
                                }, 'View Original Posting →')
                            ])
                        ])
                    ]
                ])
            ])
        ]);
    }
};

// Analysis Page
const AnalysisPage = {
    oninit: () => {
        api.getAnalysisIndex().then(data => {
            state.analysisIndex = data;
        });
    },
    view: () => m('div', { class: 'container mx-auto px-4 py-8' }, [
        m('h1', { class: 'text-3xl font-bold mb-6' }, 'Job Market Analysis'),
        
        state.analysisIndex ? [
            m('div', { class: 'stats shadow mb-6 w-full' }, [
                m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Total Jobs Analyzed'),
                    m('div', { class: 'stat-value' }, state.analysisIndex.data_summary.total_jobs.toLocaleString())
                ]),
                m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Jobs with Salary'),
                    m('div', { class: 'stat-value' }, state.analysisIndex.data_summary.jobs_with_salary?.toLocaleString() || 'N/A')
                ]),
                m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Unique Companies'),
                    m('div', { class: 'stat-value' }, state.analysisIndex.data_summary.unique_companies?.toLocaleString() || 'N/A')
                ])
            ]),
            
            m('div', { class: 'alert alert-info mb-6' }, [
                m('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', class: 'stroke-current shrink-0 w-6 h-6' }, [
                    m('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
                ]),
                m('span', 'Analysis features are available when JSON data is generated. See README for instructions.')
            ]),
            
            m('div', { class: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' },
                state.analysisIndex.available_analyses.map(analysis => 
                    m('div', { class: 'card bg-base-100 shadow-xl' }, [
                        m('div', { class: 'card-body' }, [
                            m('h2', { class: 'card-title' }, analysis.title),
                            m('p', { class: 'text-sm text-gray-600' }, analysis.id),
                            analysis.temporal && m('span', { class: 'badge badge-secondary' }, 'Temporal'),
                            m('div', { class: 'card-actions justify-end' }, [
                                m('button', { 
                                    class: 'btn btn-primary btn-sm',
                                    onclick: () => {
                                        state.selectedAnalysis = analysis;
                                        api.getAnalysis(analysis.endpoint).then(data => {
                                            console.log('Analysis data:', data);
                                            // Would render charts here
                                        });
                                    }
                                }, 'View')
                            ])
                        ])
                    ])
                )
            )
        ] : m(Loading)
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
    }
});
