import re
import logging
import requests
from urllib.parse import urlparse, urlunparse
from config.logging_config import setup_logging

# Call setup_logging to configure logging
setup_logging()

# Now you can use the logger in this file
logger = logging.getLogger(__name__) 

def is_valid_format(url: str) -> bool:
    """
    Check the URL format correctness.
    
    Validates if the given URL matches acceptable patterns such as the 
    correct scheme (http or https), domain names, and overall structure.
    
    Args:
        url (str): The URL to validate.
        
    Returns:
        bool: True if the format is valid, False otherwise.
    """
    # Regular expression to check the protocol, domain, and port
    regex = re.compile(
        r'^(https?://)'  # Allow http and https
        r'((([A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|[A-Z0-9-]{2,})?)|'  # Domain
        r'localhost|'  # Local host
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # IPv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # IPv6
        r'(?::\d+)?'  # Optional port
        r'(?:/?|[/?]\S*)$',  # Path
        re.IGNORECASE)

    if re.match(regex, url):
        logger.info("URL is valid: %s", url)
        return True
    else:
        logger.warning("Invalid URL format: %s", url)
        return False

def exists(url: str) -> dict:
    """
    Check the existence of a URL by sending a HEAD request.
    
    This function sends a HEAD request to the specified URL to check 
    if it is reachable and responds with a status in the 2XX range.
    
    Args:
        url (str): The URL to check.
        
    Returns:
        dict: A dictionary containing the existence check result and any error message.
    """
    logger.info("Checking URL existence: %s", url)
    try:
        logger.debug("Sending HEAD request to %s", url)
        # Send a HEAD request to the URL to check its existence
        response = requests.head(url, allow_redirects=True, timeout=10)
        # Return True if status is 2XX
        return {'exists': 200 <= response.status_code < 300, 'error': None}
    except requests.ConnectionError:
        logger.error(f"Connection error while checking URL: {url}")
        return {'exists': False, 'error': 'Connection error'}
    except requests.Timeout:
        logger.error(f"Timeout error while checking URL: {url}")
        return {'exists': False, 'error': 'Timeout error'}
    except requests.RequestException as e:
        logger.error(f"Error checking URL {url} existence: {e}")
        return {'exists': False, 'error': str(e)}

def clean_url(url: str) -> str:
    """
    Clean the given URL to remove harmful elements and validate its format.
    
    This function strips HTML tags, removes special characters, and ensures
    the URL is valid before returning it.
    
    Args:
        url (str): The URL to clean.
        
    Returns:
        str: The sanitized and valid URL.
        
    Raises:
        ValueError: If the cleaned URL is not valid after sanitization.
    """
    # Remove substrings that can be used in attacks
    logger.debug("Cleaning URL: %s", url)

    # Remove HTML tags
    url = re.sub(r'<.*?>', '', url)

    # Remove potentially harmful characters
    url = re.sub(r"[;\"'<>]", '', url)  # Remove semicolons, quotes, and angle brackets
    url = re.sub(r'[\s]', '%20', url)  # Replace spaces with %20 (URL encoding)

    # Validate that no JavaScript injection is present
    if 'javascript:' in url.lower():
        raise ValueError("Sanitized URL is invalid due to JavaScript injection.")
    
    # Validate that no major security risks are present
    if re.search(r'(alert|eval|script)', url.lower()):  # Check for known XSS patterns
        raise ValueError("Sanitized URL is invalid due to malicious content.")
     

    # Parse the URL
    parsed_url = urlparse(url)
    cleaned_url = urlunparse(parsed_url._replace(query='', fragment=''))

    # Validate the cleaned URL
    if is_valid_format(cleaned_url):
        logger.info("Cleaned URL is valid: %s", cleaned_url)
        return cleaned_url
    else:
        logger.error("Cleaned URL is invalid: %s", cleaned_url)
        raise ValueError("Cleaned URL is invalid")

def check_url(url: str) -> dict:
    """
    Validates the provided URL by cleaning it and checking its existence.

    This function first sanitizes the input URL to remove any potentially
    harmful elements. After sanitization, it checks if the cleaned URL exists 
    by sending a HEAD request.

    Args:
        url (str): The URL to be validated.

    Returns:
        dict: A dictionary containing the validation result, which includes:
            - 'valid' (bool): Indicates whether the URL is valid.
            - 'url' (str or None): The cleaned URL if valid, otherwise None.
            - 'message' (str): A message providing context on validity. Could indicate errors or success.
    
    Raises:
        ValueError: If the cleaning process fails due to invalid input.
    """

    # Clean the URL first
    try:
        cleaned_url = clean_url(url)
        logger.info("Cleaned URL: %s", cleaned_url)
    except ValueError as e:
        return {'valid': False, 'url': None, 'message': str(e)}

    # Check existence
    existence_result = exists(cleaned_url)
    if not existence_result['exists']:
        error_message = existence_result['error'] if existence_result['error'] else "URL does not exist"
        return {'valid': False, 'url': None, 'message': error_message}

    # URL is valid
    return {'valid': True, 'url': cleaned_url, 'message': ''}