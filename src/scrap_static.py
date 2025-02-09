import requests
import logging
import asyncio
import aiohttp
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from typing import List, Set

logger = logging.getLogger(__name__)

def get_domain(url: str) -> str:
    """Extracts the domain from the given URL."""
    parsed_url = urlparse(url)
    return parsed_url.netloc

def is_page_url(url: str) -> bool:
    """Checks if the URL points to a web page and not an image, file, or other resource."""
    # Define unacceptable extensions for pages (e.g., images, files)
    non_page_extensions = (
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',  # Images
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  # Documents
        '.zip', '.tar', '.gz', '.rar',  # Archives
        '.mp3', '.mp4', '.avi', '.mkv',  # Media files
        '.css', '.js', '.json', '.xml',  # Web resources
        '.ico', '.woff', '.woff2', '.ttf', '.eot'  # Fonts and icons
    )
    
    # Define paths or patterns that indicate non-page URLs
    non_page_paths = (
        '/exe/file/',  # Exclude URLs containing this path
        '/download/',  # Example: Exclude download links
        '/static/',    # Example: Exclude static resources
    )

    # Extract the path and query from the URL
    parsed_url = urlparse(url)
    path = parsed_url.path.lower()
    query = parsed_url.query
    
    # Check if the URL contains a non-page path
    if any(non_page_path in path for non_page_path in non_page_paths):
        return False


    # Check if the URL ends with a non-page extension
    if any(path.endswith(ext) for ext in non_page_extensions):
        return False
    
    # Allow URLs with no extension or common page extensions
    common_page_extensions = ('.html', '.htm', '.php', '.aspx', '.jsp', '/')
    if any(path.endswith(ext) for ext in common_page_extensions) or query:
        return True
    
    # Allow URLs with no extension (e.g., https://example.com/page)
    if '.' not in path.split('/')[-1]:
        return True
    
    return False

async def fetch_links(session: aiohttp.ClientSession, url: str) -> Set[str]:
    """Asynchronously fetch links from a given URL.

    Args:
        session (aiohttp.ClientSession): The session used for fetching web pages.
        url (str): The URL to fetch links from.

    Returns:
        Set[str]: A set of absolute URLs found on the page.
    """
    links = set()
    try:
        logger.info("Fetching links from: %s", url)
        async with session.get(url, verify_ssl=False, timeout=10) as response:
            response.raise_for_status()  # Raise an error for bad responses
            soup = BeautifulSoup(await response.text(), 'html.parser')
        
            for a in soup.find_all('a', href=True):  # Find all anchor tags
                link = a['href']
                absolute_link = urljoin(url, link)  # Convert to absolute URL
                
                # Check if the link is a valid page URL
                if is_page_url(absolute_link):
                    links.add(absolute_link)  # Add link to the set
                    logger.debug("Found valid link: %s", absolute_link)
            
    except Exception as e:
        logger.error("Error fetching %s: %s", url, e)
    
    return links

async def scrap_website(base_url: str, max_depth: int = 1, current_depth: int = 0, max_pages: int = None) -> Set[str]:
    """Asynchronously scrapes the given website up to a specified depth and collects all unique links.

    Args:
        base_url (str): The base URL of the website to scrape.
        max_depth (int): The maximum depth to scrape (default is 1).
        max_pages (int): Maximum pages to scrape (default is None).

    Returns:
        Set[str]: A set of all visited URLs.
    """
    
    visited = set() # To keep track of visited URLs
    to_visit = [base_url]  # Start with the base URL
    pages_scraped = 0

    async with aiohttp.ClientSession() as session: # Create a session for all requests
        while to_visit:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue  # Skip if already visited
            
            visited.add(current_url)
            logger.info("Scraping: %s", current_url)

            links = await fetch_links(session, current_url)  # Get links from the current page
            
            # Filter links for same domain and add them to the queue
            for link in links:
                if get_domain(link) == get_domain(base_url) and link not in visited:
                    to_visit.append(link)

            pages_scraped += 1
            logger.debug("Total pages scraped: %d", pages_scraped)
            # Stop if max_pages is provided and limit is reached
            if max_pages is not None and pages_scraped >= max_pages:
                logger.info("Max pages limit reached: %d", max_pages)
                break

    logger.info("Scraping complete. Total visited URLs: %d", len(visited))
    return visited

