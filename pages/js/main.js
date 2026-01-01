/**
 * Main Application Entry Point
 * Initializes Mithril app with state management and routing
 */

import { Header } from './components/Header.js';
import { FilterPanel } from './components/FilterPanel.js';
import { JobList } from './components/JobList.js';
import { Pagination } from './components/Pagination.js';
import { JobDetail } from './components/JobDetail.js';

// Get global instances
const api = window.api;
const filterManager = window.filterManager;
const FilterUtils = window.FilterUtils;

// Application state
const state = {
    jobs: [],
    loading: false,
    error: '',
    currentPage: 1,
    totalPages: 1,
    totalJobs: 0,
    selectedJob: null,
    detailTab: 'parsed',
    sidebarOpen: window.innerWidth >= 1024, // Open on desktop by default
    filters: filterManager.filters,
    lastUpdated: 'Loading...',
    stats: {
        total_jobs: 0,
        filtered_jobs: 0,
        companies: 0,
        cities: 0,
        avg_salary: '—'
    }
};

// Debounced filter update
let filterTimeout = null;
const debouncedFilterUpdate = () => {
    clearTimeout(filterTimeout);
    filterTimeout = setTimeout(() => {
        fetchJobs(1); // Reset to page 1 when filters change
        updateURL();
    }, 300);
};

// Actions
const actions = {
    // Navigation
    goToPage: (page) => {
        state.currentPage = page;
        fetchJobs(page);
        updateURL();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    
    // Filters
    updateFilter: (key, value) => {
        state.filters[key] = value;
        
        // Clear dependent filters for hierarchical filtering
        if (key === 'industry') {
            state.filters.department = '';
            state.filters.job_family = '';
            state.filters.specialization = '';
        } else if (key === 'department') {
            state.filters.job_family = '';
            state.filters.specialization = '';
        } else if (key === 'job_family') {
            state.filters.specialization = '';
        }
        
        debouncedFilterUpdate();
    },
    
    updateSearch: (value) => {
        state.filters.search = value;
        debouncedFilterUpdate();
    },
    
    resetFilters: () => {
        state.filters = filterManager.createDefaultFilters();
        filterManager.filters = state.filters;
        fetchJobs(1);
        updateURL();
    },
    
    // UI
    toggleSidebar: () => {
        state.sidebarOpen = !state.sidebarOpen;
        m.redraw();
    },
    
    openJobDetail: (job) => {
        state.selectedJob = job;
        state.detailTab = 'parsed';
        m.redraw();
    },
    
    closeJobDetail: () => {
        state.selectedJob = null;
        m.redraw();
    },
    
    setDetailTab: (tab) => {
        state.detailTab = tab;
        m.redraw();
    },
    
    // Hierarchical filter helpers
    getFilteredDepartments: () => {
        if (!state.filters.industry) return [];
        return (filterManager.lookups.departments || []).filter(dept =>
            dept.parent_industry_id == state.filters.industry
        );
    },
    
    getFilteredJobFamilies: () => {
        if (!state.filters.department) return [];
        return (filterManager.lookups.job_families || []).filter(family =>
            family.parent_department_id == state.filters.department
        );
    },
    
    getFilteredSpecializations: () => {
        if (!state.filters.job_family) return [];
        return (filterManager.lookups.specializations || []).filter(spec =>
            spec.parent_job_family_id == state.filters.job_family
        );
    }
};

// Data fetching
async function fetchJobs(page = 1) {
    try {
        state.loading = true;
        state.error = '';
        m.redraw();
        
        // Fetch all jobs if not already loaded
        if (filterManager.allJobs.length === 0) {
            await api.fetchAllJobs();
            filterManager.allJobs = api.allJobs;
        }
        
        // Apply filters
        const filtered = filterManager.filterJobs(filterManager.allJobs);
        
        // Paginate
        const result = filterManager.paginateJobs(filtered, page);
        
        state.jobs = result.jobs;
        state.currentPage = result.page;
        state.totalPages = result.total_pages;
        state.totalJobs = result.total_jobs;
        
        // Update stats
        updateStats(filtered);
        
        state.loading = false;
        m.redraw();
    } catch (err) {
        state.error = 'Failed to load jobs. Please try again.';
        state.loading = false;
        console.error('Error fetching jobs:', err);
        m.redraw();
    }
}

async function loadInitialData() {
    try {
        state.loading = true;
        m.redraw();
        
        // Load metadata and lookups in parallel
        await Promise.all([
            api.fetchMetadata(),
            api.fetchLookups()
        ]);
        
        filterManager.metadata = api.metadata;
        filterManager.lookups = api.lookups;
        
        // Update last updated time
        if (api.metadata.generated_at) {
            state.lastUpdated = new Date(api.metadata.generated_at).toLocaleString();
        }
        
        // Parse URL parameters
        parseURL();
        
        // Fetch jobs
        await fetchJobs(state.currentPage);
        
    } catch (err) {
        state.error = 'Failed to load initial data. Please refresh the page.';
        state.loading = false;
        console.error('Error loading initial data:', err);
        m.redraw();
    }
}

// URL state management
function updateURL() {
    const params = new URLSearchParams();
    
    params.set('page', state.currentPage.toString());
    
    // Add active filters to URL
    Object.entries(state.filters).forEach(([key, value]) => {
        if (value && value !== '' && value !== false) {
            if (Array.isArray(value) && value.length > 0) {
                params.set(key, value.join(','));
            } else if (typeof value === 'number' || typeof value === 'string') {
                params.set(key, value.toString());
            } else if (typeof value === 'boolean' && value) {
                params.set(key, 'true');
            }
        }
    });
    
    const url = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', url);
}

function parseURL() {
    const params = new URLSearchParams(window.location.search);
    
    // Parse page
    const page = parseInt(params.get('page') || '1');
    state.currentPage = Math.max(1, page);
    
    // Parse filters
    params.forEach((value, key) => {
        if (key === 'page') return;
        
        if (state.filters.hasOwnProperty(key)) {
            const filterValue = state.filters[key];
            
            if (Array.isArray(filterValue)) {
                state.filters[key] = value.split(',').filter(v => v);
            } else if (typeof filterValue === 'number') {
                state.filters[key] = parseInt(value) || null;
            } else if (typeof filterValue === 'boolean') {
                state.filters[key] = value === 'true';
            } else {
                state.filters[key] = value;
            }
        }
    });
}

function updateStats(filteredJobs) {
    const lookups = filterManager.lookups;
    
    state.stats.total_jobs = filterManager.metadata.total_jobs || filterManager.allJobs.length;
    state.stats.filtered_jobs = filteredJobs.length;
    state.stats.companies = lookups.companies ? lookups.companies.length : 0;
    state.stats.cities = lookups.cities ? lookups.cities.length : 0;
    
    // Calculate average salary
    const jobsWithSalary = filteredJobs.filter(j => j.min_salary_mdl || j.max_salary_mdl);
    if (jobsWithSalary.length > 0) {
        const avgSalary = jobsWithSalary.reduce((sum, j) => {
            const salary = j.min_salary_mdl || j.max_salary_mdl || 0;
            return sum + salary;
        }, 0) / jobsWithSalary.length;
        state.stats.avg_salary = Math.round(avgSalary).toLocaleString() + ' MDL';
    } else {
        state.stats.avg_salary = '—';
    }
}

// Main App Component
const App = {
    oninit: () => {
        loadInitialData();
    },
    
    view: () => {
        return m('div', [
            // Header
            m(Header, { state, actions }),
            
            // Main content
            m('.max-w-7xl.mx-auto.px-4.sm:px-6.lg:px-8.py-6', [
                m('.grid.grid-cols-1.lg:grid-cols-4.gap-6', [
                    // Sidebar (filters)
                    m('aside', {
                        class: state.sidebarOpen ? 'block' : 'hidden lg:block'
                    }, [
                        m(FilterPanel, {
                            state,
                            actions,
                            lookups: filterManager.lookups
                        })
                    ]),
                    
                    // Main content area
                    m('.lg:col-span-3', [
                        // Job list
                        m(JobList, { state, actions }),
                        
                        // Pagination
                        m(Pagination, { state, actions })
                    ])
                ])
            ]),
            
            // Job detail modal
            state.selectedJob ? m(JobDetail, { state, actions }) : null
        ]);
    }
};

// Mount the app
m.mount(document.getElementById('app'), App);

console.log('Mithril app initialized');
