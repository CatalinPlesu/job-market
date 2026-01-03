// API Configuration
// Dynamically determine the base path based on the current URL
// For GitHub Pages: /repo-name/api
// For localhost: /api
function getApiBase() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    // Check if we're on GitHub Pages by examining the hostname
    const isGitHubPages = hostname.endsWith('.github.io') || hostname.includes('githubusercontent.com');
    
    if (isGitHubPages) {
        // Extract repo name from pathname
        // GitHub Pages URLs: username.github.io/repo-name/...
        const pathParts = pathname.split('/').filter(part => part.length > 0);
        
        if (pathParts.length > 0) {
            // First path segment is the repository name
            const repoName = pathParts[0];
            return `/${repoName}/api`;
        }
    }
    
    // Default to /api for localhost and other hosting
    return '/api';
}

const API_BASE = getApiBase();

console.log('API_BASE configured as:', API_BASE);

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
