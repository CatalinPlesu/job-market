const CustomAnalysisState = {
    savedQueries: [],
    currentQuery: {
        name: '',
        description: '',
        sql: '',
        chartType: 'bar',
        chartConfig: null,  // Custom chart configuration
        dataAdapter: null,  // JS function to transform data
        labelColumn: null,  // Column to use for labels (auto-detect if null)
        valueColumns: []    // Columns to use for values (auto-detect if empty)
    },
    queryResult: null,
    chartInstance: null,
    showHelp: false,
    showStatistics: true,  // Enable statistical computations
    selectedAnalysisName: null,  // Track selected analysis for visual highlighting
    jobPageFilters: null,  // Filters passed from jobs page
    
    // Load saved queries from localStorage
    loadSavedQueries: () => {
        try {
            const saved = localStorage.getItem('customAnalysisQueries');
            if (saved) {
                CustomAnalysisState.savedQueries = JSON.parse(saved);
            }
        } catch (e) {
            console.error('Failed to load saved queries:', e);
        }
    },
    
    // Save queries to localStorage
    saveQueries: () => {
        try {
            localStorage.setItem('customAnalysisQueries', JSON.stringify(CustomAnalysisState.savedQueries));
        } catch (e) {
            console.error('Failed to save queries:', e);
        }
    },
    
    // Add new query
    addQuery: (query) => {
        CustomAnalysisState.savedQueries.push({
            ...query,
            id: Date.now(),
            createdAt: new Date().toISOString()
        });
        CustomAnalysisState.saveQueries();
    },
    
    // Delete query
    deleteQuery: (id) => {
        CustomAnalysisState.savedQueries = CustomAnalysisState.savedQueries.filter(q => q.id !== id);
        CustomAnalysisState.saveQueries();
    },
    
    // Execute query
    executeQuery: async (sql) => {
        try {
            await DatabaseManager.init();
            
            // Inject job page filters if present AND if current query allows it
            let finalSQL = sql;
            let params = [];
            
            const shouldApplyFilters = CustomAnalysisState.currentQuery.applyFilters !== false;
            
            if (shouldApplyFilters && CustomAnalysisState.jobPageFilters && Object.keys(CustomAnalysisState.jobPageFilters).length > 0) {
                // Build filter conditions and determine needed JOINs
                const filterConditions = [];
                const neededJoins = new Set();
                
                // Map filters to their table info
                const filterTableMap = {
                    'industry': { table: 'industries', alias: 'ind_filter', fk: 'industry_id', condition: 'ind_filter.name = ?' },
                    'job_function': { table: 'job_functions', alias: 'jf_filter', fk: 'job_function_id', condition: 'jf_filter.name = ?' },
                    'seniority_level': { table: 'seniority_levels', alias: 'sl_filter', fk: 'seniority_level_id', condition: 'sl_filter.name = ?' },
                    'department': { table: 'departments', alias: 'dept_filter', fk: 'department_id', condition: 'dept_filter.name = ?' },
                    'remote_work': { table: 'remote_work_options', alias: 'rw_filter', fk: 'remote_work_id', condition: 'rw_filter.name = ?' },
                    'city': { table: 'cities', alias: 'city_filter', fk: 'city_id', condition: 'city_filter.name = ?' },
                    'company': { table: 'companies', alias: 'comp_filter', fk: 'company_name_id', condition: 'comp_filter.name = ?' },
                    'employment_type': { table: 'employment_types', alias: 'et_filter', fk: 'employment_type_id', condition: 'et_filter.name = ?' }
                };
                
                // Build conditions and track needed joins
                for (const [filterKey, filterValue] of Object.entries(CustomAnalysisState.jobPageFilters)) {
                    if (filterTableMap[filterKey]) {
                        const tableInfo = filterTableMap[filterKey];
                        filterConditions.push(tableInfo.condition);
                        params.push(filterValue);
                        neededJoins.add(tableInfo);
                    }
                }
                
                if (filterConditions.length > 0) {
                    // Find the main job_details reference in the SQL
                    // Look for patterns like "FROM job_details" or "FROM job_details jd" or "FROM job_details AS jd"
                    const jdAliasMatch = sql.match(/(?:FROM|JOIN)\s+job_details(?:\s+(?:AS\s+)?(\w+))?/i);
                    let jdAlias = 'job_details'; // Default to full table name
                    
                    if (jdAliasMatch && jdAliasMatch[1]) {
                        // An alias was found
                        jdAlias = jdAliasMatch[1];
                    }
                    
                    // Build JOIN statements for needed tables
                    const joinStatements = [];
                    for (const joinInfo of neededJoins) {
                        joinStatements.push(
                            `LEFT JOIN ${joinInfo.table} ${joinInfo.alias} ON ${jdAlias}.${joinInfo.fk} = ${joinInfo.alias}.id`
                        );
                    }
                    
                    // Combine filter conditions
                    const combinedConditions = filterConditions.join(' AND ');
                    
                    // Insert JOINs after the job_details table reference
                    if (joinStatements.length > 0) {
                        // Find position to insert JOINs (after job_details FROM/JOIN with or without alias)
                        const fromMatch = sql.match(/(FROM\s+job_details(?:\s+(?:AS\s+)?\w+)?)/i);
                        if (fromMatch) {
                            const insertPos = fromMatch.index + fromMatch[0].length;
                            finalSQL = sql.slice(0, insertPos) + '\n' + joinStatements.join('\n') + '\n' + sql.slice(insertPos);
                        } else {
                            // Fallback: If we can't find the position, log error but continue
                            console.error('Could not find position to insert JOINs in SQL:', sql);
                        }
                    }
                    
                    // Inject WHERE conditions
                    finalSQL = SQLUtils.injectWhereConditions(finalSQL, combinedConditions);
                    
                    // Debug logging
                    console.log('Filter Debug Info:');
                    console.log('- Active Filters:', CustomAnalysisState.jobPageFilters);
                    console.log('- Filter Conditions:', combinedConditions);
                    console.log('- Parameters:', params);
                    console.log('- JD Alias detected:', jdAlias);
                    console.log('- Joins added:', joinStatements);
                    console.log('- Final SQL:', finalSQL);
                }
            }
            
            let results = DatabaseManager.queryObjects(finalSQL, params);
            
            // Apply data adapter if provided
            if (CustomAnalysisState.currentQuery.dataAdapter) {
                try {
                    const adapterFn = new Function('data', CustomAnalysisState.currentQuery.dataAdapter);
                    results = adapterFn(results);
                } catch (e) {
                    console.error('Data adapter error:', e);
                }
            }
            
            // Calculate statistics for numeric columns
            const statistics = CustomAnalysisState.showStatistics ? CustomAnalysisState.calculateStatistics(results) : null;
            
            CustomAnalysisState.queryResult = {
                success: true,
                data: results,
                rowCount: results.length,
                statistics: statistics
            };
        } catch (error) {
            CustomAnalysisState.queryResult = {
                success: false,
                error: error.message || 'Query execution failed'
            };
        }
        m.redraw();
    },
    
    // Calculate statistics for numeric columns
    calculateStatistics: (data) => {
        if (!data || data.length === 0) return null;
        
        const stats = {};
        const firstRow = data[0];
        
        // Find numeric columns
        Object.keys(firstRow).forEach(key => {
            const values = data.map(row => row[key]).filter(v => typeof v === 'number' && !isNaN(v));
            
            if (values.length > 0) {
                const sorted = [...values].sort((a, b) => a - b);
                const sum = values.reduce((a, b) => a + b, 0);
                const mean = sum / values.length;
                
                // Median
                const mid = Math.floor(sorted.length / 2);
                const median = sorted.length % 2 === 0 
                    ? (sorted[mid - 1] + sorted[mid]) / 2 
                    : sorted[mid];
                
                // Mode (most frequent value)
                const frequency = {};
                let maxFreq = 0;
                let mode = null;
                values.forEach(v => {
                    frequency[v] = (frequency[v] || 0) + 1;
                    if (frequency[v] > maxFreq) {
                        maxFreq = frequency[v];
                        mode = v;
                    }
                });
                
                // Standard deviation
                const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length;
                const stdDev = Math.sqrt(variance);
                
                // Percentiles
                const percentile = (p) => {
                    const index = (p / 100) * (sorted.length - 1);
                    const lower = Math.floor(index);
                    const upper = Math.ceil(index);
                    const weight = index - lower;
                    return sorted[lower] * (1 - weight) + sorted[upper] * weight;
                };
                
                stats[key] = {
                    count: values.length,
                    min: sorted[0],
                    max: sorted[sorted.length - 1],
                    mean: mean,
                    median: median,
                    mode: mode,
                    stdDev: stdDev,
                    p25: percentile(25),
                    p50: median,
                    p75: percentile(75),
                    p90: percentile(90),
                    p95: percentile(95),
                    p99: percentile(99)
                };
            }
        });
        
        return Object.keys(stats).length > 0 ? stats : null;
    }
};

