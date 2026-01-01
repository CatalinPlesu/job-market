/**
 * JobCard Component
 * Individual job card displaying job summary
 */

export const JobCard = {
    view: (vnode) => {
        const { job, onclick } = vnode.attrs;
        
        return m('.job-card.card.bg-base-100.shadow-sm.border.cursor-pointer', {
            onclick: () => onclick(job)
        }, [
            m('.card-body.p-4', [
                // Title and Company
                m('.flex.items-start.justify-between.gap-2', [
                    m('div.flex-1', [
                        m('h3.card-title.text-lg.mb-1', job.title || 'Untitled Position'),
                        m('p.text-sm.opacity-70', [
                            m('span.font-medium', job.company || 'Unknown Company'),
                            job.company_size ? m('span.ml-2.text-xs', `(${job.company_size})`) : null
                        ])
                    ]),
                    // Days open badge
                    job.days_open !== undefined ? m('.badge.badge-sm.badge-outline', `${job.days_open}d`) : null
                ]),
                
                // Location and Remote
                m('.flex.items-center.gap-2.mt-2.text-sm.opacity-70', [
                    job.city ? m('span', `📍 ${job.city}`) : null,
                    job.remote_work ? m('.badge.badge-sm.badge-primary', job.remote_work) : null
                ]),
                
                // Salary
                job.has_salary && (job.min_salary_mdl || job.max_salary_mdl) ? 
                    m('.mt-2', [
                        m('p.text-sm.font-semibold.text-success', [
                            FilterUtils.formatSalaryRange(job.min_salary_mdl, job.max_salary_mdl, 'MDL', job.salary_period),
                            job.original_currency && job.original_currency !== 'MDL' ?
                                m('span.text-xs.opacity-70.ml-2', 
                                    `(${FilterUtils.formatSalaryRange(job.original_min_salary, job.original_max_salary, job.original_currency, job.salary_period)})`
                                ) : null
                        ])
                    ]) : null,
                
                // Skills preview
                job.skills_preview && job.skills_preview.length > 0 ?
                    m('.mt-3.flex.flex-wrap.gap-1', 
                        job.skills_preview.slice(0, 5).map(skill =>
                            m('.badge.badge-sm.badge-ghost', skill)
                        ).concat(
                            job.total_skills > 5 ? 
                                m('.badge.badge-sm.badge-ghost', `+${job.total_skills - 5} more`) : []
                        )
                    ) : null,
                
                // Footer with sites and details
                m('.mt-3.flex.items-center.justify-between.text-xs.opacity-70', [
                    // Multiple sites indicator
                    job.sites && job.sites.length > 0 ?
                        m('.flex.gap-1',
                            job.sites.map(site =>
                                m('.badge.badge-xs.badge-outline', site)
                            )
                        ) : null,
                    
                    // Additional indicators
                    m('.flex.gap-2', [
                        job.seniority_level ? m('span', job.seniority_level) : null,
                        job.employment_type ? m('span', job.employment_type) : null
                    ])
                ])
            ])
        ]);
    }
};

// Reference FilterUtils from window for formatting
const FilterUtils = window.FilterUtils || {
    formatSalaryRange: (min, max, currency, period) => {
        if (!min && !max) return 'Not specified';
        const format = (val) => val ? val.toLocaleString() : '';
        const range = min && max ? `${format(min)} - ${format(max)}` : format(min || max);
        return `${range} ${currency}${period ? '/' + period : ''}`;
    }
};
