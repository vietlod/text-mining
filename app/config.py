import os

# Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
CACHE_DB = os.path.join(DATA_DIR, "cache.db")
LOG_FILE = os.path.join(DATA_DIR, "app.log")

# App Settings
APP_TITLE = "Text-Mining Research Tool"
APP_VERSION = "1.0.0"

# OCR Settings
OCR_ENABLED = True
OCR_LANGUAGES = ['vi', 'en']
OCR_GPU = False # Set to True if GPU is available

# AI/API Configuration
# For Google Gemini API - Get from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyC9XToxN39FXMZ8s9NfKuYmCv36Tn2YEUc")

# For Google Custom Search API - Get from: https://console.cloud.google.com/
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "AIzaSyDEPzXIuavPE0sYWTB7twXFtrvkPC2zRsU")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "e2c89312249b3456b")

# Analysis Settings
DEFAULT_KEYWORDS_FILE = os.path.join(DATA_DIR, "keywords.json")

# Create directories if they don't exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
