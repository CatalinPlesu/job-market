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
            
            // Inject job page filters if present
            let finalSQL = sql;
            let params = [];
            
            if (CustomAnalysisState.jobPageFilters && Object.keys(CustomAnalysisState.jobPageFilters).length > 0) {
                // Build WHERE clause from job page filters
                const { whereClause, params: filterParams } = dbApi.buildWhereClause(
                    CustomAnalysisState.jobPageFilters, 
                    ''
                );
                
                if (whereClause) {
                    // Inject the filter WHERE clause into the query
                    // Extract the WHERE keyword and conditions safely
                    const whereMatch = whereClause.match(/^WHERE\s+(.+)$/i);
                    const conditions = whereMatch ? whereMatch[1] : whereClause;
                    
                    // If query already has WHERE, combine with AND
                    // If not, add WHERE before GROUP BY, ORDER BY, or LIMIT
                    if (finalSQL.toLowerCase().includes('where')) {
                        // Find the WHERE clause and add our filters
                        finalSQL = finalSQL.replace(/WHERE/i, `WHERE ${conditions} AND `);
                    } else {
                        // Insert WHERE clause before GROUP BY, ORDER BY, or LIMIT
                        const insertPosition = finalSQL.search(/GROUP BY|ORDER BY|LIMIT/i);
                        if (insertPosition > 0) {
                            finalSQL = finalSQL.slice(0, insertPosition) + 
                                      `WHERE ${conditions}\n` + 
                                      finalSQL.slice(insertPosition);
                        } else {
                            // Add at the end if no GROUP BY, ORDER BY, or LIMIT found
                            finalSQL = finalSQL.trim() + `\nWHERE ${conditions}`;
                        }
                    }
                    params = filterParams;
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

