// API Client for fetching JSON data

const API_BASE = import.meta.env.PROD ? '/api' : '/api';

export class APIError extends Error {
  status: number;
  
  constructor(status: number, message: string) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

async function fetchJSON<T>(url: string): Promise<T> {
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new APIError(
        response.status,
        `HTTP ${response.status}: ${response.statusText}`
      );
    }
    
    const data = await response.json();
    return data as T;
  } catch (error) {
    if (error instanceof APIError) throw error;
    if (error instanceof Error) {
      throw new APIError(0, `Network error: ${error.message}`);
    }
    throw new APIError(0, 'Unknown error occurred');
  }
}

export const api = {
  // Jobs API
  getJobsIndex: () => 
    fetchJSON<import('./types').JobsIndexResponse>(`${API_BASE}/jobs/index.json`),
  
  getJobsPage: (page: number) => 
    fetchJSON<import('./types').JobsPageResponse>(`${API_BASE}/jobs/page-${page}.json`),
  
  getJobDetail: (jobId: number) =>
    fetchJSON<import('./types').JobDetailResponse>(`${API_BASE}/jobs/${jobId}/detail.json`),
  
  // Analysis API
  getAnalysisIndex: () =>
    fetchJSON<import('./types').AnalysisIndexResponse>(`${API_BASE}/analysis/index.json`),
  
  getAnalysis: (endpoint: string) =>
    fetchJSON<any>(`${API_BASE}${endpoint}`),
};
