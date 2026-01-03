// Code Viewer Component - Shows the JS code that executes queries and creates charts
const CodeViewer = {
    state: {
        showCode: false,
        activeTab: 'query' // 'query', 'data', 'chart'
    },
    
    generateQueryCode: (sql, filters) => {
        const filtersCode = filters && Object.keys(filters).length > 0 
            ? `// Applied filters from jobs page:
const filters = ${JSON.stringify(filters, null, 2)};

// Build WHERE clause from filters
const { whereClause, params } = dbApi.buildWhereClause(filters, '');

// Extract conditions from WHERE clause safely
const whereMatch = whereClause.match(/^WHERE\\s+(.+)$/i);
const conditions = whereMatch ? whereMatch[1] : whereClause;

// Inject filters into base query
const enhancedSQL = \`
${sql}
\${conditions ? (sql.toLowerCase().includes('where') ? ' AND ' + conditions : ' WHERE ' + conditions) : ''}
\`;
`
            : `const sql = \`${sql}\`;
const params = [];
`;
        
        return `// Execute SQL query against the database
async function executeQuery() {
    // Initialize database connection
    await DatabaseManager.init();
    
    ${filtersCode}
    
    // Execute query with parameters
    const results = DatabaseManager.queryObjects(sql, params);
    
    console.log(\`Query returned \${results.length} rows\`);
    return results;
}

// Run the query
const data = await executeQuery();
`;
    },
    
    generateDataTransformCode: (data) => {
        if (!data || data.length === 0) return '// No data to transform';
        
        const firstRow = data[0];
        const columns = Object.keys(firstRow);
        const numericCols = columns.filter(col => typeof firstRow[col] === 'number');
        const stringCols = columns.filter(col => typeof firstRow[col] === 'string');
        
        return `// Data transformation and preparation
function transformData(rawData) {
    // Raw data structure:
    // Columns: ${columns.join(', ')}
    // Total rows: ${data.length}
    // Numeric columns: ${numericCols.join(', ') || 'none'}
    // String columns: ${stringCols.join(', ') || 'none'}
    
    // Extract labels (X-axis) from first string column or first column
    const labels = rawData.map(row => row.${stringCols[0] || columns[0]});
    
    // Extract values (Y-axis) from numeric columns
    const datasets = [
        ${numericCols.map(col => `{
            label: '${col}',
            data: rawData.map(row => row.${col} || 0)
        }`).join(',\n        ')}
    ];
    
    return { labels, datasets };
}

// Transform the data
const chartData = transformData(data);
console.log('Prepared data for', chartData.datasets.length, 'datasets');
`;
    },
    
    generateChartCode: (chartType, labelColumn, valueColumns) => {
        return `// Create Chart.js visualization
function createChart(labels, datasets, type = '${chartType}') {
    const canvas = document.getElementById('analysisChart');
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if present
    if (window.currentChart) {
        window.currentChart.destroy();
    }
    
    // Generate colors for datasets
    const colors = [
        'rgba(99, 102, 241, 0.7)',   // Indigo
        'rgba(236, 72, 153, 0.7)',   // Pink
        'rgba(34, 197, 94, 0.7)',    // Green
        'rgba(251, 146, 60, 0.7)',   // Orange
        'rgba(168, 85, 247, 0.7)'    // Purple
    ];
    
    // Configure datasets with colors
    const chartDatasets = datasets.map((ds, idx) => ({
        ...ds,
        backgroundColor: type === 'line' || type === 'radar'
            ? colors[idx].replace('0.7', '0.2')
            : colors[idx],
        borderColor: colors[idx].replace('0.7', '1'),
        borderWidth: 2,
        fill: type === 'line' || type === 'radar',
        tension: 0  // No curve smoothing for accuracy
    }));
    
    // Chart configuration
    const config = {
        type: type,
        data: {
            labels: labels,
            datasets: chartDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: type === 'doughnut' || type === 'pie' || datasets.length > 1
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    };
    
    // Add axis configuration for non-circular charts
    if (!['doughnut', 'pie', 'polarArea', 'radar'].includes(type)) {
        config.options.scales = {
            x: {
                type: typeof labels[0] === 'string' ? 'category' : 'linear',
                ticks: { autoSkip: true, maxRotation: 45, minRotation: 0 }
            },
            y: {
                beginAtZero: true
            }
        };
    }
    
    // Create and render the chart
    window.currentChart = new Chart(ctx, config);
    console.log('Chart rendered successfully');
    
    return window.currentChart;
}

// Create the visualization
createChart(chartData.labels, chartData.datasets, '${chartType}');
`;
    },
    
    generateFullPipeline: (sql, data, chartType, labelColumn, valueColumns, filters) => {
        return `// Complete Analysis Pipeline
// This code shows how your query is executed and visualized

${CodeViewer.generateQueryCode(sql, filters)}

${CodeViewer.generateDataTransformCode(data)}

${CodeViewer.generateChartCode(chartType, labelColumn, valueColumns)}

// Complete! Your analysis is now visible in the chart above.
`;
    },
    
    view: (vnode) => {
        const { sql, data, chartType, labelColumn, valueColumns, filters } = vnode.attrs;
        
        if (!sql) return null;
        
        return m('div', { class: 'card bg-base-100 shadow-xl mb-6' }, [
            m('div', { class: 'card-body' }, [
                m('div', { class: 'flex justify-between items-center mb-4' }, [
                    m('h3', { class: 'card-title text-lg' }, [
                        m('span', '💻 '),
                        'Code Execution Pipeline'
                    ]),
                    m('button', {
                        class: 'btn btn-sm btn-ghost',
                        onclick: () => {
                            CodeViewer.state.showCode = !CodeViewer.state.showCode;
                        }
                    }, CodeViewer.state.showCode ? '▼ Hide Code' : '▶ Show Code')
                ]),
                
                // Expandable code section
                CodeViewer.state.showCode && m('div', { class: 'space-y-4' }, [
                    // Tab selector
                    m('div', { class: 'tabs tabs-boxed' }, [
                        m('button', {
                            class: `tab ${CodeViewer.state.activeTab === 'query' ? 'tab-active' : ''}`,
                            onclick: () => { CodeViewer.state.activeTab = 'query'; }
                        }, '1. Query Execution'),
                        m('button', {
                            class: `tab ${CodeViewer.state.activeTab === 'data' ? 'tab-active' : ''}`,
                            onclick: () => { CodeViewer.state.activeTab = 'data'; }
                        }, '2. Data Transform'),
                        m('button', {
                            class: `tab ${CodeViewer.state.activeTab === 'chart' ? 'tab-active' : ''}`,
                            onclick: () => { CodeViewer.state.activeTab = 'chart'; }
                        }, '3. Chart Creation'),
                        m('button', {
                            class: `tab ${CodeViewer.state.activeTab === 'full' ? 'tab-active' : ''}`,
                            onclick: () => { CodeViewer.state.activeTab = 'full'; }
                        }, 'Full Pipeline')
                    ]),
                    
                    // Code display area
                    m('div', { class: 'mockup-code overflow-x-auto' }, [
                        m('pre', [
                            m('code', { class: 'language-javascript text-xs' }, 
                                CodeViewer.state.activeTab === 'query' ? CodeViewer.generateQueryCode(sql, filters) :
                                CodeViewer.state.activeTab === 'data' ? CodeViewer.generateDataTransformCode(data) :
                                CodeViewer.state.activeTab === 'chart' ? CodeViewer.generateChartCode(chartType, labelColumn, valueColumns) :
                                CodeViewer.generateFullPipeline(sql, data, chartType, labelColumn, valueColumns, filters)
                            )
                        ])
                    ]),
                    
                    // Copy button
                    m('div', { class: 'flex justify-end' }, [
                        m('button', {
                            class: 'btn btn-sm btn-outline',
                            onclick: () => {
                                const code = CodeViewer.state.activeTab === 'query' ? CodeViewer.generateQueryCode(sql, filters) :
                                    CodeViewer.state.activeTab === 'data' ? CodeViewer.generateDataTransformCode(data) :
                                    CodeViewer.state.activeTab === 'chart' ? CodeViewer.generateChartCode(chartType, labelColumn, valueColumns) :
                                    CodeViewer.generateFullPipeline(sql, data, chartType, labelColumn, valueColumns, filters);
                                
                                navigator.clipboard.writeText(code);
                                const btn = event.target;
                                const originalText = btn.textContent;
                                btn.textContent = '✓ Copied!';
                                setTimeout(() => { btn.textContent = originalText; }, 2000);
                            }
                        }, '📋 Copy Code')
                    ])
                ])
            ])
        ]);
    }
};
