import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Directory where QR codes are saved (default: './qr_codes')
QR_DIRECTORY = Path(os.getenv('QR_CODE_DIR', './qr_codes'))
QR_DIRECTORY.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

# QR code colors
FILL_COLOR = os.getenv('FILL_COLOR', 'red')
BACK_COLOR = os.getenv('BACK_COLOR', 'white')

# Server configuration
SERVER_BASE_URL = os.getenv('SERVER_BASE_URL', 'http://localhost:8000')
SERVER_DOWNLOAD_FOLDER = os.getenv('SERVER_DOWNLOAD_FOLDER', 'downloads')

# JWT and authentication configuration
SECRET_KEY = os.getenv("SECRET_KEY", "secret-getenvkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Basic admin credentials (use secure authentication in production)
ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'secret')
