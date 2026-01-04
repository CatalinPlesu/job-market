// API Configuration
// For files >100MB: Use Git LFS + GitHub API to get LFS download URL
// GitHub won't accept files >100MB without LFS
// GitHub Pages can't serve LFS files directly, so we use GitHub API to get actual LFS URL
// GitHub's LFS storage has proper CORS headers enabled

const API_CONFIG = {
    type: "github-lfs-api",
    owner: "CatalinPlesu",
    repo: "Job-Market-Frontend",
    branch: "master",
    filePath: "public/data.db"
};

function getApiBase() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    // Check if we're on GitHub Pages
    const isGitHubPages = hostname.endsWith('.github.io') || hostname.includes('githubusercontent.com');
    
    if (isGitHubPages) {
        // For Git LFS files on GitHub Pages, use GitHub API approach
        const pathParts = pathname.split('/').filter(part => part.length > 0);
        
        if (pathParts.length > 0) {
            // Extract username from hostname (username.github.io)
            const username = hostname.split('.')[0];
            const repoName = pathParts[0];
            
            // Return metadata for GitHub API LFS approach
            return {
                type: 'github-lfs-api',
                owner: username,
                repo: repoName,
                branch: 'master', // Change this if your branch is different (e.g., 'main')
                filePath: 'public/data.db'
            };
        }
    }
    
    // Default to /public for localhost
    return '/public';
}

const API_BASE = getApiBase();

console.log('API_BASE configured as:', API_BASE);
if (typeof API_BASE === 'object' && API_BASE.type === 'github-lfs-api') {
    console.log('Using GitHub API to fetch LFS file with proper CORS');
} else {
    console.log('Using local path:', API_BASE);
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
