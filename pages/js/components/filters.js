const FiltersComponent = {
    props: ['lookups', 'filters'],
    
    data() {
        return {
            showFilters: false
        };
    },
    
    template: `
        <div class="filters">
            <button @click="showFilters = !showFilters" class="btn-toggle-filters">
                {{ showFilters ? '✕ Hide' : '⚙ Show' }} Filters
            </button>
            
            <div v-show="showFilters" class="filters-panel">
                <div class="filter-group">
                    <label>Search</label>
                    <input 
                        type="text" 
                        v-model="localFilters.search"
                        @input="updateFilters"
                        placeholder="Job title or company..."
                        class="filter-input"
                    />
                </div>
                
                <div class="filter-group">
                    <label>City</label>
                    <select v-model="localFilters.city" @change="updateFilters" class="filter-select">
                        <option :value="null">All Cities</option>
                        <option v-for="(name, id) in lookups.cities" :key="id" :value="id">
                            {{ name }}
                        </option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Work Location</label>
                    <select v-model="localFilters.remote_work" @change="updateFilters" class="filter-select">
                        <option :value="null">All</option>
                        <option v-for="(name, id) in lookups.remote_work_options" :key="id" :value="id">
                            {{ name }}
                        </option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Seniority Level</label>
                    <select v-model="localFilters.seniority_level" @change="updateFilters" class="filter-select">
                        <option :value="null">All Levels</option>
                        <option v-for="(name, id) in lookups.seniority_levels" :key="id" :value="id">
                            {{ name }}
                        </option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Employment Type</label>
                    <select v-model="localFilters.employment_type" @change="updateFilters" class="filter-select">
                        <option :value="null">All Types</option>
                        <option v-for="(name, id) in lookups.employment_types" :key="id" :value="id">
                            {{ name }}
                        </option>
                    </select>
                </div>
                
                <button @click="clearFilters" class="btn-clear">Clear Filters</button>
            </div>
        </div>
    `,
    
    data() {
        return {
            showFilters: false,
            localFilters: { ...this.filters }
        };
    },
    
    watch: {
        filters: {
            handler(newFilters) {
                this.localFilters = { ...newFilters };
            },
            deep: true
        }
    },
    
    methods: {
        updateFilters() {
            this.$emit('update-filters', this.localFilters);
        },
        
        clearFilters() {
            this.localFilters = {
                search: '',
                city: null,
                remote_work: null,
                seniority_level: null,
                employment_type: null,
            };
            this.updateFilters();
        }
    }
};

// Styles
const style = document.createElement('style');
style.textContent = `
    .filters {
        margin-bottom: 20px;
    }
    
    .btn-toggle-filters {
        background: #667eea;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 1em;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s;
        width: 100%;
    }
    
    .btn-toggle-filters:hover {
        background: #5568d3;
    }
    
    .filters-panel {
        background: white;
        padding: 24px;
        border-radius: 12px;
        margin-top: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
    }
    
    .filter-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .filter-group label {
        font-weight: 600;
        color: #555;
        font-size: 0.9em;
    }
    
    .filter-input,
    .filter-select {
        padding: 10px 12px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-size: 1em;
        transition: border-color 0.2s;
    }
    
    .filter-input:focus,
    .filter-select:focus {
        outline: none;
        border-color: #667eea;
    }
    
    .btn-clear {
        grid-column: 1 / -1;
        background: #f0f0f0;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 0.95em;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .btn-clear:hover {
        background: #e0e0e0;
    }
    
    @media (max-width: 768px) {
        .filters-panel {
            grid-template-columns: 1fr;
        }
    }
`;
document.head.appendChild(style);

export default FiltersComponent;
