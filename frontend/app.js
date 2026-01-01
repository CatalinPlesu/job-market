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
    filters: {},
    loading: false,
    analysisIndex: null,
    selectedAnalysis: null,
    selectedAnalysisData: null,
    showAnalysisModal: false,
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
        const filteredJobs = state.allLoadedJobs.filter(job => matchesFilters(job, state.filters));
        
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
        
        const handleFilterChange = async () => {
            JobsPage.displayPage = 1;
            // Trigger loading more pages if needed
            await JobsPage.ensureSufficientJobs();
            m.redraw();
        };
        
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
                            handleFilterChange();
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
                                handleFilterChange();
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
                                handleFilterChange();
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
                                handleFilterChange();
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
    displayPage: 1, // Current display page for filtered results
    
    oninit: async () => {
        state.loading = true;
        try {
            // Load index first to know how many pages we need
            const index = await api.getJobsIndex();
            state.jobsIndex = index;
            state.allLoadedJobs = [];
            state.loadedPages = new Set();
            
            // Automatically load ALL pages from the API
            const pagePromises = [];
            for (let i = 1; i <= index.total_pages; i++) {
                pagePromises.push(api.getJobsPage(i));
            }
            
            // Load all pages in parallel for speed
            const pages = await Promise.all(pagePromises);
            
            // Combine all jobs from all pages
            pages.forEach((page, idx) => {
                state.allLoadedJobs = [...state.allLoadedJobs, ...page.jobs];
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
        const hasActiveFilters = Object.keys(state.filters).some(k => state.filters[k]);
        
        // Calculate accurate job counts
        const totalJobsInAPI = state.jobsIndex ? state.jobsIndex.total_jobs : 0;
        const loadedJobsCount = state.allLoadedJobs.length;
        
        return m('div', { class: 'container mx-auto px-4 py-8' }, [
            m('h1', { class: 'text-3xl font-bold mb-6' }, 'Browse Jobs'),
            
            state.jobsIndex && m(FilterPanel),
            
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
                m('div', { class: 'text-sm text-gray-600' }, [
                    hasActiveFilters ? 
                        `Showing ${jobs.length} of ${total} filtered jobs` :
                        `Showing ${jobs.length} of ${totalJobsInAPI} jobs`
                ])
            ]),
            
            // Top pagination
            state.jobsIndex && JobsPage.renderPagination(totalPages),
            
            state.loading ? m(Loading) : [
                m('div', { class: 'bg-base-100 rounded-lg shadow my-4 p-4' }, [
                    jobs.length > 0 ? 
                        jobs.map((job, idx) => m(JobListItem, { 
                            job, 
                            index: ((JobsPage.displayPage - 1) * state.itemsPerPage) + idx + 1 
                        })) :
                        m('div', { class: 'text-center py-8 text-gray-500' }, 
                            hasActiveFilters ? 'No jobs match your filters. Try adjusting your criteria.' : 'No jobs found'
                        )
                ]),
                
                // Bottom pagination
                JobsPage.renderPagination(totalPages)
            ]
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
    viewAnalysis: (analysis) => {
        state.selectedAnalysis = analysis;
        state.showAnalysisModal = true;
        const filename = `${analysis.id}.json`;
        api.getAnalysis(filename).then(data => {
            state.selectedAnalysisData = data;
            m.redraw();
        }).catch(err => {
            console.error(`Error loading ${filename}:`, err);
            state.selectedAnalysisData = { error: `Failed to load ${filename}` };
            m.redraw();
        });
    },
    renderAnalysisData: (data) => {
        if (!data) return m(Loading);
        if (data.error) return m('div', { class: 'alert alert-error' }, data.error);
        
        // Render based on analysis type
        return m('div', { class: 'space-y-4' }, [
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
            
            // Distribution chart
            data.distribution && m('div', { class: 'card bg-base-100 shadow-xl' }, [
                m('div', { class: 'card-body' }, [
                    m('h3', { class: 'card-title' }, 'Distribution'),
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
            
            // By function/category data
            (data.by_function || data.by_seniority || data.by_location || data.by_company_size || data.by_education) && 
            m('div', { class: 'card bg-base-100 shadow-xl' }, [
                m('div', { class: 'card-body' }, [
                    m('h3', { class: 'card-title' }, 'Breakdown'),
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
            
            // Top skills/companies
            (data.top_skills || data.top_companies) && m('div', { class: 'card bg-base-100 shadow-xl' }, [
                m('div', { class: 'card-body' }, [
                    m('h3', { class: 'card-title' }, data.top_skills ? 'Top Skills' : 'Top Companies'),
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
            
            // Time series data
            data.time_series && m('div', { class: 'card bg-base-100 shadow-xl' }, [
                m('div', { class: 'card-body' }, [
                    m('h3', { class: 'card-title' }, 'Trend Over Time'),
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
                    m('span', `${state.analysisIndex.available_analyses?.length || 0} analyses available. Click "View" to see data visualizations.`)
                ]),
            
            state.analysisIndex.available_analyses && m('div', { class: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' },
                state.analysisIndex.available_analyses.map(analysis => 
                    m('div', { class: 'card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow' }, [
                        m('div', { class: 'card-body' }, [
                            m('h2', { class: 'card-title text-lg' }, analysis.title),
                            m('p', { class: 'text-xs text-gray-500' }, `${analysis.id}.json`),
                            analysis.temporal && m('span', { class: 'badge badge-secondary mt-2' }, 'Time Series'),
                            m('div', { class: 'card-actions justify-end mt-4' }, [
                                m('button', { 
                                    class: 'btn btn-primary btn-sm',
                                    onclick: () => AnalysisPage.viewAnalysis(analysis)
                                }, 'View Data')
                            ])
                        ])
                    ])
                )
            )
        ] : m(Loading),
        
        // Analysis Modal
        state.showAnalysisModal && m('div', { class: 'modal modal-open' }, [
            m('div', { class: 'modal-box max-w-4xl max-h-[90vh] overflow-y-auto' }, [
                m('div', { class: 'flex justify-between items-start mb-4' }, [
                    m('h3', { class: 'font-bold text-2xl' }, state.selectedAnalysis?.title),
                    m('button', { 
                        class: 'btn btn-sm btn-circle btn-ghost',
                        onclick: () => {
                            state.showAnalysisModal = false;
                            state.selectedAnalysisData = null;
                        }
                    }, '✕')
                ]),
                AnalysisPage.renderAnalysisData(state.selectedAnalysisData)
            ]),
            m('div', { 
                class: 'modal-backdrop', 
                onclick: () => {
                    state.showAnalysisModal = false;
                    state.selectedAnalysisData = null;
                }
            })
        ])
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
