// Predefined Filtered Analyses - High Quality Queries with OR logic
// These analyses work with the OR filter logic of the Filtered Analysis Page

const FilteredAnalyses = [
    {
        name: 'Tech Hub Analysis',
        description: 'Analyze jobs in major tech cities OR requiring key tech skills',
        baseSql: `
            SELECT 
                CASE 
                    WHEN ci.name IN ('Chisinau', 'Balti') THEN ci.name
                    ELSE 'Tech Skills'
                END as category,
                COUNT(DISTINCT jd.id) as job_count,
                ROUND(AVG(jd.max_salary)) as avg_max_salary
            FROM job_details jd
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            GROUP BY category
            ORDER BY job_count DESC`,
        chartType: 'bar'
    },
    {
        name: 'Remote vs Office Distribution',
        description: 'Compare fully remote, hybrid, and office-based positions',
        baseSql: `
            SELECT 
                rw.name as remote_option,
                COUNT(DISTINCT jd.id) as job_count,
                ROUND(AVG(jd.max_salary)) as avg_max_salary
            FROM job_details jd
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            GROUP BY rw.name
            ORDER BY job_count DESC`,
        chartType: 'doughnut'
    },
    {
        name: 'Top Job Functions Analysis',
        description: 'Analyze most common job functions',
        baseSql: `
            SELECT 
                jf.name as job_function,
                COUNT(DISTINCT jd.id) as job_count,
                ROUND(AVG(jd.max_salary)) as avg_max_salary
            FROM job_details jd
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            GROUP BY jf.name
            HAVING job_count >= 5
            ORDER BY job_count DESC
            LIMIT 15`,
        chartType: 'bar'
    },
    {
        name: 'Seniority Level Distribution',
        description: 'Breakdown of positions by seniority level',
        baseSql: `
            SELECT 
                sl.name as seniority_level,
                COUNT(DISTINCT jd.id) as job_count,
                ROUND(AVG(jd.min_salary)) as avg_min_salary,
                ROUND(AVG(jd.max_salary)) as avg_max_salary
            FROM job_details jd
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            WHERE jd.max_salary IS NOT NULL
            GROUP BY sl.name
            ORDER BY avg_max_salary DESC`,
        chartType: 'bar'
    },
    {
        name: 'Industry Comparison',
        description: 'Compare opportunities across different industries',
        baseSql: `
            SELECT 
                ind.name as industry,
                COUNT(DISTINCT jd.id) as job_count,
                ROUND(AVG(jd.max_salary)) as avg_max_salary
            FROM job_details jd
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            WHERE jd.max_salary IS NOT NULL
            GROUP BY ind.name
            HAVING job_count >= 10
            ORDER BY job_count DESC
            LIMIT 15`,
        chartType: 'bar'
    },
    {
        name: 'Geographic Distribution',
        description: 'Job opportunities by location',
        baseSql: `
            SELECT 
                ci.name as city,
                COUNT(DISTINCT jd.id) as job_count,
                ROUND(AVG(jd.max_salary)) as avg_max_salary
            FROM job_details jd
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            WHERE jd.max_salary IS NOT NULL
            GROUP BY ci.name
            HAVING job_count >= 10
            ORDER BY job_count DESC
            LIMIT 20`,
        chartType: 'bar'
    },
    {
        name: 'Employment Type Analysis',
        description: 'Full-time, part-time, contract distribution',
        baseSql: `
            SELECT 
                et.name as employment_type,
                COUNT(DISTINCT jd.id) as job_count,
                ROUND(AVG(jd.max_salary)) as avg_max_salary
            FROM job_details jd
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            WHERE jd.max_salary IS NOT NULL
            GROUP BY et.name
            ORDER BY job_count DESC`,
        chartType: 'doughnut'
    },
    {
        name: 'Company Size Preferences',
        description: 'Opportunities by company size',
        baseSql: `
            SELECT 
                cs.name as company_size,
                COUNT(DISTINCT jd.id) as job_count,
                ROUND(AVG(jd.max_salary)) as avg_max_salary
            FROM job_details jd
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            WHERE jd.max_salary IS NOT NULL
            GROUP BY cs.name
            ORDER BY job_count DESC`,
        chartType: 'doughnut'
    },
    {
        name: 'Education Requirements',
        description: 'Distribution of education level requirements',
        baseSql: `
            SELECT 
                el.name as education_level,
                COUNT(DISTINCT jd.id) as job_count,
                ROUND(AVG(jd.max_salary)) as avg_max_salary
            FROM job_details jd
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            WHERE jd.max_salary IS NOT NULL
            GROUP BY el.name
            ORDER BY job_count DESC`,
        chartType: 'bar'
    },
    {
        name: 'Top Hiring Companies',
        description: 'Companies with most job openings',
        baseSql: `
            SELECT 
                c.name as company,
                COUNT(DISTINCT jd.id) as job_count,
                ROUND(AVG(jd.max_salary)) as avg_max_salary
            FROM job_details jd
            LEFT JOIN companies c ON jd.company_name_id = c.id
            LEFT JOIN titles t ON jd.title_id = t.id
            LEFT JOIN job_functions jf ON jd.job_function_id = jf.id
            LEFT JOIN seniority_levels sl ON jd.seniority_level_id = sl.id
            LEFT JOIN cities ci ON jd.city_id = ci.id
            LEFT JOIN remote_work_options rw ON jd.remote_work_id = rw.id
            LEFT JOIN industries ind ON jd.industry_id = ind.id
            LEFT JOIN employment_types et ON jd.employment_type_id = et.id
            LEFT JOIN contract_types ct ON jd.contract_type_id = ct.id
            LEFT JOIN departments d ON jd.department_id = d.id
            LEFT JOIN specializations sp ON jd.specialization_id = sp.id
            LEFT JOIN education_levels el ON jd.required_education_id = el.id
            LEFT JOIN company_sizes cs ON jd.company_size_id = cs.id
            LEFT JOIN job_families jf2 ON jd.job_family_id = jf2.id
            LEFT JOIN work_schedules ws ON jd.work_schedule_id = ws.id
            LEFT JOIN shift_details sd ON jd.shift_details_id = sd.id
            LEFT JOIN travel_requirements tr ON jd.travel_required_id = tr.id
            LEFT JOIN regions reg ON jd.region_id = reg.id
            LEFT JOIN countries cou ON jd.country_id = cou.id
            WHERE jd.max_salary IS NOT NULL
            GROUP BY c.name
            HAVING job_count >= 5
            ORDER BY job_count DESC
            LIMIT 20`,
        chartType: 'bar'
    }
];
