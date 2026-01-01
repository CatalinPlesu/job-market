"""Index builder for generating metadata with page mappings."""

from typing import Dict, Any, List
from collections import defaultdict
from math import ceil
from src.data_database import JobDetail
from .config import GeneratorConfig


class IndexBuilder:
    """Build index.json with comprehensive metadata."""
    
    def __init__(self, jobs: List[JobDetail], jobs_per_page: int = None):
        """
        Initialize index builder.
        
        Args:
            jobs: List of all JobDetail objects.
            jobs_per_page: Number of jobs per page.
        """
        self.jobs = jobs
        self.jobs_per_page = jobs_per_page or GeneratorConfig.JOBS_PER_PAGE
        self.total_pages = ceil(len(jobs) / self.jobs_per_page) if jobs else 0
    
    def build(self) -> Dict[str, Any]:
        """
        Build complete index with metadata.
        
        Returns:
            Index dictionary with all metadata.
        """
        index = {
            'version': GeneratorConfig.API_VERSION,
            'generated_at': self._get_timestamp(),
            'total_jobs': len(self.jobs),
            'total_pages': self.total_pages,
            'jobs_per_page': self.jobs_per_page,
            'metadata': {},
            'filters': {}
        }
        
        # Build metadata for all one-to-one fields
        for field in GeneratorConfig.ONE_TO_ONE_FIELDS:
            index['metadata'][field] = self._build_field_metadata(field)
            index['filters'][field] = self._get_unique_values(field)
        
        # Build metadata for all many-to-many fields
        for field in GeneratorConfig.MANY_TO_MANY_FIELDS:
            index['metadata'][field] = self._build_m2m_field_metadata(field)
            index['filters'][field] = self._get_unique_m2m_values(field)
        
        # Add date range
        index['metadata']['date_range'] = self._get_date_range()
        
        return index
    
    def _build_field_metadata(self, field: str) -> List[Dict[str, Any]]:
        """
        Build metadata for a one-to-one field with per-page counts.
        
        Args:
            field: Field name to build metadata for.
            
        Returns:
            List of metadata entries with name, count, and pages.
        """
        field_map = defaultdict(lambda: {'count': 0, 'pages': {}})
        
        for i, job in enumerate(self.jobs):
            page = (i // self.jobs_per_page) + 1
            value = self._get_field_value(job, field)
            
            if value:
                field_map[value]['count'] += 1
                if page not in field_map[value]['pages']:
                    field_map[value]['pages'][page] = 0
                field_map[value]['pages'][page] += 1
        
        # Convert to final format
        result = []
        for name, data in sorted(field_map.items()):
            result.append({
                'name': name,
                'count': data['count'],
                'pages': [
                    {'page': page, 'count': count}
                    for page, count in sorted(data['pages'].items())
                ]
            })
        
        return result
    
    def _build_m2m_field_metadata(self, field: str) -> List[Dict[str, Any]]:
        """
        Build metadata for a many-to-many field with per-page counts.
        
        Args:
            field: Field name to build metadata for.
            
        Returns:
            List of metadata entries with name, count, and pages.
        """
        field_map = defaultdict(lambda: {'count': 0, 'pages': {}})
        
        for i, job in enumerate(self.jobs):
            page = (i // self.jobs_per_page) + 1
            values = self._get_m2m_field_values(job, field)
            
            for value in values:
                if value:
                    field_map[value]['count'] += 1
                    if page not in field_map[value]['pages']:
                        field_map[value]['pages'][page] = 0
                    field_map[value]['pages'][page] += 1
        
        # Convert to final format
        result = []
        for name, data in sorted(field_map.items()):
            result.append({
                'name': name,
                'count': data['count'],
                'pages': [
                    {'page': page, 'count': count}
                    for page, count in sorted(data['pages'].items())
                ]
            })
        
        return result
    
    def _get_field_value(self, job: JobDetail, field: str) -> str:
        """
        Get value for a one-to-one field.
        
        Args:
            job: JobDetail object.
            field: Field name.
            
        Returns:
            Field value or None.
        """
        field_mappings = {
            'title': lambda j: j.title.name if j.title else None,
            'job_function': lambda j: j.job_function.name if j.job_function else None,
            'seniority_level': lambda j: j.seniority_level.name if j.seniority_level else None,
            'industry': lambda j: j.industry.name if j.industry else None,
            'department': lambda j: j.department.name if j.department else None,
            'job_family': lambda j: j.job_family.name if j.job_family else None,
            'specialization': lambda j: j.specialization.name if j.specialization else None,
            'education_level': lambda j: j.education_level.name if j.education_level else None,
            'employment_type': lambda j: j.employment_type.name if j.employment_type else None,
            'contract_type': lambda j: j.contract_type.name if j.contract_type else None,
            'work_schedule': lambda j: j.work_schedule.name if j.work_schedule else None,
            'shift_details': lambda j: j.shift_details.name if j.shift_details else None,
            'remote_work': lambda j: j.remote_work.name if j.remote_work else None,
            'travel_requirements': lambda j: j.travel_requirements.name if j.travel_requirements else None,
            'city': lambda j: j.city.name if j.city else None,
            'region': lambda j: j.region.name if j.region else None,
            'country': lambda j: j.country.name if j.country else None,
            'company_name': lambda j: j.company.name if j.company else j.company_name,
            'company_size': lambda j: j.company_size.name if j.company_size else None,
            'currency': lambda j: j.salary_currency.code if j.salary_currency else None,
            'salary_period': lambda j: j.salary_period.name if j.salary_period else None,
        }
        
        if field in field_mappings:
            return field_mappings[field](job)
        
        return None
    
    def _get_m2m_field_values(self, job: JobDetail, field: str) -> List[str]:
        """
        Get values for a many-to-many field.
        
        Args:
            job: JobDetail object.
            field: Field name.
            
        Returns:
            List of values.
        """
        field_mappings = {
            'hard_skills': lambda j: [skill.name for skill in j.hard_skills] if j.hard_skills else [],
            'soft_skills': lambda j: [skill.name for skill in j.soft_skills] if j.soft_skills else [],
            'languages': lambda j: [lang.language for lang in j.languages] if j.languages else [],
            'certifications': lambda j: [cert.name for cert in j.certifications] if j.certifications else [],
            'licenses': lambda j: [lic.name for lic in j.licenses] if j.licenses else [],
            'benefits': lambda j: [benefit.description for benefit in j.benefits] if j.benefits else [],
            'work_environment': lambda j: [env.description for env in j.work_environment] if j.work_environment else [],
            'professional_development': lambda j: [pd.description for pd in j.professional_development] if j.professional_development else [],
            'work_life_balance': lambda j: [wlb.description for wlb in j.work_life_balance] if j.work_life_balance else [],
            'physical_requirements': lambda j: [pr.description for pr in j.physical_requirements] if j.physical_requirements else [],
            'work_conditions': lambda j: [wc.description for wc in j.work_conditions] if j.work_conditions else [],
            'special_requirements': lambda j: [sr.description for sr in j.special_requirements] if j.special_requirements else [],
        }
        
        if field in field_mappings:
            return field_mappings[field](job)
        
        return []
    
    def _get_unique_values(self, field: str) -> List[str]:
        """Get unique values for a field."""
        values = set()
        for job in self.jobs:
            value = self._get_field_value(job, field)
            if value:
                values.add(value)
        return sorted(list(values))
    
    def _get_unique_m2m_values(self, field: str) -> List[str]:
        """Get unique values for a many-to-many field."""
        values = set()
        for job in self.jobs:
            for value in self._get_m2m_field_values(job, field):
                if value:
                    values.add(value)
        return sorted(list(values))
    
    def _get_date_range(self) -> Dict[str, str]:
        """Get earliest and latest posting dates."""
        dates = [job.posting_date for job in self.jobs if job.posting_date]
        if not dates:
            return {'earliest': None, 'latest': None}
        
        return {
            'earliest': min(dates).isoformat(),
            'latest': max(dates).isoformat()
        }
    
    def _get_timestamp(self) -> str:
        """Get current UTC timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
