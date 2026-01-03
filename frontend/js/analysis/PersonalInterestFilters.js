// Personal Interest Filter Panel for Analysis Page
// Allows users to filter analyses based on their career interests
const PersonalInterestFilters = {
    state: {
        pendingFilters: {},  // Filters being selected (not yet applied)
        appliedFilters: {},  // Filters actually applied to analyses
        showFilters: true,
        filterCounts: {} // Store dynamic filter counts
    },
    
    // Async function to get counts for a specific field
    async getCountsForField(fieldKey) {
        try {
            // Use pending filters for count computation (preview)
            const counts = await dbApi.getFilteredCounts(fieldKey, PersonalInterestFilters.state.pendingFilters);
            PersonalInterestFilters.state.filterCounts[fieldKey] = counts;
            m.redraw();
        } catch (error) {
            console.error(`Error getting counts for ${fieldKey}:`, error);
            PersonalInterestFilters.state.filterCounts[fieldKey] = [];
        }
    },
    
    handleFilterChange: async (fieldKey, value) => {
        // Update pending filters (not applied yet)
        if (value) {
            PersonalInterestFilters.state.pendingFilters[fieldKey] = value;
        } else {
            delete PersonalInterestFilters.state.pendingFilters[fieldKey];
        }
        
        // Recompute counts for all filters based on pending selections
        const filterFields = ['industry', 'job_function', 'seniority_level', 'department', 'remote_work', 'city'];
        for (const field of filterFields) {
            await PersonalInterestFilters.getCountsForField(field);
        }
        
        m.redraw();
    },
    
    applyFilters: () => {
        // Apply pending filters to analyses
        PersonalInterestFilters.state.appliedFilters = { ...PersonalInterestFilters.state.pendingFilters };
        CustomAnalysisState.jobPageFilters = { ...PersonalInterestFilters.state.pendingFilters };
        m.redraw();
    },
    
    clearAllFilters: async () => {
        PersonalInterestFilters.state.pendingFilters = {};
        PersonalInterestFilters.state.appliedFilters = {};
        CustomAnalysisState.jobPageFilters = null;
        
        // Recompute counts for all filters
        const filterFields = ['industry', 'job_function', 'seniority_level', 'department', 'remote_work', 'city'];
        for (const field of filterFields) {
            await PersonalInterestFilters.getCountsForField(field);
        }
        
        m.redraw();
    },
    
    view: () => {
        // Define filter fields with their metadata keys
        const filterFields = [
            { key: 'industry', label: 'Industry', metadataKey: 'industry' },
            { key: 'job_function', label: 'Job Function', metadataKey: 'job_function' },
            { key: 'seniority_level', label: 'Seniority Level', metadataKey: 'seniority_level' },
            { key: 'department', label: 'Department', metadataKey: 'department' },
            { key: 'remote_work', label: 'Remote Work', metadataKey: 'remote_work' },
            { key: 'city', label: 'City', metadataKey: 'location' }
        ];
        
        const hasPendingChanges = JSON.stringify(PersonalInterestFilters.state.pendingFilters) !== 
                                   JSON.stringify(PersonalInterestFilters.state.appliedFilters);
        
        return m('div', { class: 'card bg-base-200 mb-6' }, [
            m('div', { class: 'card-body p-4' }, [
                m('div', { class: 'flex justify-between items-center mb-3' }, [
                    m('h3', { class: 'font-bold text-lg' }, '🎯 Your Career Interests'),
                    m('button', {
                        class: 'btn btn-xs btn-ghost',
                        onclick: () => {
                            PersonalInterestFilters.state.showFilters = !PersonalInterestFilters.state.showFilters;
                        }
                    }, PersonalInterestFilters.state.showFilters ? 'Hide Filters' : 'Show Filters')
                ]),
                
                m('div', { class: 'text-sm opacity-70 mb-3' }, 
                    'Select your interests, then click "Apply Filters" to see personalized insights'
                ),
                
                PersonalInterestFilters.state.showFilters && m('div', { class: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3' }, 
                    filterFields.map(field => {
                        // Get options from filterCounts if available, otherwise from initial metadata
                        let options = [];
                        
                        if (PersonalInterestFilters.state.filterCounts[field.key]) {
                            // Use dynamic counts
                            options = PersonalInterestFilters.state.filterCounts[field.key];
                        } else if (state.jobsIndex?.metadata?.[field.metadataKey]) {
                            // Use initial metadata
                            options = state.jobsIndex.metadata[field.metadataKey];
                            // Trigger loading of dynamic counts
                            PersonalInterestFilters.getCountsForField(field.key);
                        }
                        
                        // Filter out options with 0 count
                        const availableOptions = options.filter(opt => opt.count > 0);
                        
                        return m('div', { class: 'form-control' }, [
                            m('label', { class: 'label' }, 
                                m('span', { class: 'label-text text-xs font-semibold' }, field.label)
                            ),
                            m('select', {
                                class: 'select select-bordered select-sm',
                                value: PersonalInterestFilters.state.pendingFilters[field.key] || '',
                                onchange: (e) => {
                                    PersonalInterestFilters.handleFilterChange(field.key, e.target.value || null);
                                }
                            }, [
                                m('option', { value: '' }, `All ${field.label}s`),
                                ...availableOptions.map(item =>
                                    m('option', { value: item.name }, `${item.name} (${item.count})`)
                                )
                            ])
                        ]);
                    })
                ),
                
                // Apply and Clear buttons
                PersonalInterestFilters.state.showFilters && m('div', { class: 'mt-4 flex gap-2' }, [
                    m('button', {
                        class: `btn btn-sm btn-primary ${!hasPendingChanges ? 'btn-disabled' : ''}`,
                        disabled: !hasPendingChanges,
                        onclick: () => {
                            PersonalInterestFilters.applyFilters();
                        }
                    }, [
                        m('svg', { xmlns: 'http://www.w3.org/2000/svg', class: 'h-4 w-4 mr-1', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
                            m('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M5 13l4 4L19 7' })
                        ]),
                        'Apply Filters'
                    ]),
                    Object.keys(PersonalInterestFilters.state.pendingFilters).length > 0 && m('button', {
                        class: 'btn btn-sm btn-ghost',
                        onclick: () => {
                            PersonalInterestFilters.clearAllFilters();
                        }
                    }, 'Clear All')
                ]),
                
                // Applied filters display
                Object.keys(PersonalInterestFilters.state.appliedFilters).length > 0 && m('div', { class: 'mt-4 pt-4 border-t border-base-300' }, [
                    m('div', { class: 'flex flex-wrap gap-2 items-center' }, [
                        m('span', { class: 'text-xs font-semibold' }, 'Applied Filters:'),
                        ...Object.entries(PersonalInterestFilters.state.appliedFilters).map(([key, value]) =>
                            m('div', { class: 'badge badge-primary gap-2' }, [
                                m('span', value),
                                m('button', {
                                    class: 'btn btn-ghost btn-xs p-0 h-auto min-h-0',
                                    onclick: () => {
                                        // Remove from both pending and applied
                                        delete PersonalInterestFilters.state.pendingFilters[key];
                                        delete PersonalInterestFilters.state.appliedFilters[key];
                                        CustomAnalysisState.jobPageFilters = { ...PersonalInterestFilters.state.appliedFilters };
                                        
                                        // Recompute counts
                                        const filterFields = ['industry', 'job_function', 'seniority_level', 'department', 'remote_work', 'city'];
                                        filterFields.forEach(field => PersonalInterestFilters.getCountsForField(field));
                                        
                                        m.redraw();
                                    }
                                }, '×')
                            ])
                        )
                    ])
                ])
            ])
        ]);
    }
};
