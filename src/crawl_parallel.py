import os
import sys
import psutil
import asyncio
import logging
from .results_saver import save_markdown, save_metadata
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

logger = logging.getLogger(__name__)

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)


async def crawl_parallel(urls: List[str], max_concurrent: int = 3, output_dir: str = 'crawled_data', base_url: str = None):
    """
    Asynchronously crawl a list of URLs in parallel.

    This function performs web crawling using an AsyncWebCrawler instance, 
    tracks memory usage, and saves the results and metadata.

    Args:
        urls (List[str]): The list of URLs to crawl.
        max_concurrent (int): The maximum number of concurrent crawls (default is 3).
        output_dir (str): The directory where markdown and metadata should be saved (default is 'crawled_data').
        base_url (str): The base URL for relative links (default is None).
    """
    
    logger.info("=== Parallel Crawling with Browser Reuse + Memory Check ===")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # We'll keep track of peak memory usage across all tasks
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        """Logs current and peak memory usage."""
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        logger.debug(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")
        
    # Minimal browser config
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,   # corrected from 'verbos=False'
        extra_args=["--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    ],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    results_md = []  # To store markdown results
    metadata = []  # To store metadata for JSON output

    try:
        # We'll chunk the URLs in batches of 'max_concurrent'
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i: i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                # Unique session_id per concurrent sub-task
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(
                    url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

                # Check memory usage prior to launching tasks
                log_memory(prefix=f"Before batch {i//max_concurrent + 1}: ")

                # Gather results
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Check memory usage after tasks complete
                log_memory(prefix=f"After batch {i//max_concurrent + 1}: ")

                # Evaluate results
                for url, result in zip(batch, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error crawling {url}: {result}")
                        fail_count += 1
                    else:
                        # Assuming result returns HTML for conversion to Markdown
                        markdown_content = result.markdown if hasattr(
                            result, 'markdown') else ''

                        # Save markdown content to a file and store the path
                        file_path = await save_markdown(
                            url, markdown_content, output_dir)

                        # Store metadata
                        metadata.append({
                            'url': url,
                            'markdown_file': file_path
                        })

                        success_count += 1

                logger.info(f"Summary:")
                logger.info(f"  - Successfully crawled: {success_count}")
                logger.info(f"  - Failed: {fail_count}")

    finally:
        logger.info("Closing crawler...")
        await crawler.close()
        # Final memory log
        log_memory(prefix="Final: ")
        logger.info("=== Parallel Crawling Complete ===")
        logger.info(f"Peak memory usage (MB): {peak_memory // (1024 * 1024)}")
       # Save metadata to JSON file
        metadata_file_path = await save_metadata(metadata, output_dir, base_url)
        logger.info(f"Metadata saved to {metadata_file_path}")
