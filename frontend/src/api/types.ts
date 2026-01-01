// API Response Types for Job Market Application

export interface DateRange {
  earliest: string;
  latest: string;
}

export interface PageInfo {
  page: number;
  count: number;
}

export interface CategoryMetadata {
  name: string;
  count: number;
  pages: PageInfo[];
}

export interface SalaryRangeMetadata {
  min: number;
  max: number | null;
  currency: string;
  count: number;
  pages: PageInfo[];
}

export interface JobsIndexResponse {
  version: string;
  generated_at: string;
  total_jobs: number;
  total_pages: number;
  jobs_per_page: number;
  metadata: {
    date_range: DateRange;
    // One-to-one lookups
    titles: CategoryMetadata[];
    job_functions: CategoryMetadata[];
    seniority_levels: CategoryMetadata[];
    industries: CategoryMetadata[];
    departments: CategoryMetadata[];
    job_families: CategoryMetadata[];
    specializations: CategoryMetadata[];
    education_levels: CategoryMetadata[];
    employment_types: CategoryMetadata[];
    contract_types: CategoryMetadata[];
    work_schedules: CategoryMetadata[];
    shift_details: CategoryMetadata[];
    remote_work: CategoryMetadata[];
    travel_requirements: CategoryMetadata[];
    cities: CategoryMetadata[];
    regions: CategoryMetadata[];
    countries: CategoryMetadata[];
    companies: CategoryMetadata[];
    company_sizes: CategoryMetadata[];
    currencies: CategoryMetadata[];
    salary_periods: CategoryMetadata[];
    salary_ranges: SalaryRangeMetadata[];
    // Many-to-many fields
    hard_skills: CategoryMetadata[];
    soft_skills: CategoryMetadata[];
    languages: CategoryMetadata[];
    certifications: CategoryMetadata[];
    licenses: CategoryMetadata[];
    benefits: CategoryMetadata[];
    work_environment: CategoryMetadata[];
    professional_development: CategoryMetadata[];
    work_life_balance: CategoryMetadata[];
    physical_requirements: CategoryMetadata[];
    work_conditions: CategoryMetadata[];
    special_requirements: CategoryMetadata[];
  };
  filters: {
    title: string[];
    job_function: string[];
    seniority_level: string[];
    industry: string[];
    department: string[];
    job_family: string[];
    specialization: string[];
    education_level: string[];
    employment_type: string[];
    contract_type: string[];
    work_schedule: string[];
    shift_details: string[];
    remote_work: string[];
    travel_requirements: string[];
    city: string[];
    region: string[];
    country: string[];
    company: string[];
    company_size: string[];
    currency: string[];
    salary_period: string[];
    hard_skills: string[];
    soft_skills: string[];
    languages: string[];
    certifications: string[];
    licenses: string[];
    benefits: string[];
    work_environment: string[];
    professional_development: string[];
    work_life_balance: string[];
    physical_requirements: string[];
    work_conditions: string[];
    special_requirements: string[];
  };
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

export interface Job {
  id: number;
  title: string;
  job_function: string | null;
  specialization: string | null;
  seniority_level: string | null;
  industry: string | null;
  department: string | null;
  job_family: string | null;
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

export interface JobsPageResponse {
  version: string;
  page: number;
  total_pages: number;
  jobs_per_page: number;
  jobs: Job[];
}

export interface ParsedData {
  job_function: string | null;
  specialization: string | null;
  seniority_level: string | null;
  industry: string | null;
  department: string | null;
  job_family: string | null;
  company: string;
  company_size: string | null;
  location: Location;
  salary: Salary | null;
  employment: Employment;
  requirements: Requirements;
  responsibilities: string[];
  benefits: string[];
  work_environment: string[];
  professional_development: string[];
  work_life_balance: string[];
  posting_date: string;
}

export interface RawData {
  original_title: string;
  original_company: string;
  original_description: string;
  original_language: string;
  source_site: string;
  source_url: string;
  scraped_at: string;
}

export interface JobDetailResponse {
  version: string;
  job: {
    id: number;
    title: string;
    parsed: ParsedData;
    raw: RawData;
    metadata: {
      processed_at: string;
      llm_model: string;
    };
  };
}

export interface AnalysisMetadata {
  id: string;
  title: string;
  endpoint: string;
  last_updated?: string;
  temporal?: boolean;
}

export interface DataSummary {
  total_jobs: number;
  date_range: { start: string; end: string };
  jobs_with_salary: number;
  unique_companies: number;
  unique_skills: number;
}

export interface AnalysisIndexResponse {
  version: string;
  generated_at: string;
  available_analyses: AnalysisMetadata[];
  data_summary: DataSummary;
}

// Analysis Data Types
export interface SalaryStats {
  count: number;
  average: number;
  median: number;
  min: number;
  max: number;
  currency: string;
  period: string;
  percentile_25?: number;
  percentile_75?: number;
}

export interface SalaryDistribution {
  range: string;
  count: number;
  percentage: number;
}

export interface SalaryOverviewData {
  version: string;
  analysis_id: string;
  generated_at: string;
  type: 'static';
  data: {
    overall: SalaryStats;
    by_currency: SalaryStats[];
    distribution: SalaryDistribution[];
  };
  visualization_hints: {
    chart_types: string[];
    recommended_chart: string;
  };
}

export interface TrendDataPoint {
  date: string;
  count: number;
  new: number;
  closed: number;
}

export interface SalaryTrendDataPoint {
  date: string;
  average: number;
  median: number;
  sample_size: number;
}

export interface RemoteWorkDataPoint {
  date: string;
  remote: number;
  hybrid: number;
  on_site: number;
}

export interface MarketTrendsData {
  version: string;
  analysis_id: string;
  generated_at: string;
  type: 'temporal';
  granularity: string;
  data: {
    job_posting_volume: TrendDataPoint[];
    average_salary_trend: SalaryTrendDataPoint[];
    remote_work_adoption: RemoteWorkDataPoint[];
  };
  visualization_hints: {
    chart_types: string[];
    recommended_chart: string;
  };
}

export interface SkillData {
  name: string;
  count: number;
  average_salary?: number;
  percentage?: number;
}

export interface SkillsDemandData {
  version: string;
  analysis_id: string;
  generated_at: string;
  type: 'static';
  data: {
    top_hard_skills: SkillData[];
    top_soft_skills: SkillData[];
    emerging_skills: SkillData[];
  };
}

// Filters type
export interface Filters {
  title?: string;
  job_function?: string;
  seniority_level?: string;
  industry?: string;
  department?: string;
  job_family?: string;
  specialization?: string;
  education_level?: string;
  employment_type?: string;
  contract_type?: string;
  work_schedule?: string;
  shift_details?: string;
  remote_work?: string;
  travel_requirements?: string;
  city?: string;
  region?: string;
  country?: string;
  company?: string;
  company_size?: string;
  currency?: string;
  salary_period?: string;
  salary_range?: string;
  hard_skills?: string[];
  soft_skills?: string[];
  languages?: string[];
  certifications?: string[];
  licenses?: string[];
  benefits?: string[];
  work_environment?: string[];
  professional_development?: string[];
  work_life_balance?: string[];
  physical_requirements?: string[];
  work_conditions?: string[];
  special_requirements?: string[];
}
