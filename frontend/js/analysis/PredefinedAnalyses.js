// Predefined analyses organized by type
// General Trends: Overall market insights (no user filters applied by default)
// Personal Interest: Filtered analyses based on user's career interests

const PredefinedAnalyses = {
    // ========== GENERAL MARKET TRENDS ==========
    // These show overall job market health and don't require personal filters
    generalTrends: [
        {
            name: 'Daily Job Openings',
            description: 'Track how many new jobs are posted each day',
            sql: `SELECT 
    DATE(posting_date) as date,
    COUNT(*) as jobs_posted,
    COUNT(DISTINCT company_name_id) as companies_hiring
FROM job_details
WHERE posting_date >= date('now', '-90 days')
GROUP BY DATE(posting_date)
ORDER BY date ASC`,
            chartType: 'line',
            category: 'general',
            applyFilters: false  // Don't apply user filters to general trends
        },
        {
            name: 'Job Creation Rate',
            description: 'Average number of jobs created per day over time',
            sql: `SELECT 
    strftime('%Y-%m', posting_date) as month,
    COUNT(*) as total_jobs,
    ROUND(COUNT(*) * 1.0 / 30, 1) as avg_per_day
FROM job_details
WHERE posting_date >= date('now', '-6 months')
GROUP BY month
ORDER BY month ASC`,
            chartType: 'bar',
            category: 'general',
            applyFilters: false
        },
        {
            name: 'Market Activity by Industry',
            description: 'Which industries are most active in hiring',
            sql: `SELECT 
    i.name as industry,
    COUNT(*) as job_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM job_details WHERE posting_date >= date('now', '-30 days')), 2) as market_share
FROM job_details jd
JOIN industries i ON jd.industry_id = i.id
WHERE jd.posting_date >= date('now', '-30 days')
GROUP BY i.name
HAVING job_count >= 5
ORDER BY job_count DESC
LIMIT 15`,
            chartType: 'bar',
            category: 'general',
            applyFilters: false
        },
        {
            name: 'Seasonal Hiring Patterns',
            description: 'Best months to apply based on historical hiring data',
            sql: `SELECT 
    CASE CAST(strftime('%m', posting_date) AS INTEGER)
        WHEN 1 THEN 'January'
        WHEN 2 THEN 'February'
        WHEN 3 THEN 'March'
        WHEN 4 THEN 'April'
        WHEN 5 THEN 'May'
        WHEN 6 THEN 'June'
        WHEN 7 THEN 'July'
        WHEN 8 THEN 'August'
        WHEN 9 THEN 'September'
        WHEN 10 THEN 'October'
        WHEN 11 THEN 'November'
        ELSE 'December'
    END as month,
    COUNT(*) as job_count
FROM job_details
GROUP BY strftime('%m', posting_date)
ORDER BY CAST(strftime('%m', posting_date) AS INTEGER)`,
            chartType: 'line',
            category: 'general',
            applyFilters: false
        },
        {
            name: 'Top Hiring Companies',
            description: 'Companies posting the most jobs recently',
            sql: `SELECT 
    c.name as company,
    COUNT(*) as jobs_posted,
    COUNT(DISTINCT jd.title_id) as unique_roles
FROM job_details jd
JOIN companies c ON jd.company_name_id = c.id
WHERE jd.posting_date >= date('now', '-30 days')
GROUP BY c.name
ORDER BY jobs_posted DESC
LIMIT 20`,
            chartType: 'bar',
            category: 'general',
            applyFilters: false
        }
    ],
    
    // ========== PERSONAL INTEREST ANALYSES ==========
    // These analyses WILL apply user's selected filters (industry, function, skills, etc.)
    personalInterest: [
        {
            name: 'Salary Trends in Your Field',
            description: 'Salary distribution for jobs matching your interests',
            sql: `SELECT 
    CASE 
        WHEN min_salary < 10000 THEN '< 10k'
        WHEN min_salary < 20000 THEN '10k-20k'
        WHEN min_salary < 30000 THEN '20k-30k'
        WHEN min_salary < 40000 THEN '30k-40k'
        WHEN min_salary < 50000 THEN '40k-50k'
        ELSE '50k+'
    END as salary_range,
    COUNT(*) as job_count
FROM job_details
WHERE min_salary IS NOT NULL
GROUP BY salary_range
ORDER BY 
    CASE salary_range
        WHEN '< 10k' THEN 1
        WHEN '10k-20k' THEN 2
        WHEN '20k-30k' THEN 3
        WHEN '30k-40k' THEN 4
        WHEN '40k-50k' THEN 5
        ELSE 6
    END`,
            chartType: 'bar',
            category: 'personal',
            applyFilters: true
        },
        {
            name: 'Top Skills in Demand',
            description: 'Most requested skills for your career path',
            sql: `SELECT 
    hs.name as skill,
    COUNT(DISTINCT jd.id) as job_count,
    ROUND(AVG(jd.max_salary)) as avg_salary
FROM hard_skills hs
JOIN job_details_hard_skills jhs ON hs.id = jhs.hard_skills_id
JOIN job_details jd ON jhs.job_details_id = jd.id
WHERE jd.max_salary IS NOT NULL
GROUP BY hs.name
HAVING job_count >= 3
ORDER BY job_count DESC
LIMIT 20`,
            chartType: 'bar',
            category: 'personal',
            applyFilters: true
        },
        {
            name: 'Job Opportunities by Seniority',
            description: 'Available positions at different experience levels',
            sql: `SELECT 
    sl.name as seniority,
    COUNT(*) as job_count,
    ROUND(AVG(jd.max_salary)) as avg_salary
FROM job_details jd
JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
WHERE jd.max_salary IS NOT NULL
GROUP BY sl.name
ORDER BY avg_salary DESC`,
            chartType: 'bar',
            category: 'personal',
            applyFilters: true
        },
        {
            name: 'Remote Work Availability',
            description: 'Remote vs hybrid vs on-site opportunities in your field',
            sql: `SELECT 
    rw.name as remote_option,
    COUNT(*) as job_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM job_details), 2) as percentage
FROM job_details jd
LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
GROUP BY rw.name
ORDER BY job_count DESC`,
            chartType: 'doughnut',
            category: 'personal',
            applyFilters: true
        },
        {
            name: 'Experience Requirements',
            description: 'Years of experience typically required',
            sql: `SELECT 
    CASE 
        WHEN experience_years = 0 THEN 'Entry Level'
        WHEN experience_years BETWEEN 1 AND 2 THEN '1-2 years'
        WHEN experience_years BETWEEN 3 AND 5 THEN '3-5 years'
        WHEN experience_years BETWEEN 6 AND 10 THEN '6-10 years'
        ELSE '10+ years'
    END as experience_range,
    COUNT(*) as job_count
FROM job_details
WHERE experience_years IS NOT NULL
GROUP BY experience_range
ORDER BY 
    CASE experience_range
        WHEN 'Entry Level' THEN 1
        WHEN '1-2 years' THEN 2
        WHEN '3-5 years' THEN 3
        WHEN '6-10 years' THEN 4
        ELSE 5
    END`,
            chartType: 'bar',
            category: 'personal',
            applyFilters: true
        },
        {
            name: 'Top Companies Hiring in Your Field',
            description: 'Companies with most opportunities matching your profile',
            sql: `SELECT 
    c.name as company,
    COUNT(*) as job_count,
    ROUND(AVG(jd.max_salary)) as avg_salary
FROM job_details jd
JOIN companies c ON jd.company_name_id = c.id
WHERE jd.max_salary IS NOT NULL
GROUP BY c.name
HAVING job_count >= 2
ORDER BY job_count DESC
LIMIT 20`,
            chartType: 'bar',
            category: 'personal',
            applyFilters: true
        },
        {
            name: 'Certifications in Demand',
            description: 'Most valuable certifications in your field',
            sql: `SELECT 
    cert.name as certification,
    COUNT(DISTINCT jd.id) as job_count,
    ROUND(AVG(jd.max_salary)) as avg_salary
FROM certifications cert
JOIN job_details_certifications jc ON cert.id = jc.certifications_id
JOIN job_details jd ON jc.job_details_id = jd.id
WHERE jd.max_salary IS NOT NULL
GROUP BY cert.name
HAVING job_count >= 2
ORDER BY job_count DESC
LIMIT 15`,
            chartType: 'bar',
            category: 'personal',
            applyFilters: true
        },
        {
            name: 'Employment Types Available',
            description: 'Full-time, part-time, and contract opportunities',
            sql: `SELECT 
    et.name as employment_type,
    COUNT(*) as job_count,
    ROUND(AVG(jd.max_salary)) as avg_salary
FROM job_details jd
JOIN employment_types et ON jd.employment_type_id = et.id
WHERE jd.max_salary IS NOT NULL
GROUP BY et.name
ORDER BY job_count DESC`,
            chartType: 'bar',
            category: 'personal',
            applyFilters: true
        },
        {
            name: 'Geographic Distribution',
            description: 'Where jobs in your field are located',
            sql: `SELECT 
    c.name as city,
    COUNT(*) as job_count,
    ROUND(AVG(jd.max_salary)) as avg_salary
FROM job_details jd
JOIN cities c ON jd.city_id = c.id
WHERE jd.max_salary IS NOT NULL
GROUP BY c.name
HAVING job_count >= 3
ORDER BY job_count DESC
LIMIT 20`,
            chartType: 'bar',
            category: 'personal',
            applyFilters: true
        },
        {
            name: 'Benefits Offered',
            description: 'Most common benefits in your target positions',
            sql: `SELECT 
    b.description as benefit,
    COUNT(DISTINCT jd.id) as job_count,
    ROUND(COUNT(DISTINCT jd.id) * 100.0 / (SELECT COUNT(*) FROM job_details), 2) as percentage
FROM benefits b
JOIN job_details_benefits jb ON b.id = jb.benefits_id
JOIN job_details jd ON jb.job_details_id = jd.id
GROUP BY b.description
HAVING job_count >= 2
ORDER BY job_count DESC
LIMIT 15`,
            chartType: 'bar',
            category: 'personal',
            applyFilters: true
        }
    ],
    
    // Helper to get all analyses as flat array (for backward compatibility)
    getAllAnalyses: function() {
        return [...this.generalTrends, ...this.personalInterest];
    }
};
