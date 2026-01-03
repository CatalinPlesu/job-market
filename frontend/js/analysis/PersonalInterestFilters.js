// Personal Interest Filter Panel for Analysis Page
// Allows users to filter analyses based on their career interests
const PersonalInterestFilters = {
    state: {
        activeFilters: {},
        showFilters: true
    },
    
    view: () => {
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
                
                PersonalInterestFilters.state.showFilters && m('div', { class: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3' }, [
                    // Industry filter
                    m('div', { class: 'form-control' }, [
                        m('label', { class: 'label' }, m('span', { class: 'label-text text-xs font-semibold' }, 'Industry')),
                        m('select', {
                            class: 'select select-bordered select-sm',
                            value: PersonalInterestFilters.state.activeFilters.industry || '',
                            onchange: async (e) => {
                                if (e.target.value) {
                                    PersonalInterestFilters.state.activeFilters.industry = e.target.value;
                                } else {
                                    delete PersonalInterestFilters.state.activeFilters.industry;
                                }
                                CustomAnalysisState.jobPageFilters = { ...PersonalInterestFilters.state.activeFilters };
                                m.redraw();
                            }
                        }, [
                            m('option', { value: '' }, 'All Industries'),
                            ...(state.jobsIndex?.metadata?.industry || []).map(item =>
                                m('option', { value: item.name }, `${item.name} (${item.count})`)
                            )
                        ])
                    ]),
                    
                    // Job Function filter
                    m('div', { class: 'form-control' }, [
                        m('label', { class: 'label' }, m('span', { class: 'label-text text-xs font-semibold' }, 'Job Function')),
                        m('select', {
                            class: 'select select-bordered select-sm',
                            value: PersonalInterestFilters.state.activeFilters.job_function || '',
                            onchange: async (e) => {
                                if (e.target.value) {
                                    PersonalInterestFilters.state.activeFilters.job_function = e.target.value;
                                } else {
                                    delete PersonalInterestFilters.state.activeFilters.job_function;
                                }
                                CustomAnalysisState.jobPageFilters = { ...PersonalInterestFilters.state.activeFilters };
                                m.redraw();
                            }
                        }, [
                            m('option', { value: '' }, 'All Functions'),
                            ...(state.jobsIndex?.metadata?.job_function || []).map(item =>
                                m('option', { value: item.name }, `${item.name} (${item.count})`)
                            )
                        ])
                    ]),
                    
                    // Seniority Level filter
                    m('div', { class: 'form-control' }, [
                        m('label', { class: 'label' }, m('span', { class: 'label-text text-xs font-semibold' }, 'Seniority Level')),
                        m('select', {
                            class: 'select select-bordered select-sm',
                            value: PersonalInterestFilters.state.activeFilters.seniority_level || '',
                            onchange: async (e) => {
                                if (e.target.value) {
                                    PersonalInterestFilters.state.activeFilters.seniority_level = e.target.value;
                                } else {
                                    delete PersonalInterestFilters.state.activeFilters.seniority_level;
                                }
                                CustomAnalysisState.jobPageFilters = { ...PersonalInterestFilters.state.activeFilters };
                                m.redraw();
                            }
                        }, [
                            m('option', { value: '' }, 'All Levels'),
                            ...(state.jobsIndex?.metadata?.seniority_level || []).map(item =>
                                m('option', { value: item.name }, `${item.name} (${item.count})`)
                            )
                        ])
                    ]),
                    
                    // Department filter
                    m('div', { class: 'form-control' }, [
                        m('label', { class: 'label' }, m('span', { class: 'label-text text-xs font-semibold' }, 'Department')),
                        m('select', {
                            class: 'select select-bordered select-sm',
                            value: PersonalInterestFilters.state.activeFilters.department || '',
                            onchange: async (e) => {
                                if (e.target.value) {
                                    PersonalInterestFilters.state.activeFilters.department = e.target.value;
                                } else {
                                    delete PersonalInterestFilters.state.activeFilters.department;
                                }
                                CustomAnalysisState.jobPageFilters = { ...PersonalInterestFilters.state.activeFilters };
                                m.redraw();
                            }
                        }, [
                            m('option', { value: '' }, 'All Departments'),
                            ...(state.jobsIndex?.metadata?.department || []).map(item =>
                                m('option', { value: item.name }, `${item.name} (${item.count})`)
                            )
                        ])
                    ]),
                    
                    // Remote Work filter
                    m('div', { class: 'form-control' }, [
                        m('label', { class: 'label' }, m('span', { class: 'label-text text-xs font-semibold' }, 'Remote Work')),
                        m('select', {
                            class: 'select select-bordered select-sm',
                            value: PersonalInterestFilters.state.activeFilters.remote_work || '',
                            onchange: async (e) => {
                                if (e.target.value) {
                                    PersonalInterestFilters.state.activeFilters.remote_work = e.target.value;
                                } else {
                                    delete PersonalInterestFilters.state.activeFilters.remote_work;
                                }
                                CustomAnalysisState.jobPageFilters = { ...PersonalInterestFilters.state.activeFilters };
                                m.redraw();
                            }
                        }, [
                            m('option', { value: '' }, 'All Options'),
                            ...(state.jobsIndex?.metadata?.remote_work || []).map(item =>
                                m('option', { value: item.name }, `${item.name} (${item.count})`)
                            )
                        ])
                    ]),
                    
                    // City filter
                    m('div', { class: 'form-control' }, [
                        m('label', { class: 'label' }, m('span', { class: 'label-text text-xs font-semibold' }, 'City')),
                        m('select', {
                            class: 'select select-bordered select-sm',
                            value: PersonalInterestFilters.state.activeFilters.city || '',
                            onchange: async (e) => {
                                if (e.target.value) {
                                    PersonalInterestFilters.state.activeFilters.city = e.target.value;
                                } else {
                                    delete PersonalInterestFilters.state.activeFilters.city;
                                }
                                CustomAnalysisState.jobPageFilters = { ...PersonalInterestFilters.state.activeFilters };
                                m.redraw();
                            }
                        }, [
                            m('option', { value: '' }, 'All Cities'),
                            ...(state.jobsIndex?.metadata?.location || []).slice(0, 20).map(item =>
                                m('option', { value: item.name }, `${item.name} (${item.count})`)
                            )
                        ])
                    ])
                ]),
                
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
                                        delete PersonalInterestFilters.state.activeFilters[key];
                                        CustomAnalysisState.jobPageFilters = { ...PersonalInterestFilters.state.activeFilters };
                                        m.redraw();
                                    }
                                }, '×')
                            ])
                        ),
                        m('button', {
                            class: 'btn btn-xs btn-ghost',
                            onclick: () => {
                                PersonalInterestFilters.state.activeFilters = {};
                                CustomAnalysisState.jobPageFilters = null;
                                m.redraw();
                            }
                        }, 'Clear All')
                    ])
                ])
            ])
        ]);
    }
};
