"""Main entry point for JSON generator."""

import argparse
import sys
from pathlib import Path

from .db_connector import DatabaseConnector
from .jobs_generator import JobsGenerator
from .config import GeneratorConfig


def main():
    """Main entry point for JSON generator CLI."""
    parser = argparse.ArgumentParser(
        description='Generate paginated JSON API from job databases'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=GeneratorConfig.OUTPUT_DIR,
        help=f'Output directory (default: {GeneratorConfig.OUTPUT_DIR})'
    )
    parser.add_argument(
        '--jobs-per-page',
        type=int,
        default=GeneratorConfig.JOBS_PER_PAGE,
        help=f'Jobs per page (default: {GeneratorConfig.JOBS_PER_PAGE})'
    )
    
    args = parser.parse_args()
    
    try:
        print("=== Job Market JSON Generator ===")
        print(f"Output directory: {args.output}")
        print(f"Jobs per page: {args.jobs_per_page}")
        print()
        
        # Query jobs from database
        print("Connecting to database...")
        with DatabaseConnector() as db:
            jobs_count = db.get_jobs_count()
            print(f"Found {jobs_count} jobs in database")
            
            if jobs_count == 0:
                print("⚠ No jobs found in database. Nothing to generate.")
                return 0
            
            print("Loading jobs with relationships...")
            jobs = db.get_all_jobs()
            print(f"✓ Loaded {len(jobs)} jobs")
        
        # Generate JSON files
        print()
        generator = JobsGenerator(args.output, args.jobs_per_page)
        generator.generate(jobs)
        
        print()
        print("=== Generation Complete ===")
        print(f"✓ Files written to: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
