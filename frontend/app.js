// API Configuration
const API_BASE = '/api';

// Database Management
const DatabaseManager = {
    db: null,
    loading: false,
    loaded: false,
    error: null,
    initPromise: null,
    
    // Initialize SQL.js and load the database
    async init() {
        if (this.loaded) return this.db;
        if (this.loading && this.initPromise) {
            // Wait for existing initialization to complete
            return this.initPromise;
        }
        
        this.loading = true;
        this.error = null;
        
        // Store the initialization promise so multiple calls can await it
        this.initPromise = (async () => {
            try {
                console.log('Initializing SQL.js...');
                
                // Initialize SQL.js with CDN WASM files
                const SQL = await initSqlJs({
                    locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${file}`
                });
                
                console.log('Loading database file...');
                
                // Load the database file
                const response = await fetch(`${API_BASE}/data.db`);
                if (!response.ok) {
                    throw new Error(`Failed to load database: ${response.status} ${response.statusText}`);
                }
                
                const buffer = await response.arrayBuffer();
                console.log(`Database loaded: ${(buffer.byteLength / 1024 / 1024).toFixed(2)} MB`);
                
                // Create database instance
                this.db = new SQL.Database(new Uint8Array(buffer));
                this.loaded = true;
                this.loading = false;
                
                console.log('Database ready for queries');
                return this.db;
                
            } catch (error) {
                console.error('Database initialization failed:', error);
                this.error = error;
                this.loading = false;
                this.initPromise = null;
                throw error;
            }
        })();
        
        return this.initPromise;
    },
    
    // Execute a SQL query
    query(sql, params = []) {
        if (!this.db) {
            throw new Error('Database not initialized. Call init() first.');
        }
        
        try {
            const results = this.db.exec(sql, params);
            return results;
        } catch (error) {
            console.error('Query failed:', sql, error);
            throw error;
        }
    },
    
    // Get query results as objects
    queryObjects(sql, params = []) {
        const results = this.query(sql, params);
        if (results.length === 0) return [];
        
        const [result] = results;
        const { columns, values } = result;
        
        return values.map(row => {
            const obj = {};
            columns.forEach((col, idx) => {
                obj[col] = row[idx];
            });
            return obj;
        });
    }
};

// URL State Management Utilities
const URLState = {
    // Parse query parameters from URL
    parse: () => {
        const params = new URLSearchParams(window.location.search);
        const state = {
            filters: {},
            page: parseInt(params.get('page')) || 1,
            itemsPerPage: parseInt(params.get('limit')) || 20,
            sort: params.get('sort') || 'date_desc',
            search: params.get('q') || ''
        };
        
        // List of multi-select fields (many-to-many relationships)
        const multiSelectFields = [
            'hard_skills', 'soft_skills', 'certifications', 'licenses_required',
            'benefits', 'work_environment', 'professional_development', 
            'work_life_balance', 'physical_requirements', 'work_conditions', 
            'special_requirements'
        ];
        
        // Parse all filter parameters
        for (const [key, value] of params.entries()) {
            if (['page', 'limit', 'sort', 'q'].includes(key)) continue;
            if (value && value !== '') {
                // Convert numeric values for range filters
                if (['salaryMin', 'salaryMax', 'experienceMin', 'experienceMax'].includes(key)) {
                    state.filters[key] = value === 'null' ? null : parseInt(value);
                } else if (multiSelectFields.includes(key)) {
                    // Handle multi-select fields - support comma-separated values
                    state.filters[key] = value.split(',').map(v => v.trim()).filter(v => v);
                } else {
                    state.filters[key] = value;
                }
            }
        }
        
        return state;
    },
    
    // Update URL with current state
    update: (newState) => {
        const url = new URL(window.location);
        
        // Update filters
        Object.keys(state.filters).forEach(key => {
            const value = state.filters[key];
            if (Array.isArray(value) && value.length > 0) {
                // Join array values with comma for URL
                url.searchParams.set(key, value.join(','));
            } else if (value !== null && value !== undefined && value !== '' && !Array.isArray(value)) {
                url.searchParams.set(key, value);
            } else {
                url.searchParams.delete(key);
            }
        });
        
        // Update search
        if (state.search && state.search.trim()) {
            url.searchParams.set('q', state.search.trim());
        } else {
            url.searchParams.delete('q');
        }
        
        // Update pagination and sorting
        if (JobsPage.displayPage !== 1) {
            url.searchParams.set('page', JobsPage.displayPage);
        } else {
            url.searchParams.delete('page');
        }
        
        if (state.itemsPerPage !== 20) {
            url.searchParams.set('limit', state.itemsPerPage);
        } else {
            url.searchParams.delete('limit');
        }
        
        if (state.sort !== 'date_desc') {
            url.searchParams.set('sort', state.sort);
        } else {
            url.searchParams.delete('sort');
        }
        
        // Update browser URL without triggering route change
        window.history.replaceState({}, '', url.toString());
    },
    
    // Initialize state from URL
    initialize: () => {
        const urlState = URLState.parse();
        
        // Return URL state for later application
        return urlState;
    }
};

// API Client
const api = {
    getJobsIndex: () => m.request({ url: `${API_BASE}/jobs/index.json` }),
    getJobsPage: (page) => m.request({ url: `${API_BASE}/jobs/page-${page}.json` }),
    getAnalysisIndex: () => m.request({ url: `${API_BASE}/analysis/index.json` }),
    getAnalysis: (filename) => m.request({ url: `${API_BASE}/analysis/${filename}` })
};

// SQL-based data access functions
const dbApi = {
    // Build WHERE clause from filters
    buildWhereClause(filters, search) {
        const conditions = [];
        const params = [];  // Changed from {} to [] for positional parameters
        
        // Text search across multiple fields
        if (search && search.trim()) {
            const searchValue = `%${search.trim()}%`;
            conditions.push(`(
                jd.job_title LIKE ? OR
                t.name LIKE ? OR
                c.name LIKE ? OR
                jf.name LIKE ? OR
                sp.name LIKE ?
            )`);
            // Add the same search value 5 times for the 5 LIKE clauses
            params.push(searchValue, searchValue, searchValue, searchValue, searchValue);
        }
        
        // Job function filter
        if (filters.job_function) {
            conditions.push('jf.name = ?');
            params.push(filters.job_function);
        }
        
        // Seniority filter
        if (filters.seniority_level) {
            conditions.push('sl.name = ?');
            params.push(filters.seniority_level);
        }
        
        // City filter
        if (filters.city) {
            conditions.push('ci.name = ?');
            params.push(filters.city);
        }
        
        // Remote work filter
        if (filters.remote_work) {
            conditions.push('rw.name = ?');
            params.push(filters.remote_work);
        }
        
        // Industry filter
        if (filters.industry) {
            conditions.push('ind.name = ?');
            params.push(filters.industry);
        }
        
        // Company filter
        if (filters.company) {
            conditions.push('c.name = ?');
            params.push(filters.company);
        }
        
        // Employment type filter
        if (filters.employment_type) {
            conditions.push('et.name = ?');
            params.push(filters.employment_type);
        }
        
        // Contract type filter
        if (filters.contract_type) {
            conditions.push('ct.name = ?');
            params.push(filters.contract_type);
        }
        
        // Department filter
        if (filters.department) {
            conditions.push('d.name = ?');
            params.push(filters.department);
        }
        
        // Specialization filter
        if (filters.specialization) {
            conditions.push('sp.name = ?');
            params.push(filters.specialization);
        }
        
        // Education level filter
        if (filters.education_level) {
            conditions.push('el.name = ?');
            params.push(filters.education_level);
        }
        
        // Company size filter
        if (filters.company_size) {
            conditions.push('cs.name = ?');
            params.push(filters.company_size);
        }
        
        // Title filter
        if (filters.title) {
            conditions.push('t.name = ?');
            params.push(filters.title);
        }
        
        // Job family filter
        if (filters.job_family) {
            conditions.push('jf2.name = ?');
            params.push(filters.job_family);
        }
        
        // Work schedule filter
        if (filters.work_schedule) {
            conditions.push('ws.name = ?');
            params.push(filters.work_schedule);
        }
        
        // Shift details filter
        if (filters.shift_details) {
            conditions.push('sd.name = ?');
            params.push(filters.shift_details);
        }
        
        // Travel requirements filter
        if (filters.travel_required) {
            conditions.push('tr.name = ?');
            params.push(filters.travel_required);
        }
        
        // Region filter
        if (filters.region) {
            conditions.push('reg.name = ?');
            params.push(filters.region);
        }
        
        // Country filter
        if (filters.country) {
            conditions.push('cou.name = ?');
            params.push(filters.country);
        }
        
        // Many-to-many filters (multi-select with OR logic)
        // Helper function to build many-to-many conditions
        const addM2MFilter = (filterKey, tableName, columnName = 'name') => {
            const filterValue = filters[filterKey];
            if (filterValue && filterValue.length > 0) {
                // For multi-select, we use IN clause
                // But we need to ensure job has ALL selected items (AND logic across selections)
                const placeholders = filterValue.map(() => '?').join(',');
                conditions.push(`jd.id IN (
                    SELECT jm.job_details_id 
                    FROM job_details_${tableName} jm
                    JOIN ${tableName} mt ON jm.${tableName}_id = mt.id
                    WHERE mt.${columnName} IN (${placeholders})
                    GROUP BY jm.job_details_id
                    HAVING COUNT(DISTINCT mt.${columnName}) = ${filterValue.length}
                )`);
                params.push(...filterValue);
            }
        };
        
        addM2MFilter('hard_skills', 'hard_skills');
        addM2MFilter('soft_skills', 'soft_skills');
        addM2MFilter('certifications', 'certifications');
        addM2MFilter('licenses_required', 'licenses');
        addM2MFilter('benefits', 'benefits', 'description');
        addM2MFilter('work_environment', 'work_environment', 'description');
        addM2MFilter('professional_development', 'professional_development', 'description');
        addM2MFilter('work_life_balance', 'work_life_balance', 'description');
        addM2MFilter('physical_requirements', 'physical_requirements', 'description');
        addM2MFilter('work_conditions', 'work_conditions', 'description');
        addM2MFilter('special_requirements', 'special_requirements', 'description');
        
        // Salary range filters
        if (filters.salaryMin !== null && filters.salaryMin !== undefined) {
            conditions.push('jd.min_salary >= ?');
            params.push(filters.salaryMin);
        }
        
        if (filters.salaryMax !== null && filters.salaryMax !== undefined) {
            conditions.push('jd.max_salary <= ?');
            params.push(filters.salaryMax);
        }
        
        // Experience filters
        if (filters.experienceMin !== null && filters.experienceMin !== undefined) {
            conditions.push('jd.experience_years >= ?');
            params.push(filters.experienceMin);
        }
        
        if (filters.experienceMax !== null && filters.experienceMax !== undefined) {
            conditions.push('jd.experience_years <= ?');
            params.push(filters.experienceMax);
        }
        
        const whereClause = conditions.length > 0 ? 'WHERE ' + conditions.join(' AND ') : '';
        return { whereClause, params };
    },
    
    // Build ORDER BY clause from sort option
    buildOrderByClause(sortOption) {
        const sortMap = {
            'date_desc': 'jd.posting_date DESC',
            'date_asc': 'jd.posting_date ASC',
            'salary_desc': 'jd.min_salary DESC',
            'salary_asc': 'jd.min_salary ASC',
            'title_asc': 't.name ASC',
            'title_desc': 't.name DESC',
            'company_asc': 'c.name ASC',
            'company_desc': 'c.name DESC'
        };
        
        return sortMap[sortOption] || sortMap['date_desc'];
    },
    
    // Get jobs with pagination, filtering, and sorting
    async getJobs(page = 1, limit = 20, filters = {}, search = '', sort = 'date_desc') {
        await DatabaseManager.init();
        
        const { whereClause, params } = this.buildWhereClause(filters, search);
        const orderBy = this.buildOrderByClause(sort);
        const offset = (page - 1) * limit;
        
        // Main query to get jobs
        const jobsQuery = `
            SELECT 
                jd.id,
                t.name as title,
                jf.name as job_function,
                sp.name as specialization,
                sl.name as seniority_level,
                c.name as company,
                cs.name as company_size,
                ci.name as city,
                reg.name as region,
                cou.name as country,
                rw.name as remote_work,
                jd.min_salary,
                jd.max_salary,
                curr.code as salary_currency,
                sper.name as salary_period,
                et.name as employment_type,
                ct.name as contract_type,
                ws.name as work_schedule,
                el.name as education_level,
                jd.experience_years,
                jd.posting_date,
                jd.site,
                jd.job_url,
                jd.job_title as original_title,
                jd.company_name as original_company,
                jd.job_description as original_description,
                ind.name as industry,
                d.name as department,
                jf2.name as job_family,
                sd.name as shift_details,
                tr.name as travel_requirements
            FROM job_details jd
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN currencies curr ON jd.salary_currency_id = curr.id
            LEFT JOIN salary_periods sper ON jd.salary_period_id = sper.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            ${whereClause}
            ORDER BY ${orderBy}
            LIMIT ${limit} OFFSET ${offset}
        `;
        
        const jobs = DatabaseManager.queryObjects(jobsQuery, params);
        
        // Get total count
        const countQuery = `
            SELECT COUNT(*) as total
            FROM job_details jd
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            ${whereClause}
        `;
        
        const countResult = DatabaseManager.queryObjects(countQuery, params);
        const total = countResult[0]?.total || 0;
        
        // Format jobs to match the JSON API structure
        const formattedJobs = await Promise.all(jobs.map(job => this.formatJob(job)));
        
        return {
            jobs: formattedJobs,
            total,
            page,
            totalPages: Math.ceil(total / limit)
        };
    },
    
    // Format a job to match JSON API structure
    async formatJob(job) {
        // Get related data (skills, benefits, etc.)
        const hardSkills = await this.getJobSkills(job.id, 'hard_skills');
        const softSkills = await this.getJobSkills(job.id, 'soft_skills');
        const certifications = await this.getJobRelated(job.id, 'certifications');
        const benefits = await this.getJobRelated(job.id, 'benefits');
        const responsibilities = await this.getJobResponsibilities(job.id);
        const languages = await this.getJobLanguages(job.id);
        const workEnvironment = await this.getJobRelated(job.id, 'work_environment');
        const professionalDevelopment = await this.getJobRelated(job.id, 'professional_development');
        
        return {
            id: job.id,
            title: job.title,
            job_function: job.job_function,
            specialization: job.specialization,
            seniority_level: job.seniority_level,
            company: job.company,
            company_size: job.company_size,
            location: {
                city: job.city,
                region: job.region,
                country: job.country,
                remote_work: job.remote_work
            },
            salary: {
                min: job.min_salary,
                max: job.max_salary,
                currency: job.salary_currency || 'MDL',
                period: job.salary_period,
                min_mdl: job.min_salary, // For Moldova market, assume MDL
                max_mdl: job.max_salary
            },
            employment: {
                type: job.employment_type,
                contract: job.contract_type,
                schedule: job.work_schedule
            },
            requirements: {
                education: job.education_level,
                experience_years: job.experience_years,
                languages: languages,
                hard_skills: hardSkills,
                soft_skills: softSkills,
                certifications: certifications
            },
            benefits: benefits,
            posting_date: job.posting_date,
            source: {
                site: job.site,
                url: job.job_url
            },
            parsed_view: {
                responsibilities: responsibilities,
                work_environment: workEnvironment,
                professional_development: professionalDevelopment
            },
            raw: {
                original_title: job.original_title,
                original_company: job.original_company,
                original_description: job.original_description
            },
            industry: job.industry,
            department: job.department,
            job_family: job.job_family,
            shift_details: job.shift_details,
            travel_requirements: job.travel_requirements
        };
    },
    
    // Get job skills (hard or soft)
    async getJobSkills(jobId, skillType) {
        // Validate skillType to prevent SQL injection
        const allowedTypes = ['hard_skills', 'soft_skills'];
        if (!allowedTypes.includes(skillType)) {
            console.error('Invalid skill type:', skillType);
            return [];
        }
        
        const table = skillType;
        const query = `
            SELECT s.name
            FROM ${table} s
            JOIN job_details_${table} js ON s.id = js.${table}_id
            WHERE js.job_details_id = ?
        `;
        
        const results = DatabaseManager.queryObjects(query, [jobId]);
        return results.map(r => r.name);
    },
    
    // Get job related data (benefits, certifications, etc.)
    async getJobRelated(jobId, relationType) {
        // Validate relationType to prevent SQL injection
        const allowedTypes = [
            'certifications', 'benefits', 'work_environment', 
            'professional_development', 'work_life_balance',
            'physical_requirements', 'work_conditions', 'special_requirements'
        ];
        if (!allowedTypes.includes(relationType)) {
            console.error('Invalid relation type:', relationType);
            return [];
        }
        
        const columnName = relationType === 'benefits' || relationType === 'work_environment' || 
                          relationType === 'professional_development' ? 'description' : 'name';
        const query = `
            SELECT r.${columnName} as value
            FROM ${relationType} r
            JOIN job_details_${relationType} jr ON r.id = jr.${relationType}_id
            WHERE jr.job_details_id = ?
        `;
        
        const results = DatabaseManager.queryObjects(query, [jobId]);
        return results.map(r => r.value);
    },
    
    // Get job responsibilities
    async getJobResponsibilities(jobId) {
        const query = `
            SELECT description
            FROM responsibilities
            WHERE job_detail_id = ?
        `;
        
        const results = DatabaseManager.queryObjects(query, [jobId]);
        return results.map(r => r.description);
    },
    
    // Get job languages
    async getJobLanguages(jobId) {
        const query = `
            SELECT language
            FROM job_languages
            WHERE job_detail_id = ?
        `;
        
        const results = DatabaseManager.queryObjects(query, [jobId]);
        return results.map(r => r.language);
    },
    
    // Get metadata for filters (distinct values with counts)
    async getMetadata() {
        await DatabaseManager.init();
        
        const metadata = {};
        
        // Map table names to their foreign key column names in job_details
        const tableToForeignKey = {
            'titles': 'title_id',
            'job_functions': 'job_function_id',
            'seniority_levels': 'seniority_level_id',
            'industries': 'industry_id',
            'departments': 'department_id',
            'job_families': 'job_family_id',
            'specializations': 'specialization_id',
            'education_levels': 'required_education_id',
            'employment_types': 'employment_type_id',
            'contract_types': 'contract_type_id',
            'work_schedules': 'work_schedule_id',
            'shift_details': 'shift_details_id',
            'remote_work_options': 'remote_work_id',
            'travel_requirements': 'travel_required_id',
            'cities': 'city_id',
            'regions': 'region_id',
            'countries': 'country_id',
            'companies': 'company_name_id',
            'company_sizes': 'company_size_id'
        };
        
        // Helper function to get distinct values with counts
        const getDistinctValues = (table, column, label) => {
            const foreignKey = tableToForeignKey[table];
            if (!foreignKey) {
                console.error(`No foreign key mapping found for table: ${table}`);
                return [];
            }
            
            const query = `
                SELECT ${column} as name, COUNT(*) as count
                FROM job_details jd
                LEFT JOIN ${table} t ON jd.${foreignKey} = t.id
                WHERE t.${column} IS NOT NULL
                GROUP BY t.${column}
                ORDER BY count DESC, t.${column} ASC
            `;
            return DatabaseManager.queryObjects(query);
        };
        
        // Helper function to get many-to-many values with counts
        const getM2MValues = (table, column) => {
            const query = `
                SELECT t.${column} as name, COUNT(DISTINCT jd.id) as count
                FROM job_details jd
                JOIN job_details_${table} jm ON jd.id = jm.job_details_id
                JOIN ${table} t ON jm.${table}_id = t.id
                WHERE t.${column} IS NOT NULL
                GROUP BY t.${column}
                ORDER BY count DESC, t.${column} ASC
            `;
            return DatabaseManager.queryObjects(query);
        };
        
        // Get metadata for each filterable field
        try {
            // Single-select fields (many-to-one)
            metadata.title = getDistinctValues('titles', 'name', 'Title');
            metadata.job_function = getDistinctValues('job_functions', 'name', 'Job Function');
            metadata.seniority_level = getDistinctValues('seniority_levels', 'name', 'Seniority');
            metadata.industry = getDistinctValues('industries', 'name', 'Industry');
            metadata.department = getDistinctValues('departments', 'name', 'Department');
            metadata.job_family = getDistinctValues('job_families', 'name', 'Job Family');
            metadata.specialization = getDistinctValues('specializations', 'name', 'Specialization');
            metadata.education_level = getDistinctValues('education_levels', 'name', 'Education');
            metadata.employment_type = getDistinctValues('employment_types', 'name', 'Employment Type');
            metadata.contract_type = getDistinctValues('contract_types', 'name', 'Contract Type');
            metadata.work_schedule = getDistinctValues('work_schedules', 'name', 'Work Schedule');
            metadata.shift_details = getDistinctValues('shift_details', 'name', 'Shift Details');
            metadata.remote_work = getDistinctValues('remote_work_options', 'name', 'Remote Work');
            metadata.travel_required = getDistinctValues('travel_requirements', 'name', 'Travel Required');
            metadata.location = getDistinctValues('cities', 'name', 'City');
            metadata.region = getDistinctValues('regions', 'name', 'Region');
            metadata.country = getDistinctValues('countries', 'name', 'Country');
            metadata.company_name = getDistinctValues('companies', 'name', 'Company');
            metadata.company_size = getDistinctValues('company_sizes', 'name', 'Company Size');
            
            // Multi-select fields (many-to-many)
            metadata.hard_skills = getM2MValues('hard_skills', 'name');
            metadata.soft_skills = getM2MValues('soft_skills', 'name');
            metadata.certifications = getM2MValues('certifications', 'name');
            metadata.licenses_required = getM2MValues('licenses', 'name');
            metadata.benefits = getM2MValues('benefits', 'description');
            metadata.work_environment = getM2MValues('work_environment', 'description');
            metadata.professional_development = getM2MValues('professional_development', 'description');
            metadata.work_life_balance = getM2MValues('work_life_balance', 'description');
            metadata.physical_requirements = getM2MValues('physical_requirements', 'description');
            metadata.work_conditions = getM2MValues('work_conditions', 'description');
            metadata.special_requirements = getM2MValues('special_requirements', 'description');
        } catch (error) {
            console.error('Error getting metadata:', error);
        }
        
        // Get total jobs count
        const totalQuery = 'SELECT COUNT(*) as total FROM job_details';
        const totalResult = DatabaseManager.queryObjects(totalQuery);
        const totalJobs = totalResult[0]?.total || 0;
        
        return {
            total_jobs: totalJobs,
            metadata: metadata
        };
    },
    
    // Get filter counts based on currently active filters
    async getFilteredCounts(fieldKey, activeFilters = {}) {
        await DatabaseManager.init();
        
        // Map field keys to table info for single-select (many-to-one) fields
        const fieldToTableMap = {
            'title': { table: 'titles', foreignKey: 'title_id', column: 'name' },
            'job_function': { table: 'job_functions', foreignKey: 'job_function_id', column: 'name' },
            'seniority_level': { table: 'seniority_levels', foreignKey: 'seniority_level_id', column: 'name' },
            'industry': { table: 'industries', foreignKey: 'industry_id', column: 'name' },
            'department': { table: 'departments', foreignKey: 'department_id', column: 'name' },
            'job_family': { table: 'job_families', foreignKey: 'job_family_id', column: 'name' },
            'specialization': { table: 'specializations', foreignKey: 'specialization_id', column: 'name' },
            'education_level': { table: 'education_levels', foreignKey: 'required_education_id', column: 'name' },
            'employment_type': { table: 'employment_types', foreignKey: 'employment_type_id', column: 'name' },
            'contract_type': { table: 'contract_types', foreignKey: 'contract_type_id', column: 'name' },
            'work_schedule': { table: 'work_schedules', foreignKey: 'work_schedule_id', column: 'name' },
            'shift_details': { table: 'shift_details', foreignKey: 'shift_details_id', column: 'name' },
            'remote_work': { table: 'remote_work_options', foreignKey: 'remote_work_id', column: 'name' },
            'travel_required': { table: 'travel_requirements', foreignKey: 'travel_required_id', column: 'name' },
            'city': { table: 'cities', foreignKey: 'city_id', column: 'name' },
            'region': { table: 'regions', foreignKey: 'region_id', column: 'name' },
            'country': { table: 'countries', foreignKey: 'country_id', column: 'name' },
            'company': { table: 'companies', foreignKey: 'company_name_id', column: 'name' },
            'company_size': { table: 'company_sizes', foreignKey: 'company_size_id', column: 'name' }
        };
        
        // Map for many-to-many fields
        const m2mFieldMap = {
            'hard_skills': { table: 'hard_skills', column: 'name' },
            'soft_skills': { table: 'soft_skills', column: 'name' },
            'certifications': { table: 'certifications', column: 'name' },
            'licenses_required': { table: 'licenses', column: 'name' },
            'benefits': { table: 'benefits', column: 'description' },
            'work_environment': { table: 'work_environment', column: 'description' },
            'professional_development': { table: 'professional_development', column: 'description' },
            'work_life_balance': { table: 'work_life_balance', column: 'description' },
            'physical_requirements': { table: 'physical_requirements', column: 'description' },
            'work_conditions': { table: 'work_conditions', column: 'description' },
            'special_requirements': { table: 'special_requirements', column: 'description' }
        };
        
        const tableInfo = fieldToTableMap[fieldKey];
        const m2mInfo = m2mFieldMap[fieldKey];
        
        if (!tableInfo && !m2mInfo) {
            console.error(`No table mapping found for field: ${fieldKey}`);
            return [];
        }
        
        // Build WHERE clause excluding the current field
        const filtersWithoutCurrent = { ...activeFilters };
        delete filtersWithoutCurrent[fieldKey];
        
        const { whereClause, params } = this.buildWhereClause(filtersWithoutCurrent, '');
        
        // Handle many-to-many fields differently
        if (m2mInfo) {
            const query = `
                SELECT t.${m2mInfo.column} as name, COUNT(DISTINCT jd.id) as count
                FROM job_details jd
                LEFT JOIN titles ti ON jd.title_id = ti.id
                LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
                LEFT JOIN specializations sp ON jd.specialization_id = sp.id
                LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
                LEFT JOIN companies c ON jd.company_name_id = c.id
                LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
                LEFT JOIN cities ci ON jd.city_id = ci.id
                LEFT JOIN regions reg ON jd.region_id = reg.id
                LEFT JOIN countries cou ON jd.country_id = cou.id
                LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
                LEFT JOIN employment_types et ON jd.employment_type_id = et.id
                LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
                LEFT JOIN departments d ON jd.department_id = d.id
                LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
                LEFT JOIN education_levels el ON jd.required_education_id = el.id
                LEFT JOIN industries ind ON jd.industry_id = ind.id
                LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
                LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
                LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
                JOIN job_details_${m2mInfo.table} jm ON jd.id = jm.job_details_id
                JOIN ${m2mInfo.table} t ON jm.${m2mInfo.table}_id = t.id
                ${whereClause}
                GROUP BY t.${m2mInfo.column}
                HAVING t.${m2mInfo.column} IS NOT NULL
                ORDER BY count DESC, t.${m2mInfo.column} ASC
            `;
            
            return DatabaseManager.queryObjects(query, params);
        }
        
        // Query to get counts for this field with current filters applied
        const query = `
            SELECT t.${tableInfo.column} as name, COUNT(*) as count
            FROM job_details jd
            LEFT JOIN titles ti ON jd.title_id = ti.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN ${tableInfo.table} t ON jd.${tableInfo.foreignKey} = t.id
            ${whereClause}
            GROUP BY t.${tableInfo.column}
            HAVING t.${tableInfo.column} IS NOT NULL
            ORDER BY count DESC, t.${tableInfo.column} ASC
        `;
        
        return DatabaseManager.queryObjects(query, params);
    }
};

// Helper to check if filters are active
const hasActiveFilters = (filters) => {
    return Object.keys(filters).some(k => {
        const val = filters[k];
        if (Array.isArray(val)) {
            return val.length > 0;
        }
        return val !== null && val !== undefined && val !== '';
    });
};

// State Management
const state = {
    jobsIndex: null,
    currentPage: 1,
    jobs: [],
    allLoadedJobs: [], // Cache of all jobs loaded so far
    loadedJobIds: new Set(), // Track job IDs for fast duplicate checking
    loadedPages: new Set(), // Track which pages have been loaded
    filters: {
        salaryMin: null,
        salaryMax: null,
        experienceMin: null,
        experienceMax: null
    },
    loading: false,
    dbLoading: false,
    dbLoaded: false,
    dbError: null,
    analysisIndex: null,
    selectedAnalysis: null,
    selectedAnalysisData: null,
    itemsPerPage: 20, // User-configurable items per page for display
    availablePageSizes: [10, 20, 50, 100],
    sort: 'date_desc', // Default sorting: newest first
    search: '', // Global search term
    sortOptions: [
        { value: 'date_desc', label: 'Newest First', field: 'posting_date', order: 'desc' },
        { value: 'date_asc', label: 'Oldest First', field: 'posting_date', order: 'asc' },
        { value: 'salary_desc', label: 'Highest Salary', field: 'salary', order: 'desc' },
        { value: 'salary_asc', label: 'Lowest Salary', field: 'salary', order: 'asc' },
        { value: 'title_asc', label: 'Job Title A-Z', field: 'title', order: 'asc' },
        { value: 'title_desc', label: 'Job Title Z-A', field: 'title', order: 'desc' },
        { value: 'company_asc', label: 'Company A-Z', field: 'company', order: 'asc' },
        { value: 'company_desc', label: 'Company Z-A', field: 'company', order: 'desc' }
    ]
};

// Configuration constants
const DEFAULT_JOBS_PER_API_PAGE = 100;

// Utility Functions

// Map filter keys to metadata keys
const filterKeyToMetadataKey = {
    'city': 'location',
    'company': 'company_name'
};

const getMetadataKey = (filterKey) => {
    return filterKeyToMetadataKey[filterKey] || filterKey;
};

// Helper to find filter metadata for active filters
// Note: Currently only supports single filter metadata lookups.
// When multiple filters are active, returns metadata for the first one found.
// This is a limitation of the current metadata structure which doesn't include
// intersection counts for multiple filter combinations.
const getActiveFilterMetadata = (filters, jobsIndex) => {
    if (!jobsIndex || !jobsIndex.metadata) return null;
    
    let activeFilterCount = 0;
    let firstFilterMetadata = null;
    
    for (const [filterKey, filterValue] of Object.entries(filters)) {
        if (filterValue === null || filterValue === undefined || filterValue === '') continue;
        
        // Skip numeric range filters (salaryMin, salaryMax, experienceMin, experienceMax)
        if (['salaryMin', 'salaryMax', 'experienceMin', 'experienceMax'].includes(filterKey)) continue;
        
        activeFilterCount++;
        
        const metadataKey = getMetadataKey(filterKey);
        
        if (jobsIndex.metadata[metadataKey] && !firstFilterMetadata) {
            const metadataItems = jobsIndex.metadata[metadataKey];
            
            // Find the matching metadata entry
            for (const item of metadataItems) {
                if (item.name === filterValue) {
                    firstFilterMetadata = item;
                    break;
                }
            }
        }
    }
    
    // Only return metadata if there's exactly one active filter
    // When multiple filters are active, we can't use single-filter metadata counts
    return activeFilterCount === 1 ? firstFilterMetadata : null;
};

// Sort Functions
const sortJobs = (jobs, sortBy) => {
    const sortOption = state.sortOptions.find(opt => opt.value === sortBy) || state.sortOptions[0];
    const { field, order } = sortOption;
    
    return jobs.slice().sort((a, b) => {
        let aVal, bVal;
        
        // Handle different field types
        switch (field) {
            case 'salary':
                // Compare by min salary in MDL, jobs without salary data go to end
                if (hasValidSalary(a)) {
                    aVal = a.salary?.min_mdl || a.salary?.min;
                } else {
                    aVal = null; // Let the null handling logic put these at the end
                }
                
                if (hasValidSalary(b)) {
                    bVal = b.salary?.min_mdl || b.salary?.min;
                } else {
                    bVal = null; // Let the null handling logic put these at the end
                }
                break;
            case 'title':
                aVal = (a.title || '').toLowerCase();
                bVal = (b.title || '').toLowerCase();
                break;
            case 'company':
                aVal = (a.company || '').toLowerCase();
                bVal = (b.company || '').toLowerCase();
                break;
            case 'posting_date':
                aVal = new Date(a.posting_date || '1970-01-01');
                bVal = new Date(b.posting_date || '1970-01-01');
                break;
            default:
                aVal = (a[field] || '').toLowerCase();
                bVal = (b[field] || '').toLowerCase();
        }
        
        // Handle null/undefined values
        if (aVal == null && bVal == null) return 0;
        if (aVal == null) return order === 'asc' ? 1 : -1;
        if (bVal == null) return order === 'asc' ? -1 : 1;
        
        // Compare values
        let comparison = 0;
        if (typeof aVal === 'number' && typeof bVal === 'number') {
            comparison = aVal - bVal;
        } else {
            comparison = aVal.toString().localeCompare(bVal.toString());
        }
        
        return order === 'asc' ? comparison : -comparison;
    });
};

// Enhanced filter matching with search functionality

const formatSalary = (salary) => {
    if (!salary) return 'Not specified';
    
    // Check if we have MDL values (handles 0 as valid salary)
    const hasMdlValues = salary.min_mdl != null;
    
    if (hasMdlValues) {
        // Use MDL values
        const minMdl = salary.min_mdl;
        const maxMdl = salary.max_mdl;
        
        if (minMdl == null) return 'Not specified';
        
        const minStr = minMdl.toLocaleString();
        const maxStr = maxMdl != null ? maxMdl.toLocaleString() : '';
        const mdlRange = maxStr ? `${minStr} - ${maxStr} MDL` : `${minStr} MDL`;
        
        // Show original currency if different from MDL
        if (salary.currency && salary.currency.toUpperCase() !== 'MDL' && salary.min != null) {
            const origMin = salary.min.toLocaleString();
            const origMax = salary.max != null ? salary.max.toLocaleString() : '';
            const origRange = origMax ? `${origMin} - ${origMax} ${salary.currency.toUpperCase()}` : `${origMin} ${salary.currency.toUpperCase()}`;
            return `${mdlRange} (${origRange})`;
        }
        
        return mdlRange;
    } else {
        // Fallback: no MDL conversion available
        // Only use if currency is MDL or not specified (assume MDL for Moldova market)
        const currency = salary.currency ? salary.currency.toUpperCase() : 'MDL';
        
        if (salary.min == null) return 'Not specified';
        
        const minStr = salary.min.toLocaleString();
        const maxStr = salary.max != null ? salary.max.toLocaleString() : '';
        return maxStr ? `${minStr} - ${maxStr} ${currency}` : `${minStr} ${currency}`;
    }
};

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString();
};

// Components

// Header Component
const Header = {
    view: () => m('div', { class: 'navbar bg-base-100 shadow-lg' }, [
        m('div', { class: 'navbar-start' }, [
            m('a', { 
                class: 'btn btn-ghost text-xl', 
                href: '#!/',
                oncreate: m.route.link 
            }, 'Moldova Job Market')
        ]),
        m('div', { class: 'navbar-center hidden lg:flex' }, [
            m('ul', { class: 'menu menu-horizontal px-1' }, [
                m('li', m('a', { href: '#!/', oncreate: m.route.link }, 'Home')),
                m('li', m('a', { href: '#!/jobs', oncreate: m.route.link }, 'Jobs')),
                m('li', m('a', { href: '#!/analysis', oncreate: m.route.link }, 'Analysis'))
            ])
        ]),
        m('div', { class: 'navbar-end' }, [
            m('label', { class: 'swap swap-rotate btn btn-ghost btn-circle' }, [
                m('input', { 
                    type: 'checkbox',
                    onchange: (e) => {
                        const theme = e.target.checked ? 'dark' : 'light';
                        document.documentElement.setAttribute('data-theme', theme);
                    }
                }),
                m('svg', { class: 'swap-on fill-current w-6 h-6', xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24' }, 
                    m('path', { d: 'M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z' })),
                m('svg', { class: 'swap-off fill-current w-6 h-6', xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24' }, 
                    m('path', { d: 'M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z' }))
            ])
        ])
    ])
};

// Footer Component
const Footer = {
    view: () => m('footer', { class: 'footer footer-center p-4 bg-base-300 text-base-content mt-8' }, [
        m('div', [
            m('p', '© 2026 Moldova Job Market - Data updated regularly')
        ])
    ])
};

// Loading Component
const Loading = {
    view: () => m('div', { class: 'flex justify-center items-center h-64' }, [
        m('span', { class: 'loading loading-spinner loading-lg' })
    ])
};

// Home Page
const HomePage = {
    oninit: async () => {
        try {
            state.dbLoading = true;
            await DatabaseManager.init();
            state.dbLoaded = true;
            
            const metadata = await dbApi.getMetadata();
            state.jobsIndex = metadata;
            state.dbLoading = false;
            m.redraw();
        } catch (error) {
            console.error('Failed to load database:', error);
            state.dbError = error;
            state.dbLoading = false;
            m.redraw();
        }
    },
    view: () => m('div', { class: 'container mx-auto px-4 py-8' }, [
        state.dbLoading ? m('div', { class: 'hero min-h-[50vh] bg-base-200 rounded-lg' }, [
            m('div', { class: 'hero-content text-center' }, [
                m('div', { class: 'max-w-md' }, [
                    m('h1', { class: 'text-5xl font-bold mb-4' }, 'Moldova Job Market'),
                    m('div', { class: 'flex flex-col items-center gap-4' }, [
                        m('span', { class: 'loading loading-spinner loading-lg' }),
                        m('p', { class: 'text-sm opacity-70' }, 'Loading job database...')
                    ])
                ])
            ])
        ]) : state.dbError ? m('div', { class: 'hero min-h-[50vh] bg-base-200 rounded-lg' }, [
            m('div', { class: 'hero-content text-center' }, [
                m('div', { class: 'max-w-md' }, [
                    m('h1', { class: 'text-5xl font-bold' }, 'Moldova Job Market'),
                    m('div', { class: 'alert alert-error mt-6' }, [
                        m('span', 'Failed to load database. Please make sure data.db is available in /api/')
                    ])
                ])
            ])
        ]) : m('div', { class: 'hero min-h-[50vh] bg-base-200 rounded-lg' }, [
            m('div', { class: 'hero-content text-center' }, [
                m('div', { class: 'max-w-md' }, [
                    m('h1', { class: 'text-5xl font-bold' }, 'Moldova Job Market'),
                    m('p', { class: 'py-6' }, 'Browse thousands of job opportunities across Moldova. Filter by location, salary, skills, and more.'),
                    state.jobsIndex ? 
                        m('a', { 
                            class: 'stats shadow cursor-pointer hover:shadow-xl transition-shadow justify-center',
                            href: '#!/jobs',
                            oncreate: m.route.link,
                            'aria-label': 'Browse all jobs'
                        }, [
                            m('div', { class: 'stat place-items-center' }, [
                                m('div', { class: 'stat-title' }, 'Total Jobs'),
                                m('div', { class: 'stat-value text-primary' }, state.jobsIndex.total_jobs.toLocaleString()),
                                m('div', { class: 'stat-desc' }, 'Click to browse jobs')
                            ])
                        ])
                    : m(Loading)
                ])
            ])
        ])
    ])
};

// Job List Item Component (Extra Slim - HN Style)
const JobListItem = {
    view: (vnode) => {
        const job = vnode.attrs.job;
        return m('div', { class: 'px-2 py-1 border-b border-base-300 hover:bg-base-200' }, [
            m('div', { class: 'flex items-start gap-2' }, [
                m('span', { class: 'text-xs opacity-60 mt-1' }, `${vnode.attrs.index}.`),
                m('div', { class: 'flex-1' }, [
                    m('a', { 
                        href: `#!/jobs/${job.id}`,
                        class: 'text-sm font-medium hover:underline text-base-content',
                        oncreate: m.route.link
                    }, job.title),
                    m('div', { class: 'flex flex-wrap gap-2 mt-1 text-xs opacity-70' }, [
                        job.company && m('span', { class: 'badge badge-outline badge-sm' }, job.company),
                        job.location && job.location.city && m('span', job.location.city),
                        job.salary && m('span', formatSalary(job.salary)),
                        job.posting_date && m('span', formatDate(job.posting_date))
                    ])
                ])
            ])
        ]);
    }
};

// Helper function to check if a job has valid salary data
const hasValidSalary = (job) => {
    return (job.salary?.min_mdl || job.salary?.min) && (job.salary?.max_mdl || job.salary?.max);
};

// Helper function to get field value from a job object
const getJobFieldValue = (job, fieldKey) => {
    switch (fieldKey) {
        case 'title': return job.title;
        case 'job_function': return job.job_function;
        case 'seniority_level': return job.seniority_level;
        case 'industry': return job.industry;
        case 'department': return job.department;
        case 'job_family': return job.job_family;
        case 'specialization': return job.specialization;
        case 'education_level': return job.requirements?.education;
        case 'languages': return job.requirements?.languages;
        case 'hard_skills': return job.requirements?.hard_skills;
        case 'soft_skills': return job.requirements?.soft_skills;
        case 'certifications': return job.requirements?.certifications;
        case 'licenses_required': return job.requirements?.licenses;
        case 'employment_type': return job.employment?.type;
        case 'contract_type': return job.employment?.contract_type;
        case 'work_schedule': return job.employment?.work_schedule;
        case 'shift_details': return job.employment?.shift_details;
        case 'remote_work': return job.employment?.remote_work;
        case 'travel_required': return job.employment?.travel_required;
        case 'city': return job.location?.city;
        case 'region': return job.location?.region;
        case 'country': return job.location?.country;
        case 'company_name': return job.company;
        case 'company_size': return job.company_size;
        case 'benefits': return job.benefits;
        case 'work_environment': return job.work_environment;
        case 'professional_development': return job.professional_development;
        case 'work_life_balance': return job.work_life_balance;
        case 'physical_requirements': return job.physical_requirements;
        case 'work_conditions': return job.work_conditions;
        case 'special_requirements': return job.special_requirements;
        default: return null;
    }
};

// Filter matching logic - ALL filters work as AND (combined)
const matchesFilters = (job, filters) => {
    for (const [key, value] of Object.entries(filters)) {
        if (value === null || value === undefined || value === '') continue;
        
        switch (key) {
            // Job Details
            case 'title':
                if (job.title !== value) return false;
                break;
            case 'job_function':
                if (job.job_function !== value) return false;
                break;
            case 'seniority_level':
                if (job.seniority_level !== value) return false;
                break;
            case 'industry':
                if (job.industry !== value) return false;
                break;
            case 'department':
                if (job.department !== value) return false;
                break;
            case 'job_family':
                if (job.job_family !== value) return false;
                break;
            case 'specialization':
                if (job.specialization !== value) return false;
                break;
            
            // Requirements
            case 'education_level':
                if (job.requirements?.education !== value) return false;
                break;
            case 'languages':
                if (!job.requirements?.languages || !job.requirements.languages.includes(value)) return false;
                break;
            case 'hard_skills':
                if (!job.requirements?.hard_skills || !job.requirements.hard_skills.some(skill => skill.includes(value))) return false;
                break;
            case 'soft_skills':
                if (!job.requirements?.soft_skills || !job.requirements.soft_skills.some(skill => skill.includes(value))) return false;
                break;
            case 'certifications':
                if (!job.requirements?.certifications || !job.requirements.certifications.includes(value)) return false;
                break;
            case 'licenses_required':
                if (!job.requirements?.licenses || !job.requirements.licenses.includes(value)) return false;
                break;
            
            // Work Arrangement
            case 'employment_type':
                if (job.employment?.type !== value) return false;
                break;
            case 'contract_type':
                if (job.employment?.contract !== value) return false;
                break;
            case 'work_schedule':
                if (job.employment?.schedule !== value) return false;
                break;
            case 'shift_details':
                if (job.employment?.shift !== value) return false;
                break;
            case 'remote_work':
                if (job.location?.remote_work !== value) return false;
                break;
            case 'travel_required':
                if (job.requirements?.travel !== value) return false;
                break;
            
            // Location
            case 'city':
                if (job.location?.city !== value) return false;
                break;
            case 'region':
                if (job.location?.region !== value) return false;
                break;
            case 'country':
                if (job.location?.country !== value) return false;
                break;
            
            // Company
            case 'company':
                if (job.company !== value) return false;
                break;
            case 'company_size':
                if (job.company_size !== value) return false;
                break;
            
            // Benefits & Culture
            case 'benefits':
                if (!job.benefits || !job.benefits.includes(value)) return false;
                break;
            case 'work_environment':
                if (!job.work_environment || !job.work_environment.includes(value)) return false;
                break;
            case 'professional_development':
                if (!job.professional_development || !job.professional_development.includes(value)) return false;
                break;
            case 'work_life_balance':
                if (!job.work_life_balance || !job.work_life_balance.includes(value)) return false;
                break;
            
            // Conditions
            case 'physical_requirements':
                if (!job.requirements?.physical || !job.requirements.physical.includes(value)) return false;
                break;
            case 'work_conditions':
                if (!job.work_conditions || !job.work_conditions.includes(value)) return false;
                break;
            case 'special_requirements':
                if (!job.requirements?.special || !job.requirements.special.includes(value)) return false;
                break;
            
            // Numeric Filters
            case 'salaryMin':
                // Filter out jobs without salary specified
                if (!hasValidSalary(job)) return false;
                const jobMinSalary = job.salary?.min_mdl || job.salary?.min;
                if (jobMinSalary < value) return false;
                break;
            case 'salaryMax':
                // Filter out jobs without salary specified
                if (!hasValidSalary(job)) return false;
                const jobMaxSalary = job.salary?.max_mdl || job.salary?.max;
                if (jobMaxSalary > value) return false;
                break;
            case 'experienceMin':
                const jobExpYears = job.requirements?.experience_years;
                if (jobExpYears === null || jobExpYears === undefined) return false;
                if (jobExpYears < value) return false;
                break;
            case 'experienceMax':
                const jobExpYearsMax = job.requirements?.experience_years;
                if (jobExpYearsMax === null || jobExpYearsMax === undefined) return false;
                if (jobExpYearsMax > value) return false;
                break;
        }
    }
    return true;
};

// Get available filter options based on current filters (hierarchical)
const getAvailableOptions = (jobs, filterKey) => {
    const options = new Set();
    jobs.forEach(job => {
        let value;
        switch (filterKey) {
            case 'job_function':
                value = job.job_function;
                break;
            case 'seniority_level':
                value = job.seniority_level;
                break;
            case 'city':
                value = job.location?.city;
                break;
            case 'remote_work':
                value = job.location?.remote_work;
                break;
            case 'industry':
                value = job.industry;
                break;
            case 'company':
                value = job.company;
                break;
            case 'employment_type':
                value = job.employment?.type;
                break;
            case 'contract_type':
                value = job.employment?.contract;
                break;
        }
        if (value) options.add(value);
    });
    return Array.from(options).sort();
};

// Filter Component with Hierarchical Filtering (Left Sidebar)
const FilterPanel = {
    showAdvanced: false,
    salaryMinTimer: null,
    salaryMaxTimer: null,
    experienceMinTimer: null,
    experienceMaxTimer: null,
    filterCounts: {}, // Store dynamic filter counts
    suggestions: [], // Store filter suggestions
    suggestionsTimer: null,
    
    // Async function to get counts for a specific field
    async getCountsForField(fieldKey) {
        try {
            const counts = await dbApi.getFilteredCounts(fieldKey, state.filters);
            FilterPanel.filterCounts[fieldKey] = counts;
            m.redraw();
        } catch (error) {
            console.error(`Error getting counts for ${fieldKey}:`, error);
            FilterPanel.filterCounts[fieldKey] = [];
        }
    },
    
    // Async function to fetch suggestions
    async fetchSuggestions() {
        if (!state.search || state.search.trim() === '') {
            FilterPanel.suggestions = [];
            return;
        }
        
        try {
            const searchTerm = state.search.toLowerCase().trim();
            const suggestions = [];
            
            await DatabaseManager.init();
            
            // Map of filterable fields to their table and foreign key info
            const filterableFields = [
                { key: 'job_function', table: 'job_functions', foreignKey: 'job_function_id', column: 'name', label: 'Job Function' },
                { key: 'seniority_level', table: 'seniority_levels', foreignKey: 'seniority_level_id', column: 'name', label: 'Seniority Level' },
                { key: 'industry', table: 'industries', foreignKey: 'industry_id', column: 'name', label: 'Industry' },
                { key: 'department', table: 'departments', foreignKey: 'department_id', column: 'name', label: 'Department' },
                { key: 'specialization', table: 'specializations', foreignKey: 'specialization_id', column: 'name', label: 'Specialization' },
                { key: 'city', table: 'cities', foreignKey: 'city_id', column: 'name', label: 'City' },
                { key: 'company', table: 'companies', foreignKey: 'company_name_id', column: 'name', label: 'Company' },
                { key: 'employment_type', table: 'employment_types', foreignKey: 'employment_type_id', column: 'name', label: 'Employment Type' },
                { key: 'contract_type', table: 'contract_types', foreignKey: 'contract_type_id', column: 'name', label: 'Contract Type' },
                { key: 'remote_work', table: 'remote_work_options', foreignKey: 'remote_work_id', column: 'name', label: 'Remote Work' },
                { key: 'education_level', table: 'education_levels', foreignKey: 'required_education_id', column: 'name', label: 'Education Level' },
                { key: 'company_size', table: 'company_sizes', foreignKey: 'company_size_id', column: 'name', label: 'Company Size' }
            ];
            
            // Search across all filterable fields with counts
            for (const fieldInfo of filterableFields) {
                // Build WHERE clause for current active filters (excluding this field)
                const filtersWithoutCurrent = { ...state.filters };
                delete filtersWithoutCurrent[fieldInfo.key];
                
                const { whereClause, params } = dbApi.buildWhereClause(filtersWithoutCurrent, '');
                
                // Query with JOIN to count actual jobs
                const query = `
                    SELECT t.${fieldInfo.column} as value, COUNT(DISTINCT jd.id) as count
                    FROM job_details jd
                    LEFT JOIN titles ti ON jd.title_id = ti.id
                    LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
                    LEFT JOIN specializations sp ON jd.specialization_id = sp.id
                    LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
                    LEFT JOIN companies c ON jd.company_name_id = c.id
                    LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
                    LEFT JOIN cities ci ON jd.city_id = ci.id
                    LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
                    LEFT JOIN employment_types et ON jd.employment_type_id = et.id
                    LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
                    LEFT JOIN departments d ON jd.department_id = d.id
                    LEFT JOIN education_levels el ON jd.required_education_id = el.id
                    LEFT JOIN industries ind ON jd.industry_id = ind.id
                    LEFT JOIN ${fieldInfo.table} t ON jd.${fieldInfo.foreignKey} = t.id
                    ${whereClause}
                    ${whereClause ? 'AND' : 'WHERE'} LOWER(t.${fieldInfo.column}) LIKE ?
                    GROUP BY t.${fieldInfo.column}
                    HAVING count > 0
                    ORDER BY count DESC, t.${fieldInfo.column}
                    LIMIT 3
                `;
                
                const results = DatabaseManager.queryObjects(query, [...params, `%${searchTerm}%`]);
                
                results.forEach(row => {
                    suggestions.push({
                        value: row.value,
                        count: row.count,
                        field: fieldInfo.key,
                        fieldName: fieldInfo.label,
                        fieldDisplay: fieldInfo.label
                    });
                });
            }
            
            // Sort suggestions by relevance (exact match, then starts with, then by count)
            suggestions.sort((a, b) => {
                const aLower = a.value.toLowerCase();
                const bLower = b.value.toLowerCase();
                const searchLower = searchTerm.toLowerCase();
                
                // Exact match first
                if (aLower === searchLower && bLower !== searchLower) return -1;
                if (bLower === searchLower && aLower !== searchLower) return 1;
                
                // Starts with
                if (aLower.startsWith(searchLower) && !bLower.startsWith(searchLower)) return -1;
                if (bLower.startsWith(searchLower) && !aLower.startsWith(searchLower)) return 1;
                
                // Sort by count (higher counts first)
                return b.count - a.count;
            });
            
            FilterPanel.suggestions = suggestions.slice(0, 10);
            m.redraw();
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            FilterPanel.suggestions = [];
        }
    },
    
    view: () => {
        if (!state.jobsIndex) return null;
        
        // Calculate salary range - use reasonable defaults
        const salaryRange = { min: 0, max: 100000 };
        
        // All available filter fields - organized following schema order
        // Excludes non-filterable fields like contact info
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
            { key: 'languages', label: 'Languages', section: 'Requirements' },
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
            { key: 'benefits', label: 'Benefits', section: 'Benefits & Culture' },
            { key: 'work_environment', label: 'Work Environment', section: 'Benefits & Culture' },
            { key: 'professional_development', label: 'Professional Development', section: 'Benefits & Culture' },
            { key: 'work_life_balance', label: 'Work Life Balance', section: 'Benefits & Culture' },
            
            // Conditions
            { key: 'physical_requirements', label: 'Physical Requirements', section: 'Conditions' },
            { key: 'work_conditions', label: 'Work Conditions', section: 'Conditions' },
            { key: 'special_requirements', label: 'Special Requirements', section: 'Conditions' }
        ];
        
        const handleFilterChange = async () => {
            JobsPage.displayPage = 1;
            
            // Update URL with new filter state
            URLState.update();
            
            // Reload jobs with new filters
            await JobsPage.loadJobs();
            m.redraw();
        };
        
        // Function to apply search as filter
        const applySearchAsFilter = async (suggestion = null) => {
            if (!state.search || state.search.trim() === '') return;
            
            // If suggestion provided, use it
            if (suggestion) {
                state.filters[suggestion.field] = suggestion.value;
                state.search = ''; // Clear search input
                
                // Clear filter counts cache
                FilterPanel.filterCounts = {};
                
                await handleFilterChange();
                m.redraw();
            } else {
                // Keep as general search and trigger filter
                await handleFilterChange();
            }
        };
        
        return m('div', { class: 'bg-base-200 p-4' }, [
            m('div', { class: 'flex justify-between items-center mb-4' }, [
                m('h3', { class: 'font-bold text-lg' }, 'Filters'),
                m('button', { 
                    class: 'btn btn-xs btn-ghost',
                    onclick: async () => {
                        // Clear all filters - both numeric and categorical
                        Object.keys(state.filters).forEach(key => {
                            state.filters[key] = null;
                        });
                        state.search = '';
                        JobsPage.displayPage = 1;
                        
                        // Clear filter counts cache
                        FilterPanel.filterCounts = {};
                        
                        // Update URL
                        URLState.update();
                        
                        // Reload jobs with no filters
                        await JobsPage.loadJobs();
                        m.redraw();
                    }
                }, 'Clear All')
            ]),
            
            // Apply Filter (Search) Field
            m('div', { class: 'form-control mb-6 relative' }, [
                m('label', { class: 'label' }, m('span', { class: 'label-text font-semibold' }, 'Apply Filter')),
                m('div', { class: 'flex gap-2' }, [
                    m('div', { class: 'relative flex-1' }, [
                        m('input', { 
                            type: 'text',
                            class: `input input-bordered input-sm w-full ${state.search ? 'input-info' : ''}`,
                            placeholder: 'Type to search/filter by title, company, skills, location...',
                            value: state.search || '',
                            oninput: (e) => {
                                state.search = e.target.value;
                                // Debounce suggestions fetching
                                clearTimeout(FilterPanel.suggestionsTimer);
                                FilterPanel.suggestionsTimer = setTimeout(() => {
                                    FilterPanel.fetchSuggestions();
                                }, 300);
                                m.redraw(); // Trigger redraw to show/hide suggestions
                            },
                            onkeypress: (e) => {
                                if (e.key === 'Enter') {
                                    e.preventDefault();
                                    applySearchAsFilter();
                                }
                            },
                            onfocus: (e) => {
                                // Show hint text
                                if (!state.search) {
                                    e.target.placeholder = 'Type and press Enter to apply as filter...';
                                }
                            },
                            onblur: (e) => {
                                e.target.placeholder = 'Type to search/filter by title, company, skills, location...';
                            }
                        }),
                        // Suggestions dropdown
                        (() => {
                            const suggestions = FilterPanel.suggestions;
                            if (suggestions.length === 0 || !state.search) return null;
                            
                            return m('div', { 
                                class: 'absolute top-full left-0 right-0 bg-base-100 border border-base-300 rounded-box shadow-lg z-50 max-h-60 overflow-y-auto',
                                style: 'margin-top: 2px;'
                            }, [
                                suggestions.map(suggestion => 
                                    m('button', {
                                        class: 'w-full text-left px-4 py-2 hover:bg-base-200 text-sm',
                                        onclick: (e) => {
                                            e.preventDefault();
                                            applySearchAsFilter(suggestion);
                                        },
                                        title: `Apply "${suggestion.value}" to ${suggestion.fieldDisplay}`
                                    }, [
                                        m('div', { class: 'flex justify-between items-center' }, [
                                            m('div', [
                                                m('div', { class: 'font-medium text-base-content' }, suggestion.value),
                                                m('div', { class: 'text-xs opacity-70' }, `Apply to: ${suggestion.fieldDisplay}`)
                                            ]),
                                            m('div', { class: 'badge badge-sm badge-info' }, suggestion.count)
                                        ])
                                    ])
                                )
                            ]);
                        })()
                    ]),
                    m('button', { 
                        class: 'btn btn-sm btn-primary',
                        onclick: applySearchAsFilter
                    }, 'Apply')
                ])
            ]),
            
            m('div', { class: 'divider' }),
            
            // Items Per Page Selector
            m('div', { class: 'form-control mb-6' }, [
                m('label', { class: 'label' }, m('span', { class: 'label-text font-semibold' }, 'Items Per Page')),
                m('div', { class: 'flex gap-2' }, [
                    state.availablePageSizes.map(size =>
                        m('button', {
                            class: `btn btn-sm ${state.itemsPerPage === size ? 'btn-primary' : 'btn-ghost'}`,
                            onclick: async () => {
                                state.itemsPerPage = size;
                                JobsPage.displayPage = 1;
                                URLState.update();
                                await JobsPage.loadJobs();
                                m.redraw();
                            }
                        }, size)
                    )
                ]),
                m('div', { class: 'text-xs opacity-70 mt-2' }, `Showing ${state.itemsPerPage} jobs per page`)
            ]),
            
            // Sort Controls
            m('div', { class: 'form-control mb-6' }, [
                m('label', { class: 'label' }, m('span', { class: 'label-text font-semibold' }, 'Sort By')),
                m('div', { class: 'grid grid-cols-2 gap-2' }, [
                    state.sortOptions.map(option =>
                        m('button', {
                            class: `btn btn-sm ${state.sort === option.value ? 'btn-primary' : 'btn-ghost'} w-full`,
                            onclick: async () => {
                                state.sort = option.value;
                                URLState.update();
                                await JobsPage.loadJobs();
                                m.redraw();
                            }
                        }, option.label)
                    )
                ])
            ]),
            
            m('div', { class: 'divider' }),
            
            // Salary Range Filter
            m('div', { class: 'form-control mb-6' }, [
                m('label', { class: 'label' }, m('span', { class: 'label-text font-semibold' }, 'Salary Range (MDL)')),
                m('div', { class: 'space-y-2' }, [
                    m('input', { 
                        type: 'number',
                        class: `input input-bordered input-sm w-full ${state.filters.salaryMin ? 'input-info' : ''}`,
                        placeholder: 'Minimum',
                        value: state.filters.salaryMin || '',
                        oninput: (e) => {
                            state.filters.salaryMin = e.target.value ? parseInt(e.target.value) : null;
                            // Debounce the filter change
                            clearTimeout(FilterPanel.salaryMinTimer);
                            FilterPanel.salaryMinTimer = setTimeout(() => {
                                handleFilterChange();
                            }, 500);
                            URLState.update();
                        }
                    }),
                    m('input', { 
                        type: 'number',
                        class: `input input-bordered input-sm w-full ${state.filters.salaryMax ? 'input-info' : ''}`,
                        placeholder: 'Maximum',
                        value: state.filters.salaryMax || '',
                        oninput: (e) => {
                            state.filters.salaryMax = e.target.value ? parseInt(e.target.value) : null;
                            // Debounce the filter change
                            clearTimeout(FilterPanel.salaryMaxTimer);
                            FilterPanel.salaryMaxTimer = setTimeout(() => {
                                handleFilterChange();
                            }, 500);
                            URLState.update();
                        }
                    }),
                    (state.filters.salaryMin || state.filters.salaryMax) && m('div', { class: 'text-xs opacity-70' }, 
                        `${state.filters.salaryMin ? state.filters.salaryMin.toLocaleString() : '0'} - ${state.filters.salaryMax ? state.filters.salaryMax.toLocaleString() : '∞'} MDL`
                    )
                ])
            ]),
            
            // Experience Years Filter
            m('div', { class: 'form-control mb-6' }, [
                m('label', { class: 'label' }, m('span', { class: 'label-text font-semibold' }, 'Experience (Years)')),
                m('div', { class: 'space-y-2' }, [
                    m('input', { 
                        type: 'number',
                        class: `input input-bordered input-sm w-full ${state.filters.experienceMin !== null ? 'input-info' : ''}`,
                        placeholder: 'Minimum',
                        min: 0,
                        value: state.filters.experienceMin !== null ? state.filters.experienceMin : '',
                        oninput: (e) => {
                            state.filters.experienceMin = e.target.value ? parseInt(e.target.value) : null;
                            // Debounce the filter change
                            clearTimeout(FilterPanel.experienceMinTimer);
                            FilterPanel.experienceMinTimer = setTimeout(() => {
                                handleFilterChange();
                            }, 500);
                            URLState.update();
                        }
                    }),
                    m('input', { 
                        type: 'number',
                        class: `input input-bordered input-sm w-full ${state.filters.experienceMax !== null ? 'input-info' : ''}`,
                        placeholder: 'Maximum',
                        min: 0,
                        value: state.filters.experienceMax !== null ? state.filters.experienceMax : '',
                        oninput: (e) => {
                            state.filters.experienceMax = e.target.value ? parseInt(e.target.value) : null;
                            // Debounce the filter change
                            clearTimeout(FilterPanel.experienceMaxTimer);
                            FilterPanel.experienceMaxTimer = setTimeout(() => {
                                handleFilterChange();
                            }, 500);
                            URLState.update();
                        }
                    }),
                    (state.filters.experienceMin !== null || state.filters.experienceMax !== null) && 
                        m('div', { class: 'text-xs opacity-70' }, 
                            `${state.filters.experienceMin || 0} - ${state.filters.experienceMax || '∞'} years`
                        )
                ])
            ]),
            
            m('div', { class: 'divider' }),
            
            // All filters grouped by section
            m('div', { class: 'space-y-6' },
                // Group filters by section - only show basic filters from metadata
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
                            // Get metadata or dynamic counts for this field
                            const metadataKey = getMetadataKey(field.key);
                            
                            // Use dynamic counts if available, otherwise fall back to static metadata
                            let options = [];
                            if (FilterPanel.filterCounts[field.key]) {
                                options = FilterPanel.filterCounts[field.key];
                            } else {
                                // Use static metadata as initial fallback
                                options = state.jobsIndex.metadata[metadataKey] || [];
                                // Trigger async fetch of dynamic counts
                                FilterPanel.getCountsForField(field.key);
                            }
                            
                            // Filter out options with 0 count
                            const availableOptions = options.filter(opt => opt.count > 0);
                            
                            // Determine if this is a multi-select field (many-to-many)
                            const multiSelectFields = [
                                'hard_skills', 'soft_skills', 'certifications', 'licenses_required',
                                'benefits', 'work_environment', 'professional_development', 
                                'work_life_balance', 'physical_requirements', 'work_conditions', 
                                'special_requirements'
                            ];
                            const isMultiSelect = multiSelectFields.includes(field.key);
                            
                            // Initialize filter value as array for multi-select fields
                            if (isMultiSelect && !Array.isArray(state.filters[field.key])) {
                                state.filters[field.key] = state.filters[field.key] ? [state.filters[field.key]] : [];
                            }
                            
                            return m('div', { class: 'form-control' }, [
                                m('label', { class: 'label py-1' }, [
                                    m('span', { class: 'label-text text-sm' }, field.label),
                                    isMultiSelect && state.filters[field.key] && state.filters[field.key].length > 0 && 
                                        m('span', { class: 'badge badge-info badge-sm ml-2' }, state.filters[field.key].length)
                                ]),
                                isMultiSelect ? 
                                    // Multi-select for many-to-many fields
                                    m('select', { 
                                        class: `select select-bordered select-sm w-full ${state.filters[field.key] && state.filters[field.key].length > 0 ? 'select-info' : ''}`,
                                        multiple: true,
                                        size: Math.min(5, availableOptions.length + 1),
                                        onchange: (e) => {
                                            const selectedOptions = Array.from(e.target.selectedOptions).map(opt => opt.value);
                                            state.filters[field.key] = selectedOptions.length > 0 ? selectedOptions : [];
                                            // Clear cached counts so they refresh
                                            FilterPanel.filterCounts = {};
                                            handleFilterChange();
                                        }
                                    }, [
                                        ...availableOptions.map(item => {
                                            const isSelected = state.filters[field.key] && state.filters[field.key].includes(item.name);
                                            return m('option', { 
                                                value: item.name,
                                                selected: isSelected
                                            }, `${item.name} (${item.count})`);
                                        })
                                    ])
                                    :
                                    // Single-select for many-to-one fields
                                    m('select', { 
                                        class: `select select-bordered select-sm w-full ${state.filters[field.key] ? 'select-info' : ''}`,
                                        value: state.filters[field.key] || '',
                                        onchange: (e) => {
                                            if (e.target.value) {
                                                state.filters[field.key] = e.target.value;
                                            } else {
                                                state.filters[field.key] = null;
                                            }
                                            // Clear cached counts so they refresh
                                            FilterPanel.filterCounts = {};
                                            handleFilterChange();
                                        }
                                    }, [
                                        m('option', { value: '' }, 'All'),
                                        ...availableOptions.map(item => 
                                            m('option', { value: item.name }, `${item.name} (${item.count})`)
                                        )
                                    ])
                            ]);
                        })
                    ])
                )
            )
        ]);
    }
};

// Jobs Page
const JobsPage = {
    displayPage: 1, // Current display page for filtered results
    loadingMore: false,
    
    oninit: async () => {
        // Initialize URL state before loading data
        const urlState = URLState.initialize();
        
        // Apply URL state to our state objects
        if (urlState) {
            Object.assign(state.filters, urlState.filters);
            JobsPage.displayPage = urlState.page;
            state.itemsPerPage = urlState.itemsPerPage;
            state.sort = urlState.sort;
            state.search = urlState.search;
        }
        
        // Ensure database is loaded
        state.loading = true;
        try {
            await DatabaseManager.init();
            state.dbLoaded = true;
            
            // Load metadata if not already loaded
            if (!state.jobsIndex) {
                const metadata = await dbApi.getMetadata();
                state.jobsIndex = metadata;
            }
            
            // Load initial jobs
            await JobsPage.loadJobs();
            
            state.loading = false;
            m.redraw();
        } catch (err) {
            console.error('Error loading jobs:', err);
            state.dbError = err;
            state.loading = false;
            m.redraw();
        }
    },
    
    loadJobs: async () => {
        try {
            const result = await dbApi.getJobs(
                JobsPage.displayPage,
                state.itemsPerPage,
                state.filters,
                state.search,
                state.sort
            );
            
            state.jobs = result.jobs;
            state.totalJobs = result.total;
            state.totalPages = result.totalPages;
            
        } catch (err) {
            console.error('Error loading jobs:', err);
            state.jobs = [];
        }
    },
    
    navigateToPage: async (pageNumber) => {
        JobsPage.displayPage = pageNumber;
        window.scrollTo(0, 0);
        
        // Update URL with new page number
        URLState.update();
        
        // Load jobs for this page
        await JobsPage.loadJobs();
        m.redraw();
    },
    
    renderPagination: (totalPages) => {
        if (totalPages <= 1) return null;
        
        const currentPage = JobsPage.displayPage;
        const pageButtons = [];
        
        // First page button
        pageButtons.push(
            m('button', {
                class: `btn btn-sm ${currentPage === 1 ? 'btn-disabled' : ''}`,
                disabled: currentPage === 1,
                onclick: () => JobsPage.navigateToPage(1)
            }, '« First')
        );
        
        // Previous button
        pageButtons.push(
            m('button', {
                class: `btn btn-sm ${currentPage === 1 ? 'btn-disabled' : ''}`,
                disabled: currentPage === 1,
                onclick: () => JobsPage.navigateToPage(currentPage - 1)
            }, '‹ Prev')
        );
        
        // Page number buttons: show current, -3 to +3
        const startPage = Math.max(1, currentPage - 3);
        const endPage = Math.min(totalPages, currentPage + 3);
        
        if (startPage > 1) {
            pageButtons.push(m('div', { class: 'px-2 py-1 text-sm text-gray-500' }, '...'));
        }
        
        for (let i = startPage; i <= endPage; i++) {
            pageButtons.push(
                m('button', {
                    class: `btn btn-sm ${i === currentPage ? 'btn-primary' : ''}`,
                    onclick: () => JobsPage.navigateToPage(i)
                }, i)
            );
        }
        
        if (endPage < totalPages) {
            pageButtons.push(m('div', { class: 'px-2 py-1 text-sm text-gray-500' }, '...'));
        }
        
        // Next button
        pageButtons.push(
            m('button', {
                class: `btn btn-sm ${currentPage === totalPages ? 'btn-disabled' : ''}`,
                disabled: currentPage === totalPages,
                onclick: () => JobsPage.navigateToPage(currentPage + 1)
            }, 'Next ›')
        );
        
        // Last page button
        pageButtons.push(
            m('button', {
                class: `btn btn-sm ${currentPage === totalPages ? 'btn-disabled' : ''}`,
                disabled: currentPage === totalPages,
                onclick: () => JobsPage.navigateToPage(totalPages)
            }, 'Last »')
        );
        
        return m('div', { class: 'flex justify-center gap-1 items-center flex-wrap' }, pageButtons);
    },
    
    view: () => {
        const jobs = state.jobs || [];
        const total = state.totalJobs || 0;
        const totalPages = state.totalPages || 0;
        
        return m('div', { class: 'flex min-h-0 flex-1' }, [
            // Left Sidebar - Filters
            state.jobsIndex && m('div', { class: 'w-80 border-r border-base-300 overflow-y-auto' }, [
                m(FilterPanel)
            ]),
            
            // Main Content Area
            m('div', { class: 'flex-1 overflow-y-auto min-h-0' }, [
                m('div', { class: 'container mx-auto px-4 py-8' }, [
                    state.loading ? m(Loading) : [
                        JobsPage.renderPagination(totalPages),
                        
                        m('div', { class: 'bg-base-100 rounded-lg shadow my-4' }, [
                            jobs.length > 0 ? 
                                jobs.map((job, idx) => m(JobListItem, { 
                                    job, 
                                    index: ((JobsPage.displayPage - 1) * state.itemsPerPage) + idx + 1 
                                })) :
                                m('div', { class: 'text-center py-8 opacity-70' }, 
                                    hasActiveFilters(state.filters) || state.search ? 'No jobs match your filters. Try adjusting your criteria.' : 'No jobs found'
                                )
                        ]),
                        
                        // Bottom pagination
                        JobsPage.renderPagination(totalPages),
                        
                        // Stats footer
                        m('div', { class: 'text-center text-sm opacity-70 mt-4' }, 
                            `Showing ${jobs.length > 0 ? ((JobsPage.displayPage - 1) * state.itemsPerPage) + 1 : 0} - ${((JobsPage.displayPage - 1) * state.itemsPerPage) + jobs.length} of ${total.toLocaleString()} jobs`
                        )
                    ]
                ])
            ])
        ]);
    }
};

// Job Detail Page
const JobDetailPage = {
    job: null,
    activeTab: 'parsed',
    oninit: async (vnode) => {
        const jobId = parseInt(vnode.attrs.id);
        
        // Try to get job from database using SQL
        JobDetailPage.job = null;
        
        try {
            await DatabaseManager.init();
            
            // Query for specific job by ID
            const query = `
                SELECT 
                    jd.id,
                    t.name as title,
                    jf.name as job_function,
                    sp.name as specialization,
                    sl.name as seniority_level,
                    c.name as company,
                    cs.name as company_size,
                    ci.name as city,
                    reg.name as region,
                    cou.name as country,
                    rw.name as remote_work,
                    jd.min_salary,
                    jd.max_salary,
                    curr.code as salary_currency,
                    sper.name as salary_period,
                    et.name as employment_type,
                    ct.name as contract_type,
                    ws.name as work_schedule,
                    el.name as education_level,
                    jd.experience_years,
                    jd.posting_date,
                    jd.site,
                    jd.job_url,
                    jd.job_title as original_title,
                    jd.company_name as original_company,
                    jd.job_description as original_description,
                    ind.name as industry,
                    d.name as department,
                    jf2.name as job_family,
                    sd.name as shift_details,
                    tr.name as travel_requirements
                FROM job_details jd
                LEFT JOIN titles t ON jd.title_id = t.id
                LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
                LEFT JOIN specializations sp ON jd.specialization_id = sp.id
                LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
                LEFT JOIN companies c ON jd.company_name_id = c.id
                LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
                LEFT JOIN cities ci ON jd.city_id = ci.id
                LEFT JOIN regions reg ON jd.region_id = reg.id
                LEFT JOIN countries cou ON jd.country_id = cou.id
                LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
                LEFT JOIN currencies curr ON jd.salary_currency_id = curr.id
                LEFT JOIN salary_periods sper ON jd.salary_period_id = sper.id
                LEFT JOIN employment_types et ON jd.employment_type_id = et.id
                LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
                LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
                LEFT JOIN education_levels el ON jd.required_education_id = el.id
                LEFT JOIN industries ind ON jd.industry_id = ind.id
                LEFT JOIN departments d ON jd.department_id = d.id
                LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
                LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
                LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
                WHERE jd.id = ?
            `;
            
            const jobs = DatabaseManager.queryObjects(query, [jobId]);
            
            if (jobs.length > 0) {
                // Format the job
                JobDetailPage.job = await dbApi.formatJob(jobs[0]);
                m.redraw();
            }
        } catch (err) {
            console.error('Error loading job:', err);
        }
    },
    view: () => {
        if (!JobDetailPage.job) return m('div', { class: 'container mx-auto px-4 py-8' }, [
            m('div', { class: 'mb-4' }, [
                m('a', { 
                    href: '#!/jobs',
                    class: 'btn btn-sm btn-ghost',
                    oncreate: m.route.link
                }, '← Back to Jobs')
            ]),
            m(Loading)
        ]);
        
        const job = JobDetailPage.job;
        
        return m('div', { class: 'container mx-auto px-4 py-8' }, [
            m('div', { class: 'mb-4' }, [
                m('a', { 
                    href: '#!/jobs',
                    class: 'btn btn-sm btn-ghost',
                    oncreate: m.route.link
                }, '← Back to Jobs')
            ]),
            
            m('div', { class: 'card bg-base-100 shadow-xl' }, [
                m('div', { class: 'card-body' }, [
                    m('h1', { class: 'card-title text-2xl' }, job.title),
                    m('div', { class: 'flex flex-wrap gap-2 mb-4' }, [
                        job.company && m('span', { class: 'badge badge-primary' }, job.company),
                        job.location?.city && m('span', { class: 'badge badge-secondary' }, job.location.city),
                        job.seniority_level && m('span', { class: 'badge badge-accent' }, job.seniority_level)
                    ]),
                    
                    // Tabs
                    m('div', { class: 'tabs tabs-boxed mb-4' }, [
                        m('a', { 
                            class: `tab ${JobDetailPage.activeTab === 'parsed' ? 'tab-active' : ''}`,
                            onclick: () => JobDetailPage.activeTab = 'parsed'
                        }, 'Job Details'),
                        m('a', { 
                            class: `tab ${JobDetailPage.activeTab === 'raw' ? 'tab-active' : ''}`,
                            onclick: () => JobDetailPage.activeTab = 'raw'
                        }, 'Source Info')
                    ]),
                    
                    // Tab Content
                    JobDetailPage.activeTab === 'parsed' ? [
                        // Job Details View
                        m('div', { class: 'space-y-4' }, [
                            // Salary
                            job.salary && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Salary'),
                                m('p', formatSalary(job.salary))
                            ]),
                            
                            // Location
                            job.location && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Location'),
                                m('p', [
                                    job.location.city && m('span', job.location.city),
                                    job.location.region && m('span', `, ${job.location.region}`),
                                    job.location.country && m('span', `, ${job.location.country}`)
                                ]),
                                job.location.remote_work && m('p', [
                                    m('strong', 'Remote: '),
                                    job.location.remote_work
                                ])
                            ]),
                            
                            // Employment
                            job.employment && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Employment'),
                                job.employment.type && m('p', [m('strong', 'Type: '), job.employment.type]),
                                job.employment.contract && m('p', [m('strong', 'Contract: '), job.employment.contract]),
                                job.employment.schedule && m('p', [m('strong', 'Schedule: '), job.employment.schedule])
                            ]),
                            
                            // Requirements
                            job.requirements && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Requirements'),
                                job.requirements.education && m('p', [
                                    m('strong', 'Education: '),
                                    job.requirements.education
                                ]),
                                job.requirements.experience_years && m('p', [
                                    m('strong', 'Experience: '),
                                    `${job.requirements.experience_years} years`
                                ]),
                                job.requirements.languages && job.requirements.languages.length > 0 && m('div', [
                                    m('strong', 'Languages: '),
                                    m('div', { class: 'flex flex-wrap gap-2 mt-2' },
                                        job.requirements.languages.map(lang => 
                                            m('span', { class: 'badge badge-outline' }, lang)
                                        )
                                    )
                                ]),
                                job.requirements.hard_skills && job.requirements.hard_skills.length > 0 && m('div', [
                                    m('strong', 'Skills: '),
                                    m('div', { class: 'flex flex-wrap gap-2 mt-2' },
                                        job.requirements.hard_skills.map(skill => 
                                            m('span', { class: 'badge badge-primary' }, skill)
                                        )
                                    )
                                ]),
                                job.requirements.soft_skills && job.requirements.soft_skills.length > 0 && m('div', [
                                    m('strong', 'Soft Skills: '),
                                    m('div', { class: 'flex flex-wrap gap-2 mt-2' },
                                        job.requirements.soft_skills.map(skill => 
                                            m('span', { class: 'badge badge-secondary' }, skill)
                                        )
                                    )
                                ])
                            ]),
                            
                            // Responsibilities
                            job.parsed_view?.responsibilities && job.parsed_view.responsibilities.length > 0 && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Responsibilities'),
                                m('ul', { class: 'list-disc list-inside space-y-1' },
                                    job.parsed_view.responsibilities.map(r => m('li', r))
                                )
                            ]),
                            
                            // Benefits
                            job.benefits && job.benefits.length > 0 && m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Benefits'),
                                m('div', { class: 'flex flex-wrap gap-2' },
                                    job.benefits.map(b => m('span', { class: 'badge badge-success' }, b))
                                )
                            ])
                        ])
                    ] : [
                        // Source Info View - Show raw original job description
                        m('div', { class: 'space-y-4' }, [
                            m('div', [
                                m('h3', { class: 'font-bold mb-2' }, 'Source Information'),
                                job.source?.site && m('p', [m('strong', 'Source: '), job.source.site]),
                                job.source?.url && m('div', { class: 'mt-2' }, [
                                    m('a', { 
                                        href: job.source.url, 
                                        target: '_blank',
                                        class: 'btn btn-primary btn-sm'
                                    }, 'View Original Posting →')
                                ]),
                                job.posting_date && m('p', { class: 'mt-2' }, [
                                    m('strong', 'Posted: '), 
                                    formatDate(job.posting_date)
                                ])
                            ]),
                            // Show raw original data
                            job.raw && m('div', { class: 'mt-4' }, [
                                m('h3', { class: 'font-bold mb-2' }, 'Original Job Posting'),
                                job.raw.original_title && m('div', { class: 'mb-2' }, [
                                    m('p', { class: 'text-sm text-gray-500' }, 'Original Title:'),
                                    m('p', { class: 'font-medium' }, job.raw.original_title)
                                ]),
                                job.raw.original_company && m('div', { class: 'mb-2' }, [
                                    m('p', { class: 'text-sm text-gray-500' }, 'Original Company:'),
                                    m('p', { class: 'font-medium' }, job.raw.original_company)
                                ]),
                                job.raw.original_description && m('div', { class: 'mt-4' }, [
                                    m('p', { class: 'text-sm text-gray-500 mb-2' }, 'Original Description:'),
                                    m('div', { class: 'bg-base-200 p-4 rounded-lg max-h-96 overflow-y-auto' }, [
                                        m('pre', { class: 'whitespace-pre-wrap text-sm' }, job.raw.original_description)
                                    ])
                                ])
                            ])
                        ])
                    ]
                ])
            ])
        ]);
    }
};

// Helper object for field name mapping (backward compatibility)
const FieldMapping = {
    map: {
        'function': ['function'],
        'seniority': ['seniority', 'seniority_level'],
        'location': ['location', 'city'],
        'size': ['size', 'company_size'],
        'education': ['education', 'education_level']
    },
    getValue: (item, fieldName) => {
        if (FieldMapping.map[fieldName]) {
            for (const field of FieldMapping.map[fieldName]) {
                if (field in item && item[field] !== null && item[field] !== undefined) {
                    return item[field];
                }
            }
        }
        return item[fieldName];
    },
    extractLabel: (item) => {
        // Try known field mappings first
        for (const fieldName of ['function', 'seniority', 'location', 'size', 'education']) {
            const value = FieldMapping.getValue(item, fieldName);
            if (value !== null && value !== undefined) return value;
        }
        // Fallback to other common fields
        return item.employment_type || item.remote_option || 
               item.benefit || item.name || item.skill || 
               item.company || 'Unknown';
    }
};

// Chart Helper Functions
const ChartHelpers = {
    createChart: (canvas, config) => {
        if (!canvas) return null;
        // Destroy existing chart if present
        if (canvas.chart) {
            canvas.chart.destroy();
        }
        canvas.chart = new Chart(canvas, config);
        return canvas.chart;
    },
    destroyChart: (canvas) => {
        if (canvas && canvas.chart) {
            canvas.chart.destroy();
            canvas.chart = null;
        }
    },
    formatTitle: (key) => {
        // Remove 'by_' prefix and format title
        return key.includes('by_') ? 
            key.replace('by_', '').replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) :
            key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    },
    extractLabel: (item) => {
        // Use centralized field mapping for consistency
        return FieldMapping.extractLabel(item);
    },
    generateColors: (count) => {
        // Generate an array of colors for charts
        return Array.from({ length: count }, (_, i) => {
            const hue = (i * 360 / count);
            return `hsla(${hue}, 70%, 60%, 0.7)`;
        });
    }
};

// Analysis Page
const AnalysisPage = {
    // Helper function to get field value with fallback for backward compatibility
    getFieldValue: (item, fieldName) => {
        return FieldMapping.getValue(item, fieldName);
    },
    // Get preview text for analysis based on its type
    getPreviewText: (analysis) => {
        const previewMap = {
            'salary-overview': 'Overall salary statistics across all jobs with distribution ranges',
            'salary-by-function': 'Salary breakdown by different job functions and roles',
            'salary-by-seniority': 'Salary progression across seniority levels from entry to executive',
            'salary-by-location': 'Salary comparison across different cities and regions',
            'salary-by-company-size': 'How company size impacts salary ranges',
            'salary-by-education': 'Salary correlation with education level requirements',
            'skills-demand': 'Most in-demand skills in the job market',
            'skills-salary': 'Skills that command the highest salaries',
            'skill-combinations': 'Common skill pairings in job postings',
            'employment-types': 'Distribution of full-time, part-time, and contract positions',
            'remote-work': 'Remote work availability and trends',
            'benefits': 'Most frequently offered employee benefits',
            'requirements': 'Common job requirements and qualifications',
            'top-companies': 'Companies posting the most jobs',
            'posting-trends': 'Job posting volume over time',
            'salary-trends': 'Salary changes and trends over time',
            'skills-trends': 'Evolving skill demand over time',
            'remote-work-trends': 'Remote work adoption trends',
            'job-duration': 'How long job postings remain active',
            'market-health': 'Overall job market health indicators',
            'salary-by-hierarchy': 'Salary structure across organizational hierarchy'
        };
        return previewMap[analysis.id] || 'Detailed analysis with visualizations and statistics';
    },
    // Render mini chart preview for analysis card
    renderMiniChart: (analysis) => {
        if (!analysis.previewData || analysis.previewData.error) {
            return m('div', { class: 'flex items-center justify-center h-32 text-xs opacity-60' }, 
                'Loading preview...'
            );
        }
        
        const data = analysis.previewData;
        
        // Create mini chart based on data type
        return m('div', { class: 'h-32' }, [
            m('canvas', {
                oncreate: (vnode) => {
                    AnalysisPage.createMiniChart(vnode.dom, data, analysis.id);
                },
                onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
            })
        ]);
    },
    // Create mini chart for preview
    createMiniChart: (canvas, data, analysisId) => {
        let chartConfig = null;
        
        // Distribution-based analyses (bar chart)
        if (data.distribution && data.distribution.length > 0) {
            const items = data.distribution.slice(0, 5);
            chartConfig = {
                type: 'bar',
                data: {
                    labels: items.map(item => item.range || `${item.min}-${item.max}`),
                    datasets: [{
                        data: items.map(item => item.count),
                        backgroundColor: 'rgba(99, 102, 241, 0.7)',
                        borderColor: 'rgba(99, 102, 241, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { display: false },
                        x: { display: false }
                    }
                }
            };
        }
        // Breakdown analyses (top items - horizontal bar)
        else if (data.by_function || data.by_seniority || data.by_location || data.by_company_size || data.by_education) {
            const breakdownKey = data.by_function ? 'by_function' : 
                                data.by_seniority ? 'by_seniority' : 
                                data.by_location ? 'by_location' : 
                                data.by_company_size ? 'by_company_size' : 'by_education';
            const items = data[breakdownKey].slice(0, 5);
            
            chartConfig = {
                type: 'bar',
                data: {
                    labels: items.map(item => FieldMapping.extractLabel(item)),
                    datasets: [{
                        data: items.map(item => item.average || item.count),
                        backgroundColor: 'rgba(168, 85, 247, 0.7)',
                        borderColor: 'rgba(168, 85, 247, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { display: false }
                    }
                }
            };
        }
        // Top items (skills, companies, benefits)
        else if (data.top_skills || data.top_companies || data.top_benefits) {
            const itemsKey = data.top_skills ? 'top_skills' : data.top_companies ? 'top_companies' : 'top_benefits';
            const items = data[itemsKey].slice(0, 5);
            
            chartConfig = {
                type: 'bar',
                data: {
                    labels: items.map(item => item.name || item.skill || item.benefit || item.company),
                    datasets: [{
                        data: items.map(item => item.count || item.job_count),
                        backgroundColor: 'rgba(34, 197, 94, 0.7)',
                        borderColor: 'rgba(34, 197, 94, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { display: false }
                    }
                }
            };
        }
        // Time series data (line chart) - check for various time series field names
        else if (data.time_series || data.trends || data.salary_trends || data.market_trends) {
            const series = data.time_series || data.trends || data.salary_trends || data.market_trends;
            const items = series.slice(0, 10);
            
            chartConfig = {
                type: 'line',
                data: {
                    labels: items.map(item => item.date || item.period),
                    datasets: [{
                        data: items.map(item => item.count || item.new_jobs || item.average),
                        borderColor: 'rgba(59, 130, 246, 1)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { display: false },
                        x: { display: false }
                    }
                }
            };
        }
        // Skills-salary (bubble style with bars)
        else if (data.skills_salary || data.top_10_highest_paying) {
            const items = (data.top_10_highest_paying || data.skills_salary).slice(0, 5);
            
            chartConfig = {
                type: 'bar',
                data: {
                    labels: items.map(item => item.skill),
                    datasets: [{
                        data: items.map(item => item.average),
                        backgroundColor: 'rgba(234, 179, 8, 0.7)',
                        borderColor: 'rgba(234, 179, 8, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { display: false }
                    }
                }
            };
        }
        // Employment types, remote work (doughnut for categorical data)
        else if (data.employment_types || data.remote_options) {
            const itemsKey = data.employment_types ? 'employment_types' : 'remote_options';
            const items = data[itemsKey].slice(0, 4);
            
            chartConfig = {
                type: 'doughnut',
                data: {
                    labels: items.map(item => item.type || item.option),
                    datasets: [{
                        data: items.map(item => item.count),
                        backgroundColor: [
                            'rgba(99, 102, 241, 0.7)',
                            'rgba(168, 85, 247, 0.7)',
                            'rgba(34, 197, 94, 0.7)',
                            'rgba(234, 179, 8, 0.7)'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    cutout: '60%'
                }
            };
        }
        // Overall stats (simple stat display)
        else if (data.overall) {
            const stats = data.overall;
            chartConfig = {
                type: 'bar',
                data: {
                    labels: ['Min', '25%', 'Avg', 'Median', '75%', 'Max'],
                    datasets: [{
                        data: [
                            stats.min || 0,
                            stats.percentile_25 || 0,
                            stats.average || 0,
                            stats.median || 0,
                            stats.percentile_75 || 0,
                            stats.max || 0
                        ],
                        backgroundColor: 'rgba(239, 68, 68, 0.7)',
                        borderColor: 'rgba(239, 68, 68, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { display: false },
                        x: { display: false }
                    }
                }
            };
        }
        // Education requirements (bar chart)
        else if (data.education_requirements && data.education_requirements.length > 0) {
            const items = data.education_requirements.slice(0, 5);
            chartConfig = {
                type: 'bar',
                data: {
                    labels: items.map(item => item.education_level || item.education),
                    datasets: [{
                        data: items.map(item => item.count),
                        backgroundColor: 'rgba(168, 85, 247, 0.7)',
                        borderColor: 'rgba(168, 85, 247, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { display: false }
                    }
                }
            };
        }
        // Duration distribution
        else if (data.duration_distribution && data.duration_distribution.length > 0) {
            const items = data.duration_distribution.slice(0, 5);
            chartConfig = {
                type: 'bar',
                data: {
                    labels: items.map(item => item.range),
                    datasets: [{
                        data: items.map(item => item.count),
                        backgroundColor: 'rgba(99, 102, 241, 0.7)',
                        borderColor: 'rgba(99, 102, 241, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { display: false },
                        x: { display: false }
                    }
                }
            };
        }
        // Hierarchy tree (horizontal bar for top levels)
        else if (data.tree && data.tree.length > 0) {
            const items = data.tree.slice(0, 5);
            chartConfig = {
                type: 'bar',
                data: {
                    labels: items.map(item => item.name),
                    datasets: [{
                        data: items.map(item => item.average_salary || item.count),
                        backgroundColor: 'rgba(234, 179, 8, 0.7)',
                        borderColor: 'rgba(234, 179, 8, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { display: false }
                    }
                }
            };
        }
        // Remote work trends (stacked area approximation with line chart)
        else if (data.remote_trends && data.remote_trends.length > 0) {
            const items = data.remote_trends.slice(0, 10);
            chartConfig = {
                type: 'line',
                data: {
                    labels: items.map(item => item.period),
                    datasets: [{
                        label: 'Remote',
                        data: items.map(item => item.remote?.count || 0),
                        borderColor: 'rgba(34, 197, 94, 1)',
                        backgroundColor: 'rgba(34, 197, 94, 0.3)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { display: false },
                        x: { display: false }
                    }
                }
            };
        }
        // Skill trends (complex - show first skill's trend)
        else if (data.skill_trends && Object.keys(data.skill_trends).length > 0) {
            const firstSkill = Object.keys(data.skill_trends)[0];
            const skillData = data.skill_trends[firstSkill];
            if (Array.isArray(skillData) && skillData.length > 0) {
                const items = skillData.slice(0, 10);
                chartConfig = {
                    type: 'line',
                    data: {
                        labels: items.map(item => item.period),
                        datasets: [{
                            data: items.map(item => item.count),
                            borderColor: 'rgba(168, 85, 247, 1)',
                            backgroundColor: 'rgba(168, 85, 247, 0.1)',
                            fill: true,
                            tension: 0.4,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { display: false },
                            x: { display: false }
                        }
                    }
                };
            }
        }
        // Duration stats as fallback
        else if (data.duration_stats) {
            const stats = data.duration_stats;
            chartConfig = {
                type: 'bar',
                data: {
                    labels: ['Min', '25%', 'Avg', 'Median', '75%', 'Max'],
                    datasets: [{
                        data: [
                            stats.min || 0,
                            stats.percentile_25 || 0,
                            stats.average || 0,
                            stats.median || 0,
                            stats.percentile_75 || 0,
                            stats.max || 0
                        ],
                        backgroundColor: 'rgba(59, 130, 246, 0.7)',
                        borderColor: 'rgba(59, 130, 246, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { display: false },
                        x: { display: false }
                    }
                }
            };
        }
        
        if (chartConfig) {
            ChartHelpers.createChart(canvas, chartConfig);
        }
    },
    oninit: () => {
        api.getAnalysisIndex().then(data => {
            state.analysisIndex = data;
            // Load preview data for each analysis
            if (data.analyses) {
                data.analyses.forEach(analysis => {
                    analysis.previewData = null; // Initialize
                    api.getAnalysis(`${analysis.id}.json`).then(response => {
                        analysis.previewData = response.data || response;
                        m.redraw();
                    }).catch(err => {
                        console.error(`Error loading preview for ${analysis.id}:`, err);
                    });
                });
            }
        }).catch(err => {
            console.error('Error loading analysis index:', err);
            state.analysisIndex = { error: true };
        });
    },
    renderDistributionChart: (data) => {
        if (!data || !data.distribution || data.distribution.length === 0) return null;
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body' }, [
                m('h3', { class: 'card-title' }, 'Distribution Chart'),
                m('div', { class: 'chart-container' }, [
                    m('canvas', {
                        oncreate: (vnode) => {
                            const labels = data.distribution.map(item => item.range || `${item.min}-${item.max}`);
                            const values = data.distribution.map(item => item.count);
                            
                            ChartHelpers.createChart(vnode.dom, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Number of Jobs',
                                        data: values,
                                        backgroundColor: 'rgba(99, 102, 241, 0.7)',
                                        borderColor: 'rgba(99, 102, 241, 1)',
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            ticks: {
                                                precision: 0
                                            }
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: false
                                        },
                                        tooltip: {
                                            callbacks: {
                                                afterLabel: (context) => {
                                                    const item = data.distribution[context.dataIndex];
                                                    return item.percentage ? `${item.percentage.toFixed(1)}% of total` : '';
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        },
                        onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                    })
                ])
            ])
        ]);
    },
    renderTimeSeriesChart: (data) => {
        if (!data || !data.time_series || data.time_series.length === 0) {
            if (!data || !data.trends || data.trends.length === 0) return null;
            // Use trends if time_series is not available
            const trends = data.trends;
            
            return m('div', { class: 'card bg-base-100 shadow-xl' }, [
                m('div', { class: 'card-body' }, [
                    m('h3', { class: 'card-title' }, 'Trend Over Time'),
                    m('div', { class: 'chart-container' }, [
                        m('canvas', {
                            oncreate: (vnode) => {
                                const labels = trends.map(item => item.date || item.period);
                                const newJobs = trends.map(item => item.new_jobs || item.count || 0);
                                const closedJobs = trends.map(item => item.closed_jobs || 0);
                                
                                const datasets = [{
                                    label: 'New Jobs',
                                    data: newJobs,
                                    borderColor: 'rgba(34, 197, 94, 1)',
                                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                                    fill: true,
                                    tension: 0.4
                                }];
                                
                                if (closedJobs.some(v => v > 0)) {
                                    datasets.push({
                                        label: 'Closed Jobs',
                                        data: closedJobs,
                                        borderColor: 'rgba(239, 68, 68, 1)',
                                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                        fill: true,
                                        tension: 0.4
                                    });
                                }
                                
                                ChartHelpers.createChart(vnode.dom, {
                                    type: 'line',
                                    data: {
                                        labels: labels,
                                        datasets: datasets
                                    },
                                    options: {
                                        responsive: true,
                                        maintainAspectRatio: false,
                                        scales: {
                                            y: {
                                                beginAtZero: true,
                                                ticks: {
                                                    precision: 0
                                                }
                                            }
                                        },
                                        plugins: {
                                            legend: {
                                                display: datasets.length > 1
                                            }
                                        }
                                    }
                                });
                            },
                            onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                        })
                    ])
                ])
            ]);
        }
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body' }, [
                m('h3', { class: 'card-title' }, 'Trend Over Time'),
                m('div', { class: 'chart-container' }, [
                    m('canvas', {
                        oncreate: (vnode) => {
                            const labels = data.time_series.map(item => item.date || item.period);
                            const values = data.time_series.map(item => item.average || item.count || 0);
                            
                            ChartHelpers.createChart(vnode.dom, {
                                type: 'line',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Average',
                                        data: values,
                                        borderColor: 'rgba(99, 102, 241, 1)',
                                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                                        fill: true,
                                        tension: 0.4
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: false
                                        }
                                    }
                                }
                            });
                        },
                        onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                    })
                ])
            ])
        ]);
    },
    renderTopItemsChart: (data, key, title) => {
        const items = data[key];
        if (!items || items.length === 0) return null;
        
        const topItems = items.slice(0, 15); // Show top 15
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body' }, [
                m('h3', { class: 'card-title' }, title),
                m('div', { class: 'chart-container' }, [
                    m('canvas', {
                        oncreate: (vnode) => {
                            const labels = topItems.map(item => ChartHelpers.extractLabel(item));
                            const values = topItems.map(item => item.count);
                            
                            ChartHelpers.createChart(vnode.dom, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Count',
                                        data: values,
                                        backgroundColor: 'rgba(168, 85, 247, 0.7)',
                                        borderColor: 'rgba(168, 85, 247, 1)',
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    indexAxis: 'y', // Horizontal bars
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        x: {
                                            beginAtZero: true,
                                            ticks: {
                                                precision: 0
                                            }
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: false
                                        },
                                        tooltip: {
                                            callbacks: {
                                                afterLabel: (context) => {
                                                    const item = topItems[context.dataIndex];
                                                    return item.percentage ? `${item.percentage.toFixed(1)}% of total` : '';
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        },
                        onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                    })
                ])
            ])
        ]);
    },
    renderEducationChart: (data) => {
        if (!data || !data.by_education || data.by_education.length === 0) return null;
        
        const items = data.by_education;
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body' }, [
                m('h3', { class: 'card-title' }, 'Salary by Education Level'),
                
                // Statistics cards
                m('div', { class: 'grid grid-cols-2 md:grid-cols-4 gap-2 mb-4' }, 
                    items.map(item => 
                        m('div', { class: 'stat bg-base-200 rounded-lg p-2' }, [
                            m('div', { class: 'stat-title text-xs' }, AnalysisPage.getFieldValue(item, 'education')),
                            m('div', { class: 'stat-value text-sm' }, `${Math.round(item.average || 0).toLocaleString()}`),
                            m('div', { class: 'stat-desc text-xs' }, `${item.count} jobs`)
                        ])
                    )
                ),
                
                // Bar chart with grouped data
                m('div', { class: 'chart-container' }, [
                    m('canvas', {
                        oncreate: (vnode) => {
                            const labels = items.map(item => AnalysisPage.getFieldValue(item, 'education'));
                            const avgSalaries = items.map(item => Math.round(item.average || 0));
                            const medianSalaries = items.map(item => Math.round(item.median || 0));
                            
                            ChartHelpers.createChart(vnode.dom, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Average Salary',
                                        data: avgSalaries,
                                        backgroundColor: 'rgba(99, 102, 241, 0.7)',
                                        borderColor: 'rgba(99, 102, 241, 1)',
                                        borderWidth: 1
                                    }, {
                                        label: 'Median Salary',
                                        data: medianSalaries,
                                        backgroundColor: 'rgba(168, 85, 247, 0.7)',
                                        borderColor: 'rgba(168, 85, 247, 1)',
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            ticks: {
                                                callback: (value) => `${value.toLocaleString()} MDL`
                                            }
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: true,
                                            position: 'top'
                                        },
                                        tooltip: {
                                            callbacks: {
                                                label: (context) => {
                                                    const item = items[context.dataIndex];
                                                    const label = context.dataset.label || '';
                                                    const value = context.parsed.y;
                                                    return [
                                                        `${label}: ${value.toLocaleString()} MDL`,
                                                        `Jobs: ${item.count}`,
                                                        `Min: ${Math.round(item.min || 0).toLocaleString()} MDL`,
                                                        `Max: ${Math.round(item.max || 0).toLocaleString()} MDL`
                                                    ];
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        },
                        onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                    })
                ])
            ])
        ]);
    },
    renderSkillsSalaryChart: (data) => {
        if (!data || !data.top_10_highest_paying || data.top_10_highest_paying.length === 0) return null;
        
        const skills = data.top_10_highest_paying;
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body' }, [
                m('h3', { class: 'card-title' }, 'Top 10 Highest Paying Skills'),
                m('p', { class: 'text-sm text-gray-600 mb-4' }, 'Skills with the highest average salaries'),
                
                // Horizontal bar chart with statistics
                m('div', { class: 'chart-container' }, [
                    m('canvas', {
                        oncreate: (vnode) => {
                            const labels = skills.map(item => item.skill);
                            const averages = skills.map(item => Math.round(item.average || 0));
                            const medians = skills.map(item => Math.round(item.median || 0));
                            
                            ChartHelpers.createChart(vnode.dom, {
                                type: 'bar',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Average Salary',
                                        data: averages,
                                        backgroundColor: 'rgba(34, 197, 94, 0.7)',
                                        borderColor: 'rgba(34, 197, 94, 1)',
                                        borderWidth: 1
                                    }, {
                                        label: 'Median Salary',
                                        data: medians,
                                        backgroundColor: 'rgba(59, 130, 246, 0.7)',
                                        borderColor: 'rgba(59, 130, 246, 1)',
                                        borderWidth: 1
                                    }]
                                },
                                options: {
                                    indexAxis: 'y',
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    scales: {
                                        x: {
                                            beginAtZero: true,
                                            ticks: {
                                                callback: (value) => `${value.toLocaleString()} MDL`
                                            }
                                        }
                                    },
                                    plugins: {
                                        legend: {
                                            display: true,
                                            position: 'top'
                                        },
                                        tooltip: {
                                            callbacks: {
                                                label: (context) => {
                                                    const item = skills[context.dataIndex];
                                                    const label = context.dataset.label || '';
                                                    const value = context.parsed.x;
                                                    return [
                                                        `${label}: ${value.toLocaleString()} MDL`,
                                                        `Jobs: ${item.count}`,
                                                        `Min: ${Math.round(item.min || 0).toLocaleString()} MDL`,
                                                        `Max: ${Math.round(item.max || 0).toLocaleString()} MDL`,
                                                        `25th percentile: ${Math.round(item.percentile_25 || 0).toLocaleString()} MDL`,
                                                        `75th percentile: ${Math.round(item.percentile_75 || 0).toLocaleString()} MDL`
                                                    ];
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        },
                        onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                    })
                ])
            ])
        ]);
    },
    renderBreakdownChart: (data) => {
        // Check for various breakdown formats
        const breakdownKey = data.by_function ? 'by_function' : 
                            data.by_seniority ? 'by_seniority' : 
                            data.by_location ? 'by_location' : 
                            data.by_company_size ? 'by_company_size' : 
                            data.by_education ? 'by_education' : 
                            data.employment_types ? 'employment_types' :
                            data.remote_options ? 'remote_options' :
                            data.education_requirements ? 'education_requirements' :
                            data.top_benefits ? 'top_benefits' : null;
        
        if (!breakdownKey || !data[breakdownKey] || data[breakdownKey].length === 0) return null;
        
        // Skip education - it has specialized rendering
        if (breakdownKey === 'by_education') return null;
        
        const items = data[breakdownKey].slice(0, 10); // Top 10
        const title = ChartHelpers.formatTitle(breakdownKey);
        
        return m('div', { class: 'card bg-base-100 shadow-xl' }, [
            m('div', { class: 'card-body' }, [
                m('h3', { class: 'card-title' }, `${title}`),
                m('div', { class: 'chart-container' }, [
                    m('canvas', {
                        oncreate: (vnode) => {
                            const labels = items.map(item => ChartHelpers.extractLabel(item));
                            const values = items.map(item => item.count);
                            const backgroundColors = ChartHelpers.generateColors(items.length);
                            
                            ChartHelpers.createChart(vnode.dom, {
                                type: 'doughnut',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        data: values,
                                        backgroundColor: backgroundColors,
                                        borderWidth: 2,
                                        borderColor: '#fff'
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: {
                                        legend: {
                                            position: 'right',
                                            labels: {
                                                boxWidth: 12,
                                                font: {
                                                    size: 11
                                                }
                                            }
                                        },
                                        tooltip: {
                                            callbacks: {
                                                label: (context) => {
                                                    const item = items[context.dataIndex];
                                                    const label = context.label || '';
                                                    const count = item.count || 0;
                                                    const percentage = item.percentage ? ` (${item.percentage.toFixed(1)}%)` : '';
                                                    const avg = item.average ? ` (Avg: ${Math.round(item.average).toLocaleString()} MDL)` : '';
                                                    return `${label}: ${count}${percentage}${avg}`;
                                                }
                                            }
                                        }
                                    }
                                }
                            });
                        },
                        onremove: (vnode) => ChartHelpers.destroyChart(vnode.dom)
                    })
                ])
            ])
        ]);
    },
    renderAnalysisData: (data) => {
        if (!data) return m(Loading);
        if (data.error) return m('div', { class: 'alert alert-error' }, data.error);
        
        // Render based on analysis type - CHARTS FIRST, then tables as fallback
        return m('div', { class: 'space-y-6' }, [
            // Overall stats if present
            data.overall && m('div', { class: 'stats stats-vertical lg:stats-horizontal shadow w-full' }, [
                data.overall.count && m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Sample Size'),
                    m('div', { class: 'stat-value text-primary' }, data.overall.count.toLocaleString())
                ]),
                data.overall.average && m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Average'),
                    m('div', { class: 'stat-value' }, `${Math.round(data.overall.average).toLocaleString()} ${data.overall.currency || 'MDL'}`)
                ]),
                data.overall.median && m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Median'),
                    m('div', { class: 'stat-value' }, `${Math.round(data.overall.median).toLocaleString()} ${data.overall.currency || 'MDL'}`)
                ]),
                data.overall.min && m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Range'),
                    m('div', { class: 'stat-value text-sm' }, 
                        `${Math.round(data.overall.min).toLocaleString()} - ${Math.round(data.overall.max).toLocaleString()}`)
                ])
            ]),
            
            // === CHARTS FIRST (Primary Visualizations) ===
            
            // Distribution chart (if available)
            AnalysisPage.renderDistributionChart(data),
            
            // Time series chart (for temporal data)
            AnalysisPage.renderTimeSeriesChart(data),
            
            // Top items charts (skills, companies, etc.)
            data.top_skills && AnalysisPage.renderTopItemsChart(data, 'top_skills', 'Top In-Demand Skills'),
            data.top_companies && AnalysisPage.renderTopItemsChart(data, 'top_companies', 'Top Companies'),
            data.top_benefits && AnalysisPage.renderTopItemsChart(data, 'top_benefits', 'Most Common Benefits'),
            
            // Specialized skills-salary visualization
            data.skills_salary && AnalysisPage.renderSkillsSalaryChart(data),
            
            // Requirements charts
            data.education_requirements && AnalysisPage.renderBreakdownChart({ education_requirements: data.education_requirements }),
            data.experience_requirements && AnalysisPage.renderDistributionChart({ distribution: data.experience_requirements }),
            
            // Education level - specialized bar chart with statistics
            data.by_education && AnalysisPage.renderEducationChart(data),
            
            // Breakdown pie chart (general)
            AnalysisPage.renderBreakdownChart(data),
            
            // === TABLES AS FALLBACK (Collapsible for detail) ===
            
            // Distribution table (detailed view, collapsed by default)
            data.distribution && m('details', { class: 'collapse collapse-arrow bg-base-100 shadow-xl' }, [
                m('summary', { class: 'collapse-title font-bold text-lg' }, 'Distribution Table (Detailed)'),
                m('div', { class: 'collapse-content' }, [
                    m('div', { class: 'overflow-x-auto' }, [
                        m('table', { class: 'table table-zebra' }, [
                            m('thead', [
                                m('tr', [
                                    m('th', 'Range'),
                                    m('th', 'Count'),
                                    m('th', 'Percentage'),
                                    m('th', 'Visual')
                                ])
                            ]),
                            m('tbody', 
                                data.distribution.map(item => 
                                    m('tr', [
                                        m('td', item.range || `${item.min}-${item.max}`),
                                        m('td', item.count.toLocaleString()),
                                        m('td', `${item.percentage?.toFixed(1) || '0'}%`),
                                        m('td', [
                                            m('progress', { 
                                                class: 'progress progress-primary w-32', 
                                                value: item.percentage || 0, 
                                                max: 100 
                                            })
                                        ])
                                    ])
                                )
                            )
                        ])
                    ])
                ])
            ]),
            
            // Breakdown table (collapsed by default)
            (data.by_function || data.by_seniority || data.by_location || data.by_company_size || data.by_education) && 
            m('details', { class: 'collapse collapse-arrow bg-base-100 shadow-xl' }, [
                m('summary', { class: 'collapse-title font-bold text-lg' }, 'Breakdown Table (Detailed)'),
                m('div', { class: 'collapse-content' }, [
                    m('div', { class: 'overflow-x-auto' }, [
                        m('table', { class: 'table table-zebra' }, [
                            m('thead', [
                                m('tr', [
                                    m('th', 'Category'),
                                    m('th', 'Count'),
                                    m('th', 'Average'),
                                    m('th', 'Median')
                                ])
                            ]),
                            m('tbody', 
                                (data.by_function || data.by_seniority || data.by_location || data.by_company_size || data.by_education || []).map(item => 
                                    m('tr', [
                                        m('td', { class: 'font-medium' }, 
                                            item.function || item.seniority || item.location || item.size || item.education || item.name
                                        ),
                                        m('td', item.count?.toLocaleString() || 'N/A'),
                                        m('td', item.average ? `${Math.round(item.average).toLocaleString()} MDL` : 'N/A'),
                                        m('td', item.median ? `${Math.round(item.median).toLocaleString()} MDL` : 'N/A')
                                    ])
                                )
                            )
                        ])
                    ])
                ])
            ]),
            
            // Top skills/companies table (collapsed by default)
            (data.top_skills || data.top_companies) && m('details', { class: 'collapse collapse-arrow bg-base-100 shadow-xl' }, [
                m('summary', { class: 'collapse-title font-bold text-lg' }, data.top_skills ? 'Top Skills Table (Detailed)' : 'Top Companies Table (Detailed)'),
                m('div', { class: 'collapse-content' }, [
                    m('div', { class: 'overflow-x-auto' }, [
                        m('table', { class: 'table table-zebra' }, [
                            m('thead', [
                                m('tr', [
                                    m('th', '#'),
                                    m('th', 'Name'),
                                    m('th', 'Count'),
                                    m('th', 'Percentage')
                                ])
                            ]),
                            m('tbody', 
                                (data.top_skills || data.top_companies || []).slice(0, 20).map((item, idx) => 
                                    m('tr', [
                                        m('td', idx + 1),
                                        m('td', { class: 'font-medium' }, item.name || item.skill || item.company),
                                        m('td', item.count?.toLocaleString() || 'N/A'),
                                        m('td', [
                                            m('progress', { 
                                                class: 'progress progress-secondary w-24', 
                                                value: item.percentage || 0, 
                                                max: 100 
                                            }),
                                            m('span', { class: 'text-xs ml-2' }, `${item.percentage?.toFixed(1) || 0}%`)
                                        ])
                                    ])
                                )
                            )
                        ])
                    ])
                ])
            ]),
            
            // Time series table (collapsed by default)
            data.time_series && m('details', { class: 'collapse collapse-arrow bg-base-100 shadow-xl' }, [
                m('summary', { class: 'collapse-title font-bold text-lg' }, 'Time Series Table (Detailed)'),
                m('div', { class: 'collapse-content' }, [
                    m('div', { class: 'overflow-x-auto' }, [
                        m('table', { class: 'table table-sm' }, [
                            m('thead', [
                                m('tr', [
                                    m('th', 'Date'),
                                    m('th', 'Count'),
                                    m('th', 'Average'),
                                    m('th', 'Change')
                                ])
                            ]),
                            m('tbody', 
                                data.time_series.map((item, idx) => {
                                    const prevItem = idx > 0 ? data.time_series[idx - 1] : null;
                                    const change = prevItem && item.average && prevItem.average ? 
                                        ((item.average - prevItem.average) / prevItem.average * 100).toFixed(1) : null;
                                    return m('tr', [
                                        m('td', item.date || item.period),
                                        m('td', item.count?.toLocaleString() || 'N/A'),
                                        m('td', item.average ? Math.round(item.average).toLocaleString() : 'N/A'),
                                        m('td', change ? [
                                            m('span', { 
                                                class: change > 0 ? 'text-success' : 'text-error' 
                                            }, `${change > 0 ? '+' : ''}${change}%`)
                                        ] : '-')
                                    ]);
                                })
                            )
                        ])
                    ])
                ])
            ]),
            
            // Skill combinations table (if present)
            data.top_combinations && m('details', { class: 'collapse collapse-arrow bg-base-100 shadow-xl' }, [
                m('summary', { class: 'collapse-title font-bold text-lg' }, 'Skill Combinations (Detailed)'),
                m('div', { class: 'collapse-content' }, [
                    m('div', { class: 'overflow-x-auto' }, [
                        m('table', { class: 'table table-zebra' }, [
                            m('thead', [
                                m('tr', [
                                    m('th', 'Skill 1'),
                                    m('th', 'Skill 2'),
                                    m('th', 'Count')
                                ])
                            ]),
                            m('tbody', 
                                data.top_combinations.slice(0, 30).map(item => 
                                    m('tr', [
                                        m('td', { class: 'font-medium' }, item.skill1),
                                        m('td', { class: 'font-medium' }, item.skill2),
                                        m('td', item.count?.toLocaleString() || 'N/A')
                                    ])
                                )
                            )
                        ])
                    ])
                ])
            ]),
            
            // Raw JSON view (collapsible)
            m('details', { class: 'collapse collapse-arrow bg-base-200' }, [
                m('summary', { class: 'collapse-title font-medium' }, 'View Raw JSON'),
                m('div', { class: 'collapse-content' }, [
                    m('pre', { class: 'bg-base-300 p-4 rounded text-xs overflow-x-auto' }, 
                        JSON.stringify(data, null, 2)
                    )
                ])
            ])
        ]);
    },
    view: () => m('div', { class: 'container mx-auto px-4 py-8' }, [
        m('h1', { class: 'text-3xl font-bold mb-6' }, 'Job Market Analysis'),
        
        state.analysisIndex ? [
            !state.analysisIndex.error && state.analysisIndex.data_summary && m('div', { class: 'stats shadow mb-6 w-full' }, [
                m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Total Jobs Analyzed'),
                    m('div', { class: 'stat-value' }, state.analysisIndex.data_summary.total_jobs?.toLocaleString() || 'N/A')
                ]),
                m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Date Range'),
                    m('div', { class: 'stat-value text-2xl' }, 
                        state.analysisIndex.data_summary.date_range ? 
                            `${formatDate(state.analysisIndex.data_summary.date_range.start)} - ${formatDate(state.analysisIndex.data_summary.date_range.end)}` :
                            'N/A'
                    )
                ]),
                m('div', { class: 'stat' }, [
                    m('div', { class: 'stat-title' }, 'Jobs with Salary'),
                    m('div', { class: 'stat-value' }, state.analysisIndex.data_summary.jobs_with_salary?.toLocaleString() || 'N/A')
                ])
            ]),
            
            state.analysisIndex.error ? 
                m('div', { class: 'alert alert-warning mb-6' }, [
                    m('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', class: 'stroke-current shrink-0 w-6 h-6' }, [
                        m('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' })
                    ]),
                    m('span', 'Analysis data not yet generated. Run: python -m json_generator --output frontend/api')
                ]) :
                m('div', { class: 'alert alert-info mb-6' }, [
                    m('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', class: 'stroke-current shrink-0 w-6 h-6' }, [
                        m('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
                    ]),
                    m('span', `${state.analysisIndex.analyses?.length || 0} analyses available. Click "View" to see data visualizations.`)
                ]),
            
            state.analysisIndex.analyses && m('div', { class: 'grid grid-cols-1 lg:grid-cols-2 gap-4' },
                state.analysisIndex.analyses.map((analysis, idx) => 
                    m('a', { 
                        href: `#!/analysis/${analysis.id}`,
                        oncreate: m.route.link,
                        class: 'card bg-base-100 shadow-lg hover:shadow-xl transition-shadow cursor-pointer border border-base-300'
                    }, [
                        m('div', { class: 'card-body p-4' }, [
                            // Header with number and title
                            m('div', { class: 'flex items-start gap-2 mb-2' }, [
                                m('span', { class: 'text-sm opacity-60 mt-1' }, `${idx + 1}.`),
                                m('h3', { class: 'card-title text-base flex-1' }, analysis.title)
                            ]),
                            
                            // Badges
                            m('div', { class: 'flex flex-wrap gap-2 mb-3' }, [
                                m('span', { class: 'badge badge-ghost badge-sm' }, analysis.id),
                                analysis.temporal && m('span', { class: 'badge badge-secondary badge-sm' }, 'Time Series'),
                                analysis.type && m('span', { class: 'badge badge-outline badge-sm' }, analysis.type)
                            ]),
                            
                            // Preview section with mini chart
                            m('div', { class: 'bg-base-200 rounded-lg p-3 mt-2' }, [
                                m('div', { class: 'flex items-center justify-between mb-2' }, [
                                    m('span', { class: 'text-xs opacity-70' }, 'Quick Preview'),
                                    m('div', { class: 'flex items-center gap-1 text-primary' }, [
                                        m('svg', { xmlns: 'http://www.w3.org/2000/svg', class: 'h-4 w-4', fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
                                            m('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' })
                                        ]),
                                        m('span', { class: 'text-xs font-medium' }, 'Click for details')
                                    ])
                                ]),
                                AnalysisPage.renderMiniChart(analysis)
                            ])
                        ])
                    ])
                )
            )
        ] : m(Loading)
    ])
};

// Analysis Detail Page (Full Page View)
const AnalysisDetailPage = {
    oninit: (vnode) => {
        const analysisId = vnode.attrs.id;
        state.selectedAnalysisData = null;
        state.selectedAnalysis = null;
        
        // Load analysis index if not already loaded
        if (!state.analysisIndex) {
            api.getAnalysisIndex().then(data => {
                state.analysisIndex = data;
                // Find the analysis
                state.selectedAnalysis = data.analyses?.find(a => a.id === analysisId);
                m.redraw();
            });
        } else {
            state.selectedAnalysis = state.analysisIndex.analyses?.find(a => a.id === analysisId);
        }
        
        // Load analysis data
        const filename = `${analysisId}.json`;
        api.getAnalysis(filename).then(response => {
            state.selectedAnalysisData = response.data || response;
            m.redraw();
        }).catch(err => {
            console.error(`Error loading ${filename}:`, err);
            state.selectedAnalysisData = { error: `Failed to load ${filename}` };
            m.redraw();
        });
    },
    view: () => m('div', { class: 'container mx-auto px-4 py-8' }, [
        // Breadcrumb navigation
        m('div', { class: 'text-sm breadcrumbs mb-4' }, [
            m('ul', [
                m('li', m('a', { href: '#!/analysis', oncreate: m.route.link }, 'Analysis')),
                m('li', state.selectedAnalysis?.title || 'Loading...')
            ])
        ]),
        
        // Title
        state.selectedAnalysis && m('h1', { class: 'text-4xl font-bold mb-6' }, state.selectedAnalysis.title),
        
        // Analysis data
        state.selectedAnalysisData ? 
            AnalysisPage.renderAnalysisData(state.selectedAnalysisData) :
            m(Loading)
    ])
};

// Layout Component
const Layout = {
    view: (vnode) => m('div', { class: 'min-h-screen flex flex-col' }, [
        m(Header),
        m('main', { class: 'flex-1' }, vnode.children),
        m(Footer)
    ])
};

// Router Configuration
m.route(document.getElementById('app'), '/', {
    '/': {
        render: () => m(Layout, m(HomePage))
    },
    '/jobs': {
        render: () => m(Layout, m(JobsPage))
    },
    '/jobs/:id': {
        render: (vnode) => m(Layout, m(JobDetailPage, { id: vnode.attrs.id }))
    },
    '/analysis': {
        render: () => m(Layout, m(AnalysisPage))
    },
    '/analysis/:id': {
        render: (vnode) => m(Layout, m(AnalysisDetailPage, { id: vnode.attrs.id }))
    }
});
