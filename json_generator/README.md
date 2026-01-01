# JSON Generator Module

Generates paginated JSON files from SQLite databases for GitHub Pages API.

## Features

- **Paginated Job Listings**: Generates page-1.json, page-2.json, etc. with configurable jobs per page (default: 100)
- **Comprehensive Metadata**: index.json contains metadata for ALL 50+ filterable fields with per-page item counts
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

## Performance

- Generates <30 seconds for 10,000 jobs
- Total API size <20MB
- Uses eager loading for optimal database queries
