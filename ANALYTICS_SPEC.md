# Job Market Analytics & Reporting Specification

This document outlines the planned analytics features and HTML report generation for the job market scraper. These features are designed for **job seekers** to gain insights into the Moldovan job market across all industries and sectors (manufacturing, retail, healthcare, IT, finance, hospitality, agriculture, construction, etc.).

## Overview

The analytics system will process data from `data.db` (LLM-extracted structured job information) to generate insights and trends valuable for job seekers. The output will be an interactive HTML site with visualizations and filterable data.

## Analytics Categories

### 1. Salary Analysis

Provide salary insights at multiple granularity levels to help job seekers understand compensation trends.

#### 1.1 Overall Market Salary Trends
- **Metric**: Average, median, min, max salaries across all jobs
- **Breakdown by**:
  - Currency (MDL, EUR, USD, GBP)
  - Salary period (hourly, monthly, yearly)
- **Visualization**: Box plots, histograms showing salary distributions
- **Time series**: Track how average salaries change over time (if historical data available)

#### 1.2 Salary by Job Function
- **Metric**: Average and median salary per job function (e.g., Sales, Marketing, Engineering, Healthcare, Administration, Manufacturing, Customer Service, etc.)
- **Visualization**: Bar charts comparing job functions
- **Ranking**: Top 10 highest-paying job functions
- **Sample size**: Show number of jobs in each category

#### 1.3 Salary by Seniority Level
- **Metric**: Average salary progression across seniority levels
  - Entry → Junior → Mid → Senior → Lead → Manager → Director → Executive
- **Visualization**: Line chart showing salary growth path
- **Comparison**: Overlay multiple job functions to compare career progression

#### 1.4 Salary by Specialization
- **Metric**: Average and median salary for specific specializations
- **Examples**: Nurse, Electrician, Accountant, Sales Manager, Machine Operator, Teacher, Driver, etc.
- **Visualization**: Sortable table with bar charts
- **Filters**: Allow filtering by job function, seniority, location

#### 1.5 Salary by Industry
- **Metric**: Average compensation across different industries
- **Examples**: Manufacturing, Retail, Healthcare, Finance, IT, Agriculture, Construction, Hospitality, Transportation, Education, etc.
- **Visualization**: Horizontal bar chart
- **Insight**: Which industries pay best for similar roles

#### 1.6 Salary by Location
- **Metric**: Average salary by city, region
- **Visualization**: Map visualization (if feasible) or bar chart
- **Comparison**: Cost-of-living adjusted salaries (future enhancement)

#### 1.7 Salary by Company Size
- **Metric**: Average compensation at startup vs. small vs. medium vs. large vs. enterprise companies
- **Visualization**: Grouped bar chart
- **Insight**: Trade-offs between company sizes

#### 1.8 Salary by Education Level
- **Metric**: Average salary by required education (none, high school, vocational, bachelor's, master's, PhD)
- **Visualization**: Bar chart showing ROI of education
- **Insight**: Does higher education correlate with higher pay?

#### 1.9 Salary by Experience Years
- **Metric**: Average salary by years of experience required (0, 1-2, 3-5, 5-10, 10+)
- **Visualization**: Scatter plot with trend line
- **Insight**: Experience vs. compensation curve

### 2. Skills Analysis

Help job seekers understand which skills are in demand and how they correlate with compensation.

#### 2.1 Most In-Demand Skills
- **Metric**: Top 20 hard skills by frequency of appearance in job postings
- **Breakdown by**:
  - Job function
  - Seniority level
  - Time period
- **Visualization**: Word cloud, horizontal bar chart
- **Trend**: Track skill popularity over time

#### 2.2 Skills to Salary Correlation
- **Metric**: Average salary for jobs requiring specific skills
- **Analysis**: Which skills command the highest salaries?
- **Examples**: 
  - Welding: $X average salary
  - Accounting software (e.g., 1C): $Y average salary
  - Heavy machinery operation: $Z average salary
  - English language proficiency: $W average salary
- **Visualization**: Bubble chart (skill frequency vs. average salary)
- **Insight**: High-value skills to learn for career growth

#### 2.3 Skill Combinations
- **Metric**: Common skill pairs/triplets (e.g., "Driver's License + English + Customer Service" or "Welding + Blueprint Reading + Safety Certification")
- **Analysis**: Which skill combinations appear together frequently?
- **Visualization**: Network graph or co-occurrence matrix
- **Salary impact**: Does combining certain skills increase average salary?

#### 2.4 Emerging Skills
- **Metric**: Skills showing rapid growth in job postings (month-over-month or quarter-over-quarter)
- **Visualization**: Line chart showing skill trend
- **Insight**: Early indicators of market shifts

#### 2.5 Skills Gap by Seniority
- **Metric**: How skill requirements differ across seniority levels
- **Visualization**: Stacked bar chart or heatmap
- **Insight**: What skills to develop for career advancement

### 3. Job Availability & Duration Analysis

Understand job market dynamics and employer behavior.

#### 3.1 Job Posting Duration (Time to Fill)
- **Metric**: Average number of days a job posting stays active
- **Breakdown by**:
  - Job function
  - Seniority level
  - Company size
  - Salary range
- **Visualization**: Box plot showing distribution
- **Insight**: Which roles are hardest to fill?

#### 3.2 Job Posting Velocity
- **Metric**: Number of new jobs posted per day/week/month
- **Trend**: Track over time to identify market heating/cooling
- **Breakdown by**: Job function, industry, location
- **Visualization**: Time series line chart
- **Insight**: Market growth indicators

#### 3.3 Jobs Alive Trends
- **Metric**: Track ratio of active vs. expired job postings over time
- **Analysis**: Market health indicator (more active jobs = healthy market)
- **Visualization**: Stacked area chart
- **Breakdown by**: Job function, location

#### 3.4 "Unfillable" Positions
- **Metric**: Jobs that remain open for extended periods (e.g., 90+ days, 1+ year)
- **Analysis**: Identify positions or companies with unrealistic requirements
- **Warning flag**: Jobs open for 1+ year might indicate:
  - Unrealistic salary expectations
  - Too many required skills
  - Poor company reputation
  - Role not actually open (evergreen posting)
- **Visualization**: Table with filters
- **Insight**: Help job seekers avoid problematic postings

#### 3.5 Company Posting Patterns
- **Metric**: Companies with highest job posting volume
- **Analysis**: 
  - Rapidly growing companies (increasing postings)
  - High-churn companies (many short-duration postings)
  - Consistent hirers
- **Visualization**: Company ranking table
- **Insight**: Which companies are actively hiring?

### 4. Employment Type & Work Arrangement Analysis

Help job seekers understand market trends in work flexibility.

#### 4.1 Remote Work Availability
- **Metric**: Percentage of jobs offering remote, hybrid, on-site
- **Trend**: Track over time
- **Breakdown by**: Job function, seniority, company size
- **Visualization**: Pie chart, stacked bar chart
- **Insight**: Which fields offer most remote work?

#### 4.2 Contract Types
- **Metric**: Distribution of permanent vs. fixed-term vs. contract vs. internship positions
- **Breakdown by**: Job function, seniority
- **Visualization**: Stacked bar chart
- **Insight**: Employment security by field

#### 4.3 Work Schedule Flexibility
- **Metric**: Percentage offering flexible vs. standard vs. shift work
- **Breakdown by**: Industry, job function
- **Visualization**: Grouped bar chart

### 5. Benefits & Perks Analysis

Understand non-salary compensation trends.

#### 5.1 Most Common Benefits
- **Metric**: Top benefits by frequency (health insurance, PTO, training budget, etc.)
- **Breakdown by**: Company size, industry
- **Visualization**: Horizontal bar chart
- **Insight**: What to expect/negotiate

#### 5.2 Benefits by Salary Range
- **Analysis**: Do higher-paying jobs offer more/better benefits?
- **Visualization**: Correlation scatter plot or grouped comparison

#### 5.3 Professional Development Opportunities
- **Metric**: Percentage of jobs offering training, certifications, conferences
- **Breakdown by**: Job function, company size
- **Insight**: Which roles invest in employee growth?

### 6. Job Requirements Analysis

Help job seekers understand what employers are looking for.

#### 6.1 Education Requirements Trends
- **Metric**: Distribution of required education levels
- **Trend**: Are requirements increasing or decreasing over time?
- **Breakdown by**: Job function, seniority
- **Visualization**: Stacked area chart

#### 6.2 Experience Requirements
- **Metric**: Average years of experience required
- **Breakdown by**: Seniority level, job function
- **Visualization**: Box plot
- **Insight**: Are requirements realistic?

#### 6.3 Language Requirements
- **Metric**: Most commonly required languages (Romanian, Russian, English, etc.)
- **Proficiency levels required
- **Breakdown by**: Job function, company type
- **Visualization**: Stacked bar chart

#### 6.4 Certification Requirements
- **Metric**: Most commonly required certifications
- **Salary premium**: Do certifications correlate with higher pay?
- **Breakdown by**: Job function
- **Visualization**: Table with frequency and average salary

### 7. Location-Based Analysis

Help job seekers understand geographic market differences.

#### 7.1 Jobs by Location
- **Metric**: Number of job postings by city/region
- **Visualization**: Map or bar chart
- **Insight**: Where are the most opportunities?

#### 7.2 Location vs. Remote Work
- **Metric**: Percentage of remote-friendly jobs by location
- **Insight**: Do certain cities have more remote options?

#### 7.3 Location-Specific Trends
- **Analysis**: How do job characteristics vary by location?
  - Salary differences
  - Industry concentration
  - Skill demands

### 8. Company Analysis

Insights about employers in the market.

#### 8.1 Top Hiring Companies
- **Metric**: Companies with most active job postings
- **Visualization**: Table with company info
- **Link**: Direct links to their job listings

#### 8.2 Company Size Distribution
- **Metric**: Percentage of jobs at startups vs. large enterprises
- **Salary comparison**: Pay differences by company size

#### 8.3 Company Hiring Velocity
- **Metric**: New postings per month by company
- **Insight**: Identify rapidly growing companies

## HTML Site Structure

### Navigation
- Dashboard (overview page)
- Salary Analytics
- Skills Analysis
- Job Market Trends
- Requirements Analysis
- Companies
- Search & Filter Jobs

### Features
- **Interactive filters**: Job function, location, seniority, salary range, remote work
- **Responsive design**: Mobile-friendly
- **Export options**: Download filtered data as CSV
- **Share functionality**: Share specific views via URL parameters
- **Dark/light mode**: Theme toggle
- **Date range selector**: Filter by time period (last 7 days, 30 days, 3 months, all time)

### Visualizations
- Use **Chart.js** or **Plotly** for interactive charts
- **D3.js** for advanced visualizations (network graphs, maps)
- **DataTables** for sortable, filterable tables
- **Color scheme**: Professional, accessible (colorblind-friendly)

### Data Freshness
- Display last update timestamp on every page
- Show data collection statistics (# jobs scraped, date range)

### Technical Implementation
- **Static site generation**: Generate HTML/CSS/JS files that can be hosted anywhere
- **No backend required**: All data embedded in JS or loaded from JSON files
- **Fast loading**: Optimize for performance with lazy loading
- **SEO-friendly**: Proper meta tags, semantic HTML

## Data Privacy & Ethics

- **No personal information**: Never display contact emails, phone numbers, or names in public reports
- **Aggregation only**: All analytics based on aggregated data, not individual jobs (unless >10 jobs in category)
- **Company anonymity option**: Allow filtering out company names if requested
- **Fair use**: Respect robots.txt and terms of service of scraped sites

## Implementation Priority

### Phase 1 (MVP)
1. Salary by job function, seniority, location
2. Top in-demand skills
3. Skills to salary correlation
4. Job posting duration
5. Remote work availability
6. Basic HTML dashboard with filtering

### Phase 2
1. Time series trends (salary, job volume, skills)
2. Skill combinations and correlations
3. Unfillable positions analysis
4. Benefits analysis
5. Enhanced visualizations (maps, network graphs)

### Phase 3
1. Predictive analytics (salary predictions, job availability forecasts)
2. Personalized recommendations (based on user skills/experience)
3. Email alerts for matching jobs
4. Mobile app

## Success Metrics

- **Usefulness**: Do job seekers find actionable insights?
- **Accuracy**: How well do salary estimates match reality?
- **Coverage**: Percentage of jobs with complete data
- **Freshness**: How recent is the data?
- **Adoption**: Number of users viewing reports

## Technical Notes

- **Performance**: Pre-calculate analytics and cache results
- **Incremental updates**: Only reprocess new/changed data
- **Scalability**: Design for thousands of jobs, hundreds of companies
- **Maintainability**: Modular code, clear documentation
- **Testing**: Validate analytics with known data samples

## Future Enhancements

- **Career path mapping**: Visualize common career progressions
- **Skill gap analysis**: Compare job seeker skills to market demands
- **Salary negotiation tool**: Provide data-driven salary ranges for negotiation
- **Job match score**: Score how well a job seeker matches a posting
- **Market reports**: Monthly PDF reports with key insights
- **API access**: Allow developers to query analytics data
