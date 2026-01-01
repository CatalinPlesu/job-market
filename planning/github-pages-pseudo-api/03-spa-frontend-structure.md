# SPA Frontend Structure Specification

## Document Purpose
This specification defines the single-page application (SPA) that will consume the JSON API and provide an interactive interface for job seekers to explore the Moldova job market.

## System Responsibilities

### Core Functions
1. Fetch and render paginated job listings
2. Implement client-side filtering and search
3. Display job details with parsed/raw tabs
4. Render interactive data visualizations
5. Provide responsive, mobile-friendly UI
6. Handle routing and navigation

### Out of Scope
- JSON generation (handled by separate component)
- Backend server implementation
- User authentication (public site)
- Job application submission

## Technology Stack

### Recommended: React + Vite

**Core Framework:**
- **React 18+** - Component-based UI library
- **Vite** - Fast build tool and dev server
- **TypeScript** - Type safety for API contracts

**Routing:**
- **React Router v6** - Client-side routing
- **Hash routing** (#/jobs) - Simpler for GitHub Pages
- **Alternative:** History API with 404.html fallback

**State Management:**
- **React Context + useReducer** - For simple global state
- **TanStack Query (React Query)** - API data fetching and caching
- **Alternative:** Zustand for more complex state

**Styling:**
- **Tailwind CSS** - Utility-first CSS framework
- **Alternative:** Styled Components or CSS Modules
- **Responsive breakpoints** - Mobile-first design

**Charting:**
- **Recharts** - React-native declarative charts
- **Chart.js** - Canvas-based charts (via react-chartjs-2)
- **D3.js** - Custom complex visualizations
- **TanStack Table** - Interactive data tables

### Project Structure
```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── main.tsx                    # App entry point
│   ├── App.tsx                     # Root component
│   ├── api/
│   │   ├── client.ts              # API fetch utilities
│   │   ├── types.ts               # TypeScript types for API
│   │   └── hooks.ts               # React Query hooks
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── jobs/
│   │   │   ├── JobList.tsx
│   │   │   ├── JobCard.tsx
│   │   │   ├── JobDetail.tsx
│   │   │   ├── JobFilters.tsx
│   │   │   └── Pagination.tsx
│   │   ├── analysis/
│   │   │   ├── AnalysisDashboard.tsx
│   │   │   ├── SalaryCharts.tsx
│   │   │   ├── SkillsCharts.tsx
│   │   │   ├── TrendsCharts.tsx
│   │   │   └── ChartCard.tsx
│   │   └── charts/
│   │       ├── BarChart.tsx
│   │       ├── LineChart.tsx
│   │       ├── PieChart.tsx
│   │       └── TableChart.tsx
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── JobsPage.tsx
│   │   ├── JobDetailPage.tsx
│   │   ├── AnalysisPage.tsx
│   │   └── AboutPage.tsx
│   ├── hooks/
│   │   ├── useJobs.ts
│   │   ├── useFilters.ts
│   │   ├── useAnalysis.ts
│   │   └── usePagination.ts
│   ├── context/
│   │   └── FilterContext.tsx
│   ├── utils/
│   │   ├── formatting.ts
│   │   ├── filtering.ts
│   │   └── constants.ts
│   └── styles/
│       └── globals.css
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

## API Integration

### TypeScript Types

```typescript
// src/api/types.ts

export interface JobsIndexResponse {
  version: string;
  generated_at: string;
  total_jobs: number;
  total_pages: number;
  jobs_per_page: number;
  metadata: {
    date_range: DateRange;
    job_functions: CategoryMetadata[];
    seniority_levels: CategoryMetadata[];
    locations: CategoryMetadata[];
    remote_work: CategoryMetadata[];
    salary_ranges: SalaryRangeMetadata[];
    companies: CategoryMetadata[];
    industries: CategoryMetadata[];
  };
  filters: {
    job_function: string[];
    seniority_level: string[];
    location: string[];
    remote_work: string[];
    employment_type: string[];
    industry: string[];
  };
}

export interface CategoryMetadata {
  name: string;
  count: number;
  pages: number[];
}

export interface SalaryRangeMetadata {
  min: number;
  max: number;
  currency: string;
  count: number;
  pages: number[];
}

export interface JobsPageResponse {
  version: string;
  page: number;
  total_pages: number;
  jobs_per_page: number;
  jobs: Job[];
}

export interface Job {
  id: number;
  title: string;
  job_function: string | null;
  specialization: string | null;
  seniority_level: string | null;
  company: string;
  company_size: string | null;
  location: Location;
  salary: Salary | null;
  employment: Employment;
  requirements: Requirements;
  benefits: string[];
  posting_date: string;
  source: Source;
  parsed_view: ParsedView;
}

export interface Location {
  city: string | null;
  region: string | null;
  country: string;
  remote_work: string | null;
}

export interface Salary {
  min: number | null;
  max: number | null;
  currency: string;
  period: string;
}

export interface Employment {
  type: string | null;
  contract: string | null;
  schedule: string | null;
}

export interface Requirements {
  education: string | null;
  experience_years: number | null;
  languages: string[];
  hard_skills: string[];
  soft_skills: string[];
  certifications: string[];
}

export interface ParsedView {
  responsibilities: string[];
  work_environment: string[];
  professional_development: string[];
}

export interface Source {
  site: string;
  url: string;
}

export interface AnalysisIndexResponse {
  version: string;
  generated_at: string;
  available_analyses: AnalysisMetadata[];
  data_summary: DataSummary;
}

export interface AnalysisMetadata {
  id: string;
  title: string;
  endpoint: string;
  last_updated?: string;
  temporal?: boolean;
}
```

### API Client

```typescript
// src/api/client.ts

const API_BASE = import.meta.env.PROD ? '/api' : '/api';

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
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
    throw new APIError(0, `Network error: ${error.message}`);
  }
}

export const api = {
  // Jobs API
  getJobsIndex: () => 
    fetchJSON<JobsIndexResponse>(`${API_BASE}/jobs/index.json`),
  
  getJobsPage: (page: number) => 
    fetchJSON<JobsPageResponse>(`${API_BASE}/jobs/page-${page}.json`),
  
  getJobDetail: (jobId: number) =>
    fetchJSON<JobDetailResponse>(`${API_BASE}/jobs/${jobId}/detail.json`),
  
  // Analysis API
  getAnalysisIndex: () =>
    fetchJSON<AnalysisIndexResponse>(`${API_BASE}/analysis/index.json`),
  
  getAnalysis: (endpoint: string) =>
    fetchJSON<any>(`${API_BASE}${endpoint}`),
};
```

### React Query Hooks

```typescript
// src/api/hooks.ts

import { useQuery, useQueries } from '@tanstack/react-query';
import { api } from './client';

export function useJobsIndex() {
  return useQuery({
    queryKey: ['jobs', 'index'],
    queryFn: api.getJobsIndex,
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

export function useJobsPage(page: number) {
  return useQuery({
    queryKey: ['jobs', 'page', page],
    queryFn: () => api.getJobsPage(page),
    staleTime: 1000 * 60 * 60,
  });
}

export function useJobsPages(pages: number[]) {
  return useQueries({
    queries: pages.map(page => ({
      queryKey: ['jobs', 'page', page],
      queryFn: () => api.getJobsPage(page),
      staleTime: 1000 * 60 * 60,
    })),
  });
}

export function useJobDetail(jobId: number) {
  return useQuery({
    queryKey: ['jobs', 'detail', jobId],
    queryFn: () => api.getJobDetail(jobId),
    staleTime: 1000 * 60 * 60,
  });
}

export function useAnalysisIndex() {
  return useQuery({
    queryKey: ['analysis', 'index'],
    queryFn: api.getAnalysisIndex,
    staleTime: 1000 * 60 * 60,
  });
}

export function useAnalysis(endpoint: string) {
  return useQuery({
    queryKey: ['analysis', endpoint],
    queryFn: () => api.getAnalysis(endpoint),
    staleTime: 1000 * 60 * 60,
    enabled: !!endpoint,
  });
}
```

## Key Features & Implementation

### 1. Job Browsing with Smart Pagination

**Component: JobsPage.tsx**
```typescript
function JobsPage() {
  const [currentPage, setCurrentPage] = useState(1);
  const { data: index, isLoading: indexLoading } = useJobsIndex();
  const { data: page, isLoading: pageLoading } = useJobsPage(currentPage);
  
  // Smart prefetching: load next page in background
  const queryClient = useQueryClient();
  useEffect(() => {
    if (currentPage < (index?.total_pages || 0)) {
      queryClient.prefetchQuery({
        queryKey: ['jobs', 'page', currentPage + 1],
        queryFn: () => api.getJobsPage(currentPage + 1),
      });
    }
  }, [currentPage, index?.total_pages]);
  
  if (indexLoading || pageLoading) return <Loading />;
  
  return (
    <div>
      <JobFilters index={index} />
      <JobList jobs={page.jobs} />
      <Pagination 
        currentPage={currentPage}
        totalPages={index.total_pages}
        onPageChange={setCurrentPage}
      />
    </div>
  );
}
```

### 2. Client-Side Filtering

**Strategy:**
- Load index.json to get metadata about which pages contain filtered jobs
- When user applies filter, only fetch relevant pages
- Merge results client-side and display

**Component: JobFilters.tsx**
```typescript
function JobFilters({ index }: { index: JobsIndexResponse }) {
  const { filters, updateFilter, clearFilters } = useFilters();
  
  return (
    <div className="filters">
      <FilterSelect
        label="Job Function"
        options={index.filters.job_function}
        value={filters.job_function}
        onChange={(v) => updateFilter('job_function', v)}
      />
      <FilterSelect
        label="Seniority"
        options={index.filters.seniority_level}
        value={filters.seniority_level}
        onChange={(v) => updateFilter('seniority_level', v)}
      />
      <FilterSelect
        label="Location"
        options={index.filters.location}
        value={filters.location}
        onChange={(v) => updateFilter('location', v)}
      />
      <FilterSelect
        label="Remote Work"
        options={index.filters.remote_work}
        value={filters.remote_work}
        onChange={(v) => updateFilter('remote_work', v)}
      />
      <SalaryRangeFilter
        ranges={index.metadata.salary_ranges}
        value={filters.salary_range}
        onChange={(v) => updateFilter('salary_range', v)}
      />
      <button onClick={clearFilters}>Clear All</button>
    </div>
  );
}
```

**Hook: useFilters.ts**
```typescript
function useFilters() {
  const [filters, setFilters] = useState<Filters>({});
  const { data: index } = useJobsIndex();
  
  const updateFilter = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };
  
  const clearFilters = () => {
    setFilters({});
  };
  
  // Calculate which pages to load based on active filters
  const relevantPages = useMemo(() => {
    if (!index || Object.keys(filters).length === 0) {
      return [1]; // No filters, show first page
    }
    
    // Find pages that match ALL active filters
    const pageSets = Object.entries(filters).map(([key, value]) => {
      const metadata = index.metadata[key];
      const item = metadata?.find(m => m.name === value);
      return new Set(item?.pages || []);
    });
    
    // Intersection of all page sets
    const intersection = pageSets.reduce((acc, set) => 
      new Set([...acc].filter(x => set.has(x)))
    );
    
    return Array.from(intersection).sort((a, b) => a - b);
  }, [filters, index]);
  
  return { filters, updateFilter, clearFilters, relevantPages };
}
```

**Component: FilteredJobList.tsx**
```typescript
function FilteredJobList() {
  const { filters, relevantPages } = useFilters();
  const pageQueries = useJobsPages(relevantPages);
  
  const allJobs = useMemo(() => {
    return pageQueries
      .filter(q => q.isSuccess)
      .flatMap(q => q.data.jobs)
      .filter(job => matchesFilters(job, filters));
  }, [pageQueries, filters]);
  
  const isLoading = pageQueries.some(q => q.isLoading);
  
  if (isLoading) return <Loading />;
  
  return <JobList jobs={allJobs} />;
}

function matchesFilters(job: Job, filters: Filters): boolean {
  if (filters.job_function && job.job_function !== filters.job_function) {
    return false;
  }
  if (filters.seniority_level && job.seniority_level !== filters.seniority_level) {
    return false;
  }
  if (filters.location && job.location.city !== filters.location) {
    return false;
  }
  if (filters.remote_work && job.location.remote_work !== filters.remote_work) {
    return false;
  }
  return true;
}
```

### 3. Job Detail with Tabs

**Component: JobDetailPage.tsx**
```typescript
function JobDetailPage() {
  const { jobId } = useParams();
  const { data: job, isLoading } = useJobDetail(Number(jobId));
  const [activeTab, setActiveTab] = useState<'parsed' | 'raw'>('parsed');
  
  if (isLoading) return <Loading />;
  if (!job) return <NotFound />;
  
  return (
    <div className="job-detail">
      <JobHeader job={job.job} />
      
      <Tabs activeTab={activeTab} onTabChange={setActiveTab}>
        <Tab id="parsed" label="Parsed View">
          <ParsedJobView data={job.job.parsed} />
        </Tab>
        <Tab id="raw" label="Raw View">
          <RawJobView data={job.job.raw} />
        </Tab>
      </Tabs>
    </div>
  );
}

function ParsedJobView({ data }: { data: ParsedData }) {
  return (
    <div className="parsed-view">
      <Section title="Overview">
        <InfoGrid>
          <InfoItem label="Job Function" value={data.job_function} />
          <InfoItem label="Seniority" value={data.seniority_level} />
          <InfoItem label="Industry" value={data.industry} />
          <InfoItem label="Company" value={data.company} />
        </InfoGrid>
      </Section>
      
      <Section title="Location">
        <InfoGrid>
          <InfoItem label="City" value={data.location.city} />
          <InfoItem label="Remote Work" value={data.location.remote_work} />
        </InfoGrid>
      </Section>
      
      <Section title="Compensation">
        {data.salary && (
          <SalaryDisplay salary={data.salary} />
        )}
      </Section>
      
      <Section title="Requirements">
        <SubSection title="Education">
          {data.requirements.education}
        </SubSection>
        <SubSection title="Experience">
          {data.requirements.experience_years} years
        </SubSection>
        <SubSection title="Languages">
          <TagList items={data.requirements.languages} />
        </SubSection>
        <SubSection title="Hard Skills">
          <TagList items={data.requirements.hard_skills} />
        </SubSection>
        <SubSection title="Soft Skills">
          <TagList items={data.requirements.soft_skills} />
        </SubSection>
      </Section>
      
      <Section title="Responsibilities">
        <List items={data.responsibilities} />
      </Section>
      
      <Section title="Benefits">
        <List items={data.benefits} />
      </Section>
    </div>
  );
}

function RawJobView({ data }: { data: RawData }) {
  return (
    <div className="raw-view">
      <Section title="Original Posting">
        <InfoItem label="Title" value={data.original_title} />
        <InfoItem label="Company" value={data.original_company} />
        <InfoItem label="Language" value={data.original_language} />
        <InfoItem label="Source" value={data.source_site} />
        <InfoItem label="Scraped At" value={formatDate(data.scraped_at)} />
      </Section>
      
      <Section title="Description">
        <pre className="whitespace-pre-wrap">
          {data.original_description}
        </pre>
      </Section>
      
      <Section title="Actions">
        <a href={data.source_url} target="_blank" rel="noopener noreferrer">
          View Original Posting →
        </a>
      </Section>
    </div>
  );
}
```

### 4. Analysis Dashboard with Charts

**Component: AnalysisPage.tsx**
```typescript
function AnalysisPage() {
  const { data: analysisIndex } = useAnalysisIndex();
  const [selectedAnalysis, setSelectedAnalysis] = useState<string>('');
  
  if (!analysisIndex) return <Loading />;
  
  return (
    <div className="analysis-page">
      <h1>Job Market Analysis</h1>
      
      <DataSummary summary={analysisIndex.data_summary} />
      
      <AnalysisNav
        analyses={analysisIndex.available_analyses}
        selected={selectedAnalysis}
        onSelect={setSelectedAnalysis}
      />
      
      {selectedAnalysis && (
        <AnalysisView endpoint={selectedAnalysis} />
      )}
    </div>
  );
}

function AnalysisView({ endpoint }: { endpoint: string }) {
  const { data, isLoading } = useAnalysis(endpoint);
  
  if (isLoading) return <Loading />;
  
  // Route to appropriate chart component based on analysis type
  switch (data.analysis_id) {
    case 'salary-overview':
      return <SalaryOverviewCharts data={data} />;
    case 'salary-by-function':
      return <SalaryByFunctionCharts data={data} />;
    case 'market-trends':
      return <MarketTrendsCharts data={data} />;
    case 'skills-demand':
      return <SkillsDemandCharts data={data} />;
    default:
      return <GenericAnalysisView data={data} />;
  }
}
```

**Component: SalaryOverviewCharts.tsx**
```typescript
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

function SalaryOverviewCharts({ data }: { data: SalaryOverviewData }) {
  const { overall, by_currency, distribution } = data.data;
  
  return (
    <div className="salary-overview">
      <ChartCard title="Overall Salary Statistics">
        <StatsGrid>
          <Stat label="Average" value={formatCurrency(overall.average, overall.currency)} />
          <Stat label="Median" value={formatCurrency(overall.median, overall.currency)} />
          <Stat label="Min" value={formatCurrency(overall.min, overall.currency)} />
          <Stat label="Max" value={formatCurrency(overall.max, overall.currency)} />
          <Stat label="Sample Size" value={overall.count} />
        </StatsGrid>
      </ChartCard>
      
      <ChartCard title="Salary Distribution">
        <BarChart width={600} height={300} data={distribution}>
          <XAxis dataKey="range" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#3b82f6" />
        </BarChart>
      </ChartCard>
      
      <ChartCard title="By Currency">
        <BarChart width={600} height={300} data={by_currency}>
          <XAxis dataKey="currency" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="average" fill="#3b82f6" name="Average" />
          <Bar dataKey="median" fill="#10b981" name="Median" />
        </BarChart>
      </ChartCard>
    </div>
  );
}
```

**Component: MarketTrendsCharts.tsx**
```typescript
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts';

function MarketTrendsCharts({ data }: { data: MarketTrendsData }) {
  const { job_posting_volume, average_salary_trend, remote_work_adoption } = data.data;
  
  return (
    <div className="market-trends">
      <ChartCard title="Job Posting Volume Over Time">
        <LineChart width={800} height={400} data={job_posting_volume}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="count" stroke="#3b82f6" name="Total Jobs" />
          <Line type="monotone" dataKey="new" stroke="#10b981" name="New Postings" />
          <Line type="monotone" dataKey="closed" stroke="#ef4444" name="Closed Jobs" />
        </LineChart>
      </ChartCard>
      
      <ChartCard title="Average Salary Trend">
        <LineChart width={800} height={400} data={average_salary_trend}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="average" stroke="#3b82f6" name="Average Salary" />
          <Line type="monotone" dataKey="median" stroke="#10b981" name="Median Salary" />
        </LineChart>
      </ChartCard>
      
      <ChartCard title="Remote Work Adoption">
        <LineChart width={800} height={400} data={remote_work_adoption}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="remote" stroke="#3b82f6" name="Remote %" />
          <Line type="monotone" dataKey="hybrid" stroke="#10b981" name="Hybrid %" />
          <Line type="monotone" dataKey="on_site" stroke="#6b7280" name="On-site %" />
        </LineChart>
      </ChartCard>
    </div>
  );
}
```

### 5. Routing

**App.tsx**
```typescript
import { HashRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <HashRouter>
        <div className="app">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/jobs" element={<JobsPage />} />
              <Route path="/jobs/:jobId" element={<JobDetailPage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </HashRouter>
    </QueryClientProvider>
  );
}
```

### 6. Mobile Responsiveness

**Tailwind Configuration:**
```javascript
// tailwind.config.js
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#10b981',
        accent: '#8b5cf6',
      },
    },
  },
  plugins: [],
};
```

**Responsive Components:**
```typescript
// Mobile-first approach
<div className="
  grid 
  grid-cols-1 
  md:grid-cols-2 
  lg:grid-cols-3 
  gap-4
">
  {jobs.map(job => <JobCard key={job.id} job={job} />)}
</div>

// Responsive filters
<div className="
  flex 
  flex-col 
  md:flex-row 
  gap-4 
  items-stretch 
  md:items-center
">
  <FilterSelect ... />
  <FilterSelect ... />
</div>
```

## Testing Strategy

### Unit Tests (Vitest)
```typescript
// src/utils/filtering.test.ts
import { describe, it, expect } from 'vitest';
import { matchesFilters } from './filtering';

describe('matchesFilters', () => {
  it('should match job with no filters', () => {
    const job = { job_function: 'Engineering' };
    expect(matchesFilters(job, {})).toBe(true);
  });
  
  it('should match job with matching filter', () => {
    const job = { job_function: 'Engineering' };
    expect(matchesFilters(job, { job_function: 'Engineering' })).toBe(true);
  });
  
  it('should not match job with non-matching filter', () => {
    const job = { job_function: 'Engineering' };
    expect(matchesFilters(job, { job_function: 'Sales' })).toBe(false);
  });
});
```

### Component Tests (React Testing Library)
```typescript
// src/components/jobs/JobCard.test.tsx
import { render, screen } from '@testing-library/react';
import { JobCard } from './JobCard';

describe('JobCard', () => {
  const mockJob = {
    id: 1,
    title: 'Software Engineer',
    company: 'TechCorp',
    location: { city: 'Chișinău', remote_work: 'hybrid' },
    salary: { min: 15000, max: 25000, currency: 'MDL', period: 'month' },
  };
  
  it('should render job title', () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText('Software Engineer')).toBeInTheDocument();
  });
  
  it('should render company name', () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText('TechCorp')).toBeInTheDocument();
  });
  
  it('should render salary range', () => {
    render(<JobCard job={mockJob} />);
    expect(screen.getByText(/15000.*25000.*MDL/)).toBeInTheDocument();
  });
});
```

### E2E Tests (Playwright - Optional)
```typescript
// tests/e2e/jobs.spec.ts
import { test, expect } from '@playwright/test';

test('should browse jobs and apply filters', async ({ page }) => {
  await page.goto('/');
  await page.click('a[href="#/jobs"]');
  
  // Wait for jobs to load
  await expect(page.locator('.job-card')).toHaveCount(100);
  
  // Apply filter
  await page.selectOption('select[name="job_function"]', 'Engineering');
  await page.click('button:has-text("Apply")');
  
  // Check filtered results
  await expect(page.locator('.job-card')).toHaveCountGreaterThan(0);
  await expect(page.locator('.job-card:first-child')).toContainText('Engineering');
});
```

## Performance Optimization

### Code Splitting
```typescript
// Lazy load heavy pages
const AnalysisPage = lazy(() => import('./pages/AnalysisPage'));

<Suspense fallback={<Loading />}>
  <Route path="/analysis" element={<AnalysisPage />} />
</Suspense>
```

### Memoization
```typescript
const filteredJobs = useMemo(() => 
  jobs.filter(job => matchesFilters(job, filters)),
  [jobs, filters]
);

const JobCard = memo(({ job }: { job: Job }) => {
  // Component implementation
});
```

### Virtual Scrolling (for large lists)
```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

function JobList({ jobs }: { jobs: Job[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: jobs.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 200,
  });
  
  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <div
            key={virtualRow.index}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            <JobCard job={jobs[virtualRow.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Build Configuration

### Vite Config
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/', // or '/job-market/' if not at root
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'charts': ['recharts', 'chart.js'],
        },
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### package.json Scripts
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "lint": "eslint src --ext ts,tsx",
    "format": "prettier --write src/**/*.{ts,tsx}"
  }
}
```

## Success Criteria

- [ ] Initial page load <2 seconds
- [ ] Filtering updates <100ms
- [ ] All routes work correctly
- [ ] Mobile responsive (tested on phones/tablets)
- [ ] Charts render without errors
- [ ] No accessibility violations (WCAG AA)
- [ ] Works in Chrome, Firefox, Safari, Edge
- [ ] Can browse all jobs with pagination
- [ ] Filtering correctly loads only relevant pages
- [ ] Job detail view shows both tabs
- [ ] Analysis visualizations are interactive

## Dependencies

### Core
- react, react-dom
- react-router-dom
- @tanstack/react-query
- typescript

### UI & Styling
- tailwindcss
- @headlessui/react (for accessible components)

### Charts
- recharts
- react-chartjs-2, chart.js
- d3 (for advanced visualizations)

### Dev Dependencies
- vite, @vitejs/plugin-react
- vitest, @testing-library/react
- eslint, prettier
- @types/react, @types/react-dom

## Integration Points

### Upstream: JSON API
- **Contract:** JSON schemas from JSON generation spec
- **Testing:** Use mock JSON files during development
- **Error handling:** Graceful fallbacks for missing data

### Deployment: Build Output
- **Contract:** All static assets in `dist/` folder
- **Assets:** HTML, JS, CSS, images
- **Testing:** Test production build locally with `vite preview`

## Open Questions for Implementer

1. Hash routing (#/jobs) or history API (/jobs) with 404 fallback?
2. Dark mode support from the start or future enhancement?
3. Locale support (Romanian/Russian/English) or English only?
4. Should we implement search (full-text) or just filtering?
5. Export to CSV/PDF features for jobs and analyses?

## References

- JSON API spec: `02-json-api-generation.md`
- Architecture: `01-architecture-strategy.md`
- Analytics requirements: `ANALYTICS_SPEC.md`
