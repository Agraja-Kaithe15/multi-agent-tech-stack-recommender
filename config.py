import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in .env")