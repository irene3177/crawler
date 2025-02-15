import requests
import logging
from urllib.parse import urlparse, urljoin
from typing import List

logger = logging.getLogger(__name__)

def fetch_robots_txt(url: str) -> dict:
    """Fetches the robots.txt file for the given base URL.

    Args:
        url (str): The base URL to fetch the robots.txt file from.

    Returns:
        dict: Parsed robots.txt rules, or an empty dict if an error occurs.
    """
    # Parse the URL into components
    parsed_url = urlparse(url)

    # Construct the base URL (homepage)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
    robots_url = urljoin(base_url, 'robots.txt')
    logger.info("Successfully fetched robots.txt from %s", robots_url)

    try:
        response = requests.get(robots_url, timeout=10)
        response.raise_for_status()
        return parse_robots_txt(response.text)
    except Exception as e:
        logger.error(f"Error fetching robots.txt for {url}: {e}")
        return {}


def parse_robots_txt(robots_txt: str) -> dict:
    """Parses the content of robots.txt and extracts allow/disallow rules.

    Args:
        robots_txt (str): The content of the robots.txt file.

    Returns:
        dict: A dictionary containing 'allow', 'disallow', and 'sitemap' rules.
    """
    rules = {'allow': [], 'disallow': [], 'sitemap': []}
    user_agent = '*'

    # Split the content into lines and parse
    try:
        lines = robots_txt.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith('User-agent:'):
                user_agent = line.split(':')[1].strip()
            elif line.startswith('Allow:'):
                rules['allow'].append(line.split(':')[1].strip())
            elif line.startswith('Disallow:'):
                rule = line.split(':', 1)[1].strip()
                if rule:  # Only append non-empty rules
                    rules['disallow'].append(rule)
            
            #elif line.startswith('Disallow:'):
            #    rules['disallow'].append(line.split(':')[1].strip())
            elif line.startswith('Sitemap:'):
                rules['sitemap'].append(line.split(':', 1)[1].strip())

    except Exception as e:
        logger.error(f"Error parsing robots.txt: {e}")
    return rules

def is_url_allowed(url: str, robots_rules: dict) -> bool:
    """Checks if the URL is allowed to be crawled based on the robots.txt rules.

    Args:
        url (str): The URL to check.
        robots_rules (dict): A dictionary containing 'allow' and 'disallow' rules.

    Returns:
        bool: True if the URL is allowed, False otherwise.
    """
    # Check if there are any disallow rules
    if not robots_rules['disallow']:
        logger.debug(f"No disallow rules found; URL {url} is allowed.")
        return True  # If disallow is empty, allow all URLs


    parsed_url = urlparse(url)

    path = parsed_url.path

    # Check disallow rules
    for disallow in robots_rules['disallow']:
       disallow_path = disallow.rstrip('/')
       if path.startswith(disallow_path) or path == disallow_path:
           return False  # URL is disallowed



    # Check allow rules
    for allow in robots_rules['allow']:
       allow_path = allow.rstrip('/')
       if path.startswith(allow_path) or path == allow_path:
           return True  # URL is allowed


    # Default to allow if no rules match
    return True


def filter_allowed_urls(urls: List[str], robots_rules: dict) -> List[str]:
    """Filters the given URLs based on the robots.txt rules.

    Args:
        urls (List[str]): A list of URLs to filter.
        robots_rules (dict): A dictionary containing 'allow' and 'disallow' rules.

    Returns:
        List[str]: A list of URLs that are allowed to be crawled.
    """
    logger.info(f"Filtering {len(urls)} URLs based on robots.txt rules.")
    allowed_urls = []
    for url in urls:
        if is_url_allowed(url, robots_rules):  # Use the is_url_allowed function to check each URL
            allowed_urls.append(url)
    logger.info(f"Found {len(allowed_urls)} allowed URLs.")
    return allowed_urls
