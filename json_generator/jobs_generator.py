"""Jobs API generator."""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone

from src.data_database import JobDetail
from .config import GeneratorConfig
from .job_serializer import serialize_jobs
from .data_sanitizer import DataSanitizer
from .index_builder import IndexBuilder


class JobsGenerator:
    """Generate paginated jobs API files."""
    
    def __init__(self, output_dir: str = None, jobs_per_page: int = None):
        """
        Initialize jobs generator.
        
        Args:
            output_dir: Output directory for JSON files.
            jobs_per_page: Number of jobs per page.
        """
        self.output_dir = Path(output_dir or GeneratorConfig.OUTPUT_DIR)
        self.jobs_per_page = jobs_per_page or GeneratorConfig.JOBS_PER_PAGE
        self.sanitizer = DataSanitizer(GeneratorConfig.COMPANY_BLACKLIST_FILE)
    
    def generate(self, jobs: List[JobDetail]) -> None:
        """
        Generate all jobs API files.
        
        Args:
            jobs: List of all JobDetail objects.
        """
        # Create output directories
        jobs_dir = self.output_dir / 'jobs'
        jobs_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate index.json
        print(f"Generating index.json with metadata for {len(jobs)} jobs...")
        index_builder = IndexBuilder(jobs, self.jobs_per_page)
        index = index_builder.build()
        self._write_json(jobs_dir / 'index.json', index)
        
        # Generate paginated job files
        total_pages = (len(jobs) + self.jobs_per_page - 1) // self.jobs_per_page
        print(f"Generating {total_pages} page files...")
        
        for page_num in range(1, total_pages + 1):
            start_idx = (page_num - 1) * self.jobs_per_page
            end_idx = start_idx + self.jobs_per_page
            page_jobs = jobs[start_idx:end_idx]
            
            page_data = self._generate_page(page_num, total_pages, page_jobs)
            self._write_json(jobs_dir / f'page-{page_num}.json', page_data)
            
            if page_num % 10 == 0:
                print(f"  Generated {page_num}/{total_pages} pages...")
        
        print(f"✓ Successfully generated {total_pages} page files and index")
    
    def _generate_page(self, page_num: int, total_pages: int, 
                       jobs: List[JobDetail]) -> Dict[str, Any]:
        """
        Generate a single page of jobs.
        
        Args:
            page_num: Current page number.
            total_pages: Total number of pages.
            jobs: Jobs for this page.
            
        Returns:
            Page data dictionary.
        """
        # Serialize jobs
        serialized_jobs = serialize_jobs(jobs)
        
        # Sanitize jobs
        sanitized_jobs = [self.sanitizer.sanitize_job(job) for job in serialized_jobs]
        
        return {
            'version': GeneratorConfig.API_VERSION,
            'page': page_num,
            'total_pages': total_pages,
            'jobs_per_page': self.jobs_per_page,
            'jobs': sanitized_jobs
        }
    
    def _write_json(self, filepath: Path, data: Dict[str, Any]) -> None:
        """
        Write data to JSON file.
        
        Args:
            filepath: Path to output file.
            data: Data to write.
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            if GeneratorConfig.INDENT_JSON:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
