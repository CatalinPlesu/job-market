"""Salary-related static analyses."""

from ..base import BaseAnalysis
from ..aggregator import Aggregator
from src.data_database import JobDetail
from sqlalchemy.orm import joinedload


class SalaryOverviewAnalysis(BaseAnalysis):
    """Overall salary statistics across all jobs."""
    
    @property
    def analysis_id(self):
        return 'salary-overview'
    
    @property
    def title(self):
        return 'Overall Salary Analysis'
    
    def compute(self):
        # Query jobs with salary data
        jobs = self.data_db.query(JobDetail).options(
            joinedload(JobDetail.salary_currency_id),
            joinedload(JobDetail.salary_period_id)
        ).filter(
            JobDetail.min_salary.isnot(None)
        ).all()
        
        if len(jobs) < self.config.MIN_SAMPLE_SIZE:
            return {'error': 'Insufficient data', 'count': len(jobs)}
        
        # Overall statistics
        salaries = [Aggregator.get_average_salary(job) for job in jobs if Aggregator.get_average_salary(job)]
        
        # Remove outliers
        salaries_clean = Aggregator.remove_outliers(salaries, self.config.SALARY_OUTLIER_THRESHOLD)
        
        overall = Aggregator.compute_stats(salaries_clean)
        overall['currency'] = 'MDL'  # Assuming normalized to MDL
        overall['period'] = 'month'
        
        # Distribution
        ranges = [
            (0, 5000),
            (5000, 10000),
            (10000, 15000),
            (15000, 20000),
            (20000, 30000),
            (30000, 50000),
            (50000, float('inf'))
        ]
        distribution = Aggregator.bucket_by_range(salaries_clean, ranges)
        
        return {
            'overall': overall,
            'distribution': distribution
        }
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['histogram', 'box_plot', 'bar_chart'],
            'recommended_chart': 'histogram'
        }


class SalaryByFunctionAnalysis(BaseAnalysis):
    """Salary statistics by job function."""
    
    @property
    def analysis_id(self):
        return 'salary-by-function'
    
    @property
    def title(self):
        return 'Salary by Job Function'
    
    def compute(self):
        from src.data_database import JobFunctions
        
        jobs = self.data_db.query(JobDetail).options(
            joinedload(JobDetail.job_function_id)
        ).filter(
            JobDetail.min_salary.isnot(None),
            JobDetail.job_function_id.isnot(None)
        ).all()
        
        if len(jobs) < self.config.MIN_SAMPLE_SIZE:
            return {'error': 'Insufficient data', 'count': len(jobs)}
        
        # Group by job function
        grouped = Aggregator.group_by(jobs, lambda j: self._get_job_function(j))
        
        results = []
        for function_name, function_jobs in grouped.items():
            if len(function_jobs) < self.config.MIN_SAMPLE_SIZE:
                continue
            
            salaries = [Aggregator.get_average_salary(job) for job in function_jobs 
                       if Aggregator.get_average_salary(job)]
            salaries_clean = Aggregator.remove_outliers(salaries, self.config.SALARY_OUTLIER_THRESHOLD)
            
            if salaries_clean:
                stats = Aggregator.compute_stats(salaries_clean)
                stats['function'] = function_name
                results.append(stats)
        
        # Sort by average salary descending
        results.sort(key=lambda x: x['average'], reverse=True)
        
        return {
            'by_function': results,
            'top_10': results[:10]
        }
    
    def _get_job_function(self, job):
        """Get job function name."""
        from src.data_database import JobFunctions
        if job.job_function_id:
            func = self.data_db.query(JobFunctions).filter_by(id=job.job_function_id).first()
            return func.name if func else None
        return None
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['bar_chart', 'horizontal_bar'],
            'recommended_chart': 'horizontal_bar'
        }


class SalaryBySeniorityAnalysis(BaseAnalysis):
    """Salary statistics by seniority level."""
    
    @property
    def analysis_id(self):
        return 'salary-by-seniority'
    
    @property
    def title(self):
        return 'Salary by Seniority Level'
    
    def compute(self):
        from src.data_database import SeniorityLevels
        
        jobs = self.data_db.query(JobDetail).filter(
            JobDetail.min_salary.isnot(None),
            JobDetail.seniority_level_id.isnot(None)
        ).all()
        
        if len(jobs) < self.config.MIN_SAMPLE_SIZE:
            return {'error': 'Insufficient data', 'count': len(jobs)}
        
        # Group by seniority level
        grouped = Aggregator.group_by(jobs, lambda j: self._get_seniority_level(j))
        
        # Define ordering for seniority levels
        seniority_order = ['entry', 'junior', 'mid', 'senior', 'lead', 'manager', 'director', 'executive']
        
        results = []
        for level_name, level_jobs in grouped.items():
            if len(level_jobs) < self.config.MIN_SAMPLE_SIZE:
                continue
            
            salaries = [Aggregator.get_average_salary(job) for job in level_jobs 
                       if Aggregator.get_average_salary(job)]
            salaries_clean = Aggregator.remove_outliers(salaries, self.config.SALARY_OUTLIER_THRESHOLD)
            
            if salaries_clean:
                stats = Aggregator.compute_stats(salaries_clean)
                stats['seniority_level'] = level_name
                # Add order for frontend sorting
                try:
                    stats['order'] = seniority_order.index(level_name.lower())
                except ValueError:
                    stats['order'] = 999
                results.append(stats)
        
        # Sort by order
        results.sort(key=lambda x: x['order'])
        
        return {
            'by_seniority': results
        }
    
    def _get_seniority_level(self, job):
        """Get seniority level name."""
        from src.data_database import SeniorityLevels
        if job.seniority_level_id:
            level = self.data_db.query(SeniorityLevels).filter_by(id=job.seniority_level_id).first()
            return level.name if level else None
        return None
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['line_chart', 'bar_chart'],
            'recommended_chart': 'line_chart'
        }


class SalaryByLocationAnalysis(BaseAnalysis):
    """Salary statistics by location (city)."""
    
    @property
    def analysis_id(self):
        return 'salary-by-location'
    
    @property
    def title(self):
        return 'Salary by Location'
    
    def compute(self):
        from src.data_database import Cities
        
        jobs = self.data_db.query(JobDetail).filter(
            JobDetail.min_salary.isnot(None),
            JobDetail.city_id.isnot(None)
        ).all()
        
        if len(jobs) < self.config.MIN_SAMPLE_SIZE:
            return {'error': 'Insufficient data', 'count': len(jobs)}
        
        # Group by city
        grouped = Aggregator.group_by(jobs, lambda j: self._get_city(j))
        
        results = []
        for city_name, city_jobs in grouped.items():
            if len(city_jobs) < self.config.MIN_SAMPLE_SIZE:
                continue
            
            salaries = [Aggregator.get_average_salary(job) for job in city_jobs 
                       if Aggregator.get_average_salary(job)]
            salaries_clean = Aggregator.remove_outliers(salaries, self.config.SALARY_OUTLIER_THRESHOLD)
            
            if salaries_clean:
                stats = Aggregator.compute_stats(salaries_clean)
                stats['city'] = city_name
                results.append(stats)
        
        # Sort by count descending
        results.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'by_location': results
        }
    
    def _get_city(self, job):
        """Get city name."""
        from src.data_database import Cities
        if job.city_id:
            city = self.data_db.query(Cities).filter_by(id=job.city_id).first()
            return city.name if city else None
        return None
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['bar_chart', 'map'],
            'recommended_chart': 'bar_chart'
        }


class SalaryByCompanySizeAnalysis(BaseAnalysis):
    """Salary statistics by company size."""
    
    @property
    def analysis_id(self):
        return 'salary-by-company-size'
    
    @property
    def title(self):
        return 'Salary by Company Size'
    
    def compute(self):
        from src.data_database import CompanySizes
        
        jobs = self.data_db.query(JobDetail).filter(
            JobDetail.min_salary.isnot(None),
            JobDetail.company_size_id.isnot(None)
        ).all()
        
        if len(jobs) < self.config.MIN_SAMPLE_SIZE:
            return {'error': 'Insufficient data', 'count': len(jobs)}
        
        # Group by company size
        grouped = Aggregator.group_by(jobs, lambda j: self._get_company_size(j))
        
        # Define ordering for company sizes
        size_order = ['startup', 'small', 'medium', 'large', 'enterprise']
        
        results = []
        for size_name, size_jobs in grouped.items():
            if len(size_jobs) < self.config.MIN_SAMPLE_SIZE:
                continue
            
            salaries = [Aggregator.get_average_salary(job) for job in size_jobs 
                       if Aggregator.get_average_salary(job)]
            salaries_clean = Aggregator.remove_outliers(salaries, self.config.SALARY_OUTLIER_THRESHOLD)
            
            if salaries_clean:
                stats = Aggregator.compute_stats(salaries_clean)
                stats['company_size'] = size_name
                # Add order for frontend sorting
                try:
                    stats['order'] = size_order.index(size_name.lower())
                except ValueError:
                    stats['order'] = 999
                results.append(stats)
        
        # Sort by order
        results.sort(key=lambda x: x['order'])
        
        return {
            'by_company_size': results
        }
    
    def _get_company_size(self, job):
        """Get company size name."""
        from src.data_database import CompanySizes
        if job.company_size_id:
            size = self.data_db.query(CompanySizes).filter_by(id=job.company_size_id).first()
            return size.name if size else None
        return None
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['bar_chart', 'grouped_bar'],
            'recommended_chart': 'bar_chart'
        }


class SalaryByEducationAnalysis(BaseAnalysis):
    """Salary statistics by education level."""
    
    @property
    def analysis_id(self):
        return 'salary-by-education'
    
    @property
    def title(self):
        return 'Salary by Education Level'
    
    def compute(self):
        from src.data_database import EducationLevels
        
        jobs = self.data_db.query(JobDetail).filter(
            JobDetail.min_salary.isnot(None),
            JobDetail.required_education_id.isnot(None)
        ).all()
        
        if len(jobs) < self.config.MIN_SAMPLE_SIZE:
            return {'error': 'Insufficient data', 'count': len(jobs)}
        
        # Group by education level
        grouped = Aggregator.group_by(jobs, lambda j: self._get_education_level(j))
        
        # Define ordering for education levels
        education_order = ['none', 'highschool', 'vocational', 'associate', 'bachelor', 'master', 'phd']
        
        results = []
        for edu_name, edu_jobs in grouped.items():
            if len(edu_jobs) < self.config.MIN_SAMPLE_SIZE:
                continue
            
            salaries = [Aggregator.get_average_salary(job) for job in edu_jobs 
                       if Aggregator.get_average_salary(job)]
            salaries_clean = Aggregator.remove_outliers(salaries, self.config.SALARY_OUTLIER_THRESHOLD)
            
            if salaries_clean:
                stats = Aggregator.compute_stats(salaries_clean)
                stats['education_level'] = edu_name
                # Add order for frontend sorting
                try:
                    stats['order'] = education_order.index(edu_name.lower())
                except ValueError:
                    stats['order'] = 999
                results.append(stats)
        
        # Sort by order
        results.sort(key=lambda x: x['order'])
        
        return {
            'by_education': results
        }
    
    def _get_education_level(self, job):
        """Get education level name."""
        from src.data_database import EducationLevels
        if job.required_education_id:
            edu = self.data_db.query(EducationLevels).filter_by(id=job.required_education_id).first()
            return edu.name if edu else None
        return None
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['bar_chart', 'line_chart'],
            'recommended_chart': 'bar_chart'
        }
