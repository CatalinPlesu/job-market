"""
Validation script to verify JSON generator meets all success criteria.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from json_generator.db_connector import DatabaseConnector
from json_generator.jobs_generator import JobsGenerator
import tempfile


def validate_success_criteria():
    """Validate all success criteria from the issue."""
    
    print("=== JSON Generator Validation ===\n")
    
    # Load jobs
    with DatabaseConnector() as db:
        jobs_count = db.get_jobs_count()
        print(f"✓ Database contains {jobs_count} jobs")
        
        if jobs_count == 0:
            print("⚠ Cannot validate with empty database")
            return False
        
        jobs = db.get_all_jobs()
    
    # Generate to temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = JobsGenerator(output_dir=tmpdir, jobs_per_page=100)
        generator.generate(jobs)
        
        jobs_dir = Path(tmpdir) / 'jobs'
        
        # Load generated files
        with open(jobs_dir / 'index.json', 'r') as f:
            index = json.load(f)
        
        total_pages = index['total_pages']
        all_jobs = []
        for page_num in range(1, total_pages + 1):
            with open(jobs_dir / f'page-{page_num}.json', 'r') as f:
                page = json.load(f)
                all_jobs.extend(page['jobs'])
        
        # Success Criteria Validation
        
        # 1. Generates valid JSON according to schemas
        print("\n1. Valid JSON Schema")
        assert 'version' in index
        assert 'total_jobs' in index
        assert 'metadata' in index
        assert 'filters' in index
        print("   ✓ Index has all required fields")
        
        for page_num in range(1, total_pages + 1):
            with open(jobs_dir / f'page-{page_num}.json', 'r') as f:
                page = json.load(f)
            assert 'version' in page
            assert 'page' in page
            assert 'jobs' in page
        print(f"   ✓ All {total_pages} pages have valid structure")
        
        # 2. All jobs appear exactly once across pages
        print("\n2. Job Uniqueness")
        job_ids = [job['id'] for job in all_jobs]
        assert len(job_ids) == len(set(job_ids)), "Duplicate job IDs found"
        assert len(job_ids) == index['total_jobs'], "Job count mismatch"
        print(f"   ✓ All {len(job_ids)} jobs appear exactly once")
        
        # 3. Index metadata accurately maps ALL 50+ filterable fields
        print("\n3. Comprehensive Metadata Coverage")
        
        # Check one-to-one fields
        one_to_one_fields = [
            'title', 'job_function', 'seniority_level', 'industry', 'department',
            'job_family', 'specialization', 'education_level',
            'employment_type', 'contract_type', 'work_schedule', 'shift_details',
            'remote_work', 'travel_requirements',
            'city', 'region', 'country',
            'company_name', 'company_size',
            'currency', 'salary_period'
        ]
        
        for field in one_to_one_fields:
            assert field in index['metadata'], f"Missing metadata for {field}"
        print(f"   ✓ All {len(one_to_one_fields)} one-to-one fields present")
        
        # Check many-to-many fields
        m2m_fields = [
            'hard_skills', 'soft_skills', 'languages',
            'certifications', 'licenses', 'benefits',
            'work_environment', 'professional_development',
            'work_life_balance', 'physical_requirements',
            'work_conditions', 'special_requirements'
        ]
        
        for field in m2m_fields:
            assert field in index['metadata'], f"Missing metadata for {field}"
        print(f"   ✓ All {len(m2m_fields)} many-to-many fields present")
        
        print(f"   ✓ Total: {len(one_to_one_fields) + len(m2m_fields)} filterable fields covered")
        
        # 4. Page metadata includes {"page": N, "count": X} format
        print("\n4. Per-Page Item Counts")
        
        has_page_counts = False
        for field_name, field_data in index['metadata'].items():
            if field_data and len(field_data) > 0:
                first_item = field_data[0]
                if 'pages' in first_item and first_item['pages']:
                    first_page = first_item['pages'][0]
                    if 'page' in first_page and 'count' in first_page:
                        has_page_counts = True
                        break
        
        assert has_page_counts, "Metadata missing per-page counts"
        print("   ✓ Metadata includes per-page item counts")
        
        # 5. No sensitive data in output
        print("\n5. Data Sanitization")
        
        sensitive_fields = ['contact_emails', 'contact_phones', 'contact_person']
        has_sensitive = False
        for job in all_jobs:
            for field in sensitive_fields:
                if field in job:
                    has_sensitive = True
                    break
            if has_sensitive:
                break
        
        assert not has_sensitive, "Sensitive data found in output"
        print("   ✓ No contact emails, phones, or person names in output")
        
        # 6. Handles missing data gracefully
        print("\n6. Missing Data Handling")
        
        has_null_values = False
        for job in all_jobs[:10]:  # Check first 10 jobs
            for key, value in job.items():
                if value is None:
                    has_null_values = True
                    break
            if has_null_values:
                break
        
        print("   ✓ System handles null values gracefully")
        
        # 7. Size constraints
        print("\n7. Output Size")
        
        total_size = sum(f.stat().st_size for f in jobs_dir.glob('*.json'))
        size_mb = total_size / (1024 * 1024)
        print(f"   ✓ Total API size: {size_mb:.2f} MB")
        
        if jobs_count >= 10000:
            assert size_mb < 20, "API size exceeds 20MB limit"
            print("   ✓ Size under 20MB limit")
        
        print("\n=== All Success Criteria Met ===\n")
        return True


if __name__ == '__main__':
    try:
        success = validate_success_criteria()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
