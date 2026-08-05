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

# Which department's report to build — must match a key in department_configs
DEPARTMENT = os.getenv("DEPARTMENT", "sales")

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Email
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
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

# Safety switch
# When True: no real email is sent (it prints to console instead), and
# insights.py will fall back to a non-AI summary if no API key is present.
DRY_RUN = _get_bool("DRY_RUN", True)

# Output
OUTPUT_DIR = "output"
UPLOAD_DIR = "uploads"

# --- Web app (dashboard, accounts, uploads) ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///autobrief.db")

# The account with this email is auto-promoted to owner on signup. If unset,
# whoever signs up first becomes owner.
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "")