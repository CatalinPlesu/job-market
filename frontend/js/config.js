// API Configuration
// Dynamically determine the base path based on the current URL
// For GitHub Pages: Serve files from GitHub Pages itself (no CORS issues)
// For localhost: /api

function getApiBase() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    // Check if we're on GitHub Pages by examining the hostname
    const isGitHubPages = hostname.endsWith('.github.io') || hostname.includes('githubusercontent.com');
    
    if (isGitHubPages) {
        // For GitHub Pages, use the regular path
        // Files are served from GitHub Pages itself, not from raw.githubusercontent.com
        // This avoids CORS issues
        const pathParts = pathname.split('/').filter(part => part.length > 0);
        
        if (pathParts.length > 0) {
            const repoName = pathParts[0];
            return `/${repoName}/api`;
        }
    }
    
    // Default to /api for localhost and other hosting
    return '/api';
}

const API_BASE = getApiBase();

// Helper function to get the database URL
// Always use relative paths for GitHub Pages (no CORS issues)
function getDatabaseUrl(dbName) {
    // Use the regular path - files are served from GitHub Pages
    return `${API_BASE}/${dbName}`;
}

console.log('API_BASE configured as:', API_BASE);
console.log('Example database URL:', getDatabaseUrl('data.db'));

// Constants for multi-select fields (many-to-many relationships and one-to-many like languages)
const MULTI_SELECT_FIELDS = [
    'languages',  // One-to-many (job can require multiple languages)
    'hard_skills', 'soft_skills', 'certifications', 'licenses_required',
    'benefits', 'work_environment', 'professional_development', 
    'work_life_balance', 'physical_requirements', 'work_conditions', 
    'special_requirements'
];

// Configuration constants
const DEFAULT_JOBS_PER_API_PAGE = 100;
