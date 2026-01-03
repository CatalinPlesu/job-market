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
