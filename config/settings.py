import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    job_sites = [
        "https://jobber.md/jobs/",
        "https://www.rabota.md/ro/jobs-moldova",
        "https://www.delucru.md/jobs"
    ]
    llm_api = "https://openrouter.ai/api/v1"
    llm_api_key = os.getenv("LLM_API_KEY")
    llm_model = "deepseek/deepseek-chat-v3.1:free"
