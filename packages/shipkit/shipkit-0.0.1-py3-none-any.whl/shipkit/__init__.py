from icecream import ic
import logfire
import os
from dotenv import load_dotenv

ic.configureOutput(includeContext=True)

load_dotenv()
factorial_token = os.getenv("FACTORIAL_TOKEN", "")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN", "")
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN", "")
MISTRAL_TOKEN = os.getenv("MISTRAL_TOKEN", "")


logfire.configure(token="pylf_v1_us_BS3xqrsHSlfmmDN84DYWPnPQcdvjbzK2QyCQmLcD32yp")
logfire.instrument_openai()
logfire.instrument_httpx()
logfire.instrument_mcp()
