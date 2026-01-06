# Visual Guide: Filtered Analysis Page

## Page Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Header: Moldova Job Market                          [Analysis ▼] [Theme] │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Filtered Analysis                                                        │
│  Apply filters using OR logic - jobs matching ANY selected filter        │
│                                                                            │
│  ┌────────────────────┬────────────────────────────────────────────────┐ │
│  │ Filters            │ Active Filters                  (3 filters)    │ │
│  │                    │                                                 │ │
│  │ ┌──────────────┐   │ ┌─────────────────────────────────────────┐  │ │
│  │ │ OR Logic     │   │ │ city == "Chisinau"                  [X] │  │ │
│  │ │ Jobs matching│   │ │ remote_work == "Fully Remote"       [X] │  │ │
│  │ │ ANY filter   │   │ │ seniority_level == "Senior"         [X] │  │ │
│  │ └──────────────┘   │ └─────────────────────────────────────────┘  │ │
│  │                    │                                                 │ │
│  │ [Clear All]        │ [Run Analysis with Filters]                    │ │
│  │                    ├─────────────────────────────────────────────── │ │
│  │ Job Details        │                                                 │ │
│  │ ▼ Job Title        │ Query Results                                  │ │
│  │   [Select...]      │                                                 │ │
│  │                    │ ┌───────────────────────────────────────────┐ │ │
│  │ ▼ Seniority Level  │ │                                           │ │ │
│  │   [Select...]      │ │        [Chart Visualization]              │ │ │
│  │                    │ │                                           │ │ │
│  │ ▼ Industry         │ │                                           │ │ │
│  │   [Select...]      │ └───────────────────────────────────────────┘ │ │
│  │                    │                                                 │ │
│  │ Location           │ ▼ SQL Query                                    │ │
│  │ ▼ City             │   SELECT...                                    │ │
│  │   [Select...]      │                                                 │ │
│  │                    │ ▼ View Data Table                              │ │
│  │ ▼ Remote Work      │   (collapsed)                                  │ │
│  │   [Select...]      │                                                 │ │
│  │                    ├─────────────────────────────────────────────── │ │
│  │ Company            │                                                 │ │
│  │ ▼ Company Name     │ Predefined Analyses                            │ │
│  │   [Select...]      │                                                 │ │
│  │                    │ ┌──────────────┬──────────────┬──────────────┐│ │
│  │ ▼ Company Size     │ │Tech Hub      │Remote vs     │Top Job       ││ │
│  │   [Select...]      │ │Analysis      │Office        │Functions     ││ │
│  └────────────────────┤ │              │Distribution  │              ││ │
│                        │ └──────────────┴──────────────┴──────────────┘│ │
│                        │ ... (7 more analyses)                          │ │
│                        └─────────────────────────────────────────────── │ │
└──────────────────────────────────────────────────────────────────────────┘
```

## Filter Badge Examples

### Namespace-Style Display
```
┌───────────────────────────────────┐
│ city == "Chisinau"            [X] │
└───────────────────────────────────┘

┌───────────────────────────────────┐
│ remote_work == "Fully Remote" [X] │
└───────────────────────────────────┘

┌───────────────────────────────────┐
│ job_function == "Engineering" [X] │
└───────────────────────────────────┘
```

## OR Logic Visual

### Example: City OR Remote Work
```
Filter Selection:
├─ city == "Chisinau"
└─ remote_work == "Fully Remote"

SQL Generated:
WHERE (ci.name = 'Chisinau') OR (rw.name = 'Fully Remote')

Result Set:
┌─────────────────────────────────────┐
│ All jobs in Chisinau                │
│   ├─ Office jobs in Chisinau        │
│   ├─ Hybrid jobs in Chisinau        │
│   └─ Remote jobs in Chisinau        │
├─────────────────────────────────────┤
│ All fully remote jobs               │
│   ├─ Remote jobs in Chisinau (dup)  │
│   ├─ Remote jobs in Balti           │
│   └─ Remote jobs in other cities    │
└─────────────────────────────────────┘
```

### Comparison: AND vs OR Logic

#### Jobs Page (AND Logic)
```
Filters Applied:
├─ city == "Chisinau"
└─ remote_work == "Fully Remote"

SQL: WHERE ci.name = 'Chisinau' AND rw.name = 'Fully Remote'

Result: Only jobs that are BOTH in Chisinau AND fully remote
┌─────────────────────────────┐
│ ✓ Remote job in Chisinau    │
│ ✗ Office job in Chisinau    │
│ ✗ Remote job in Balti       │
└─────────────────────────────┘
```

#### Filtered Analysis (OR Logic)
```
Filters Applied:
├─ city == "Chisinau"
└─ remote_work == "Fully Remote"

SQL: WHERE (ci.name = 'Chisinau') OR (rw.name = 'Fully Remote')

Result: Jobs that are EITHER in Chisinau OR fully remote (or both)
┌─────────────────────────────┐
│ ✓ Remote job in Chisinau    │
│ ✓ Office job in Chisinau    │
│ ✓ Remote job in Balti       │
└─────────────────────────────┘
```

## User Journey Flow

### Scenario 1: Compare Multiple Cities
```
1. User navigates to Analysis → Filtered Analysis
2. Selects: city == "Chisinau"
3. Selects: city == "Balti"
4. Clicks "Run Analysis with Filters"
5. Views chart comparing job market in both cities
```

### Scenario 2: Remote Work Analysis
```
1. User navigates to Analysis → Filtered Analysis
2. Selects: remote_work == "Fully Remote"
3. Selects: remote_work == "Hybrid"
4. Clicks predefined "Remote vs Office Distribution"
5. Views breakdown of remote work options
```

### Scenario 3: Skill Demand Research
```
1. User navigates to Analysis → Filtered Analysis
2. Selects: hard_skills == "Python"
3. Selects: hard_skills == "JavaScript"
4. Selects: hard_skills == "Java"
5. Clicks "Run Analysis with Filters"
6. Views analysis of jobs requiring any of these skills
```

## Chart Examples

### Bar Chart - Job Count by Category
```
Jobs Matching Filters (OR Logic)
                                      
Remote │████████████████ 450
Hybrid │████████ 200
Office │████ 100
       └─────┬─────┬─────┬─────┬─────
            100   200   300   400   500
```

### Doughnut Chart - Distribution
```
       ╱───────╲
      │         │
      │ Remote  │  60%
      │ 450     │
       ╲───────╱
           │
      ╱────┴────╲
     │  Hybrid  │  27%
     │  200     │
      ╲────┬────╱
           │
       ╱───┴───╲
      │ Office │  13%
      │  100   │
       ╲───────╱
```

## Predefined Analyses Preview

### 1. Tech Hub Analysis
**Description**: Jobs in major tech cities OR requiring key tech skills
**Chart Type**: Bar
**Example Output**:
- Chisinau: 350 jobs, avg salary 45,000 MDL
- Tech Skills: 280 jobs, avg salary 48,000 MDL

### 2. Remote vs Office Distribution  
**Description**: Compare fully remote, hybrid, and office-based
**Chart Type**: Doughnut
**Example Output**:
- Fully Remote: 45%
- Hybrid: 30%
- Office Only: 25%

### 3. Seniority Level Distribution
**Description**: Breakdown by seniority with salary info
**Chart Type**: Bar
**Example Output**:
- Senior: 180 jobs, avg 55,000 MDL
- Mid-level: 250 jobs, avg 38,000 MDL
- Junior: 150 jobs, avg 22,000 MDL

## Benefits Over Jobs Page

1. **Broader Analysis**: Capture jobs matching ANY criteria, not just specific combinations
2. **Market Trends**: See overall patterns across multiple dimensions
3. **Comparison**: Compare different options (e.g., multiple cities) in one view
4. **Flexibility**: Mix and match filters without over-constraining results
5. **Insights**: Discover opportunities you might miss with AND logic

## Technical Notes

- All 10 predefined queries use proper LEFT JOINs to avoid data loss
- OR logic implemented via SQL `OR` operators and `IN` clauses
- Many-to-many relationships handled via subqueries for efficiency
- Filters are applied consistently across all query types
- Chart types chosen to best visualize each analysis
