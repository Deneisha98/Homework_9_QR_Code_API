import logging.config
import os
import base64
from typing import List
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta
from app.config import ADMIN_PASSWORD, ADMIN_USER, ALGORITHM, SECRET_KEY
import validators  # Make sure to install this package
from urllib.parse import urlparse, urlunparse

# Load environment variables from .env file for security and configuration.
load_dotenv()


def setup_logging():
    """
    Sets up logging for the application using a configuration file.
    This ensures standardized logging across the entire application.
    """
    # Construct the path to 'logging.conf', assuming it's in the project's root.
    logging_config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'logging.conf')
    normalized_path = os.path.abspath(logging_config_path)  # Normalize the path for all OS
    if os.path.exists(normalized_path):
        logging.config.fileConfig(normalized_path, disable_existing_loggers=False)
    else:
        logging.warning(f"Logging configuration file not found at {normalized_path}. Using default logging.")
        logging.basicConfig(level=logging.INFO)


def authenticate_user(username: str, password: str):
    """
    Authenticates a user against static admin credentials.

    Args:
        username (str): The username provided by the user.
        password (str): The password provided by the user.

    Returns:
        dict: User details if authentication is successful.
        None: If authentication fails.
    """
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        return {"username": username}
    logging.warning(f"Authentication failed for user: {username}")
    return None


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Generates a JWT access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta, optional): Expiration time for the token. Defaults to 15 minutes.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def validate_and_sanitize_url(url_str: str):
    """
    Validates and sanitizes a URL string.

    Args:
        url_str (str): The URL to validate and sanitize.

    Returns:
        str: Sanitized URL if valid.
        None: If the URL is invalid.
    """
    if validators.url(url_str):
        parsed_url = urlparse(url_str)
        return urlunparse(parsed_url)
    logging.error(f"Invalid URL provided: {url_str}")
    raise ValueError("Invalid URL provided")


def encode_url_to_filename(url: str) -> str:
    """
    Encodes a URL into a base64 string safe for filenames.

    Args:
        url (str): The URL to encode.

    Returns:
        str: Base64-encoded string safe for filenames.
    """
    sanitized_url = validate_and_sanitize_url(url)
    encoded_bytes = base64.urlsafe_b64encode(sanitized_url.encode('utf-8'))
    return encoded_bytes.decode('utf-8').rstrip('=')


def decode_filename_to_url(encoded_str: str) -> str:
    """
    Decodes a base64 encoded string back into a URL.

    Args:
        encoded_str (str): Base64-encoded string.

    Returns:
        str: Decoded URL.
    """
    padding_needed = 4 - (len(encoded_str) % 4)
    if padding_needed:
        encoded_str += "=" * padding_needed
    decoded_bytes = base64.urlsafe_b64decode(encoded_str)  # Fix typo
    return decoded_bytes.decode('utf-8')


def generate_links(action: str, qr_filename: str, base_api_url: str, download_url: str) -> List[dict]:
    """
    Generates HATEOAS links for QR code resources.

    Args:
        action (str): The action being performed ("list", "create", "delete").
        qr_filename (str): The filename of the QR code.
        base_api_url (str): The base API URL.
        download_url (str): The download URL for the QR code.

    Returns:
        List[dict]: List of HATEOAS links.
    """
    links = []
    if action in ["list", "create"]:
        original_url = decode_filename_to_url(qr_filename[:-4])
        links.append({"rel": "view", "href": download_url, "action": "GET", "type": "image/png"})
    if action in ["list", "create", "delete"]:
        delete_url = f"{base_api_url}/qr-codes/{qr_filename}"
        links.append({"rel": "delete", "href": delete_url, "action": "DELETE", "type": "application/json"})
    return links
