# JSON Generator Module

Generates paginated JSON files from SQLite databases for GitHub Pages API.

## Features

- **Paginated Job Listings**: Generates page-1.json, page-2.json, etc. with configurable jobs per page (default: 100)
- **Comprehensive Metadata**: index.json contains metadata for ALL 50+ filterable fields with per-page item counts
- **Currency Conversion**: Automatically converts all salary values to MDL using current exchange rates
- **Data Sanitization**: Removes contact emails, phones, and person names from output
- **Company Blacklist**: Support for anonymizing companies on blacklist
- **Field Coverage**: Supports all one-to-one and many-to-many database relationships

## Usage

### Command Line

```bash
# Generate to default location (pages/api)
python -m json_generator

# Generate to custom location
python -m json_generator --output /path/to/output

# Custom jobs per page
python -m json_generator --jobs-per-page 50
```

### Programmatic

```python
from json_generator.db_connector import DatabaseConnector
from json_generator.jobs_generator import JobsGenerator

# Load jobs from database
with DatabaseConnector() as db:
    jobs = db.get_all_jobs()

# Generate JSON files
generator = JobsGenerator(output_dir='pages/api', jobs_per_page=100)
generator.generate(jobs)
```

## Output Structure

```
pages/api/
├── jobs/
│   ├── index.json       # Metadata + filters + page mappings
│   ├── page-1.json      # Jobs 1-100
│   ├── page-2.json      # Jobs 101-200
│   └── ...
```

## Index Metadata

The index.json file contains comprehensive metadata for efficient client-side filtering:

- **One-to-One Fields**: title, job_function, seniority_level, industry, department, job_family, specialization, education_level, employment_type, contract_type, work_schedule, shift_details, remote_work, travel_requirements, city, region, country, company_name, company_size, currency, salary_period

- **Many-to-Many Fields**: hard_skills, soft_skills, languages, certifications, licenses, benefits, work_environment, professional_development, work_life_balance, physical_requirements, work_conditions, special_requirements

Each metadata entry includes:
- `name`: The value
- `count`: Total occurrences
- `pages`: Array of `{page: N, count: X}` indicating which pages contain this value and how many items per page

## Currency Conversion

The generator automatically converts all salary values to MDL (Moldovan Leu) for easy comparison:

**How it works:**
1. Fetches current exchange rates from [open.er-api.com](https://open.er-api.com) at generation time
2. Converts all salary amounts to MDL
3. Includes both original and converted values in the output

**Output format:**
```json
{
  "salary": {
    "min": 1000,
    "max": 2000,
    "currency": "USD",
    "period": "month",
    "min_mdl": 17500,
    "max_mdl": 35000
  }
}
```

**Fallback behavior:**
- If exchange rates cannot be fetched (network issues, API limits), conversion is skipped
- Original salary values are always preserved
- Generator continues without error

## Configuration

Edit `json_generator/config.py`:

```python
class GeneratorConfig:
    JOBS_PER_PAGE = 100
    OUTPUT_DIR = 'pages/api'
    COMPANY_BLACKLIST_FILE = 'config/company_blacklist.txt'
    INDENT_JSON = False  # Set True for readable output
```

## Data Privacy

The generator automatically:
- Excludes `contact_emails`, `contact_phones`, `contact_person` fields
- Anonymizes companies listed in blacklist file
- Uses minimal data necessary for public API

## Job Data Fields

### Raw Job Description
The generator includes the original job description text in the `raw.original_description` field:
- **Source**: Pulled from `job_description` column in `job_details` table (data.db)
- **Content**: Complete original job posting text as scraped from the source
- **Note**: If this field is empty in the generated JSON, ensure the `job_description` column is being populated during the LLM processing stage (Stage 7 - Structure Data with LLM)

The raw description allows users to view the complete, unprocessed job posting alongside the structured data extracted by the LLM.

## Performance

**Optimized for Memory Efficiency:**
- Uses SQLAlchemy `subqueryload` strategy to batch-load relationships
- Avoids massive JOIN queries that can consume excessive memory
- Efficient for datasets of 300-10,000+ jobs
- Memory usage scales linearly with dataset size

**Benchmarks:**
- ~5-15 seconds for 1,000 jobs (depending on hardware)
- <30 seconds for 10,000 jobs
- Memory usage: ~100-200MB for 1,000 jobs
- Total API size: <20MB

**Technical Details:**
- Lazy loading (`lazy='select'`) for relationship definitions
- Batch loading with `subqueryload()` for query execution
- Prevents N+1 query problems while keeping memory usage reasonable
