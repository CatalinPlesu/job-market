"""Create test data for JSON generator."""

from datetime import datetime, date
from src.data_database import (
    DataSessionLocal, JobDetail,
    Titles, JobFunctions, SeniorityLevels, Cities, Countries,
    EmploymentTypes, RemoteWorkOptions, HardSkills, SoftSkills,
    Responsibility, JobLanguage
)


def create_test_data():
    """Create test job data in database."""
    session = DataSessionLocal()
    
    try:
        # Create lookup data
        title1 = Titles(name="Software Engineer")
        title2 = Titles(name="Data Scientist")
        title3 = Titles(name="Product Manager")
        
        job_func1 = JobFunctions(name="Engineering")
        job_func2 = JobFunctions(name="Data Science")
        job_func3 = JobFunctions(name="Product")
        
        seniority1 = SeniorityLevels(name="mid")
        seniority2 = SeniorityLevels(name="senior")
        seniority3 = SeniorityLevels(name="junior")
        
        city1 = Cities(name="Chișinău")
        country1 = Countries(name="Moldova")
        
        emp_type1 = EmploymentTypes(name="full-time")
        remote1 = RemoteWorkOptions(name="hybrid")
        remote2 = RemoteWorkOptions(name="on-site")
        
        skill1 = HardSkills(name="Python")
        skill2 = HardSkills(name="JavaScript")
        skill3 = HardSkills(name="SQL")
        
        soft1 = SoftSkills(name="Communication")
        soft2 = SoftSkills(name="Teamwork")
        
        session.add_all([
            title1, title2, title3,
            job_func1, job_func2, job_func3,
            seniority1, seniority2, seniority3,
            city1, country1,
            emp_type1, remote1, remote2,
            skill1, skill2, skill3,
            soft1, soft2
        ])
        session.commit()
        
        # Create job 1
        job1 = JobDetail(
            job_url="https://example.com/job1",
            site="example.com",
            job_title="Software Engineer - Full Stack",
            company_name="TechCorp",
            job_description="Great opportunity...",
            title_id=title1.id,
            job_function_id=job_func1.id,
            seniority_level_id=seniority1.id,
            city_id=city1.id,
            country_id=country1.id,
            employment_type_id=emp_type1.id,
            remote_work_id=remote1.id,
            posting_date=date(2025, 12, 15),
            processed_at=datetime.utcnow()
        )
        job1.hard_skills = [skill1, skill2]
        job1.soft_skills = [soft1, soft2]
        session.add(job1)
        session.commit()
        
        # Add responsibilities and languages
        resp1 = Responsibility(job_detail_id=job1.id, description="Develop web applications", order=1)
        resp2 = Responsibility(job_detail_id=job1.id, description="Write clean code", order=2)
        lang1 = JobLanguage(job_detail_id=job1.id, language="Romanian", proficiency="native")
        lang2 = JobLanguage(job_detail_id=job1.id, language="English", proficiency="fluent")
        session.add_all([resp1, resp2, lang1, lang2])
        
        # Create job 2
        job2 = JobDetail(
            job_url="https://example.com/job2",
            site="example.com",
            job_title="Data Scientist",
            company_name="DataCo",
            job_description="Analyze data...",
            title_id=title2.id,
            job_function_id=job_func2.id,
            seniority_level_id=seniority2.id,
            city_id=city1.id,
            country_id=country1.id,
            employment_type_id=emp_type1.id,
            remote_work_id=remote2.id,
            posting_date=date(2025, 12, 20),
            processed_at=datetime.utcnow()
        )
        job2.hard_skills = [skill1, skill3]
        job2.soft_skills = [soft1]
        session.add(job2)
        session.commit()
        
        # Add details for job 2
        resp3 = Responsibility(job_detail_id=job2.id, description="Build ML models", order=1)
        lang3 = JobLanguage(job_detail_id=job2.id, language="English", proficiency="fluent")
        session.add_all([resp3, lang3])
        
        # Create job 3
        job3 = JobDetail(
            job_url="https://example.com/job3",
            site="example.com",
            job_title="Product Manager",
            company_name="ProductCo",
            job_description="Manage products...",
            title_id=title3.id,
            job_function_id=job_func3.id,
            seniority_level_id=seniority3.id,
            city_id=city1.id,
            country_id=country1.id,
            employment_type_id=emp_type1.id,
            remote_work_id=remote1.id,
            posting_date=date(2025, 12, 10),
            processed_at=datetime.utcnow()
        )
        job3.soft_skills = [soft1, soft2]
        session.add(job3)
        session.commit()
        
        print(f"✓ Created 3 test jobs")
        
    except Exception as e:
        print(f"✗ Error creating test data: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    create_test_data()
