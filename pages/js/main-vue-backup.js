/**
 * Job Board Component
 * Main Vue component for the job board
 */

import { FilterManager, FilterUtils } from './core/filters.js';
import { BrowserAPI } from './core/api.js';

export class JobBoardComponent {
    constructor() {
        this.utils = FilterUtils;
        this.api = new BrowserAPI();
        this.filterManager = new FilterManager(this.api);
        
        this.state = {
            jobs: [],
            loading: false,
            error: '',
            currentPage: 1,
            totalPages: 1,
            selectedJob: null,
            detailTab: 'structured',
            sidebarOpen: true,
            skillsSearch: '',
            companiesSearch: '',
            sortOption: 'date_desc'
        };
    }

    createComponent() {
        const { createApp, ref, reactive, computed, watch, onMounted } = Vue;

        return createApp({
            setup() {
                // Reactive state
                const state = reactive({
                    jobs: [],
                    loading: false,
                    error: '',
                    currentPage: 1,
                    totalPages: 1,
                    selectedJob: null,
                    detailTab: 'structured',
                    sidebarOpen: true,
                    skillsSearch: '',
                    companiesSearch: '',
                    sortOption: 'date_desc'
                });

                // Initialize filter manager and set up reactive filters
                const filterManager = window.jobBoard.filterManager;
                const filters = reactive(filterManager.filters);

                // Computed properties
                const stats = computed(() => {
                    return FilterUtils.calculateStats(state.jobs, filterManager.metadata);
                });

                const visiblePages = computed(() => {
                    return FilterUtils.getVisiblePages(state.currentPage, state.totalPages);
                });

                const lastUpdated = computed(() => {
                    return filterManager.metadata.generated_at 
                        ? new Date(filterManager.metadata.generated_at).toLocaleString()
                        : 'Never';
                });

                const filteredCompanies = computed(() => {
                    const search = state.companiesSearch.toLowerCase();
                    return (filterManager.lookups.companies || [])
                        .filter(company => company.name.toLowerCase().includes(search))
                        .sort((a, b) => (b.jobs_count || 0) - (a.jobs_count || 0))
                        .slice(0, 50);
                });

                // Methods
                const formatDate = FilterUtils.formatDate;
                const formatSalaryRange = FilterUtils.formatSalaryRange;

                const fetchMetadata = async () => {
                    try {
                        state.loading = true;
                        filterManager.metadata = await filterManager.api.fetchMetadata();
                    } catch (err) {
                        state.error = 'Failed to load job data. Please try again later.';
                    } finally {
                        state.loading = false;
                    }
                };

                const fetchLookups = async () => {
                    try {
                        filterManager.lookups = await filterManager.api.fetchLookups();
                    } catch (err) {
                        console.error('Error fetching lookups:', err);
                    }
                };

                const fetchJobs = async (page = 1) => {
                    state.loading = true;
                    state.error = '';
                    
                    try {
                        // Fetch all jobs if not already loaded
                        const allJobs = await filterManager.api.fetchAllJobs();
                        
                        // Apply filters to get filtered jobs
                        const filteredJobs = filterManager.api.filterJobs(allJobs, filterManager.filters);
                        
                        // Apply pagination to filtered jobs
                        const paginatedData = filterManager.api.paginateJobs(filteredJobs, page);
                        
                        state.jobs = paginatedData.jobs;
                        state.currentPage = paginatedData.page;
                        state.totalPages = paginatedData.totalPages;
                    } catch (err) {
                        state.error = 'Failed to load jobs. Please try again.';
                    } finally {
                        state.loading = false;
                    }
                };

                const applyFiltersInstant = async () => {
                    filterManager.updateURL();
                    await fetchJobs(state.currentPage);
                };

                const resetFilters = () => {
                    filterManager.resetFilters();
                    state.skillsSearch = '';
                    state.companiesSearch = '';
                    fetchJobs(1);
                };

                const goToPage = async (page) => {
                    if (page >= 1 && page <= state.totalPages && page !== state.currentPage) {
                        state.currentPage = page;
                        await fetchJobs(page);
                    }
                };

                const changeSort = () => {
                    filterManager.updateURL();
                    fetchJobs(state.currentPage);
                };

                const onIndustryChange = () => {
                    filters.department = '';
                    filters.job_family = '';
                    filters.specialization = '';
                    applyFiltersInstant();
                };

                const onDepartmentChange = () => {
                    filters.job_family = '';
                    filters.specialization = '';
                    applyFiltersInstant();
                };

                const onJobFamilyChange = () => {
                    filters.specialization = '';
                    applyFiltersInstant();
                };

                const openJobDetail = (jobId) => {
                    state.selectedJob = state.jobs.find(j => j.id === jobId);
                    state.detailTab = 'structured';
                };

                const closeJobDetail = () => {
                    state.selectedJob = null;
                };

                const toggleSidebar = () => {
                    state.sidebarOpen = !state.sidebarOpen;
                };

                const handleSearch = FilterUtils.debounce(() => {
                    applyFiltersInstant();
                }, 300);

                // Watchers for instant filtering
                watch(() => filters, (newVal, oldVal) => {
                    clearTimeout(window.filterTimeout);
                    window.filterTimeout = setTimeout(() => {
                        applyFiltersInstant();
                    }, 100);
                }, { deep: true });

                watch(() => filters.search, (newVal) => {
                    if (newVal) {
                        handleSearch();
                    }
                });

                // URL parsing and updating
                const updateURL = () => {
                    const params = new URLSearchParams();
                    
                    // Add filters to URL
                    Object.entries(filters).forEach(([key, value]) => {
                        if (value !== '' && value !== null && value !== false && (Array.isArray(value) ? value.length > 0 : true)) {
                            if (Array.isArray(value)) {
                                params.set(key, value.join(','));
                            } else {
                                params.set(key, value.toString());
                            }
                        }
                    });
                    
                    // Add pagination and sorting
                    if (state.currentPage > 1) params.set('page', state.currentPage.toString());
                    if (state.sortOption !== 'date_desc') params.set('sort', state.sortOption);
                    
                    const newUrl = `${window.location.pathname}?${params.toString()}`;
                    history.replaceState({}, '', newUrl);
                };

                const parseURL = () => {
                    const urlParams = new URLSearchParams(window.location.search);
                    
                    // Parse filters
                    Object.keys(filters).forEach(key => {
                        const value = urlParams.get(key);
                        if (value) {
                            if (Array.isArray(filters[key])) {
                                filters[key] = value.split(',');
                            } else if (typeof filters[key] === 'number') {
                                filters[key] = parseInt(value);
                            } else if (typeof filters[key] === 'boolean') {
                                filters[key] = value === 'true';
                            } else {
                                filters[key] = value;
                            }
                        }
                    });
                    
                    // Parse pagination and sorting
                    const page = parseInt(urlParams.get('page') || '1');
                    const sort = urlParams.get('sort') || 'date_desc';
                    
                    state.currentPage = Math.max(1, page);
                    state.sortOption = sort;
                };

                // Lifecycle
                onMounted(async () => {
                    await fetchMetadata();
                    await fetchLookups();
                    parseURL();
                    await fetchJobs(state.currentPage);
                });

                return {
                    ...state,
                    filters,
                    stats,
                    visiblePages,
                    lastUpdated,
                    filteredCompanies,
                    formatDate,
                    formatSalaryRange,
                    fetchJobs,
                    applyFiltersInstant,
                    resetFilters,
                    goToPage,
                    changeSort,
                    onIndustryChange,
                    onDepartmentChange,
                    onJobFamilyChange,
                    openJobDetail,
                    closeJobDetail,
                    toggleSidebar,
                    handleSearch,
                    updateURL,
                    parseURL
                };
            }
        });
    }
}

// Create global component instance
window.jobBoard = new JobBoardComponent();