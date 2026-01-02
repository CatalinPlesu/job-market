# Filter Usage Guide

This guide explains how to use the comprehensive filtering system in the Moldova Job Market frontend application.

## Overview

The application now supports filtering on **30+ fields** from the job database, with both single-select and multi-select capabilities.

## Filter Types

### Single-Select Filters (19 fields)

These filters allow you to select one value from a dropdown. They represent many-to-one relationships in the database.

**Job Classification:**
- **Job Title** - The standardized job title
- **Job Function** - Primary job function (e.g., Engineering, Marketing)
- **Seniority Level** - Career level (e.g., Junior, Mid-level, Senior)
- **Industry** - Industry sector
- **Department** - Department within organization
- **Job Family** - Broader job category
- **Specialization** - Specific area of expertise

**Work Arrangement:**
- **Employment Type** - Full-time, Part-time, Contract, etc.
- **Contract Type** - Permanent, Temporary, Freelance, etc.
- **Work Schedule** - Standard, Flexible, Shift-based, etc.
- **Shift Details** - Day shift, Night shift, Rotating, etc.
- **Remote Work** - On-site, Hybrid, Remote
- **Travel Required** - None, Occasional, Frequent, etc.

**Requirements:**
- **Education Level** - High School, Bachelor's, Master's, etc.

**Location:**
- **City** - City location
- **Region** - Regional area
- **Country** - Country

**Company:**
- **Company Name** - Employer name
- **Company Size** - Small, Medium, Large, Enterprise

### Multi-Select Filters (11 fields)

These filters allow you to select **multiple values** from a listbox. They represent many-to-many relationships. Jobs must have **ALL** selected items (AND logic).

**Technical Requirements:**
- **Hard Skills** - Technical skills required (e.g., Python, JavaScript, SQL)
- **Soft Skills** - Interpersonal skills (e.g., Communication, Leadership)
- **Certifications** - Required certifications
- **Licenses** - Required licenses

**Benefits & Culture:**
- **Benefits** - Job benefits offered
- **Work Environment** - Work environment characteristics
- **Professional Development** - Learning and growth opportunities
- **Work Life Balance** - Work-life balance features

**Special Conditions:**
- **Physical Requirements** - Physical demands of the job
- **Work Conditions** - Working condition details
- **Special Requirements** - Additional special requirements

### Range Filters (4 fields)

These filters allow you to specify a numeric range:

- **Salary Range (Min/Max)** - Filter by salary in MDL
- **Experience Range (Min/Max)** - Filter by years of experience

### Text Search

**Global Search** - Search across job titles, companies, skills, and locations

## How to Use Filters

### Single-Select Filters

1. Click on the dropdown menu
2. Select one option from the list
3. Select "All" to clear the filter
4. The job list updates automatically

**Example:**
```
City: Chisinau
Seniority Level: Senior
```

### Multi-Select Filters

1. Click inside the listbox (it will have multiple visible rows)
2. Hold **Ctrl** (Windows/Linux) or **Cmd** (Mac) and click to select multiple items
3. Click again to deselect an item
4. The number of selected items appears as a badge next to the label
5. The job list updates automatically

**Example:**
```
Hard Skills: [JavaScript, Python, React]  (3)
Benefits: [Health Insurance, Remote Work]  (2)
```

**Important:** Jobs must have **ALL** selected items. If you select JavaScript, Python, and React, only jobs requiring all three will be shown.

### Range Filters

1. Enter minimum value (optional)
2. Enter maximum value (optional)
3. Leave blank for no limit
4. The filter applies after you stop typing (500ms delay)

**Example:**
```
Salary Range: 15000 - 30000 MDL
Experience: 3 - 5 years
```

### Combining Filters

You can combine any number of filters. All filters use **AND logic** between different filter types:

**Example Combination:**
```
City: Chisinau
Seniority Level: Senior
Hard Skills: [JavaScript, React]
Salary Min: 20000
```

This will show only jobs that:
- Are located in Chisinau **AND**
- Are for Senior level **AND**
- Require both JavaScript AND React **AND**
- Offer minimum salary of 20000 MDL

## Filter Counts

Each filter option shows a count in parentheses indicating how many jobs match that option:

```
City: Chisinau (245)
City: Bălți (87)
```

**Dynamic Counts:** When you apply filters, the counts for other filters update to show only jobs that match your current selection. This helps you understand the impact of each filter combination.

## URL Sharing and Bookmarks

All filter selections are saved in the URL, making it easy to:

### Share Filter Combinations

Copy the URL from your browser and share it with others. They'll see the same filter selections.

**Example URL:**
```
/jobs?city=Chisinau&seniority_level=Senior&hard_skills=JavaScript,React&salaryMin=20000
```

### Bookmark Searches

Save URLs as browser bookmarks to quickly return to common filter combinations.

### Use Browser Navigation

The back and forward buttons work correctly with filters.

## Clear Filters

Click the **"Clear All"** button at the top of the filter panel to remove all active filters and start fresh.

## Tips and Best Practices

### Finding the Right Jobs

1. **Start Broad**: Begin with 1-2 filters to see available options
2. **Refine Gradually**: Add more filters based on the counts shown
3. **Use Multi-Select Wisely**: Remember that jobs must have ALL selected skills/benefits
4. **Check Counts**: Zero results? Remove some filters to broaden your search

### Multi-Select Strategy

**For Skills:**
- Select only **essential** skills if you want more results
- Add more skills only if you need highly specialized positions
- Consider that "JavaScript, React, Node.js" is more restrictive than just "JavaScript"

**For Benefits:**
- Selecting multiple benefits requires jobs to offer ALL of them
- This helps find comprehensive benefit packages
- But it may exclude good jobs that offer most but not all benefits

### Performance

- Filters update in real-time (client-side processing)
- Large multi-select combinations may take longer to process
- All data is cached in your browser for instant subsequent filtering

## Filter Hierarchy

Some filters work better in combination:

### Geographic Filters
```
Country → Region → City
```
Most specific: City
Least specific: Country

### Job Classification
```
Job Family → Job Function → Specialization
```
Most specific: Specialization
Least specific: Job Family

### Seniority Filters
```
Seniority Level + Experience Years
```
These complement each other for precise targeting

## Advanced Use Cases

### Find Remote Senior Developer Jobs
```
Filters:
- Remote Work: Remote
- Seniority Level: Senior
- Hard Skills: [Your primary language, e.g., Python]
- Salary Min: 25000
```

### Find Entry-Level Opportunities
```
Filters:
- Seniority Level: Entry Level
- Experience Max: 2
- City: [Your city]
```

### Find Jobs with Great Benefits
```
Filters:
- Benefits: [Health Insurance, Professional Development, Flexible Schedule]
- Work Life Balance: [Any relevant options]
```

### Find Specialized Positions
```
Filters:
- Specialization: [Your specialization]
- Certifications: [Required certs]
- Experience Min: [Your experience]
```

## Troubleshooting

### No Results Shown

**Possible causes:**
1. Too many filters applied - try removing some
2. Multi-select has too many items - reduce selections
3. Salary/experience range too narrow - widen the range
4. Combination is too specific - remove one filter at a time

**Solution:** Use the "Clear All" button and start with fewer filters.

### Counts Don't Update

**Refresh the page** - Counts should load dynamically, but a refresh can help if needed.

### Multi-Select Not Working

**Make sure to hold Ctrl/Cmd** when clicking multiple items. This is standard behavior for multi-select lists in all operating systems.

### Filters Not Saved in URL

If you share a URL but filters don't appear:
1. Check that you copied the complete URL including parameters
2. The recipient should load the page fully (not use browser cache)

## Mobile Usage

On mobile devices:
- Single-select filters work with native dropdowns
- Multi-select filters use native multi-select controls
- Tap to select, tap again to deselect
- Some mobile browsers may show a picker dialog

## Feedback and Support

If you encounter issues with filters:
1. Check this guide for common solutions
2. Try clearing all filters and starting over
3. Refresh the page to reload filter data
4. Report persistent issues to the development team

---

**Remember:** Filters are powerful tools to find exactly what you're looking for. Start simple, refine gradually, and use the dynamic counts to guide your selections!
