import requests
import json
import os
import time
from pathlib import Path
from config.settings import Config
from src.database import SessionLocal, Job

# ============================================
# CONFIGURATION - CHANGE THIS
# ============================================
JOB_ID = 1  # <<< CHANGE THIS TO TEST DIFFERENT JOBS

# List of models to test
MODELS_TO_TEST = [
    "deepseek/deepseek-v3.2-exp",
    "deepseek/deepseek-chat-v3.1",
    "deepseek/deepseek-chat-v3-0324",
    "mistralai/mistral-nemo",
    "mistralai/mistral-7b-instruct",
    "mistralai/devstral-small-2505",
    "mistralai/mistral-7b-instruct",
    "qwen/qwen3-32b",
    # "qwen/qwen3-next-80b-a3b-instruct",
    # "google/gemini-2.5-flash-lite",
    # "openai/gpt-4.1-nano",
    # "qwen/qwen3-235b-a22b-2507",
    # "z-ai/glm-4-32b",
    # "meta-llama/llama-4-scout",
    # "mistralai/ministral-8b",
    # "microsoft/phi-3.5-mini-128k-instruct",
    # "google/gemma-3-27b-it",
    # "openai/gpt-oss-safeguard-20b",
    # "baidu/ernie-4.5-21b-a3b-thinking",
    # "mistralai/devstral-small",
    # "openai/gpt-5-nano",
    # "amazon/nova-lite-v1",
    # "qwen/qwen-turbo",
    # "deepseek/deepseek-r1-distill-llama-70b",
    # Add more models here
]

# Create comparison folder structure
BASE_CMP_DIR = Path("cmp")
BASE_CMP_DIR.mkdir(exist_ok=True)

print("="*80)
print(f"Testing job ID: {JOB_ID}")
print(f"Models to test: {len(MODELS_TO_TEST)}")
print("="*80)

# ============================================
# FETCH JOB FROM DATABASE
# ============================================
db = SessionLocal()
try:
    job = db.query(Job).filter(Job.id == JOB_ID).first()
    
    if not job:
        print(f"\n❌ Job with ID {JOB_ID} not found in database!")
        exit()
    
    print(f"\n✅ Job found:")
    print(f"   Title: {job.job_title}")
    print(f"   Company: {job.company_name}")
    print(f"   Site: {job.site}")
    print(f"   URL: {job.job_url}")
    print(f"   Description length: {len(job.job_description) if job.job_description else 0} chars")
    print(f"   Created: {job.created_at}")
finally:
    db.close()

# ============================================
# CHECK IF JOB HAS DESCRIPTION
# ============================================
if not job.job_description:
    print("\n⚠️  Job has no description to parse!")
    exit()

print("\n" + "="*80)
print("JOB DESCRIPTION (to be parsed):")
print("="*80)
desc = job.job_description
if len(desc) > 2000:
    print(desc[:2000] + f"\n\n... [truncated {len(desc) - 2000} more characters]")
else:
    print(desc)
print("="*80)

# ============================================
# PREPARE LLM REQUEST
# ============================================
user_message = f"""
Extract structured information from this job posting and return it as JSON matching this schema:

{Config.job_to_db_prompt}

Job Posting:
Title: {job.job_title}
Company: {job.company_name}
URL: {job.job_url}

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

print(f"\n📊 Context Estimation:")
print(f"   System prompt: ~{system_prompt_chars:,} chars (~{int(system_prompt_chars/4):,} tokens)")
print(f"   User prompt: ~{user_prompt_chars:,} chars (~{int(user_prompt_chars/4):,} tokens)")
print(f"   Total input: ~{total_chars:,} chars (~{int(estimated_tokens):,} tokens)")

# ============================================
# TEST EACH MODEL
# ============================================
for model_name in MODELS_TO_TEST:
    print("\n" + "="*80)
    print(f"🔄 Testing model: {model_name}")
    print("="*80)
    
    # Create model folder (sanitize folder name)
    safe_model_name = model_name.replace("/", "_").replace(":", "_")
    model_dir = BASE_CMP_DIR / safe_model_name
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
                    
                    # Show some key fields
                    print(f"\n📊 Key Extracted Fields:")
                    print(f"   Job Function: {parsed_data.get('job_function', 'N/A')}")
                    print(f"   Seniority: {parsed_data.get('seniority_level', 'N/A')}")
                    print(f"   Industry: {parsed_data.get('industry', 'N/A')}")
                    print(f"   Remote Work: {parsed_data.get('remote_work', 'N/A')}")
                    print(f"   City: {parsed_data.get('city', 'N/A')}")
                    
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
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        # Save exception
        with open(model_dir / "error.txt", "w", encoding="utf-8") as f:
            f.write(f"Exception: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
        
        print(f"❌ Error during request: {e}")

print("\n" + "="*80)
print("ALL TESTS COMPLETE")
print(f"Results saved in: {BASE_CMP_DIR.absolute()}")
print("="*80)
