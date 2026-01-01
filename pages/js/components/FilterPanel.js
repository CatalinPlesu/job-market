/**
 * FilterPanel Component
 * Comprehensive filtering sidebar with hierarchical and multi-select filters
 */

export const FilterPanel = {
    view: (vnode) => {
        const { state, actions, lookups } = vnode.attrs;
        const filters = state.filters;
        
        return m('aside.bg-base-100.rounded-lg.shadow-sm.border.p-6.space-y-6', [
            // Quick Stats
            m('.grid.grid-cols-2.gap-4', [
                m('.text-center.p-4.bg-primary.bg-opacity-10.rounded-lg', [
                    m('.text-2xl.font-bold.text-primary', state.stats.filtered_jobs || 0),
                    m('.text-sm.text-primary', 'Showing')
                ]),
                m('.text-center.p-4.bg-success.bg-opacity-10.rounded-lg', [
                    m('.text-2xl.font-bold.text-success', state.stats.avg_salary || '—'),
                    m('.text-sm.text-success', 'Avg Salary')
                ])
            ]),
            
            // Hierarchical Filters
            m('.space-y-4', [
                m('h3.font-semibold.text-base-content', 'Job Classification'),
                
                // Industry
                m('.form-control', [
                    m('label.label', m('span.label-text', 'Industry')),
                    m('select.select.select-bordered.select-sm', {
                        value: filters.industry,
                        onchange: (e) => actions.updateFilter('industry', e.target.value)
                    }, [
                        m('option', { value: '' }, 'All Industries'),
                        (lookups.industries || []).map(ind =>
                            m('option', { value: ind.id }, `${ind.name} (${ind.jobs_count || 0})`)
                        )
                    ])
                ]),
                
                // Department
                m('.form-control', [
                    m('label.label', m('span.label-text', 'Department')),
                    m('select.select.select-bordered.select-sm', {
                        value: filters.department,
                        onchange: (e) => actions.updateFilter('department', e.target.value),
                        disabled: !filters.industry
                    }, [
                        m('option', { value: '' }, 'All Departments'),
                        actions.getFilteredDepartments().map(dept =>
                            m('option', { value: dept.id }, `${dept.name} (${dept.jobs_count || 0})`)
                        )
                    ])
                ]),
                
                // Job Family
                m('.form-control', [
                    m('label.label', m('span.label-text', 'Job Family')),
                    m('select.select.select-bordered.select-sm', {
                        value: filters.job_family,
                        onchange: (e) => actions.updateFilter('job_family', e.target.value),
                        disabled: !filters.department
                    }, [
                        m('option', { value: '' }, 'All Job Families'),
                        actions.getFilteredJobFamilies().map(family =>
                            m('option', { value: family.id }, `${family.name} (${family.jobs_count || 0})`)
                        )
                    ])
                ]),
                
                // Specialization
                m('.form-control', [
                    m('label.label', m('span.label-text', 'Specialization')),
                    m('select.select.select-bordered.select-sm', {
                        value: filters.specialization,
                        onchange: (e) => actions.updateFilter('specialization', e.target.value),
                        disabled: !filters.job_family
                    }, [
                        m('option', { value: '' }, 'All Specializations'),
                        actions.getFilteredSpecializations().map(spec =>
                            m('option', { value: spec.id }, `${spec.name} (${spec.jobs_count || 0})`)
                        )
                    ])
                ])
            ]),
            
            // Job Details Filters
            m('.space-y-4', [
                m('h3.font-semibold.text-base-content', 'Job Details'),
                
                // Seniority Level
                m('.form-control', [
                    m('label.label', m('span.label-text', 'Seniority Level')),
                    m('select.select.select-bordered.select-sm', {
                        value: filters.seniority_level,
                        onchange: (e) => actions.updateFilter('seniority_level', e.target.value)
                    }, [
                        m('option', { value: '' }, 'All Levels'),
                        (lookups.seniority_levels || []).map(level =>
                            m('option', { value: level.id }, `${level.name} (${level.jobs_count || 0})`)
                        )
                    ])
                ]),
                
                // Employment Type
                m('.form-control', [
                    m('label.label', m('span.label-text', 'Employment Type')),
                    m('select.select.select-bordered.select-sm', {
                        value: filters.employment_type,
                        onchange: (e) => actions.updateFilter('employment_type', e.target.value)
                    }, [
                        m('option', { value: '' }, 'All Types'),
                        (lookups.employment_types || []).map(type =>
                            m('option', { value: type.id }, `${type.name} (${type.jobs_count || 0})`)
                        )
                    ])
                ]),
                
                // Remote Work
                m('.form-control', [
                    m('label.label', m('span.label-text', 'Remote Work')),
                    m('select.select.select-bordered.select-sm', {
                        value: filters.remote_work,
                        onchange: (e) => actions.updateFilter('remote_work', e.target.value)
                    }, [
                        m('option', { value: '' }, 'All Options'),
                        (lookups.remote_work_options || []).map(option =>
                            m('option', { value: option.id }, `${option.name} (${option.jobs_count || 0})`)
                        )
                    ])
                ])
            ]),
            
            // Location Filters
            m('.space-y-4', [
                m('h3.font-semibold.text-base-content', 'Location'),
                
                // City
                m('.form-control', [
                    m('label.label', m('span.label-text', 'City')),
                    m('select.select.select-bordered.select-sm', {
                        value: filters.city,
                        onchange: (e) => actions.updateFilter('city', e.target.value)
                    }, [
                        m('option', { value: '' }, 'All Cities'),
                        (lookups.cities || []).map(city =>
                            m('option', { value: city.id }, `${city.name} (${city.jobs_count || 0})`)
                        )
                    ])
                ])
            ]),
            
            // Salary Filters
            m('.space-y-4', [
                m('h3.font-semibold.text-base-content', 'Salary'),
                
                // Salary Range
                m('.form-control', [
                    m('label.label', m('span.label-text', 'Salary Range (MDL)')),
                    m('.grid.grid-cols-2.gap-2', [
                        m('input.input.input-bordered.input-sm', {
                            type: 'number',
                            placeholder: 'Min',
                            value: filters.salary_min || '',
                            oninput: (e) => actions.updateFilter('salary_min', e.target.value ? parseInt(e.target.value) : null)
                        }),
                        m('input.input.input-bordered.input-sm', {
                            type: 'number',
                            placeholder: 'Max',
                            value: filters.salary_max || '',
                            oninput: (e) => actions.updateFilter('salary_max', e.target.value ? parseInt(e.target.value) : null)
                        })
                    ])
                ]),
                
                // Has Salary checkbox
                m('.form-control', [
                    m('label.label.cursor-pointer', [
                        m('span.label-text', 'Only jobs with salary'),
                        m('input.checkbox.checkbox-sm', {
                            type: 'checkbox',
                            checked: filters.has_salary,
                            onchange: (e) => actions.updateFilter('has_salary', e.target.checked)
                        })
                    ])
                ])
            ]),
            
            // Requirements Filters
            m('.space-y-4', [
                m('h3.font-semibold.text-base-content', 'Requirements'),
                
                // Experience Years
                m('.form-control', [
                    m('label.label', m('span.label-text', 'Experience Years')),
                    m('.grid.grid-cols-2.gap-2', [
                        m('input.input.input-bordered.input-sm', {
                            type: 'number',
                            placeholder: 'Min',
                            value: filters.experience_min || '',
                            oninput: (e) => actions.updateFilter('experience_min', e.target.value ? parseInt(e.target.value) : null)
                        }),
                        m('input.input.input-bordered.input-sm', {
                            type: 'number',
                            placeholder: 'Max',
                            value: filters.experience_max || '',
                            oninput: (e) => actions.updateFilter('experience_max', e.target.value ? parseInt(e.target.value) : null)
                        })
                    ])
                ]),
                
                // Required Education
                m('.form-control', [
                    m('label.label', m('span.label-text', 'Required Education')),
                    m('select.select.select-bordered.select-sm', {
                        value: filters.required_education,
                        onchange: (e) => actions.updateFilter('required_education', e.target.value)
                    }, [
                        m('option', { value: '' }, 'All Levels'),
                        (lookups.required_education || []).map(edu =>
                            m('option', { value: edu.id }, `${edu.name} (${edu.jobs_count || 0})`)
                        )
                    ])
                ])
            ])
        ]);
    }
};
