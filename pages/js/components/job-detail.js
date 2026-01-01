const JobDetailComponent = {
    props: ['job', 'lookups'],
    
    data() {
        return {
            activeTab: 'structured'
        };
    },
    
    template: `
        <div class="job-detail">
            <button @click="$emit('back')" class="btn-back">← Back to List</button>
            
            <div class="detail-header">
                <h1>{{ job.job_title }}</h1>
                <h2>{{ job.company_name }}</h2>
                
                <div class="header-meta">
                    <span v-if="job.city_id">
                        📍 {{ getLookup('cities', job.city_id) }}
                        <span v-if="job.country_id">, {{ getLookup('countries', job.country_id) }}</span>
                    </span>
                    <span v-if="job.posting_date">Posted: {{ formatDate(job.posting_date) }}</span>
                </div>
                
                <div v-if="job.sites && job.sites.length > 1" class="found-on">
                    <strong>Found on {{ job.sites.length }} sites:</strong>
                    <div class="site-links">
                        <a v-for="link in job.job_urls" :key="link.url" 
                           :href="link.url" target="_blank" class="site-link">
                            {{ link.site }}
                        </a>
                    </div>
                </div>
                <a v-else :href="job.job_url" target="_blank" class="apply-link">
                    View Original Posting →
                </a>
            </div>
            
            <div class="tabs">
                <button 
                    @click="activeTab = 'structured'" 
                    :class="{ active: activeTab === 'structured' }"
                    class="tab-btn"
                >
                    Structured Details
                </button>
                <button 
                    @click="activeTab = 'raw'" 
                    :class="{ active: activeTab === 'raw' }"
                    class="tab-btn tab-debug"
                >
                    Raw Data (Debug)
                </button>
            </div>
            
            <div v-if="activeTab === 'structured'" class="structured-content">
                <section v-if="job.min_salary || job.max_salary" class="detail-section salary-section">
                    <h3>💰 Compensation</h3>
                    <p class="salary-amount">{{ formatSalary(job) }}</p>
                </section>
                
                <section class="detail-section">
                    <h3>📋 Job Information</h3>
                    <div class="info-grid">
                        <div v-if="job.seniority_level_id" class="info-item">
                            <label>Seniority Level:</label>
                            <span>{{ getLookup('seniority_levels', job.seniority_level_id) }}</span>
                        </div>
                        <div v-if="job.employment_type_id" class="info-item">
                            <label>Employment Type:</label>
                            <span>{{ getLookup('employment_types', job.employment_type_id) }}</span>
                        </div>
                        <div v-if="job.contract_type_id" class="info-item">
                            <label>Contract Type:</label>
                            <span>{{ getLookup('contract_types', job.contract_type_id) }}</span>
                        </div>
                        <div v-if="job.remote_work_id" class="info-item">
                            <label>Work Location:</label>
                            <span>{{ getLookup('remote_work_options', job.remote_work_id) }}</span>
                        </div>
                        <div v-if="job.experience_years" class="info-item">
                            <label>Experience Required:</label>
                            <span>{{ job.experience_years }} years</span>
                        </div>
                        <div v-if="job.required_education_id" class="info-item">
                            <label>Education:</label>
                            <span>{{ getLookup('education_levels', job.required_education_id) }}</span>
                        </div>
                    </div>
                </section>
                
                <section v-if="job.responsibilities && job.responsibilities.length" class="detail-section">
                    <h3>🎯 Responsibilities</h3>
                    <ul class="list-items">
                        <li v-for="resp in job.responsibilities" :key="resp.order">
                            {{ resp.description }}
                        </li>
                    </ul>
                </section>
                
                <section v-if="hasSkills()" class="detail-section">
                    <h3>🛠️ Required Skills</h3>
                    <div v-if="job.hard_skill_ids && job.hard_skill_ids.length" class="skills-section">
                        <h4>Technical Skills</h4>
                        <div class="skill-tags">
                            <span v-for="id in job.hard_skill_ids" :key="id" class="skill-tag">
                                {{ getLookup('hard_skills', id) }}
                            </span>
                        </div>
                    </div>
                    <div v-if="job.soft_skill_ids && job.soft_skill_ids.length" class="skills-section">
                        <h4>Soft Skills</h4>
                        <div class="skill-tags">
                            <span v-for="id in job.soft_skill_ids" :key="id" class="skill-tag soft">
                                {{ getLookup('soft_skills', id) }}
                            </span>
                        </div>
                    </div>
                </section>
                
                <section v-if="job.languages && job.languages.length" class="detail-section">
                    <h3>🌐 Languages</h3>
                    <div class="language-list">
                        <span v-for="lang in job.languages" :key="lang.language" class="language-item">
                            {{ lang.language }}
                            <span v-if="lang.proficiency" class="proficiency">({{ lang.proficiency }})</span>
                        </span>
                    </div>
                </section>
                
                <section v-if="job.benefit_ids && job.benefit_ids.length" class="detail-section">
                    <h3>✨ Benefits</h3>
                    <ul class="list-items">
                        <li v-for="id in job.benefit_ids" :key="id">
                            {{ getLookup('benefits', id) }}
                        </li>
                    </ul>
                </section>
                
                <section v-if="job.contact_emails && job.contact_emails.length" class="detail-section">
                    <h3>📧 Contact Information</h3>
                    <div class="contact-info">
                        <p v-for="email in job.contact_emails" :key="email">
                            Email: <a :href="'mailto:' + email">{{ email }}</a>
                        </p>
                        <p v-for="phone in job.contact_phones" :key="phone">
                            Phone: {{ phone }}
                        </p>
                    </div>
                </section>
            </div>
            
            <div v-else class="raw-content">
                <div class="debug-notice">
                    ⚠️ This is raw data for debugging purposes
                </div>
                <pre>{{ JSON.stringify(job, null, 2) }}</pre>
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
            return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        },
        
        hasSkills() {
            return (this.job.hard_skill_ids && this.job.hard_skill_ids.length) ||
                   (this.job.soft_skill_ids && this.job.soft_skill_ids.length);
        }
    }
};

// Styles
const style = document.createElement('style');
style.textContent = `
    .job-detail {
        background: white;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .btn-back {
        background: #f0f0f0;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 1em;
        cursor: pointer;
        margin-bottom: 20px;
        transition: background 0.2s;
    }
    
    .btn-back:hover {
        background: #e0e0e0;
    }
    
    .detail-header {
        border-bottom: 2px solid #eee;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }
    
    .detail-header h1 {
        font-size: 2em;
        color: #333;
        margin-bottom: 10px;
    }
    
    .detail-header h2 {
        font-size: 1.4em;
        color: #667eea;
        font-weight: 500;
        margin-bottom: 15px;
    }
    
    .header-meta {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        color: #666;
        margin-bottom: 15px;
    }
    
    .found-on {
        margin-top: 15px;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .site-links {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 10px;
    }
    
    .site-link {
        display: inline-block;
        padding: 8px 16px;
        background: #667eea;
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-size: 0.9em;
        transition: background 0.2s;
    }
    
    .site-link:hover {
        background: #5568d3;
    }
    
    .apply-link {
        display: inline-block;
        margin-top: 15px;
        padding: 12px 24px;
        background: #667eea;
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 500;
        transition: background 0.2s;
    }
    
    .apply-link:hover {
        background: #5568d3;
    }
    
    .tabs {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        border-bottom: 2px solid #eee;
    }
    
    .tab-btn {
        background: none;
        border: none;
        padding: 12px 24px;
        font-size: 1em;
        cursor: pointer;
        color: #666;
        border-bottom: 3px solid transparent;
        margin-bottom: -2px;
        transition: all 0.2s;
    }
    
    .tab-btn:hover {
        color: #667eea;
    }
    
    .tab-btn.active {
        color: #667eea;
        border-bottom-color: #667eea;
        font-weight: 600;
    }
    
    .tab-debug {
        margin-left: auto;
        font-size: 0.9em;
        opacity: 0.7;
    }
    
    .detail-section {
        margin-bottom: 30px;
    }
    
    .detail-section h3 {
        font-size: 1.4em;
        color: #333;
        margin-bottom: 15px;
    }
    
    .detail-section h4 {
        font-size: 1.1em;
        color: #555;
        margin: 15px 0 10px;
    }
    
    .salary-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
    }
    
    .salary-section h3 {
        color: white;
    }
    
    .salary-amount {
        font-size: 1.5em;
        font-weight: 600;
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
    }
    
    .info-item {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    
    .info-item label {
        font-weight: 600;
        color: #555;
        font-size: 0.9em;
    }
    
    .info-item span {
        color: #333;
        font-size: 1.05em;
    }
    
    .list-items {
        list-style: none;
        padding: 0;
    }
    
    .list-items li {
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
        line-height: 1.6;
    }
    
    .list-items li:last-child {
        border-bottom: none;
    }
    
    .skill-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    .skill-tag {
        background: #667eea;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: 500;
    }
    
    .skill-tag.soft {
        background: #764ba2;
    }
    
    .language-list {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
    }
    
    .language-item {
        background: #f0f0f0;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 1em;
    }
    
    .proficiency {
        color: #666;
        font-size: 0.9em;
        margin-left: 5px;
    }
    
    .contact-info {
        line-height: 1.8;
    }
    
    .contact-info a {
        color: #667eea;
        text-decoration: none;
    }
    
    .contact-info a:hover {
        text-decoration: underline;
    }
    
    .raw-content {
        margin-top: 20px;
    }
    
    .debug-notice {
        background: #fff3cd;
        border: 1px solid #ffc107;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #856404;
    }
    
    .raw-content pre {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        overflow-x: auto;
        font-size: 0.85em;
        line-height: 1.5;
        border: 1px solid #dee2e6;
    }
    
    @media (max-width: 768px) {
        .job-detail {
            padding: 20px;
        }
        
        .detail-header h1 {
            font-size: 1.5em;
        }
        
        .detail-header h2 {
            font-size: 1.2em;
        }
        
        .info-grid {
            grid-template-columns: 1fr;
        }
        
        .tabs {
            overflow-x: auto;
        }
    }
`;
document.head.appendChild(style);

export default JobDetailComponent;
