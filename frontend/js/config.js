// API Configuration
// Dynamically determine the base path based on the current URL
// For GitHub Pages with Git LFS: Use GitHub's download URL with ?download= parameter
// For GitHub Pages without LFS: Use regular path
// For localhost: /api

// Configuration for GitHub LFS downloads
// Set this to true if you're using Git LFS for database files (>100MB)
const USE_GITHUB_LFS = true; // Change to false if not using LFS

function getApiBase() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    // Check if we're on GitHub Pages by examining the hostname
    const isGitHubPages = hostname.endsWith('.github.io') || hostname.includes('githubusercontent.com');
    
    if (isGitHubPages && USE_GITHUB_LFS) {
        // For Git LFS files on GitHub Pages, we need to use GitHub's download URL
        // Extract username and repo name from pathname
        // GitHub Pages URLs: username.github.io/repo-name/...
        const pathParts = pathname.split('/').filter(part => part.length > 0);
        
        if (pathParts.length > 0) {
            // Extract username from hostname (username.github.io)
            const username = hostname.split('.')[0];
            const repoName = pathParts[0];
            
            // Return a special marker that will be replaced in the database loading function
            return {
                type: 'github-lfs',
                username: username,
                repo: repoName,
                branch: 'master' // Change this if your branch is different (e.g., 'main')
            };
        }
    } else if (isGitHubPages) {
        // Regular GitHub Pages (non-LFS)
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
// For LFS files, use GitHub's download URL with ?download= parameter to get the full file
function getDatabaseUrl(dbName) {
    if (typeof API_BASE === 'object' && API_BASE.type === 'github-lfs') {
        // Use GitHub's raw download URL with ?download= parameter for LFS files
        // This forces the download of the actual LFS file, not the pointer
        return `https://github.com/${API_BASE.username}/${API_BASE.repo}/raw/refs/heads/${API_BASE.branch}/api/${dbName}?download=`;
    } else {
        // Regular path
        return `${API_BASE}/${dbName}`;
    }
}

console.log('API_BASE configured as:', API_BASE);
if (typeof API_BASE === 'object' && API_BASE.type === 'github-lfs') {
    console.log('Using GitHub LFS download URL');
    console.log('Example database URL:', getDatabaseUrl('data.db'));
}

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
