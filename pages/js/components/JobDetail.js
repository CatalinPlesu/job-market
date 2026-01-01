/**
 * JobDetail Component
 * Modal showing detailed job information with parsed/raw tabs
 */

export const JobDetail = {
    view: (vnode) => {
        const { state, actions } = vnode.attrs;
        const job = state.selectedJob;
        
        if (!job) return null;
        
        return m('.modal.modal-open', [
            m('.modal-box.max-w-4xl.max-h-screen.overflow-y-auto', [
                // Modal header
                m('.flex.items-start.justify-between.mb-4', [
                    m('div', [
                        m('h2.text-2xl.font-bold.text-base-content', job.title || 'Job Details'),
                        m('p.text-base-content.opacity-70.mt-1', job.company || '')
                    ]),
                    m('button.btn.btn-sm.btn-circle.btn-ghost', {
                        onclick: actions.closeJobDetail
                    }, '✕')
                ]),
                
                // Tabs
                m('.tabs.tabs-boxed.mb-4', [
                    m('a.tab', {
                        class: state.detailTab === 'parsed' ? 'tab-active' : '',
                        onclick: () => actions.setDetailTab('parsed')
                    }, '📋 Parsed Details'),
                    m('a.tab', {
                        class: state.detailTab === 'raw' ? 'tab-active' : '',
                        onclick: () => actions.setDetailTab('raw')
                    }, '🔍 Raw Data')
                ]),
                
                // Tab content
                state.detailTab === 'parsed' ? 
                    m(ParsedJobView, { job }) : 
                    m(RawJobView, { job })
            ])
        ]);
    }
};

// Parsed job details view
const ParsedJobView = {
    view: (vnode) => {
        const { job } = vnode.attrs;
        
        return m('.space-y-6', [
            // Basic Info
            m('.card.bg-base-200', [
                m('.card-body.p-4', [
                    m('h3.font-semibold.text-lg.mb-2', 'Overview'),
                    m('.grid.grid-cols-2.gap-4', [
                        renderField('Location', job.city ? `${job.city}, ${job.country || ''}` : 'Not specified'),
                        renderField('Remote Work', job.remote_work || 'Not specified'),
                        renderField('Employment Type', job.employment_type || 'Not specified'),
                        renderField('Seniority Level', job.seniority_level || 'Not specified'),
                        renderField('Posted', job.posting_date ? new Date(job.posting_date).toLocaleDateString() : 'Unknown'),
                        renderField('Days Open', job.days_open !== undefined ? `${job.days_open} days` : 'Unknown')
                    ])
                ])
            ]),
            
            // Salary
            (job.has_salary || job.min_salary_mdl || job.max_salary_mdl) ? m('.card.bg-base-200', [
                m('.card-body.p-4', [
                    m('h3.font-semibold.text-lg.mb-2', 'Compensation'),
                    m('.text-2xl.font-bold.text-success', 
                        FilterUtils.formatSalaryRange(job.min_salary_mdl, job.max_salary_mdl, 'MDL', job.salary_period)
                    ),
                    job.original_currency && job.original_currency !== 'MDL' ?
                        m('.text-sm.opacity-70.mt-1', 
                            `Originally: ${FilterUtils.formatSalaryRange(job.original_min_salary, job.original_max_salary, job.original_currency, job.salary_period)}`
                        ) : null
                ])
            ]) : null,
            
            // Requirements
            m('.card.bg-base-200', [
                m('.card-body.p-4', [
                    m('h3.font-semibold.text-lg.mb-3', 'Requirements'),
                    m('.space-y-3', [
                        renderField('Education', job.required_education || 'Not specified'),
                        renderField('Experience', job.experience_years ? `${job.experience_years} years` : 'Not specified'),
                        job.languages_required && job.languages_required.length > 0 ?
                            renderFieldList('Languages', job.languages_required) : null,
                        job.hard_skills && job.hard_skills.length > 0 ?
                            renderFieldList('Hard Skills', job.hard_skills) : null,
                        job.soft_skills && job.soft_skills.length > 0 ?
                            renderFieldList('Soft Skills', job.soft_skills) : null,
                        job.certifications && job.certifications.length > 0 ?
                            renderFieldList('Certifications', job.certifications) : null
                    ])
                ])
            ]),
            
            // Company Info
            m('.card.bg-base-200', [
                m('.card-body.p-4', [
                    m('h3.font-semibold.text-lg.mb-3', 'Company Information'),
                    m('.space-y-2', [
                        renderField('Company', job.company || 'Unknown'),
                        renderField('Company Size', job.company_size || 'Not specified'),
                        job.contact_emails && job.contact_emails.length > 0 ?
                            renderField('Contact Email', job.contact_emails.join(', ')) : null,
                        job.contact_phones && job.contact_phones.length > 0 ?
                            renderField('Contact Phone', job.contact_phones.join(', ')) : null
                    ])
                ])
            ]),
            
            // Job Classification
            m('.card.bg-base-200', [
                m('.card-body.p-4', [
                    m('h3.font-semibold.text-lg.mb-3', 'Classification'),
                    m('.space-y-2', [
                        renderField('Industry', job.industry || 'Not specified'),
                        renderField('Department', job.department || 'Not specified'),
                        renderField('Job Family', job.job_family || 'Not specified'),
                        renderField('Specialization', job.specialization || 'Not specified'),
                        renderField('Job Function', job.job_function || 'Not specified')
                    ])
                ])
            ]),
            
            // Apply buttons
            job.urls ? m('.flex.gap-2', 
                Object.entries(job.urls).map(([site, url]) =>
                    m('a.btn.btn-primary', {
                        href: url,
                        target: '_blank',
                        rel: 'noopener noreferrer'
                    }, `Apply on ${site}`)
                )
            ) : null
        ]);
    }
};

// Raw job data view
const RawJobView = {
    view: (vnode) => {
        const { job } = vnode.attrs;
        
        if (!job.raw_data || !job.raw_data.sites) {
            return m('.alert.alert-info', 'No raw data available');
        }
        
        const sites = Object.keys(job.raw_data.sites);
        
        return m('.space-y-4', [
            // Site tabs if multiple sites
            sites.length > 1 ? m('.tabs.tabs-boxed', 
                sites.map(site =>
                    m('a.tab', {
                        class: job.selectedSite === site || (!job.selectedSite && site === sites[0]) ? 'tab-active' : '',
                        onclick: () => { job.selectedSite = site; m.redraw(); }
                    }, site)
                )
            ) : null,
            
            // Raw data display
            (() => {
                const activeSite = job.selectedSite || sites[0];
                const siteData = job.raw_data.sites[activeSite];
                
                if (!siteData) return null;
                
                return m('.card.bg-base-200', [
                    m('.card-body.p-4', [
                        m('h3.font-semibold.mb-2', `Raw Data from ${activeSite}`),
                        m('.space-y-3', [
                            renderField('URL', m('a.link.link-primary', { href: siteData.url, target: '_blank' }, siteData.url)),
                            renderField('Job Title', siteData.job_title || ''),
                            renderField('Company Name', siteData.company_name || ''),
                            renderField('Scraped At', siteData.scraped_at ? new Date(siteData.scraped_at).toLocaleString() : ''),
                            m('div', [
                                m('.font-semibold.mb-2', 'Job Description:'),
                                m('.prose.max-w-none.p-4.bg-base-100.rounded.overflow-auto.max-h-96', 
                                    m.trust(siteData.job_description || 'No description available')
                                )
                            ])
                        ])
                    ])
                ]);
            })()
        ]);
    }
};

// Helper functions
const renderField = (label, value) => {
    if (!value) return null;
    return m('div', [
        m('span.font-semibold', label + ': '),
        typeof value === 'string' ? m('span', value) : value
    ]);
};

const renderFieldList = (label, items) => {
    if (!items || items.length === 0) return null;
    return m('div', [
        m('.font-semibold.mb-2', label + ':'),
        m('.flex.flex-wrap.gap-1',
            items.map(item =>
                m('.badge.badge-sm', typeof item === 'string' ? item : item.name || item)
            )
        )
    ]);
};

// Reference FilterUtils from window
const FilterUtils = window.FilterUtils || {
    formatSalaryRange: (min, max, currency, period) => {
        if (!min && !max) return 'Not specified';
        const format = (val) => val ? val.toLocaleString() : '';
        const range = min && max ? `${format(min)} - ${format(max)}` : format(min || max);
        return `${range} ${currency}${period ? '/' + period : ''}`;
    }
};
