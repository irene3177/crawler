import aiohttp
import asyncio
import logging
from urllib.parse import urlparse
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from src.url_check import is_valid_format

# Setup logging
logger = logging.getLogger(__name__)

async def fetch_sitemap_urls(sitemap_url: str, session: ClientSession = None) -> list:
    """
    Fetches URLs from a sitemap, including nested sitemaps.

    Args:
        sitemap_url (str): The URL of the sitemap or sitemap index.

    Returns:
        list: A list of URLs found in the sitemap, or an empty list if an error occurs.
    """
    logger.info(f"Fetching sitemap: {sitemap_url}")
    urls = []

    try:
        async with session.get(sitemap_url, timeout=10) as response:  # 10-second timeout
            response.raise_for_status()  # Raise an error for bad responses
            content = await response.text()

            # Parse the sitemap
            soup = BeautifulSoup(content, 'xml')

            # Check if this is a sitemap index (contains links to other sitemaps)
            sitemap_tags = soup.find_all('sitemap')
            if sitemap_tags:
                logger.info(f"Found nested sitemaps in: {sitemap_url}")
                nested_sitemap_urls = [sitemap.find('loc').text for sitemap in sitemap_tags]
                nested_urls = await asyncio.gather(
                    *(fetch_sitemap_urls(nested_sitemap_url, session) for nested_sitemap_url in nested_sitemap_urls)
                )
                urls.extend(url for sublist in nested_urls for url in sublist)
            else:
                logger.info(f"Extracting URLs from: {sitemap_url}")
                # Extract URLs from the current sitemap
                url_tags = soup.find_all('url')
                urls.extend(url.find('loc').text for url in url_tags if url.find('loc'))
                
    except asyncio.TimeoutError:
        logger.error(f"Timeout while fetching sitemap: {sitemap_url}")
    except aiohttp.ClientError as e:
        logger.error(f"Client error while fetching sitemap {sitemap_url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching sitemap {sitemap_url}: {e}")

    return urls

async def get_sitemap_urls(url: str) -> list:
    """
    Constructs the sitemap URL and fetches all URLs from it, including nested sitemaps.

    Args:
        url (str): The URL of the website.

    Returns:
        list: A list of all URLs found in the sitemap.
    """
    if not is_valid_format(url):
        logger.error(f"Invalid URL: {url}")
        return []
    # Parse the URL into components
    parsed_url = urlparse(url)

    # Construct the base URL (homepage)
    # Ensure it's always the home page
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"

    sitemap_url = base_url + 'sitemap.xml'

    async with ClientSession() as session:
        return await fetch_sitemap_urls(sitemap_url, session)
