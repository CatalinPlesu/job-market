// Example configuration for using a custom database server
// Copy this to frontend/js/config.js and modify as needed

const API_CONFIG = {
    // Use "custom-server" type to fetch from your own database server
    type: "custom-server",
    
    // Custom server configuration for database.catalinplesu.xyz
    customServer: {
        url: "https://database.catalinplesu.xyz",  // Your database server URL
        path: "/db"  // API endpoint path (default: /db)
    },
    
    // GitHub LFS + CORS proxy configuration (keep this for reference)
    githubLFS: {
        owner: "CatalinPlesu",
        repo: "Job-Market-Frontend",
        branch: "master",
        filePath: "public/data.db",
        corsProxy: "https://proxy.catalinplesu.xyz/proxy/"
    }
};

// This function is already in config.js - no changes needed
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
    
    // ... rest of the function
}
