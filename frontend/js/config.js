// API Configuration
// For files >100MB: Use Git LFS + CORS Proxy
// GitHub won't accept files >100MB without LFS
// GitHub Pages can't serve LFS files directly (serves pointer files)
// GitHub's raw endpoint blocks CORS requests
// Solution: Use CORS proxy to access GitHub raw LFS files

const API_CONFIG = {
    type: "github-lfs-proxy",
    owner: "CatalinPlesu",
    repo: "Job-Market-Frontend",
    branch: "master",
    filePath: "public/data.db",
    corsProxy: "https://proxy.catalinplesu.xyz/proxy/"
};

function getApiBase() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    // Check if we're on GitHub Pages
    const isGitHubPages = hostname.endsWith('.github.io') || hostname.includes('githubusercontent.com');
    
    if (isGitHubPages) {
        // For Git LFS files on GitHub Pages, use CORS proxy approach
        const pathParts = pathname.split('/').filter(part => part.length > 0);
        
        if (pathParts.length > 0) {
            // Extract username from hostname (username.github.io)
            const username = hostname.split('.')[0];
            const repoName = pathParts[0];
            
            // Return metadata for CORS proxy + GitHub LFS approach
            return {
                type: 'github-lfs-proxy',
                owner: username,
                repo: repoName,
                branch: 'master', // Change this if your branch is different (e.g., 'main')
                filePath: 'public/data.db',
                corsProxy: 'https://proxy.catalinplesu.xyz/proxy/'
            };
        }
    }
    
    // Default to /public for localhost
    return '/public';
}

const API_BASE = getApiBase();

console.log('API_BASE configured as:', API_BASE);
if (typeof API_BASE === 'object' && API_BASE.type === 'github-lfs-proxy') {
    console.log('Using CORS proxy to fetch LFS file from GitHub');
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
