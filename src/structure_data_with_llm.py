import json
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Thread
from collections import defaultdict, deque
from openai import OpenAI
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.database import Job, JobDetail, engine
from src.repository import JobRepository
from config.settings import Config

# Constants
DEBUG = True
JOBS_PER_SITE_DEBUG = 100
NUM_THREADS = 8
JOBS_PER_BATCH = 5
DISPLAY_REFRESH_INTERVAL = 1.0

# Initialize OpenAI client
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


def extract_json_from_response(content):
    """
    Robust JSON extraction with multiple fallback strategies.
    Handles malformed responses from LLM.
    """
    if not content or not content.strip():
        return None, ["Empty content"]
    
    errors = []
    
    # Strategy 1: Direct parse
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return data, None
        elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            # LLM returned array with single dict - extract it
            return data[0], None
        else:
            errors.append(f"Direct parse: got {type(data).__name__}, expected dict")
    except json.JSONDecodeError as e:
        errors.append(f"Direct parse failed: {str(e)}")
    
    # Strategy 2: Extract first complete JSON object
    try:
        # Find the first { and its matching }
        depth = 0
        start = content.find('{')
        if start != -1:
            for i in range(start, len(content)):
                if content[i] == '{':
                    depth += 1
                elif content[i] == '}':
                    depth -= 1
                    if depth == 0:
                        json_str = content[start:i+1]
                        data = json.loads(json_str)
                        if isinstance(data, dict):
                            return data, None
                        break
        errors.append("Object extraction: no valid object found")
    except (json.JSONDecodeError, ValueError) as e:
        errors.append(f"Object extraction failed: {str(e)}")
    
    # Strategy 3: Extract from array if LLM wrapped it
    try:
        # Look for [{ pattern
        array_start = content.find('[')
        if array_start != -1:
            depth = 0
            bracket_depth = 0
            obj_start = None
            
            for i in range(array_start, len(content)):
                if content[i] == '[':
                    bracket_depth += 1
                elif content[i] == ']':
                    bracket_depth -= 1
                elif content[i] == '{':
                    if obj_start is None:
                        obj_start = i
                    depth += 1
                elif content[i] == '}':
                    depth -= 1
                    if depth == 0 and obj_start is not None:
                        json_str = content[obj_start:i+1]
                        data = json.loads(json_str)
                        if isinstance(data, dict):
                            return data, None
                        break
        errors.append("Array extraction: no valid object in array")
    except (json.JSONDecodeError, ValueError) as e:
        errors.append(f"Array extraction failed: {str(e)}")
    
    # Strategy 4: Remove markdown code blocks
    try:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split('\n')
            # Find first line with {
            start_idx = next((i for i, line in enumerate(lines) if '{' in line), None)
            # Find last line with }
            end_idx = next((i for i in range(len(lines)-1, -1, -1) if '}' in lines[i]), None)
            
            if start_idx is not None and end_idx is not None:
                json_str = '\n'.join(lines[start_idx:end_idx+1])
                data = json.loads(json_str)
                if isinstance(data, dict):
                    return data, None
                elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    return data[0], None
        errors.append("Markdown removal: no valid JSON after cleanup")
    except (json.JSONDecodeError, ValueError) as e:
        errors.append(f"Markdown removal failed: {str(e)}")
    
    return None, errors


def process_job(job_id, session_class):
    """Process a single job using LLM."""
    session = session_class()
    content = None
    extracted_data = None
    
    try:
        job = session.query(Job).filter(Job.id == job_id).first()
        if not job:
            return job_id, False, "Job not found", None, None
        
        if not job.job_description or job.job_description.strip() == '':
            return job_id, False, "Missing or empty job description", None, job.site
        
        # Check if already processed
        existing_detail = session.query(JobDetail).filter(JobDetail.job_id == job_id).first()
        if existing_detail:
            return job_id, False, "Already has JobDetail", None, job.site
        
        # Prepare LLM request
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
1. Return ONLY a single JSON object (not an array)
2. No markdown formatting (no ```json or ```)
3. No explanations before or after
4. Start with {{ and end with }}
5. All strings must use double quotes
6. Ensure valid JSON syntax

Begin JSON object:"""
        
        system_message = "You are a precise job posting data extractor. Return ONLY a single valid JSON object. Do not wrap it in an array."
        
        # Make API call
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
            return job_id, False, error_msg, error_details, job.site
        
        content = response.choices[0].message.content
        
        if not content:
            return job_id, False, "Empty response from LLM", None, job.site
        
        # Parse JSON with robust extraction
        extracted_data, parse_errors = extract_json_from_response(content)
        
        if extracted_data is None:
            error_msg = f"JSON parse failed: {'; '.join(parse_errors)}"
            error_details = f"LLM Response:\n{content}\n\nParse errors:\n" + '\n'.join(parse_errors)
            return job_id, False, error_msg, error_details, job.site
        
        # Validate it's a dict
        if not isinstance(extracted_data, dict):
            error_msg = f"Invalid JSON format: expected dict, got {type(extracted_data).__name__}"
            error_details = f"LLM Response:\n{content}\n\nParsed as: {extracted_data}"
            return job_id, False, error_msg, error_details, job.site
        
        # Create JobDetail
        detail = JobDetail(job_id=job.id)
        
        # Handle foreign keys
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
        
        try:
            with JobRepository(session=session) as repo:
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
                
                for json_key, model_name, field_name in fk_mappings:
                    value = extracted_data.get(json_key)
                    if value and value != "null":
                        model = model_map[model_name]
                        instance = repo._get_or_create_lookup(model, field_name, value)
                        if instance:
                            setattr(detail, f'{json_key}_id', instance.id)
                
                # Handle full address
                if extracted_data.get('full_address'):
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
                    if items:
                        m2m_items = repo._get_or_create_m2m_items(model, field_name, items)
                        setattr(detail, relationship_name, m2m_items)
                
                # Handle responsibilities
                from src.database import Responsibility
                responsibilities = extracted_data.get('responsibilities')
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
                
                if languages:
                    for lang in languages:
                        if lang:
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
                if contact_phones:
                    for phone in contact_phones:
                        if phone:
                            session.add(ContactPhone(
                                job_detail_id=detail.id,
                                phone=phone
                            ))
                
                session.commit()
                return job_id, True, "Success", None, job.site
                
        except SQLAlchemyError as e:
            session.rollback()
            error_detail = f"{type(e).__name__}: {str(e)[:200]}"
            error_details = f"Database error:\n{str(e)}\n\nExtracted data:\n{json.dumps(extracted_data, indent=2)}"
            return job_id, False, f"Database error: {error_detail}", error_details, job.site
    
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)[:100]}"
        error_details = f"Exception: {type(e).__name__}\nMessage: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        if 'content' in locals():
            error_details += f"\n\nLLM Response:\n{content}"
        if 'extracted_data' in locals() and extracted_data:
            error_details += f"\n\nExtracted data:\n{json.dumps(extracted_data, indent=2)}"
        return job_id, False, error_msg, error_details, None
    
    finally:
        session.close()


def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    if seconds <= 0:
        return "00:00:00"
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


class JobPool:
    """Thread-safe job pool with dynamic batching"""
    
    def __init__(self, all_jobs):
        self.lock = Lock()
        self.queue = deque(all_jobs)
        self.total_jobs = len(all_jobs)
        self.remaining_jobs = len(all_jobs)
    
    def get_batch(self, batch_size):
        """Get a batch of jobs from the pool"""
        with self.lock:
            batch = []
            for _ in range(min(batch_size, len(self.queue))):
                if self.queue:
                    batch.append(self.queue.popleft())
            self.remaining_jobs = len(self.queue)
            return batch
    
    def get_remaining(self):
        """Get number of remaining jobs"""
        with self.lock:
            return self.remaining_jobs


class ProgressTracker:
    """Thread-safe progress tracker with dynamic work distribution"""
    
    def __init__(self, num_threads, total_jobs, job_pool):
        self.lock = Lock()
        self.num_threads = num_threads
        self.total_jobs = total_jobs
        self.job_pool = job_pool  # Reference to get remaining jobs
        
        # Track actual progress
        self.thread_progress = {i: 0 for i in range(1, num_threads + 1)}
        self.thread_current_site = {i: None for i in range(1, num_threads + 1)}
        self.thread_start_times = {i: time.time() for i in range(1, num_threads + 1)}
        self.thread_success = {i: 0 for i in range(1, num_threads + 1)}
        self.thread_failed = {i: 0 for i in range(1, num_threads + 1)}
        self.thread_is_active = {i: False for i in range(1, num_threads + 1)}
        self.global_start_time = time.time()
    
    def update(self, thread_id, site, success, is_active=True):
        """Update progress for a thread"""
        with self.lock:
            self.thread_progress[thread_id] += 1
            self.thread_current_site[thread_id] = site
            self.thread_is_active[thread_id] = is_active
            if success:
                self.thread_success[thread_id] += 1
            else:
                self.thread_failed[thread_id] += 1
    
    def mark_idle(self, thread_id):
        """Mark thread as idle (finished work)"""
        with self.lock:
            self.thread_is_active[thread_id] = False
            self.thread_current_site[thread_id] = "Idle"
    
    def get_display(self):
        """Get formatted progress display"""
        with self.lock:
            lines = []
            lines.append("=" * 100)
            lines.append(f"LLM JOB PROCESSING - {self.num_threads} Threads | Debug: {DEBUG} | Batch: {JOBS_PER_BATCH}")
            lines.append("=" * 100)
            lines.append("")
            
            total_processed = sum(self.thread_progress.values())
            remaining_in_pool = self.job_pool.get_remaining()
            
            # Calculate expected totals per thread dynamically
            # Formula: completed + (remaining_pool / active_threads)
            active_threads = sum(1 for active in self.thread_is_active.values() if active)
            if active_threads == 0:
                active_threads = self.num_threads  # Fallback
            
            # Display each thread's progress
            for thread_id in sorted(self.thread_progress.keys()):
                progress = self.thread_progress[thread_id]
                success = self.thread_success[thread_id]
                failed = self.thread_failed[thread_id]
                is_active = self.thread_is_active[thread_id]
                current_site = self.thread_current_site[thread_id] or "Waiting"
                
                # Dynamic expected total for this thread
                if is_active:
                    # Active threads get share of remaining work
                    expected_total = progress + (remaining_in_pool / active_threads)
                else:
                    # Idle threads are done
                    expected_total = progress
                
                # Calculate percentage
                thread_pct = (progress / expected_total * 100) if expected_total > 0 else 100
                thread_pct = min(thread_pct, 100)  # Cap at 100%
                
                filled = int(thread_pct / 2)  # 50 chars = 100%
                bar = '#' * filled + '-' * (50 - filled)
                
                # Calculate ETA for this thread
                if progress > 0 and is_active:
                    elapsed = time.time() - self.thread_start_times[thread_id]
                    time_per_job = elapsed / progress
                    remaining_for_thread = expected_total - progress
                    eta = format_time(time_per_job * remaining_for_thread)
                else:
                    eta = "00:00:00" if not is_active else "--:--:--"
                
                site_display = f"{current_site[:15]:<15}"
                status = "●" if is_active else "○"
                
                line = (f"T{thread_id}{status} [{site_display}] [{bar}] {thread_pct:5.1f}% | "
                       f"{progress:3d}/{int(expected_total):3d} | ✓{success:2d} ✗{failed:2d} | ETA: {eta}")
                lines.append(line)
            
            # Global statistics
            lines.append("")
            lines.append("-" * 100)
            
            global_percentage = (total_processed / self.total_jobs * 100) if self.total_jobs > 0 else 0
            global_elapsed = time.time() - self.global_start_time
            
            if total_processed > 0:
                global_time_per_job = global_elapsed / total_processed
                global_remaining_time = global_time_per_job * remaining_in_pool
                global_eta = format_time(global_remaining_time)
            else:
                global_eta = "--:--:--"
            
            total_success = sum(self.thread_success.values())
            total_failed = sum(self.thread_failed.values())
            
            lines.append(f"OVERALL: {total_processed}/{self.total_jobs} ({global_percentage:.1f}%) | "
                        f"Remaining: {remaining_in_pool} | Active: {active_threads}/{self.num_threads} | "
                        f"✓ {total_success} ✗ {total_failed}")
            lines.append(f"Time: {format_time(global_elapsed)} elapsed | {global_eta} remaining | "
                        f"Speed: {total_processed/global_elapsed:.2f} jobs/sec" if global_elapsed > 0 else "Speed: 0.00 jobs/sec")
            lines.append("=" * 100)
            
            return "\n".join(lines)


def structure_data_with_llm():
    """Main function to structure data using LLM with dynamic work-stealing."""
    print("Initializing LLM job processor...")
    
    # Get all unique sites
    Session = sessionmaker(bind=engine)
    with Session() as session:
        sites = [site[0] for site in session.query(Job.site).distinct().all()]
    
    # Prepare jobs for each site
    all_jobs = []
    site_counts = {}
    
    for site in sites:
        with Session() as session:
            if DEBUG:
                job_ids = get_unprocessed_job_ids_for_site(session, site, JOBS_PER_SITE_DEBUG)
            else:
                job_ids = get_unprocessed_job_ids_for_site(session, site)
            
            if job_ids:
                site_counts[site] = len(job_ids)
                for job_id in job_ids:
                    all_jobs.append((site, job_id))
    
    if not all_jobs:
        print("No unprocessed jobs found.")
        return
    
    print(f"\nFound unprocessed jobs across {len(site_counts)} sites:")
    for site, count in site_counts.items():
        print(f"  {site}: {count} jobs")
    
    total_jobs = len(all_jobs)
    print(f"\nTotal: {total_jobs} jobs | {NUM_THREADS} threads | Batch size: {JOBS_PER_BATCH}\n")
    time.sleep(2)
    
    # Create job pool and progress tracker
    job_pool = JobPool(all_jobs)
    tracker = ProgressTracker(NUM_THREADS, total_jobs, job_pool)  # Pass job_pool reference
    
    # Error logging
    error_log = []
    error_lock = Lock()
    
    import datetime
    debug_log_path = f"llm_errors_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def log_error(thread_id, job_id, site, error, details=None):
        """Log error with details"""
        with error_lock:
            error_log.append({
                'thread': thread_id,
                'job_id': job_id,
                'site': site,
                'error': error
            })
            with open(debug_log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*100}\n")
                f.write(f"Thread {thread_id} | Job {job_id} | Site {site}\n")
                f.write(f"Error: {error}\n")
                if details:
                    f.write(f"\n{'-'*100}\n")
                    f.write(f"DETAILS:\n{details}\n")
                f.write(f"{'='*100}\n")
    
    def worker(thread_id):
        """Worker function - grabs batches dynamically"""
        local_session_class = sessionmaker(bind=engine)
        
        while True:
            batch = job_pool.get_batch(JOBS_PER_BATCH)
            if not batch:
                # Mark thread as idle when no more work
                tracker.mark_idle(thread_id)
                break
            
            for site, job_id in batch:
                job_id_result, success, message, details, result_site = process_job(job_id, local_session_class)
                display_site = result_site if result_site else site
                tracker.update(thread_id, display_site, success, is_active=True)
                
                if not success:
                    log_error(thread_id, job_id_result, display_site, message, details)
    
    # Display update thread
    stop_display = False
    
    def display_loop():
        """Continuously update display"""
        while not stop_display:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(tracker.get_display())
            time.sleep(DISPLAY_REFRESH_INTERVAL)
    
    display_thread = Thread(target=display_loop, daemon=True)
    display_thread.start()
    
    # Start processing
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(worker, tid) for tid in range(1, NUM_THREADS + 1)]
        for future in as_completed(futures):
            future.result()
    
    # Stop display
    stop_display = True
    time.sleep(0.2)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(tracker.get_display())
    print("\n✓ Processing completed!")
    
    # Show errors
    if error_log:
        print(f"\n{'=' * 100}")
        print(f"ERRORS ({len(error_log)} failed jobs)")
        print(f"Detailed log: {debug_log_path}")
        print("=" * 100)
        for err in error_log[:20]:
            print(f"T{err['thread']} | Job {err['job_id']} | {err['site']:<15} | {err['error']}")
        if len(error_log) > 20:
            print(f"... and {len(error_log) - 20} more")


if __name__ == "__main__":
    structure_data_with_llm()
