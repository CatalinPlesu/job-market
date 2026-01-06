// Filter Panel for Filtered Analysis Page (no counts shown)
const FilteredAnalysisFilterPanel = {
    view: () => {
        if (!state.jobsIndex) return m(Loading);
        
        // Define filterable fields
        const filterFields = [
            // Job Details
            { key: 'title', label: 'Job Title', section: 'Job Details' },
            { key: 'seniority_level', label: 'Seniority Level', section: 'Job Details' },
            { key: 'industry', label: 'Industry', section: 'Job Details' },
            { key: 'department', label: 'Department', section: 'Job Details' },
            { key: 'job_family', label: 'Job Family', section: 'Job Details' },
            { key: 'specialization', label: 'Specialization', section: 'Job Details' },
            { key: 'job_function', label: 'Job Function', section: 'Job Details' },
            
            // Requirements
            { key: 'education_level', label: 'Required Education', section: 'Requirements' },
            { key: 'hard_skills', label: 'Hard Skills', section: 'Requirements' },
            { key: 'soft_skills', label: 'Soft Skills', section: 'Requirements' },
            { key: 'certifications', label: 'Certifications', section: 'Requirements' },
            { key: 'licenses_required', label: 'Licenses', section: 'Requirements' },
            
            // Work Arrangement
            { key: 'employment_type', label: 'Employment Type', section: 'Work Arrangement' },
            { key: 'contract_type', label: 'Contract Type', section: 'Work Arrangement' },
            { key: 'work_schedule', label: 'Work Schedule', section: 'Work Arrangement' },
            { key: 'shift_details', label: 'Shift Details', section: 'Work Arrangement' },
            { key: 'remote_work', label: 'Remote Work', section: 'Work Arrangement' },
            { key: 'travel_required', label: 'Travel Required', section: 'Work Arrangement' },
            
            // Location
            { key: 'city', label: 'City', section: 'Location' },
            { key: 'region', label: 'Region', section: 'Location' },
            { key: 'country', label: 'Country', section: 'Location' },
            
            // Company
            { key: 'company', label: 'Company Name', section: 'Company' },
            { key: 'company_size', label: 'Company Size', section: 'Company' },
            
            // Benefits & Culture
            { key: 'benefits', label: 'Benefits', section: 'Benefits & Culture' }
        ];
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body p-4' }, [
                m('div', { class: 'flex justify-between items-center mb-4' }, [
                    m('h3', { class: 'font-bold text-lg' }, 'Filters'),
                    FilteredAnalysisState.getActiveFilterCount() > 0 && m('button', { 
                        class: 'btn btn-xs btn-ghost',
                        onclick: () => {
                            FilteredAnalysisState.clearAllFilters();
                            m.redraw();
                        }
                    }, 'Clear All')
                ]),
                
                m('div', { class: 'alert alert-info mb-4' }, [
                    m('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', class: 'stroke-current shrink-0 w-6 h-6' }, [
                        m('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
                    ]),
                    m('div', { class: 'text-xs' }, [
                        m('div', { class: 'font-bold' }, 'OR Logic'),
                        m('div', 'Jobs matching ANY selected filter will be included in analysis')
                    ])
                ]),
                
                // Grouped filters by section
                m('div', { class: 'space-y-6' },
                    Object.entries(
                        filterFields
                            .filter(field => {
                                // Only show fields that have metadata
                                const metadataKey = getMetadataKey(field.key);
                                return state.jobsIndex.metadata && state.jobsIndex.metadata[metadataKey];
                            })
                            .reduce((acc, field) => {
                                if (!acc[field.section]) acc[field.section] = [];
                                acc[field.section].push(field);
                                return acc;
                            }, {})
                    ).map(([section, fields]) => 
                        m('div', { class: 'space-y-2' }, [
                            m('div', { class: 'text-xs font-semibold opacity-60 uppercase tracking-wide' }, section),
                            ...fields.map(field => {
                                const metadataKey = getMetadataKey(field.key);
                                const options = state.jobsIndex.metadata[metadataKey] || [];
                                
                                // Filter out options with 0 count
                                const availableOptions = options.filter(opt => opt.count > 0);
                                
                                return m('div', { class: 'form-control' }, [
                                    m('label', { class: 'label py-1' }, [
                                        m('span', { class: 'label-text text-sm' }, field.label)
                                    ]),
                                    // Simple dropdown (no counts shown)
                                    m('select', { 
                                        class: 'select select-bordered select-sm w-full',
                                        value: '',
                                        onchange: (e) => {
                                            if (e.target.value) {
                                                FilteredAnalysisState.addFilter(
                                                    field.key, 
                                                    e.target.value,
                                                    field.label
                                                );
                                                e.target.value = ''; // Reset dropdown
                                                m.redraw();
                                            }
                                        }
                                    }, [
                                        m('option', { value: '', disabled: true, selected: true }, 'Select...'),
                                        ...availableOptions.map(item => 
                                            m('option', { value: item.name }, item.name)
                                        )
                                    ])
                                ]);
                            })
                        ])
                    )
                )
            ])
        ]);
    }
};

// Active Filters Display Component
const ActiveFiltersDisplay = {
    view: () => {
        const filters = FilteredAnalysisState.filters;
        const filterCount = FilteredAnalysisState.getActiveFilterCount();
        
        if (filterCount === 0) {
            return m('div', { class: 'alert mb-6' }, [
                m('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', class: 'stroke-info shrink-0 w-6 h-6' }, [
                    m('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
                ]),
                m('span', 'No filters applied. Select filters from the sidebar or run a predefined analysis.')
            ]);
        }
        
        return m('div', { class: 'card bg-base-100 shadow-xl mb-6' }, [
            m('div', { class: 'card-body p-4' }, [
                m('div', { class: 'flex justify-between items-center mb-3' }, [
                    m('h3', { class: 'font-bold' }, 'Active Filters'),
                    m('span', { class: 'badge badge-info' }, `${filterCount} filter${filterCount !== 1 ? 's' : ''}`)
                ]),
                m('div', { class: 'space-y-2' },
                    Object.entries(filters).map(([field, filterValues]) =>
                        m('div', { class: 'space-y-1' },
                            filterValues.map(filter =>
                                m('div', { 
                                    class: 'badge badge-lg badge-outline gap-2 cursor-pointer hover:badge-error',
                                    onclick: () => {
                                        FilteredAnalysisState.removeFilter(field, filter.value);
                                        m.redraw();
                                    },
                                    title: 'Click to remove'
                                }, [
                                    m('span', { class: 'font-mono text-xs' }, `${filter.label} == "${filter.value}"`),
                                    m('svg', { 
                                        xmlns: 'http://www.w3.org/2000/svg', 
                                        fill: 'none', 
                                        viewBox: '0 0 24 24', 
                                        class: 'inline-block w-4 h-4 stroke-current'
                                    }, [
                                        m('path', { 
                                            'stroke-linecap': 'round', 
                                            'stroke-linejoin': 'round', 
                                            'stroke-width': '2', 
                                            d: 'M6 18L18 6M6 6l12 12'
                                        })
                                    ])
                                ])
                            )
                        )
                    )
                ),
                m('button', { 
                    class: 'btn btn-sm btn-primary mt-4',
                    onclick: () => FilteredAnalysisState.executeQuery()
                }, 'Run Analysis with Filters')
            ])
        ]);
    }
};
