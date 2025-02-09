import os
import sys
import unittest
from unittest.mock import AsyncMock, patch
import logging

from src.crawl_parallel import crawl_parallel  # Replace with the actual import path

# Setup logging for tests (optional)
logging.basicConfig(level=logging.DEBUG)

class TestCrawlParallel(unittest.TestCase):

    @patch('src.crawl_parallel.AsyncWebCrawler', new_callable=AsyncMock)  # Mock the AsyncWebCrawler
    @patch('src.crawl_parallel.save_markdown')  # Mock the save_markdown function
    @patch('src.crawl_parallel.save_metadata')  # Mock the save_metadata function
    async def test_crawl_parallel_success(self, mock_save_metadata, mock_save_markdown, mock_crawler_class):
        # Set up the mock crawler
        mock_crawler_instance = mock_crawler_class.return_value.__aenter__.return_value
        mock_crawler_instance.arun = AsyncMock(return_value={'markdown': '# Sample Markdown Content'})
        
        # Define mock inputs
        urls = ["https://example.com/page1", "https://example.com/page2"]
        output_dir = "/output/directory"  # Adjust accordingly

        # Expected saved file path
        mock_save_markdown.return_value = "/output/directory/page1.md"

        # Run the crawl_parallel function
        await crawl_parallel(urls, max_concurrent=2, output_dir=output_dir)

        # Assertions
        mock_save_markdown.assert_called()  # Ensure save_markdown was called
        mock_save_metadata.assert_called()  # Ensure save_metadata was called

    @patch('src.crawl_parallel.AsyncWebCrawler', new_callable=AsyncMock)
    async def test_crawl_parallel_with_errors(self, mock_crawler_class):
        # Set up the mock crawler to raise an exception during crawling
        mock_crawler_instance = mock_crawler_class.return_value.__aenter__.return_value
        mock_crawler_instance.arun = AsyncMock(side_effect=Exception("Crawl error"))

        urls = ["https://example.com/page1"]
        output_dir = "/output/directory"  # Adjust accordingly

        # Run the crawl_parallel function and catch errors
        await crawl_parallel(urls, max_concurrent=1, output_dir=output_dir)

        # Log error should be verified (you may implement verification depending on logging setup)

# To run the tests
if __name__ == "__main__":
    unittest.main()