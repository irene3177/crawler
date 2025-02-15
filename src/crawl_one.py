import logging
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from src.results_saver import save_markdown, save_metadata


logger = logging.getLogger(__name__)

async def crawl_one(url: str, output_dir: str) -> str:
    """
    Crawl the specified URL and save the markdown content to a file.
    
    This function asynchronously crawls a given URL using an `AsyncWebCrawler`.
    It retrieves the markdown representation of the web page, saves it to a file,
    and stores metadata related to the crawl.

    Args:
        url (str): The URL to crawl.
        output_dir (str): The directory where markdown and metadata should be saved.

    Returns:
        str: The file path of the saved markdown file, or None if no content was found.
    """
    metadata = []  # To store metadata for JSON output
    logger.info("Starting to crawl URL: %s", url)

    async with AsyncWebCrawler() as crawler:
        try:
            result = await crawler.arun(url=url)

            # Check for markdown content in the result
            if hasattr(result, 'markdown'):
                markdown_content = result.markdown

                # Save the markdown content
                markdown_file_path = await save_markdown(url, markdown_content, output_dir)
                logger.info("Saved markdown content for URL %s at %s", url, markdown_file_path)

                # Store metadata
                metadata.append({
                    'url': url,
                    'markdown_file': markdown_file_path
                })
            
                # Save metadata to JSON file
                await save_metadata(metadata, output_dir, url)
                logger.info("Saved metadata for URL %s", url)
                return markdown_file_path
            else:
                logger.warning("No markdown content found for URL: %s", url)
                return None

        except Exception as e:
            logger.error("Error while crawling URL %s: %s", url, str(e))
            return None
