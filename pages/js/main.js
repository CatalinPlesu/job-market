/**
 * Job Board Component
 * Main Vue component for the job board
 */

import { Utils } from './utils.js';

export class JobBoardComponent {
    constructor() {
        this.utils = Utils;
        this.api = window.JobMarketAPI;
        this.filters = window.FilterManager;
        
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
                const filterManager = window.FilterManager;
                const filters = reactive(filterManager.filters);

                // Computed properties
                const stats = computed(() => {
                    return Utils.calculateStats(state.jobs, filterManager.metadata);
                });

                const visiblePages = computed(() => {
                    return Utils.getVisiblePages(state.currentPage, state.totalPages);
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
                const formatDate = Utils.formatDate;
                const formatSalaryRange = Utils.formatSalaryRange;

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
                        const data = await filterManager.api.fetchJobs(page);
                        state.jobs = data.jobs;
                        state.currentPage = data.page;
                        state.totalPages = data.totalPages;
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

                const handleSearch = Utils.debounce(() => {
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

                // Lifecycle
                onMounted(async () => {
                    await fetchMetadata();
                    await fetchLookups();
                    filterManager.parseURL();
                    await fetchJobs(filterManager.filters.page || 1);
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
                    handleSearch
                };
            }
        });
    }
}

// Create global component instance
window.JobBoardComponent = new JobBoardComponent();