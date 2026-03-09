import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from pathlib import Path
import config

def generate_unique_filename(original_filename):
    """
    Generate unique filename to prevent race conditions
    
    Format: YYYYMMDD_HHMMSS_uniqueid_originalname.ext
    Example: 20260307_143022_a3f9c2b1_businesses.csv
    
    Args:
        original_filename: Original uploaded filename
    
    Returns:
        Unique filename string
    """
    # Secure the original filename
    safe_original = secure_filename(original_filename)
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Generate short UUID (first 8 characters)
    unique_id = str(uuid.uuid4())[:8]
    
    # Extract extension
    file_path = Path(safe_original)
    name = file_path.stem
    extension = file_path.suffix
    
    # Combine into unique filename
    unique_filename = f"{timestamp}_{unique_id}_{name}{extension}"
    
    return unique_filename

def save_uploaded_file(uploaded_file):
    """
    Save uploaded file with unique filename
    
    Args:
        uploaded_file: FileStorage object from Flask request
    
    Returns:
        tuple: (unique_filepath, original_filename)
    """
    original_filename = uploaded_file.filename
    unique_filename = generate_unique_filename(original_filename)
    
    filepath = config.UPLOAD_FOLDER / unique_filename
    uploaded_file.save(str(filepath))
    
    return filepath, original_filename
