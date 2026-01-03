// Interactive Analysis Filters Component
// Creates dynamic UI controls for predefined analyses
const AnalysisFilters = {
    state: {
        activeFilters: {},
        availableFilters: []
    },
    
    // Detect filterable parameters in SQL query
    detectFilterParameters: (sql) => {
        const filters = [];
        
        // Look for common filter patterns in SQL
        if (sql.includes('posting_date')) {
            filters.push({
                name: 'timeRange',
                label: 'Time Range',
                type: 'select',
                options: [
                    { value: 7, label: 'Last 7 days' },
                    { value: 30, label: 'Last 30 days' },
                    { value: 90, label: 'Last 90 days' },
                    { value: 180, label: 'Last 6 months' },
                    { value: 365, label: 'Last year' },
                    { value: null, label: 'All time' }
                ]
            });
        }
        
        if (sql.includes('min_salary') || sql.includes('max_salary')) {
            filters.push({
                name: 'minSalary',
                label: 'Minimum Salary',
                type: 'number',
                min: 0,
                step: 1000
            });
        }
        
        if (sql.includes('LIMIT')) {
            filters.push({
                name: 'limit',
                label: 'Result Limit',
                type: 'select',
                options: [
                    { value: 10, label: 'Top 10' },
                    { value: 20, label: 'Top 20' },
                    { value: 30, label: 'Top 30' },
                    { value: 50, label: 'Top 50' }
                ]
            });
        }
        
        if (sql.includes('seniority_level')) {
            filters.push({
                name: 'seniorityLevel',
                label: 'Seniority Level',
                type: 'select',
                options: [
                    { value: null, label: 'All levels' },
                    { value: 'entry', label: 'Entry' },
                    { value: 'junior', label: 'Junior' },
                    { value: 'mid', label: 'Mid' },
                    { value: 'senior', label: 'Senior' },
                    { value: 'lead', label: 'Lead' },
                    { value: 'manager', label: 'Manager' }
                ]
            });
        }
        
        if (sql.includes('remote_work')) {
            filters.push({
                name: 'remoteWork',
                label: 'Remote Work',
                type: 'select',
                options: [
                    { value: null, label: 'All options' },
                    { value: 'remote', label: 'Remote' },
                    { value: 'hybrid', label: 'Hybrid' },
                    { value: 'on-site', label: 'On-site' }
                ]
            });
        }
        
        return filters;
    },
    
    // Apply filters to SQL query
    applyFilters: (sql, filters) => {
        let modifiedSQL = sql;
        
        // Apply time range filter
        if (filters.timeRange !== undefined && filters.timeRange !== null) {
            const daysAgo = filters.timeRange;
            const timeCondition = `posting_date >= date('now', '-${daysAgo} days')`;
            
            if (modifiedSQL.toLowerCase().includes('where')) {
                modifiedSQL = modifiedSQL.replace(
                    /WHERE/i,
                    `WHERE ${timeCondition} AND`
                );
            } else {
                // Add WHERE before GROUP BY or ORDER BY
                const insertPosition = modifiedSQL.search(/GROUP BY|ORDER BY|LIMIT/i);
                if (insertPosition > 0) {
                    modifiedSQL = modifiedSQL.slice(0, insertPosition) + 
                                  `WHERE ${timeCondition}\n` + 
                                  modifiedSQL.slice(insertPosition);
                }
            }
        }
        
        // Apply salary filter
        if (filters.minSalary !== undefined && filters.minSalary !== null) {
            const salaryCondition = `min_salary >= ${filters.minSalary}`;
            
            if (modifiedSQL.toLowerCase().includes('where')) {
                modifiedSQL = modifiedSQL.replace(
                    /WHERE/i,
                    `WHERE ${salaryCondition} AND`
                );
            } else {
                const insertPosition = modifiedSQL.search(/GROUP BY|ORDER BY|LIMIT/i);
                if (insertPosition > 0) {
                    modifiedSQL = modifiedSQL.slice(0, insertPosition) + 
                                  `WHERE ${salaryCondition}\n` + 
                                  modifiedSQL.slice(insertPosition);
                }
            }
        }
        
        // Apply result limit filter
        if (filters.limit !== undefined && filters.limit !== null) {
            modifiedSQL = modifiedSQL.replace(/LIMIT\s+\d+/i, `LIMIT ${filters.limit}`);
        }
        
        // Apply seniority level filter
        if (filters.seniorityLevel !== undefined && filters.seniorityLevel !== null) {
            const seniorityCondition = `sl.name = '${filters.seniorityLevel}'`;
            
            if (modifiedSQL.toLowerCase().includes('where')) {
                modifiedSQL = modifiedSQL.replace(
                    /WHERE/i,
                    `WHERE ${seniorityCondition} AND`
                );
            }
        }
        
        // Apply remote work filter
        if (filters.remoteWork !== undefined && filters.remoteWork !== null) {
            const remoteCondition = `rw.name = '${filters.remoteWork}'`;
            
            if (modifiedSQL.toLowerCase().includes('where')) {
                modifiedSQL = modifiedSQL.replace(
                    /WHERE/i,
                    `WHERE ${remoteCondition} AND`
                );
            }
        }
        
        return modifiedSQL;
    },
    
    view: (vnode) => {
        const { sql, onFilterChange } = vnode.attrs;
        
        if (!sql) return null;
        
        // Detect available filters for this query
        const filters = AnalysisFilters.detectFilterParameters(sql);
        
        if (filters.length === 0) return null;
        
        return m('div', { class: 'card bg-base-200 mb-4' }, [
            m('div', { class: 'card-body p-4' }, [
                m('h4', { class: 'font-semibold mb-3' }, '🎛️ Interactive Filters'),
                m('div', { class: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3' }, 
                    filters.map(filter => 
                        m('div', { class: 'form-control' }, [
                            m('label', { class: 'label' }, 
                                m('span', { class: 'label-text text-sm' }, filter.label)
                            ),
                            filter.type === 'select' ? 
                                m('select', {
                                    class: 'select select-bordered select-sm',
                                    value: AnalysisFilters.state.activeFilters[filter.name] || '',
                                    onchange: (e) => {
                                        const value = e.target.value === '' ? null : 
                                                      (filter.options.find(o => o.value == e.target.value)?.value);
                                        AnalysisFilters.state.activeFilters[filter.name] = value;
                                        
                                        // Apply filters to SQL
                                        const modifiedSQL = AnalysisFilters.applyFilters(
                                            sql, 
                                            AnalysisFilters.state.activeFilters
                                        );
                                        
                                        if (onFilterChange) {
                                            onFilterChange(modifiedSQL, AnalysisFilters.state.activeFilters);
                                        }
                                    }
                                }, 
                                    filter.options.map(opt => 
                                        m('option', { value: opt.value || '' }, opt.label)
                                    )
                                )
                            : m('input', {
                                type: filter.type,
                                class: 'input input-bordered input-sm',
                                min: filter.min,
                                step: filter.step,
                                value: AnalysisFilters.state.activeFilters[filter.name] || '',
                                oninput: (e) => {
                                    const value = e.target.value ? Number(e.target.value) : null;
                                    AnalysisFilters.state.activeFilters[filter.name] = value;
                                    
                                    // Apply filters to SQL
                                    const modifiedSQL = AnalysisFilters.applyFilters(
                                        sql, 
                                        AnalysisFilters.state.activeFilters
                                    );
                                    
                                    if (onFilterChange) {
                                        onFilterChange(modifiedSQL, AnalysisFilters.state.activeFilters);
                                    }
                                }
                            })
                        ])
                    )
                ),
                
                // Reset button
                Object.keys(AnalysisFilters.state.activeFilters).length > 0 && 
                    m('div', { class: 'mt-3' }, [
                        m('button', {
                            class: 'btn btn-xs btn-ghost',
                            onclick: () => {
                                AnalysisFilters.state.activeFilters = {};
                                if (onFilterChange) {
                                    onFilterChange(sql, {});
                                }
                            }
                        }, 'Reset Filters')
                    ])
            ])
        ]);
    }
};
