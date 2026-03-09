import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/data/lead_outreach.db')

# Upload configuration
UPLOAD_FOLDER = BASE_DIR / 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
MAX_CSV_ROWS = 50000  # Maximum rows to process

# Request timeouts (connect, read) in seconds
TIMEOUTS = {
    'cerebras_api': (5, 30),
    'website_check': (3, 5),
    'default': (5, 10)
}

# Batch configuration
DEFAULT_BATCH_SIZE = 10
BATCH_SIZE_OPTIONS = [5, 10, 25, 50, 100]

# App configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Country-specific settings (Kenya for MVP)
DEFAULT_COUNTRY_CODE = '+254'
DEFAULT_COUNTRY = 'KE'

# Opportunity scoring thresholds
MIN_OPPORTUNITY_SCORE = 50

# Column mapping confidence threshold
COLUMN_CONFIDENCE_THRESHOLD = 0.7  # 70% confidence required

# Encryption key file
ENCRYPTION_KEY_FILE = BASE_DIR / 'data' / 'encryption.key'
