// API Configuration
// For files >100MB: Use Git LFS + GitHub download URL from public folder
// GitHub won't accept files >100MB without LFS
// GitHub Pages can't serve LFS files directly, so we use raw download URL
// The 'public' folder helps avoid CORS restrictions

// Set this to true (required for files >100MB with Git LFS)
const USE_GITHUB_LFS = true;

function getApiBase() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    // Check if we're on GitHub Pages
    const isGitHubPages = hostname.endsWith('.github.io') || hostname.includes('githubusercontent.com');
    
    if (isGitHubPages && USE_GITHUB_LFS) {
        // For Git LFS files on GitHub Pages, use GitHub's download URL
        // The 'public' folder is used to help with CORS
        const pathParts = pathname.split('/').filter(part => part.length > 0);
        
        if (pathParts.length > 0) {
            // Extract username from hostname (username.github.io)
            const username = hostname.split('.')[0];
            const repoName = pathParts[0];
            
            // Return metadata for constructing the download URL
            return {
                type: 'github-lfs',
                username: username,
                repo: repoName,
                branch: 'master' // Change this if your branch is different (e.g., 'main')
            };
        }
    } else if (isGitHubPages) {
        // Regular GitHub Pages (non-LFS, files <100MB)
        const pathParts = pathname.split('/').filter(part => part.length > 0);
        
        if (pathParts.length > 0) {
            const repoName = pathParts[0];
            return `/${repoName}/public`;
        }
    }
    
    // Default to /public for localhost
    return '/public';
}

const API_BASE = getApiBase();

// Helper function to get the database URL
// For LFS files, use GitHub's raw download URL with ?download= parameter
function getDatabaseUrl(dbName) {
    if (typeof API_BASE === 'object' && API_BASE.type === 'github-lfs') {
        // Use GitHub's raw download URL with ?download= parameter for LFS files
        // Files are in the 'public' folder to help with CORS
        return `https://github.com/${API_BASE.username}/${API_BASE.repo}/raw/refs/heads/${API_BASE.branch}/public/${dbName}?download=`;
    } else {
        // Regular path for non-LFS or localhost
        return `${API_BASE}/${dbName}`;
    }
}

console.log('API_BASE configured as:', API_BASE);
if (typeof API_BASE === 'object' && API_BASE.type === 'github-lfs') {
    console.log('Using GitHub LFS download URL from public folder');
    console.log('Example database URL:', getDatabaseUrl('data.db'));
} else {
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
