// API Configuration
// Dynamically determine the base path based on the current URL
// For GitHub Pages: /repo-name/api
// For localhost: /api
function getApiBase() {
    const path = window.location.pathname;
    
    // Check if we're on GitHub Pages (path starts with a repo name)
    // GitHub Pages URLs look like: /Repository-Name/...
    const pathParts = path.split('/').filter(part => part.length > 0);
    
    // If the first part of the path is not a file (doesn't have an extension)
    // and we're not at root, assume it's the GitHub Pages repo name
    if (pathParts.length > 0 && !pathParts[0].includes('.')) {
        const potentialRepoName = pathParts[0];
        // If it looks like a repo name (contains hyphens or capital letters, typical of repo names)
        if (potentialRepoName.includes('-') || /[A-Z]/.test(potentialRepoName)) {
            return `/${potentialRepoName}/api`;
        }
    }
    
    // Default to /api for localhost and other scenarios
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
