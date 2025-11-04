import requests
import json
import os
import time
from pathlib import Path
from config.settings import Config
from src.database import SessionLocal, Job
import random
import matplotlib.pyplot as plt

# ============================================
# CONFIGURATION - CHANGE THIS
# ============================================
# Job IDs to test (specific ones or random selection)
SPECIFIC_JOB_IDS = [12, 432, 832, 11230, 16832]
RANDOM_JOB_COUNT = 5
MAX_JOB_ID = 19000

# Generate random job IDs if needed
if len(SPECIFIC_JOB_IDS) == 0:
    JOB_IDS = random.sample(range(1, MAX_JOB_ID + 1), RANDOM_JOB_COUNT)
else:
    JOB_IDS = SPECIFIC_JOB_IDS

# List of models to test
MODELS_TO_TEST = [
    "openai/gpt-oss-safeguard-20b",
    "qwen/qwen-turbo",
    "deepseek/deepseek-r1-distill-llama-70b",
]

# Create comparison folder structure
BASE_CMP_DIR = Path("cmp3")
BASE_CMP_DIR.mkdir(exist_ok=True)

print("="*80)
print(f"Testing job IDs: {JOB_IDS}")
print(f"Models to test: {len(MODELS_TO_TEST)}")
print("="*80)

# Store execution times for each job and model
execution_times = {}

# ============================================
# PROCESS EACH JOB ID
# ============================================
for job_id in JOB_IDS:
    print(f"\n{'='*80}")
    print(f"Processing Job ID: {job_id}")
    print(f"{'='*80}")
    
    # Create job directory
    job_dir = BASE_CMP_DIR / f"job_{job_id}"
    job_dir.mkdir(exist_ok=True)
    
    # ============================================
    # FETCH JOB FROM DATABASE
    # ============================================
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            print(f"❌ Job with ID {job_id} not found in database!")
            continue
        
        print(f"✅ Job found:")
        print(f"   Title: {job.job_title}")
        print(f"   Company: {job.company_name}")
        print(f"   Site: '{job.site}'")
        print(f"   URL: '{job.job_url}'")
        print(f"   Description length: {len(job.job_description) if job.job_description else 0} chars")
        print(f"   Created: {job.created_at}")
    finally:
        db.close()

    # ============================================
    # CHECK IF JOB HAS DESCRIPTION
    # ============================================
    if not job.job_description:
        print("⚠️  Job has no description to parse!")
        continue

    # ============================================
    # PREPARE LLM REQUEST
    # ============================================

    # Extract structured information from this job posting and return it as JSON matching this schema:
    user_message = f"""
{Config.job_to_db_prompt_2}

Job Posting:
Title: {job.job_title}
Company: {job.company_name}
URL: '{job.job_url}'

Description:
{job.job_description[:Config.max_body_text_length]}

Return ONLY valid JSON, no additional text.
"""

    system_message = "You are a job posting parser. Extract structured information and return only valid JSON. IMPORTANT: All extracted text fields must be in English, regardless of the input language. Translate all content (job titles, skills, responsibilities, locations, etc.) to English for consistency."

    # Estimate token count
    system_prompt_chars = len(system_message)
    user_prompt_chars = len(user_message)
    total_chars = system_prompt_chars + user_prompt_chars
    estimated_tokens = total_chars / 4

    print(f"📊 Context Estimation:")
    print(f"   System prompt: ~{system_prompt_chars:,} chars (~{int(system_prompt_chars/4):,} tokens)")
    print(f"   User prompt: ~{user_prompt_chars:,} chars (~{int(user_prompt_chars/4):,} tokens)")
    print(f"   Total input: ~{total_chars:,} chars (~{int(estimated_tokens):,} tokens)")

    # Initialize execution times for this job
    execution_times[job_id] = {}
    
    # ============================================
    # TEST EACH MODEL FOR THIS JOB
    # ============================================
    for model_name in MODELS_TO_TEST:
        print(f"\n🔄 Testing model: {model_name}")
        
        # Create model folder within job directory
        safe_model_name = model_name.replace("/", "_").replace(":", "_")
        model_dir = job_dir / safe_model_name
        model_dir.mkdir(exist_ok=True)
        
        # Save input prompt
        with open(model_dir / "input_prompt.txt", "w", encoding="utf-8") as f:
            f.write("SYSTEM PROMPT:\n")
            f.write("="*80 + "\n")
            f.write(system_message + "\n\n")
            f.write("USER PROMPT:\n")
            f.write("="*80 + "\n")
            f.write(user_message)
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {Config.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        # Send request and measure time
        try:
            start_time = time.time()
            response = requests.post(
                f"{Config.llm_api}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"⏱️  Execution time: {execution_time:.2f} seconds")
            print(f"📡 Response Status: {response.status_code}")
            
            # Store execution time
            execution_times[job_id][model_name] = execution_time
            
            # Save execution time
            with open(model_dir / "time.txt", "w", encoding="utf-8") as f:
                f.write(f"Execution Time: {execution_time:.2f} seconds\n")
                f.write(f"Response Status: {response.status_code}\n")
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    # Try to parse as JSON
                    try:
                        parsed_data = json.loads(content)
                        
                        # Save as valid JSON
                        with open(model_dir / "response.json", "w", encoding="utf-8") as f:
                            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
                        
                        print(f"✅ Valid JSON response saved")
                        print(f"   Fields extracted: {len(parsed_data.keys())}")
                        
                    except json.JSONDecodeError as e:
                        # Save as text if not valid JSON
                        with open(model_dir / "response.txt", "w", encoding="utf-8") as f:
                            f.write(content)
                        
                        print(f"❌ Invalid JSON response (saved as .txt)")
                        print(f"   Parse error: {e}")
                else:
                    with open(model_dir / "error.txt", "w", encoding="utf-8") as f:
                        f.write("No choices in response\n")
                        f.write(json.dumps(result, indent=2))
                    print("❌ No choices in response")
            else:
                # Save error response
                with open(model_dir / "error.txt", "w", encoding="utf-8") as f:
                    f.write(f"Status Code: {response.status_code}\n")
                    f.write(f"Response: {response.text}")
                
                print(f"❌ API request failed")
                
        except Exception as e:
            # Save exception
            with open(model_dir / "error.txt", "w", encoding="utf-8") as f:
                f.write(f"Exception: {str(e)}\n")
                import traceback
                f.write(traceback.format_exc())
            
            print(f"❌ Error during request: {e}")

# ============================================
# CREATE EXECUTION TIME CHART
# ============================================
if execution_times:
    print(f"\n{'='*80}")
    print("CREATING EXECUTION TIME VISUALIZATION")
    print("="*80)
    
    # Create chart for all jobs
    plt.figure(figsize=(15, 10))
    
    for job_id in execution_times:
        if job_id in execution_times and execution_times[job_id]:
            models = list(execution_times[job_id].keys())
            times = list(execution_times[job_id].values())
            
            plt.plot(models, times, marker='o', label=f'Job {job_id}', linewidth=2, markersize=6)
    
    plt.title('Model Execution Time Comparison Across Jobs', fontsize=16, fontweight='bold')
    plt.xlabel('Models', fontsize=12)
    plt.ylabel('Execution Time (seconds)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save the chart
    chart_path = BASE_CMP_DIR / "execution_times_chart.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Execution time chart saved: {chart_path}")
    
    # Create individual charts for each job
    for job_id in execution_times:
        if execution_times[job_id]:
            plt.figure(figsize=(12, 8))
            
            models = list(execution_times[job_id].keys())
            times = list(execution_times[job_id].values())
            
            plt.plot(models, times, marker='o', linewidth=2, markersize=6, color='blue')
            plt.title(f'Model Execution Time - Job {job_id}', fontsize=14, fontweight='bold')
         
