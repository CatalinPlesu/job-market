const API_BASE = './api/jobs';

const apiService = {
    async loadLookups() {
        const response = await fetch(`${API_BASE}/lookups.json`);
        if (!response.ok) throw new Error('Failed to load lookups');
        return await response.json();
    },
    
    async loadPagesList() {
        const response = await fetch(`${API_BASE}/pages-list.json`);
        if (!response.ok) throw new Error('Failed to load pages list');
        return await response.json();
    },
    
    async loadJobPage(pageNum) {
        const response = await fetch(`${API_BASE}/page-${pageNum}.json`);
        if (!response.ok) throw new Error(`Failed to load page ${pageNum}`);
        return await response.json();
    }
};

export default apiService;
