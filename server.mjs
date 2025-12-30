/**
 * Node.js API Server
 * Provides REST API endpoints for job filtering and data access
 */

import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { FilterManager, FilterUtils } from './pages/js/core/filters.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'pages')));

// Initialize filter manager
const filterManager = new FilterManager(null);

let jobsData = [];
let metadata = {};
let lookups = {};

// Load data from static files
async function loadData() {
    try {
        // Load jobs data
        const fs = await import('fs/promises');
        const path = await import('path');
        
        const jobsDir = path.join(__dirname, 'pages', 'api', 'jobs');
        const files = await fs.readdir(jobsDir);
        const jobFiles = files.filter(f => f.startsWith('page-') && f.endsWith('.json'));
        
        jobsData = [];
        for (const file of jobFiles) {
            const filePath = path.join(jobsDir, file);
            const data = JSON.parse(await fs.readFile(filePath, 'utf8'));
            jobsData = jobsData.concat(data.jobs || []);
        }
        
        // Load metadata
        const metadataFile = path.join(__dirname, 'pages', 'api', 'jobs', 'index.json');
        metadata = JSON.parse(await fs.readFile(metadataFile, 'utf8'));
        
        // Load lookups
        const lookupsDir = path.join(__dirname, 'pages', 'api', 'lookups');
        const lookupFiles = await fs.readdir(lookupsDir);
        
        lookups = {};
        for (const file of lookupFiles) {
            if (file.endsWith('.json')) {
                const key = file.replace('.json', '');
                const filePath = path.join(lookupsDir, file);
                lookups[key] = JSON.parse(await fs.readFile(filePath, 'utf8'))[key] || [];
            }
        }
        
        console.log(`Loaded ${jobsData.length} jobs, ${Object.keys(lookups).length} lookup types`);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// API Routes

// Get metadata
app.get('/api/jobs/index.json', (req, res) => {
    res.json(metadata);
});

// Get jobs by page
app.get('/api/jobs/page-:page.json', (req, res) => {
    const page = parseInt(req.params.page);
    const pageSize = 100;
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    
    const paginatedJobs = jobsData.slice(startIndex, endIndex);
    
    res.json({
        jobs: paginatedJobs,
        page: page,
        total_pages: Math.ceil(jobsData.length / pageSize),
        total_jobs: jobsData.length
    });
});

// Get all jobs with optional filters
app.get('/api/jobs', (req, res) => {
    const { page = 1, ...filters } = req.query;
    const pageNum = parseInt(page);
    
    // Apply filters
    const filteredJobs = filterManager.filterJobs(jobsData, filters);
    const result = filterManager.paginateJobs(filteredJobs, pageNum);
    
    res.json(result);
});

// Get filter metadata
app.get('/api/filters/metadata', (req, res) => {
    const metadata = filterManager.getFilterMetadata(jobsData);
    res.json(metadata);
});

// Get filter stats
app.get('/api/filters/stats', (req, res) => {
    const stats = filterManager.getFilterStats(jobsData);
    res.json(stats);
});

// Get lookups
app.get('/api/lookups/:type.json', (req, res) => {
    const type = req.params.type;
    if (lookups[type]) {
        res.json({ [type]: lookups[type] });
    } else {
        res.status(404).json({ error: 'Lookup type not found' });
    }
});

// Get all lookups
app.get('/api/lookups', (req, res) => {
    res.json(lookups);
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        jobsLoaded: jobsData.length,
        lookupsLoaded: Object.keys(lookups).length,
        timestamp: new Date().toISOString()
    });
});

// Start server
async function startServer() {
    await loadData();
    
    app.listen(PORT, () => {
        console.log(`Server running on http://localhost:${PORT}`);
        console.log(`API available at http://localhost:${PORT}/api`);
    });
}

startServer().catch(console.error);