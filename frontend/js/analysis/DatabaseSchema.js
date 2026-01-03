// Complete database schema information for analysis queries
const DatabaseSchema = {
    mainTable: {
        name: 'job_details',
        description: 'Main table storing all processed job postings',
        columns: [
            { name: 'id', type: 'INTEGER', description: 'Primary key' },
            { name: 'job_url', type: 'STRING', description: 'Unique job URL from source site' },
            { name: 'site', type: 'STRING', description: 'Source website name', indexed: true },
            { name: 'job_title', type: 'STRING', description: 'Original job title from posting' },
            { name: 'company_name', type: 'STRING', description: 'Original company name', indexed: true },
            { name: 'job_description', type: 'TEXT', description: 'Full job description text' },
            { name: 'min_salary', type: 'NUMERIC', description: 'Minimum salary value' },
            { name: 'max_salary', type: 'NUMERIC', description: 'Maximum salary value' },
            { name: 'experience_years', type: 'INTEGER', description: 'Required years of experience' },
            { name: 'posting_date', type: 'DATE', description: 'Date job was posted' },
            { name: 'original_language', type: 'STRING', description: 'Language of original posting (ISO code)' },
            { name: 'llm_model', type: 'STRING', description: 'LLM model used for processing' },
            { name: 'processed_at', type: 'DATETIME', description: 'Timestamp of data processing' }
        ],
        foreignKeys: [
            { column: 'title_id', references: 'titles(id)' },
            { column: 'job_function_id', references: 'job_functions(id)' },
            { column: 'seniority_level_id', references: 'seniority_levels(id)' },
            { column: 'industry_id', references: 'industries(id)' },
            { column: 'department_id', references: 'departments(id)' },
            { column: 'job_family_id', references: 'job_families(id)' },
            { column: 'specialization_id', references: 'specializations(id)' },
            { column: 'salary_currency_id', references: 'currencies(id)' },
            { column: 'salary_period_id', references: 'salary_periods(id)' },
            { column: 'required_education_id', references: 'education_levels(id)' },
            { column: 'employment_type_id', references: 'employment_types(id)' },
            { column: 'contract_type_id', references: 'contract_types(id)' },
            { column: 'work_schedule_id', references: 'work_schedules(id)' },
            { column: 'shift_details_id', references: 'shift_details(id)' },
            { column: 'remote_work_id', references: 'remote_work_options(id)' },
            { column: 'travel_required_id', references: 'travel_requirements(id)' },
            { column: 'city_id', references: 'cities(id)' },
            { column: 'region_id', references: 'regions(id)' },
            { column: 'country_id', references: 'countries(id)' },
            { column: 'full_address_id', references: 'full_addresses(id)' },
            { column: 'company_name_id', references: 'companies(id)' },
            { column: 'company_size_id', references: 'company_sizes(id)' },
            { column: 'contact_person_id', references: 'contact_persons(id)' }
        ]
    },
    
    lookupTables: [
        { name: 'titles', field: 'name', description: 'Standardized job titles' },
        { name: 'companies', field: 'name', description: 'Company names' },
        { name: 'cities', field: 'name', description: 'City names' },
        { name: 'regions', field: 'name', description: 'Region/state names' },
        { name: 'countries', field: 'name', description: 'Country names' },
        { name: 'job_functions', field: 'name', description: 'Job functions (e.g., Engineering, Sales)' },
        { name: 'seniority_levels', field: 'name', description: 'Seniority levels (entry, junior, mid, senior, etc.)' },
        { name: 'industries', field: 'name', description: 'Industry classifications' },
        { name: 'departments', field: 'name', description: 'Department names' },
        { name: 'job_families', field: 'name', description: 'Job family classifications' },
        { name: 'specializations', field: 'name', description: 'Job specializations' },
        { name: 'education_levels', field: 'name', description: 'Education requirements (none, highschool, bachelor, etc.)' },
        { name: 'employment_types', field: 'name', description: 'Employment types (full-time, part-time, etc.)' },
        { name: 'contract_types', field: 'name', description: 'Contract types (permanent, fixed-term, etc.)' },
        { name: 'work_schedules', field: 'name', description: 'Work schedules (standard, flexible, shift, etc.)' },
        { name: 'shift_details', field: 'name', description: 'Shift information (day, night, weekend, etc.)' },
        { name: 'remote_work_options', field: 'name', description: 'Remote work options (remote, hybrid, on-site)' },
        { name: 'travel_requirements', field: 'name', description: 'Travel requirements' },
        { name: 'company_sizes', field: 'name', description: 'Company sizes (startup, small, medium, etc.)' },
        { name: 'currencies', field: 'code', description: 'Currency codes (MDL, EUR, USD, etc.)' },
        { name: 'salary_periods', field: 'name', description: 'Salary periods (hour, month, year)' },
        { name: 'full_addresses', field: 'address', description: 'Full address strings' },
        { name: 'contact_persons', field: 'name', description: 'Contact person names' }
    ],
    
    manyToManyTables: [
        { name: 'hard_skills', field: 'name', junction: 'job_details_hard_skills', description: 'Technical skills (programming languages, tools, etc.)' },
        { name: 'soft_skills', field: 'name', junction: 'job_details_soft_skills', description: 'Soft skills (communication, leadership, etc.)' },
        { name: 'certifications', field: 'name', junction: 'job_details_certifications', description: 'Required certifications' },
        { name: 'licenses', field: 'name', junction: 'job_details_licenses', description: 'Required licenses' },
        { name: 'benefits', field: 'description', junction: 'job_details_benefits', description: 'Job benefits offered' },
        { name: 'work_environment', field: 'description', junction: 'job_details_work_environment', description: 'Work environment descriptions' },
        { name: 'professional_development', field: 'description', junction: 'job_details_professional_development', description: 'Professional development opportunities' },
        { name: 'work_life_balance', field: 'description', junction: 'job_details_work_life_balance', description: 'Work-life balance features' },
        { name: 'physical_requirements', field: 'description', junction: 'job_details_physical_requirements', description: 'Physical requirements for the job' },
        { name: 'work_conditions', field: 'description', junction: 'job_details_work_conditions', description: 'Work conditions' },
        { name: 'special_requirements', field: 'description', junction: 'job_details_special_requirements', description: 'Special requirements' }
    ],
    
    oneToManyTables: [
        { name: 'responsibilities', columns: ['id', 'job_detail_id', 'description', 'order'], description: 'Job responsibilities' },
        { name: 'job_languages', columns: ['id', 'job_detail_id', 'language', 'proficiency'], description: 'Languages required (with proficiency levels)' },
        { name: 'contact_emails', columns: ['id', 'job_detail_id', 'email'], description: 'Contact email addresses' },
        { name: 'contact_phones', columns: ['id', 'job_detail_id', 'phone'], description: 'Contact phone numbers' }
    ],
    
    // Generate example queries for different patterns
    exampleQueries: {
        basicCount: `-- Count jobs by a dimension
SELECT c.name, COUNT(*) as count
FROM job_details jd
JOIN cities c ON jd.city_id = c.id
GROUP BY c.name
ORDER BY count DESC
LIMIT 20`,
        
        salaryAnalysis: `-- Salary analysis with filtering
SELECT sl.name as seniority, 
       ROUND(AVG(jd.min_salary)) as avg_min,
       ROUND(AVG(jd.max_salary)) as avg_max,
       COUNT(*) as jobs
FROM job_details jd
JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
WHERE jd.min_salary IS NOT NULL
GROUP BY sl.name
ORDER BY avg_max DESC`,
        
        timeSeries: `-- Jobs over time
SELECT DATE(posting_date) as date, 
       COUNT(*) as count
FROM job_details
WHERE posting_date >= date('now', '-90 days')
GROUP BY DATE(posting_date)
ORDER BY date ASC`,
        
        skillsAnalysis: `-- Top skills with job counts
SELECT hs.name as skill, 
       COUNT(DISTINCT jd.id) as jobs,
       ROUND(AVG(jd.max_salary)) as avg_salary
FROM hard_skills hs
JOIN job_details_hard_skills jhs ON hs.id = jhs.hard_skills_id
JOIN job_details jd ON jhs.job_details_id = jd.id
WHERE jd.max_salary IS NOT NULL
GROUP BY hs.name
HAVING jobs >= 5
ORDER BY avg_salary DESC
LIMIT 20`,
        
        multiDimensional: `-- Multi-dimensional analysis
SELECT 
    i.name as industry,
    sl.name as seniority,
    COUNT(*) as jobs,
    ROUND(AVG(jd.max_salary)) as avg_salary
FROM job_details jd
JOIN industries i ON jd.industry_id = i.id
JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
WHERE jd.max_salary IS NOT NULL
GROUP BY i.name, sl.name
HAVING jobs >= 10
ORDER BY industry, avg_salary DESC`
    },
    
    // Generate schema documentation string
    getSchemaDocumentation: function() {
        return `# Complete Database Schema

## Main Table: job_details
${this.mainTable.description}

### Columns:
${this.mainTable.columns.map(col => 
    `- ${col.name} (${col.type}): ${col.description}${col.indexed ? ' [INDEXED]' : ''}`
).join('\n')}

### Foreign Keys:
${this.mainTable.foreignKeys.map(fk => 
    `- ${fk.column} → ${fk.references}`
).join('\n')}

## Lookup Tables (Many-to-One):
${this.lookupTables.map(t => 
    `- **${t.name}**: ${t.description} [field: ${t.field}]`
).join('\n')}

## Many-to-Many Relationships:
${this.manyToManyTables.map(t => 
    `- **${t.name}**: ${t.description} [field: ${t.field}, junction: ${t.junction}]`
).join('\n')}

## One-to-Many Tables:
${this.oneToManyTables.map(t => 
    `- **${t.name}**: ${t.description}`
).join('\n')}

## Query Patterns:

### Basic Count Query:
\`\`\`sql
${this.exampleQueries.basicCount}
\`\`\`

### Salary Analysis:
\`\`\`sql
${this.exampleQueries.salaryAnalysis}
\`\`\`

### Time Series:
\`\`\`sql
${this.exampleQueries.timeSeries}
\`\`\`

### Skills Analysis:
\`\`\`sql
${this.exampleQueries.skillsAnalysis}
\`\`\`

### Multi-Dimensional:
\`\`\`sql
${this.exampleQueries.multiDimensional}
\`\`\`

## Important Notes:
1. Always use JOINs to get readable names from lookup tables
2. Use COUNT(DISTINCT jd.id) when joining many-to-many tables to avoid duplicates
3. Filter NULL values for salary/experience analysis: WHERE field IS NOT NULL
4. Use CASE statements for creating ranges or buckets
5. LIMIT results for better visualization (typically 10-20 items)
6. Use date() function for date filtering: date('now', '-90 days')
`;
    }
};
