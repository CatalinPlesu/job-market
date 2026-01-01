"""Dynamic hierarchy analysis for drill-down."""

from .base import BaseAnalysis
from .aggregator import Aggregator
from src.data_database import JobDetail, JobFunctions, Specializations, SeniorityLevels
from collections import defaultdict


class SalaryHierarchyAnalysis(BaseAnalysis):
    """Salary analysis by job hierarchy (function → specialization → seniority)."""
    
    @property
    def analysis_id(self):
        return 'salary-by-hierarchy'
    
    @property
    def title(self):
        return 'Salary Analysis by Job Hierarchy'
    
    def compute(self):
        jobs = self.data_db.query(JobDetail).filter(
            JobDetail.min_salary.isnot(None)
        ).all()
        
        if len(jobs) < self.config.MIN_SAMPLE_SIZE:
            return {'error': 'Insufficient data', 'count': len(jobs)}
        
        levels = self.config.HIERARCHY  # ['job_function', 'specialization', 'seniority_level']
        
        tree = self._build_hierarchy_tree(jobs, levels)
        
        return {
            'hierarchy_levels': levels,
            'tree': tree
        }
    
    def _build_hierarchy_tree(self, jobs, levels, current_level=0):
        """Recursively build hierarchy tree with salary stats."""
        if current_level >= len(levels):
            return None
        
        level_field = levels[current_level]
        grouped = self._group_by_field(jobs, level_field)
        
        result = []
        for value, value_jobs in grouped.items():
            if not value or len(value_jobs) < self.config.MIN_SAMPLE_SIZE:
                continue
            
            # Compute salary stats for this node
            salaries = [Aggregator.get_average_salary(job) for job in value_jobs 
                       if Aggregator.get_average_salary(job)]
            
            if not salaries:
                continue
            
            salaries_clean = Aggregator.remove_outliers(salaries, self.config.SALARY_OUTLIER_THRESHOLD)
            
            if not salaries_clean:
                continue
            
            stats = Aggregator.compute_stats(salaries_clean)
            
            node = {
                'name': value,
                'level': level_field,
                'count': stats['count'],
                'average_salary': round(stats['average'], 2),
                'median_salary': round(stats['median'], 2),
                'salary_range': {
                    'min': round(stats['min'], 2),
                    'max': round(stats['max'], 2)
                }
            }
            
            # Recurse to next level
            if current_level < len(levels) - 1:
                children = self._build_hierarchy_tree(
                    value_jobs, 
                    levels, 
                    current_level + 1
                )
                if children:
                    node['children'] = children
            
            result.append(node)
        
        # Sort by average salary descending
        result.sort(key=lambda x: x['average_salary'], reverse=True)
        
        return result
    
    def _group_by_field(self, jobs, field):
        """Group jobs by a field (job_function, specialization, etc.)."""
        grouped = defaultdict(list)
        
        for job in jobs:
            value = self._get_field_value(job, field)
            if value:
                grouped[value].append(job)
        
        return grouped
    
    def _get_field_value(self, job, field):
        """Get the value of a field from job, handling foreign keys."""
        if field == 'job_function':
            if job.job_function_id:
                func = self.data_db.query(JobFunctions).filter_by(id=job.job_function_id).first()
                return func.name if func else None
        elif field == 'specialization':
            if job.specialization_id:
                spec = self.data_db.query(Specializations).filter_by(id=job.specialization_id).first()
                return spec.name if spec else None
        elif field == 'seniority_level':
            if job.seniority_level_id:
                level = self.data_db.query(SeniorityLevels).filter_by(id=job.seniority_level_id).first()
                return level.name if level else None
        return None
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['tree_map', 'sunburst', 'hierarchical_tree'],
            'recommended_chart': 'sunburst'
        }
