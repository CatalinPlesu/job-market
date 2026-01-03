// Personal Interest Filter Panel for Analysis Page
// Allows users to filter analyses based on their career interests
const PersonalInterestFilters = {
    state: {
        activeFilters: {},
        showFilters: true,
        filterCounts: {} // Store dynamic filter counts
    },
    
    // Async function to get counts for a specific field
    async getCountsForField(fieldKey) {
        try {
            const counts = await dbApi.getFilteredCounts(fieldKey, PersonalInterestFilters.state.activeFilters);
            PersonalInterestFilters.state.filterCounts[fieldKey] = counts;
            m.redraw();
        } catch (error) {
            console.error(`Error getting counts for ${fieldKey}:`, error);
            PersonalInterestFilters.state.filterCounts[fieldKey] = [];
        }
    },
    
    handleFilterChange: async (fieldKey, value) => {
        // Update active filters
        if (value) {
            PersonalInterestFilters.state.activeFilters[fieldKey] = value;
        } else {
            delete PersonalInterestFilters.state.activeFilters[fieldKey];
        }
        
        // Update CustomAnalysisState
        CustomAnalysisState.jobPageFilters = { ...PersonalInterestFilters.state.activeFilters };
        
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
                    'Select your interests to see personalized job market insights'
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
                                value: PersonalInterestFilters.state.activeFilters[field.key] || '',
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
                
                // Active filters display and actions
                Object.keys(PersonalInterestFilters.state.activeFilters).length > 0 && m('div', { class: 'mt-4 pt-4 border-t border-base-300' }, [
                    m('div', { class: 'flex flex-wrap gap-2 items-center' }, [
                        m('span', { class: 'text-xs font-semibold' }, 'Active Filters:'),
                        ...Object.entries(PersonalInterestFilters.state.activeFilters).map(([key, value]) =>
                            m('div', { class: 'badge badge-primary gap-2' }, [
                                m('span', value),
                                m('button', {
                                    class: 'btn btn-ghost btn-xs p-0 h-auto min-h-0',
                                    onclick: () => {
                                        PersonalInterestFilters.handleFilterChange(key, null);
                                    }
                                }, '×')
                            ])
                        ),
                        m('button', {
                            class: 'btn btn-xs btn-ghost',
                            onclick: async () => {
                                PersonalInterestFilters.state.activeFilters = {};
                                CustomAnalysisState.jobPageFilters = null;
                                
                                // Recompute counts for all filters
                                const filterFields = ['industry', 'job_function', 'seniority_level', 'department', 'remote_work', 'city'];
                                for (const field of filterFields) {
                                    await PersonalInterestFilters.getCountsForField(field);
                                }
                                
                                m.redraw();
                            }
                        }, 'Clear All')
                    ])
                ])
            ])
        ]);
    }
};
