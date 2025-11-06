import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Thread
from collections import defaultdict
from openai import OpenAI
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.database import Job, JobDetail, engine
from src.repository import JobRepository
from config.settings import Config

# Constants
DEBUG = True
BATCH_SIZE = 3 
NUM_THREADS = 3
DISPLAY_REFRESH_INTERVAL = 1.0  # seconds

# Initialize OpenAI client with proper timeout handling
client = OpenAI(
    api_key=Config.llm_api_key,
    base_url=Config.llm_api,
    timeout=Config.llm_request_timeout,
    max_retries=2
)


def get_unprocessed_job_ids_for_site(session, site, limit=None):
    """Fetch unprocessed job IDs for a specific site."""
    query = session.query(Job.id).outerjoin(JobDetail).filter(
        Job.site == site,
        JobDetail.id.is_(None),
        Job.job_description.isnot(None),
        Job.job_description != ''
    )
    
    if limit:
        query = query.limit(limit)
    
    return [job_id[0] for job_id in query.all()]

def process_job(job_id, session_class):
    """Process a single job using LLM."""
    session = session_class()
    content = None
    extracted_data = None
    
    try:
        job = session.query(Job).filter(Job.id == job_id).first()
        if not job:
            return job_id, False, "Job not found", None
        
        if not job.job_description:
            return job_id, False, "Missing job description", None
        
        # Check if already processed
        existing_detail = session.query(JobDetail).filter(JobDetail.job_id == job_id).first()
        if existing_detail:
            return job_id, False, "Already has JobDetail", None
        
        # Prepare the LLM request
        desc_truncated = len(job.job_description) > Config.max_body_text_length
        truncated_desc = job.job_description[:Config.max_body_text_length]
        
        user_message = f"""Extract information from this job posting:
POSTING DETAILS:
Title: {job.job_title}
Company: {job.company_name}
Source URL: {job.job_url}
JOB DESCRIPTION{' (first ' + str(Config.max_body_text_length) + ' characters)' if desc_truncated else ''}:
{truncated_desc}
{"... [description truncated]" if desc_truncated else ""}
---
{Config.job_to_db_prompt2}
CRITICAL OUTPUT RULES:
1. Return ONLY the JSON object
2. No markdown (no ```json or ```)
3. No explanations before or after
4. Start immediately with {{
5. End immediately with }}
6. Ensure all string values use double quotes
Begin JSON:"""
        
        system_message = "You are a precise job posting data extractor. Follow the schema and rules exactly as provided."
        
        # Make the API call using OpenAI library
        try:
            response = client.chat.completions.create(
                model=Config.llm_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
        except Exception as e:
            error_msg = f"LLM API error: {str(e)[:100]}"
            error_details = f"Full API error:\n{type(e).__name__}: {str(e)}"
            return job_id, False, error_msg, error_details
        
        content = response.choices[0].message.content
        
        if not content:
            return job_id, False, "Empty response from LLM", None
        
        # Parse the JSON response - try multiple strategies
        extracted_data = None
        parse_errors = []
        
        # Strategy 1: Direct parse
        try:
            extracted_data = json.loads(content)
        except json.JSONDecodeError as e:
            parse_errors.append(f"Direct parse: {str(e)}")
        
        # Strategy 2: Find the outermost {} pair
        if extracted_data is None:
            try:
                first_brace = content.find('{')
                last_brace = content.rfind('}')
                
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    json_str = content[first_brace:last_brace + 1]
                    extracted_data = json.loads(json_str)
            except (json.JSONDecodeError, ValueError) as e:
                parse_errors.append(f"Brace extraction: {str(e)}")
        
        # Strategy 3: Remove markdown code blocks
        if extracted_data is None:
            try:
                cleaned_content = content.strip()
                if cleaned_content.startswith("```"):
                    lines = cleaned_content.split('\n')
                    start_idx = 0
                    end_idx = len(lines)
                    for i, line in enumerate(lines):
                        if line.strip().startswith('{'):
                            start_idx = i
                            break
                    for i in range(len(lines) - 1, -1, -1):
                        if lines[i].strip().endswith('}'):
                            end_idx = i + 1
                            break
                    json_str = '\n'.join(lines[start_idx:end_idx])
                    extracted_data = json.loads(json_str)
            except (json.JSONDecodeError, ValueError) as e:
                parse_errors.append(f"Markdown removal: {str(e)}")
        
        # If all strategies failed
        if extracted_data is None:
            error_msg = f"JSON parse failed: {'; '.join(parse_errors)}"
            error_details = f"LLM Response:\n{content}\n\nParse errors: {parse_errors}"
            return job_id, False, error_msg, error_details
        
        # Validate extracted_data is a dict
        if not isinstance(extracted_data, dict):
            error_msg = f"Invalid JSON format: expected dict, got {type(extracted_data).__name__}"
            error_details = f"LLM Response:\n{content}\n\nParsed as: {extracted_data}"
            return job_id, False, error_msg, error_details
        
        # Create JobDetail directly without creating a new Job
        detail = JobDetail(job_id=job.id)
        
        # Handle simple foreign key fields
        fk_mappings = [
            ('title', 'Titles', 'name'),
            ('job_function', 'JobFunctions', 'name'),
            ('seniority_level', 'SeniorityLevels', 'name'),
            ('industry', 'Industries', 'name'),
            ('department', 'Departments', 'name'),
            ('job_family', 'JobFamilies', 'name'),
            ('specialization', 'Specializations', 'name'),
            ('required_education', 'EducationLevels', 'name'),
            ('employment_type', 'EmploymentTypes', 'name'),
            ('contract_type', 'ContractTypes', 'name'),
            ('work_schedule', 'WorkSchedules', 'name'),
            ('shift_details', 'ShiftDetails', 'name'),
            ('remote_work', 'RemoteWorkOptions', 'name'),
            ('travel_required', 'TravelRequirements', 'name'),
            ('salary_currency', 'Currencies', 'code'),
            ('salary_period', 'SalaryPeriods', 'name'),
            ('city', 'Cities', 'name'),
            ('region', 'Regions', 'name'),
            ('country', 'Countries', 'name'),
            ('company_name', 'Companies', 'name'),
            ('company_size', 'CompanySizes', 'name'),
            ('contact_person', 'ContactPersons', 'name'),
        ]
        
        # Use repository helper method to save
        try:
            with JobRepository(session=session) as repo:
                for json_key, model_name, field_name in fk_mappings:
                    value = extracted_data.get(json_key)
                    if value and value != "null":
                        from src.database import (
                            Titles, JobFunctions, SeniorityLevels, Industries, Departments,
                            JobFamilies, Specializations, EducationLevels, EmploymentTypes,
                            ContractTypes, WorkSchedules, ShiftDetails, RemoteWorkOptions,
                            TravelRequirements, Currencies, SalaryPeriods, Cities, Regions,
                            Countries, Companies, CompanySizes, ContactPersons, FullAddresses
                        )
                        
                        model_map = {
                            'Titles': Titles, 'JobFunctions': JobFunctions,
                            'SeniorityLevels': SeniorityLevels, 'Industries': Industries,
                            'Departments': Departments, 'JobFamilies': JobFamilies,
                            'Specializations': Specializations, 'EducationLevels': EducationLevels,
                            'EmploymentTypes': EmploymentTypes, 'ContractTypes': ContractTypes,
                            'WorkSchedules': WorkSchedules, 'ShiftDetails': ShiftDetails,
                            'RemoteWorkOptions': RemoteWorkOptions, 'TravelRequirements': TravelRequirements,
                            'Currencies': Currencies, 'SalaryPeriods': SalaryPeriods,
                            'Cities': Cities, 'Regions': Regions, 'Countries': Countries,
                            'Companies': Companies, 'CompanySizes': CompanySizes,
                            'ContactPersons': ContactPersons, 'FullAddresses': FullAddresses
                        }
                        
                        model = model_map[model_name]
                        instance = repo._get_or_create_lookup(model, field_name, value)
                        if instance:
                            setattr(detail, f'{json_key}_id', instance.id)
                
                # Handle full address
                if extracted_data.get('full_address'):
                    from src.database import FullAddresses
                    addr = repo._get_or_create_lookup(FullAddresses, 'address', extracted_data['full_address'])
                    detail.full_address_id = addr.id
                
                # Handle numeric/date fields
                for field in ['min_salary', 'max_salary', 'experience_years', 'original_language']:
                    if field in extracted_data and extracted_data[field] is not None:
                        setattr(detail, field, extracted_data[field])
                
                # Handle posting_date
                if extracted_data.get('posting_date'):
                    from datetime import datetime
                    posting_date = extracted_data['posting_date']
                    if isinstance(posting_date, str):
                        try:
                            posting_date = datetime.strptime(posting_date, '%Y-%m-%d').date()
                            detail.posting_date = posting_date
                        except:
                            pass
                
                session.add(detail)
                session.flush()
                
                # Handle many-to-many relationships
                from src.database import (
                    HardSkills, SoftSkills, Certifications, Licenses, Benefits,
                    WorkEnvironment, ProfessionalDevelopment, WorkLifeBalance,
                    PhysicalRequirements, WorkConditions, SpecialRequirements
                )
                
                m2m_mappings = [
                    ('hard_skills', HardSkills, 'name', 'hard_skills'),
                    ('soft_skills', SoftSkills, 'name', 'soft_skills'),
                    ('certifications', Certifications, 'name', 'certifications'),
                    ('licenses_required', Licenses, 'name', 'licenses'),
                    ('benefits', Benefits, 'description', 'benefits'),
                    ('work_environment', WorkEnvironment, 'description', 'work_environment'),
                    ('professional_development', ProfessionalDevelopment, 'description', 'professional_development'),
                    ('work_life_balance', WorkLifeBalance, 'description', 'work_life_balance'),
                    ('physical_requirements', PhysicalRequirements, 'description', 'physical_requirements'),
                    ('work_conditions', WorkConditions, 'description', 'work_conditions'),
                    ('special_requirements', SpecialRequirements, 'description', 'special_requirements'),
                ]
                
                for json_key, model, field_name, relationship_name in m2m_mappings:
                    items = extracted_data.get(json_key)
                    # FIX: Check if items is not None before processing
                    if items:
                        m2m_items = repo._get_or_create_m2m_items(model, field_name, items)
                        setattr(detail, relationship_name, m2m_items)
                
                # Handle responsibilities
                from src.database import Responsibility
                responsibilities = extracted_data.get('responsibilities')
                # FIX: Check if responsibilities is not None
                if responsibilities:
                    for i, resp in enumerate(responsibilities):
                        if resp:
                            session.add(Responsibility(
                                job_detail_id=detail.id,
                                description=resp,
                                order=i
                            ))
                
                # Handle languages
                from src.database import JobLanguage
                languages = extracted_data.get('languages')
                proficiencies = extracted_data.get('language_proficiency')
                
                # FIX: Check if languages is not None before iterating
                if languages:
                    for lang in languages:
                        if lang:
                            # FIX: Safely get proficiency, handle None case
                            proficiency = None
                            if proficiencies and isinstance(proficiencies, dict):
                                proficiency = proficiencies.get(lang)
                            
                            session.add(JobLanguage(
                                job_detail_id=detail.id,
                                language=lang,
                                proficiency=proficiency
                            ))
                
                # Handle contact emails
                from src.database import ContactEmail
                contact_emails = extracted_data.get('contact_emails')
                # FIX: Check if contact_emails is not None
                if contact_emails:
                    for email in contact_emails:
                        if email:
                            session.add(ContactEmail(
                                job_detail_id=detail.id,
                                email=email
                            ))
                
                # Handle contact phones
                from src.database import ContactPhone
                contact_phones = extracted_data.get('contact_phones')
                # FIX: Check if contact_phones is not None
                if contact_phones:
                    for phone in contact_phones:
                        if phone:
                            session.add(ContactPhone(
                                job_detail_id=detail.id,
                                phone=phone
                            ))
                
                session.commit()
                return job_id, True, "Success", None
                
        except SQLAlchemyError as e:
            session.rollback()
            error_detail = f"{type(e).__name__}: {str(e)[:200]}"
            error_details = f"Database error details:\n{str(e)}\n\nExtracted data:\n{json.dumps(extracted_data, indent=2)}"
            return job_id, False, f"Database error: {error_detail}", error_details
    
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)[:100]}"
        error_details = f"Exception: {type(e).__name__}\nMessage: {str(e)}\n\nFull traceback:\n{traceback.format_exc()}"
        if 'content' in locals():
            error_details += f"\n\nLLM Response:\n{content}"
        if 'extracted_data' in locals() and extracted_data:
            error_details += f"\n\nExtracted data:\n{json.dumps(extracted_data, indent=2)}"
        return job_id, False, error_msg, error_details
    
    finally:
        session.close()


def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    if seconds <= 0:
        return "00:00:00"
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


class ProgressTracker:
    """Thread-safe progress tracker with buffered display"""
    
    def __init__(self, thread_assignments):
        """
        Args:
            thread_assignments: dict {thread_id: [(site, job_ids)]}
        """
        self.lock = Lock()
        self.thread_assignments = thread_assignments
        self.thread_progress = {tid: 0 for tid in thread_assignments}
        self.thread_total = {tid: sum(len(jobs) for _, jobs in assignments) 
                            for tid, assignments in thread_assignments.items()}
        self.thread_current_site = {tid: None for tid in thread_assignments}
        self.thread_start_times = {tid: time.time() for tid in thread_assignments}
        self.thread_success = {tid: 0 for tid in thread_assignments}
        self.thread_failed = {tid: 0 for tid in thread_assignments}
        self.global_start_time = time.time()
        
    def update(self, thread_id, site, success):
        """Update progress for a thread"""
        with self.lock:
            self.thread_progress[thread_id] += 1
            self.thread_current_site[thread_id] = site
            if success:
                self.thread_success[thread_id] += 1
            else:
                self.thread_failed[thread_id] += 1
    
    def get_display(self):
        """Get formatted progress display (buffered)"""
        with self.lock:
            lines = []
            lines.append("=" * 100)
            lines.append(f"LLM JOB PROCESSING - {NUM_THREADS} Threads | Debug Mode: {DEBUG}")
            lines.append("=" * 100)
            lines.append("")
            
            total_processed = 0
            total_jobs = 0
            
            # Display each thread's progress
            for thread_id in sorted(self.thread_assignments.keys()):
                progress = self.thread_progress[thread_id]
                total = self.thread_total[thread_id]
                current_site = self.thread_current_site[thread_id] or "Idle"
                
                total_processed += progress
                total_jobs += total
                
                # Calculate percentage and progress bar
                percentage = (progress / total * 100) if total > 0 else 0
                filled = int(percentage / 2)  # 50 chars = 100%
                bar = '#' * filled + '-' * (50 - filled)
                
                # Calculate ETA for this thread
                if progress > 0:
                    elapsed = time.time() - self.thread_start_times[thread_id]
                    time_per_job = elapsed / progress
                    remaining = time_per_job * (total - progress)
                    eta = format_time(remaining)
                else:
                    eta = "--:--:--"
                
                # Format site name (truncate if needed)
                site_display = f"{current_site[:15]:<15}"
                
                line = (f"Thread {thread_id} [{site_display}] "
                       f"[{bar}] {percentage:5.1f}% | "
                       f"{progress:3d} / {total:3d} | "
                       f"ETA: {eta}")
                lines.append(line)
            
            # Global statistics
            lines.append("")
            lines.append("-" * 100)
            
            global_percentage = (total_processed / total_jobs * 100) if total_jobs > 0 else 0
            global_elapsed = time.time() - self.global_start_time
            
            if total_processed > 0:
                global_time_per_job = global_elapsed / total_processed
                global_remaining = global_time_per_job * (total_jobs - total_processed)
                global_eta = format_time(global_remaining)
            else:
                global_eta = "--:--:--"
            
            total_success = sum(self.thread_success.values())
            total_failed = sum(self.thread_failed.values())
            
            lines.append(f"OVERALL PROGRESS: {total_processed}/{total_jobs} ({global_percentage:.1f}%) | "
                        f"✓ {total_success} | ✗ {total_failed} | "
                        f"Elapsed: {format_time(global_elapsed)} | "
                        f"ETA: {global_eta}")
            lines.append("=" * 100)
            
            return "\n".join(lines)


def distribute_workload(site_jobs, num_threads):
    """Distribute jobs across threads as evenly as possible"""
    # Flatten all jobs with their site info
    all_jobs = []
    for site, job_ids in site_jobs.items():
        for job_id in job_ids:
            all_jobs.append((site, job_id))
    
    # Distribute round-robin
    thread_assignments = defaultdict(lambda: defaultdict(list))
    for i, (site, job_id) in enumerate(all_jobs):
        thread_id = (i % num_threads) + 1
        thread_assignments[thread_id][site].append(job_id)
    
    # Convert to format: {thread_id: [(site, [job_ids])]}
    result = {}
    for thread_id, sites_dict in thread_assignments.items():
        result[thread_id] = [(site, jobs) for site, jobs in sites_dict.items()]
    
    return result


def structure_data_with_llm():
    """Main function to structure data using LLM with threading."""
    print("Initializing LLM job processor...")
    
    # Get all unique sites
    Session = sessionmaker(bind=engine)
    with Session() as session:
        sites = [site[0] for site in session.query(Job.site).distinct().all()]
    
    # Prepare jobs for each site
    site_jobs = {}
    for site in sites:
        with Session() as session:
            if DEBUG:
                job_ids = get_unprocessed_job_ids_for_site(session, site, BATCH_SIZE)
            else:
                job_ids = get_unprocessed_job_ids_for_site(session, site)
            
            if job_ids:
                site_jobs[site] = job_ids
    
    if not site_jobs:
        print("No unprocessed jobs found. Exiting.")
        return
    
    # Report what we found
    print(f"\nFound unprocessed jobs across {len(site_jobs)} sites:")
    for site, jobs in site_jobs.items():
        print(f"  {site}: {len(jobs)} jobs")
    
    total_jobs = sum(len(jobs) for jobs in site_jobs.values())
    print(f"\nTotal jobs to process: {total_jobs}")
    print(f"Distributing across {NUM_THREADS} threads...\n")
    
    time.sleep(2)  # Give user time to read
    
    # Distribute workload
    thread_assignments = distribute_workload(site_jobs, NUM_THREADS)
    
    # Create progress tracker
    tracker = ProgressTracker(thread_assignments)
    
    # Error log
    error_log = []
    error_lock = Lock()
    
    # Create a debug log file
    import datetime
    debug_log_path = f"llm_errors_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def log_error(thread_id, job_id, site, error, details=None):
        """Log error with optional details"""
        with error_lock:
            error_log.append({
                'thread': thread_id,
                'job_id': job_id,
                'site': site,
                'error': error
            })
            # Also write to file with full details
            with open(debug_log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*100}\n")
                f.write(f"Thread {thread_id} | Job {job_id} | Site {site}\n")
                f.write(f"Error: {error}\n")
                if details:
                    f.write(f"\n{'-'*100}\n")
                    f.write(f"DETAILS:\n{details}\n")
                f.write(f"{'='*100}\n")
    
    def worker(thread_id):
        """Worker function for each thread."""
        local_session_class = sessionmaker(bind=engine)
        
        # Process assigned jobs
        for site, job_ids in thread_assignments[thread_id]:
            for job_id in job_ids:
                job_id_result, success, message, details = process_job(job_id, local_session_class)
                tracker.update(thread_id, site, success)
                
                if not success:
                    log_error(thread_id, job_id_result, site, message, details)
    
    # Display update thread
    stop_display = False
    
    def display_loop():
        """Continuously update display at intervals"""
        while not stop_display:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(tracker.get_display())
            time.sleep(DISPLAY_REFRESH_INTERVAL)
    
    # Start display thread
    display_thread = Thread(target=display_loop, daemon=True)
    display_thread.start()
    
    # Start processing threads
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(worker, tid) for tid in thread_assignments.keys()]
        
        # Wait for completion
        for future in as_completed(futures):
            future.result()
    
    # Stop display and show final result
    stop_display = True
    time.sleep(0.2)  # Let display thread finish
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(tracker.get_display())
    print("\n✓ Processing completed!")
    
    # Show errors if any
    if error_log:
        print(f"\n{'=' * 100}")
        print(f"ERRORS ({len(error_log)} failed jobs)")
        print(f"Detailed error log saved to: {debug_log_path}")
        print("=" * 100)
        for err in error_log[:20]:  # Show first 20
            print(f"Thread {err['thread']} | Job {err['job_id']} | {err['site']:<15} | {err['error']}")
        if len(error_log) > 20:
            print(f"... and {len(error_log) - 20} more errors")


if __name__ == "__main__":
    structure_data_with_llm()
