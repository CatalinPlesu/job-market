const JobListComponent = {
    props: ['jobs', 'currentPage', 'totalPages', 'lookups'],
    
    template: `
        <div class="job-list">
            <div class="job-stats">
                <p>Showing {{ jobs.length }} jobs (Page {{ currentPage }} of {{ totalPages }})</p>
            </div>
            
            <div v-if="jobs.length === 0" class="no-jobs">
                No jobs found matching your criteria.
            </div>
            
            <div v-else class="jobs-grid">
                <div v-for="job in jobs" :key="job.id" class="job-card" @click="$emit('select-job', job)">
                    <div class="job-header">
                        <h2 class="job-title">{{ job.job_title }}</h2>
                        <span v-if="job.sites" class="job-sites">{{ job.sites.length }} sites</span>
                    </div>
                    
                    <p class="company-name">{{ job.company_name }}</p>
                    
                    <div class="job-meta">
                        <span v-if="job.city_id" class="meta-item">
                            📍 {{ getLookup('cities', job.city_id) }}
                        </span>
                        <span v-if="job.remote_work_id" class="meta-item">
                            💼 {{ getLookup('remote_work_options', job.remote_work_id) }}
                        </span>
                        <span v-if="job.seniority_level_id" class="meta-item">
                            ⭐ {{ getLookup('seniority_levels', job.seniority_level_id) }}
                        </span>
                    </div>
                    
                    <div v-if="job.min_salary || job.max_salary" class="job-salary">
                        💰 {{ formatSalary(job) }}
                    </div>
                    
                    <div class="job-footer">
                        <span v-if="job.posting_date" class="posting-date">
                            Posted: {{ formatDate(job.posting_date) }}
                        </span>
                    </div>
                </div>
            </div>
            
            <div v-if="totalPages > 1" class="pagination">
                <button 
                    @click="$emit('change-page', currentPage - 1)"
                    :disabled="currentPage === 1"
                    class="btn-page"
                >
                    ← Previous
                </button>
                
                <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
                
                <button 
                    @click="$emit('change-page', currentPage + 1)"
                    :disabled="currentPage === totalPages"
                    class="btn-page"
                >
                    Next →
                </button>
            </div>
        </div>
    `,
    
    methods: {
        getLookup(table, id) {
            return this.lookups[table]?.[id] || 'N/A';
        },
        
        formatSalary(job) {
            const currency = this.getLookup('currencies', job.salary_currency_id);
            const period = this.getLookup('salary_periods', job.salary_period_id);
            
            if (job.min_salary && job.max_salary) {
                return `${job.min_salary} - ${job.max_salary} ${currency}/${period}`;
            } else if (job.min_salary) {
                return `From ${job.min_salary} ${currency}/${period}`;
            } else if (job.max_salary) {
                return `Up to ${job.max_salary} ${currency}/${period}`;
            }
            return 'Not specified';
        },
        
        formatDate(dateStr) {
            if (!dateStr) return 'N/A';
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
        }
    }
};

// Styles
const style = document.createElement('style');
style.textContent = `
    .job-list {
        margin-top: 20px;
    }
    
    .job-stats {
        background: white;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .job-stats p {
        color: #666;
        font-size: 0.95em;
    }
    
    .no-jobs {
        background: white;
        padding: 60px 20px;
        text-align: center;
        border-radius: 8px;
        color: #999;
        font-size: 1.1em;
    }
    
    .jobs-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .job-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .job-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .job-header {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 8px;
    }
    
    .job-title {
        font-size: 1.3em;
        font-weight: 600;
        color: #333;
        margin: 0;
        flex: 1;
    }
    
    .job-sites {
        background: #667eea;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 500;
        margin-left: 10px;
        white-space: nowrap;
    }
    
    .company-name {
        font-size: 1.1em;
        color: #666;
        margin: 8px 0 16px;
    }
    
    .job-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin: 16px 0;
    }
    
    .meta-item {
        background: #f0f0f0;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.9em;
        color: #555;
    }
    
    .job-salary {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 10px 12px;
        border-radius: 6px;
        margin: 12px 0;
        font-weight: 500;
    }
    
    .job-footer {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #eee;
    }
    
    .posting-date {
        font-size: 0.85em;
        color: #999;
    }
    
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        padding: 30px 0;
    }
    
    .btn-page {
        background: #667eea;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 1em;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .btn-page:hover:not(:disabled) {
        background: #5568d3;
        transform: translateY(-1px);
    }
    
    .btn-page:disabled {
        background: #ccc;
        cursor: not-allowed;
        opacity: 0.6;
    }
    
    .page-info {
        font-weight: 500;
        color: #666;
    }
    
    @media (max-width: 768px) {
        .jobs-grid {
            grid-template-columns: 1fr;
        }
        
        .job-title {
            font-size: 1.1em;
        }
        
        .pagination {
            flex-direction: column;
            gap: 10px;
        }
        
        .btn-page {
            width: 100%;
        }
    }
`;
document.head.appendChild(style);

export default JobListComponent;
