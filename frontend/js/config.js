// API Configuration
// Three approaches for database hosting:
// 1. Custom Server: Use your own server to host DB files (recommended for large files)
// 2. Git LFS + CORS Proxy: Use GitHub LFS with a CORS proxy
// 3. Local/Static: Serve from local or static file server

// Configuration object
// Set the type based on your deployment:
// - "custom-server": Use your own DB server (supports large files, no GitHub limitations)
// - "github-lfs-proxy": Use GitHub LFS + CORS proxy (for GitHub Pages)
// - "static": Use local or static file path (for localhost)

const API_CONFIG = {
    // Change this to "custom-server" to use your own database server
    type: "github-lfs-proxy",
    
    // Custom server configuration (used when type = "custom-server")
    customServer: {
        url: "https://db.example.com",  // Your database server URL
        path: "/db"  // Path to database endpoint
    },
    
    // GitHub LFS + CORS proxy configuration (used when type = "github-lfs-proxy")
    githubLFS: {
        owner: "CatalinPlesu",
        repo: "Job-Market-Frontend",
        branch: "master",
        filePath: "public/data.db",
        corsProxy: "https://proxy.catalinplesu.xyz/proxy/"
    }
};

function getApiBase() {
    const hostname = window.location.hostname;
    const pathname = window.location.pathname;
    
    // If custom server is configured and we're not on localhost, use it
    if (API_CONFIG.type === "custom-server") {
        return {
            type: 'custom-server',
            url: API_CONFIG.customServer.url,
            path: API_CONFIG.customServer.path
        };
    }
    
    // Check if we're on GitHub Pages
    const isGitHubPages = hostname.endsWith('.github.io') || hostname.includes('githubusercontent.com');
    
    if (isGitHubPages && API_CONFIG.type === "github-lfs-proxy") {
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
                branch: API_CONFIG.githubLFS.branch,
                filePath: API_CONFIG.githubLFS.filePath,
                corsProxy: API_CONFIG.githubLFS.corsProxy
            };
        }
    }
    
    // Default to /public for localhost
    return '/public';
}

const API_BASE = getApiBase();

console.log('API_BASE configured as:', API_BASE);
if (typeof API_BASE === 'object') {
    if (API_BASE.type === 'custom-server') {
        console.log('Using custom server:', API_BASE.url);
    } else if (API_BASE.type === 'github-lfs-proxy') {
        console.log('Using CORS proxy to fetch LFS file from GitHub');
    }
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
