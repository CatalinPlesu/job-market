"""Skills-related static analyses."""

from ..base import BaseAnalysis
from ..aggregator import Aggregator
from src.data_database import JobDetail, HardSkills, job_hard_skills
from collections import Counter, defaultdict


class SkillsDemandAnalysis(BaseAnalysis):
    """Top in-demand skills analysis."""
    
    @property
    def analysis_id(self):
        return 'skills-demand'
    
    @property
    def title(self):
        return 'Top In-Demand Skills'
    
    def compute(self):
        # Query all job-skill associations
        skill_counts = Counter()
        
        jobs = self.data_db.query(JobDetail).all()
        
        for job in jobs:
            # Get skills for this job through association table
            skills = self.data_db.query(HardSkills).join(
                job_hard_skills
            ).filter(
                job_hard_skills.c.job_details_id == job.id
            ).all()
            
            for skill in skills:
                skill_counts[skill.name] += 1
        
        if not skill_counts:
            return {'error': 'No skills data available'}
        
        # Get top N skills
        top_skills = skill_counts.most_common(self.config.TOP_N_SKILLS)
        
        results = []
        total_jobs = len(jobs)
        
        for skill_name, count in top_skills:
            results.append({
                'skill': skill_name,
                'count': count,
                'percentage': round((count / total_jobs) * 100, 2) if total_jobs > 0 else 0
            })
        
        return {
            'top_skills': results,
            'total_jobs': total_jobs
        }
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['bar_chart', 'word_cloud', 'horizontal_bar'],
            'recommended_chart': 'horizontal_bar'
        }


class SkillsSalaryAnalysis(BaseAnalysis):
    """Skills to salary correlation analysis."""
    
    @property
    def analysis_id(self):
        return 'skills-salary'
    
    @property
    def title(self):
        return 'Skills to Salary Correlation'
    
    def compute(self):
        # Build mapping of skills to jobs
        skill_jobs = defaultdict(list)
        
        jobs = self.data_db.query(JobDetail).filter(
            JobDetail.min_salary.isnot(None)
        ).all()
        
        for job in jobs:
            salary = Aggregator.get_average_salary(job)
            if not salary:
                continue
            
            # Get skills for this job
            skills = self.data_db.query(HardSkills).join(
                job_hard_skills
            ).filter(
                job_hard_skills.c.job_details_id == job.id
            ).all()
            
            for skill in skills:
                skill_jobs[skill.name].append(salary)
        
        if not skill_jobs:
            return {'error': 'No skills-salary data available'}
        
        # Compute stats for each skill
        results = []
        for skill_name, salaries in skill_jobs.items():
            if len(salaries) < self.config.MIN_SAMPLE_SIZE:
                continue
            
            salaries_clean = Aggregator.remove_outliers(salaries, self.config.SALARY_OUTLIER_THRESHOLD)
            
            if salaries_clean:
                stats = Aggregator.compute_stats(salaries_clean)
                stats['skill'] = skill_name
                results.append(stats)
        
        # Sort by average salary descending
        results.sort(key=lambda x: x['average'], reverse=True)
        
        return {
            'skills_salary': results,
            'top_10_highest_paying': results[:10]
        }
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['bubble_chart', 'scatter_plot', 'bar_chart'],
            'recommended_chart': 'bubble_chart'
        }


class SkillCombinationsAnalysis(BaseAnalysis):
    """Common skill combinations analysis."""
    
    @property
    def analysis_id(self):
        return 'skill-combinations'
    
    @property
    def title(self):
        return 'Common Skill Combinations'
    
    def compute(self):
        # Build skill combinations for each job
        combinations = Counter()
        
        jobs = self.data_db.query(JobDetail).all()
        
        for job in jobs:
            # Get skills for this job
            skills = self.data_db.query(HardSkills).join(
                job_hard_skills
            ).filter(
                job_hard_skills.c.job_details_id == job.id
            ).all()
            
            skill_names = sorted([s.name for s in skills])
            
            # Generate pairs
            for i in range(len(skill_names)):
                for j in range(i + 1, len(skill_names)):
                    pair = (skill_names[i], skill_names[j])
                    combinations[pair] += 1
        
        if not combinations:
            return {'error': 'No skill combinations data available'}
        
        # Get top combinations
        top_combinations = combinations.most_common(20)
        
        results = []
        for (skill1, skill2), count in top_combinations:
            if count < 5:  # Minimum threshold for meaningful combinations
                continue
            results.append({
                'skill1': skill1,
                'skill2': skill2,
                'count': count
            })
        
        return {
            'top_combinations': results
        }
    
    def get_visualization_hints(self):
        return {
            'chart_types': ['network_graph', 'heatmap', 'table'],
            'recommended_chart': 'network_graph'
        }
