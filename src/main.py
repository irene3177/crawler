import argparse
import asyncio
import logging
import os
from urllib.parse import urljoin, urlparse
from config.logging_config import setup_logging
from .crawl_one import crawl_one
from .crawl_parallel import crawl_parallel
from .robots_parser import fetch_robots_txt, filter_allowed_urls, is_url_allowed
from .scrap_static import scrap_website
from .sitemap_parser import fetch_sitemap_urls, get_sitemap_urls
from .url_check import check_url

# Call setup_logging to configure logging
setup_logging()

logger = logging.getLogger(__name__)

# Define output directory for crawled data
__location__ = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(os.path.abspath(os.path.join(__location__, '..')), "crawled_data")

# Ensure the output directory exists or is created.
os.makedirs(output_dir, exist_ok=True)


async def main():
    logger.info("Application started!")

    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Crawl URLs from a sitemap.')
    parser.add_argument('url', type=str, help='The base URL to crawl')
    parser.add_argument('--crawl-all', action='store_true',
                        help='Whether to crawl all pages (default: false)')
    parser.add_argument('--max-pages', type=int, default=10,
                        help='Maximum number of pages to crawl (default: 10)')

    args = parser.parse_args()

    logger.info("Received arguments: %s", args)

    # Validate the incoming URL
    validation_result = check_url(args.url)
    if not validation_result['valid']:
        logger.error(f"Invalid URL: {validation_result['message']}")
        return

    # Use the sanitized URL
    url = validation_result['url']
    logger.info("Sanitized URL: %s", url)

    robots_rules = {}
    # Fetch robots.txt and check crawling rules
    try:
        robots_rules = fetch_robots_txt(url)
        logger.info("Fetched robots.txt")

        sitemap_urls = robots_rules.get('sitemap', [])
        if not sitemap_urls:  # Handle case where there are no sitemaps
            logger.warning("No sitemap URLs found in robots.txt.")
            sitemap_url = None  # Set sitemap_url to None if no sitemaps exist
        else:
            sitemap_url = sitemap_urls[0]  # Assign the first sitemap URL
            logger.info("Sitemap URL found: %s", sitemap_url)
    except Exception as e:
        logger.error("Failed to fetch robots.txt: %s", e)

    urls_to_crawl = []

    # Check if we should fetch the sitemap URLs
    if args.crawl_all:
        try:
            # Fetching URLs from the sitemap if it is specified in robots.txt
            if sitemap_urls:
                urls = await fetch_sitemap_urls(sitemap_url)
                logger.info("Fetched URLs from sitemap: %d URLs found.", len(urls))
            else:
                # Fetch URLs from the sitemap.xml file
                urls = await get_sitemap_urls(url)
                logger.info("Fetched URLs from sitemap.xml: %d URLs found.", len(urls))

            if not urls:
                logger.warning("No URLs found in sitemap; fetching with scraper.")
                urls = await scrap_website(url, max_pages=args.max_pages)
                logger.info("Fetched URLs with scraper: %d URLs found.", len(urls))
            
            # Filter URLs based on robots.txt rules after fetching them
            if robots_rules:
                logger.info("Filtering URLs based on robots.txt rules.")
                urls_to_crawl = filter_allowed_urls(urls, robots_rules)[:args.max_pages]  # Limit to max_pages
            else:
                logger.info("No robots.txt rules found; using all URLs.")
                urls_to_crawl = list(urls)[:args.max_pages]  # Limit to max_pages
            if not urls_to_crawl:
                logger.warning("No allowed URLs found according to robots.txt.")
                return
        except Exception as e:
            logger.error("Error while fetching URLs from sitemap: %s", e)

    else:
        # Only crawl the current page if --crawl-all is not specified
        if is_url_allowed(url, robots_rules):
            try: 
                await crawl_one(url, output_dir)
                logger.info("Successfully crawled URL: %s", url)
            except Exception as e:
                logger.error("An error occurred while crawling the URL: %s", e)  # Log any errors
                print(f"An error occurred while crawling the URL: {e}")
            return

    # Proceed to crawl the URLs
    if urls_to_crawl:
        logger.info("Starting to crawl %d URLs...", len(urls_to_crawl))
        try:
            await crawl_parallel(urls_to_crawl, max_concurrent=10, output_dir=output_dir, base_url=url)
            logger.info("Crawling completed for %d URLs.", len(urls_to_crawl))
        except Exception as e:
            logger.error("An error occurred during crawling: %s", e)
    else:
        logger.warning("No URLs to crawl after filtering.")

if __name__ == "__main__":
    asyncio.run(main())
