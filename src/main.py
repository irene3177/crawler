import argparse
import asyncio
import logging
import os
from config.logging_config import setup_logging
from .spider_runner import SpiderRunner
from .crawl_one import crawl_one
from .crawl_parallel import crawl_parallel
from .robots_parser import fetch_robots_txt, filter_allowed_urls, is_url_allowed
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
    parser.add_argument('--max-pages', type=int, default=50,
                        help='Maximum number of pages to crawl (default: 50)')
    parser.add_argument('--check-robots', action='store_true', help='Whether to check the robots.txt rules (default: true)')


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
    sitemap_url = None
    # Fetch robots.txt and check crawling rules
    if args.check_robots:
        try:
            robots_rules = await fetch_robots_txt(url)
            logger.info("Fetched robots.txt")

            sitemap_urls = robots_rules.get('sitemap', [])
            sitemap_url = sitemap_urls[0] if sitemap_urls else None
            if sitemap_url:
                logger.info("Sitemap URL found: %s", sitemap_url)
            else:
                logger.warning("No sitemap URLs found in robots.txt.")        
        except Exception as e:
            logger.error("Failed to fetch robots.txt: %s", e)

    urls_to_crawl = []

    # Conditional crawling logic
    if args.crawl_all:
        urls = await fetch_urls_for_crawling(url, sitemap_url, robots_rules, args.max_pages, args.check_robots)
        urls_to_crawl = urls if urls is not None else []  # Ensure it's an empty list if None
        if not urls_to_crawl:
            logger.warning("No URLs found to crawl.")
            logger.info("Crawling single URL: %s", url)
            await crawl_single_url(url, robots_rules)
            return
        await crawl_urls(urls_to_crawl, url)  # Crawl the URLs if any
    else:
        await crawl_single_url(url, robots_rules if args.check_robots else None)



async def fetch_urls_for_crawling(url, sitemap_url, robots_rules, max_pages, check_robots):
    """Fetch URLs either from the sitemap or using the SpiderRunner."""
    try:
        if sitemap_url:
            urls = await fetch_sitemap_urls(sitemap_url, max_pages=max_pages)
            logger.info("Fetched URLs from sitemap: %d URLs found", len(urls))
        else:
            urls = await get_sitemap_urls(url, max_pages)
            logger.info("Fetched URLs from sitemap.xml: %d URLs found", len(urls))

        if not urls:
            logger.warning("No URLs found in sitemap; fetching with scraper.")
            runner = SpiderRunner()
            urls = runner.run_spider(url, max_pages=max_pages)
            logger.info("Fetched URLs with scraper: %d URLs found", len(urls))

        if check_robots and robots_rules:
            logger.info("Filtering URLs based on robots.txt rules.")
            return filter_allowed_urls(urls, robots_rules)[:max_pages]
        else:
            logger.info("No robots.txt rules found; using all URLs.")
            return list(urls)[:max_pages]
    except Exception as e:
        logger.error("Error while fetching URLs from sitemap: %s", e)
        return []

async def crawl_single_url(url, robots_rules):
    """Crawl a single URL with respect to robots.txt rules."""
    if not robots_rules or is_url_allowed(url, robots_rules):
        try:
            await crawl_one(url, output_dir)
            logger.info("Successfully crawled URL: %s", url)
        except Exception as e:
            logger.error("An error occurred while crawling the URL: %s", e)
        return []
    return []


async def crawl_urls(urls_to_crawl, base_url):
    """Crawl multiple URLs in parallel."""
    logger.info("Starting to crawl %d URLs...", len(urls_to_crawl))
    try:
        await crawl_parallel(urls_to_crawl, max_concurrent=10, output_dir=output_dir, base_url=base_url)
        logger.info("Crawling completed for %d URLs.", len(urls_to_crawl))
    except Exception as e:
        logger.error("An error occurred during crawling: %s", e)


if __name__ == "__main__":
    asyncio.run(main())
