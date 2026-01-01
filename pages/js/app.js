import apiService from './services/api.js';
import JobListComponent from './components/job-list.js';
import JobDetailComponent from './components/job-detail.js';
import FiltersComponent from './components/filters.js';

const { createApp } = Vue;

const app = createApp({
    data() {
        return {
            loading: true,
            error: null,
            lookups: {},
            allJobs: [],
            filteredJobs: [],
            currentPageJobs: [],
            selectedJob: null,
            currentPage: 1,
            totalPages: 1,
            filters: {
                search: '',
                city: null,
                remote_work: null,
                seniority_level: null,
                employment_type: null,
            }
        };
    },
    
    async mounted() {
        try {
            await this.loadData();
        } catch (err) {
            this.error = 'Failed to load job data: ' + err.message;
            console.error(err);
        } finally {
            this.loading = false;
        }
    },
    
    methods: {
        async loadData() {
            // Load lookups first
            this.lookups = await apiService.loadLookups();
            
            // Load pages list to determine pagination
            const pagesList = await apiService.loadPagesList();
            this.totalPages = pagesList.total_pages;
            
            // Load first page
            await this.loadPage(1);
        },
        
        async loadPage(pageNum) {
            this.loading = true;
            try {
                const pageData = await apiService.loadJobPage(pageNum);
                this.allJobs = pageData.jobs;
                this.applyFilters();
                this.currentPage = pageNum;
            } finally {
                this.loading = false;
            }
        },
        
        applyFilters() {
            let filtered = [...this.allJobs];
            
            // Search filter
            if (this.filters.search) {
                const search = this.filters.search.toLowerCase();
                filtered = filtered.filter(job => 
                    (job.job_title && job.job_title.toLowerCase().includes(search)) ||
                    (job.company_name && job.company_name.toLowerCase().includes(search))
                );
            }
            
            // City filter
            if (this.filters.city) {
                filtered = filtered.filter(job => job.city_id === parseInt(this.filters.city));
            }
            
            // Remote work filter
            if (this.filters.remote_work) {
                filtered = filtered.filter(job => job.remote_work_id === parseInt(this.filters.remote_work));
            }
            
            // Seniority filter
            if (this.filters.seniority_level) {
                filtered = filtered.filter(job => job.seniority_level_id === parseInt(this.filters.seniority_level));
            }
            
            // Employment type filter
            if (this.filters.employment_type) {
                filtered = filtered.filter(job => job.employment_type_id === parseInt(this.filters.employment_type));
            }
            
            this.filteredJobs = filtered;
            this.currentPageJobs = filtered;
        },
        
        updateFilters(newFilters) {
            this.filters = { ...this.filters, ...newFilters };
            this.applyFilters();
        },
        
        selectJob(job) {
            this.selectedJob = job;
            window.scrollTo(0, 0);
        },
        
        async changePage(pageNum) {
            await this.loadPage(pageNum);
            window.scrollTo(0, 0);
        }
    },
    
    components: {
        'job-list-component': JobListComponent,
        'job-detail-component': JobDetailComponent,
        'filters-component': FiltersComponent
    }
});

app.mount('#app');
