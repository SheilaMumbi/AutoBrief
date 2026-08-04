import os
from dotenv import load_dotenv

# Loads variables from a local .env file into the environment.

load_dotenv()

# env are always strings, so 'true'/'false need converting.
def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes")

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Email
SMTP_HOST = os.getenv("SMIP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
REPORT_SENDER = os.getenv("REPORT_SENDER", SMTP_USERNAME)

# Recipients come in as a comma-separated string — split into a clean list.
REPORT_RECIPIENTS = [
    email.strip()
    for email in os.getenv("REPORT_RECIPIENTS", "").split(",")
    if email.strip()
]

# Data source
SALES_DATA_PATH = os.getenv("SALES_DATA_PATH", "data/sample_sales_data.csv")

# Safety switch
# When True: no real email is sent (it prints to console instead), and
# insights.py will fall back to a non-AI summary if no API key is present.
DRY_RUN = _get_bool("DRY_RUN", True)

# Output
OUTPUT_DIR = "output"