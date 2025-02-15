import os
import sys
import unittest
from unittest.mock import AsyncMock, patch
import logging

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from crawl_one import crawl_one

# Setup logging for tests (optional)
logging.basicConfig(level=logging.DEBUG)

class TestCrawlOne(unittest.TestCase):

    @patch('crawl_one.save_markdown')  # Replace with the actual path
    @patch('crawl_one.save_metadata')  # Replace with the actual path
    @patch('crawl4ai.AsyncWebCrawler')  # Mock the AsyncWebCrawler class
    async def test_crawl_one_successful(self, mock_crawler_class, mock_save_markdown, mock_save_metadata):
        # Set up the mock crawler
        mock_crawler_instance = mock_crawler_class.return_value.__aenter__.return_value
        mock_crawler_instance.arun = AsyncMock(return_value={'markdown': '# Sample Markdown Content'})

        # Mocks for saving methods
        mock_save_markdown.return_value = '/path/to/markdown/file.md'
        mock_save_metadata.return_value = None  # Assuming save_metadata doesn't return anything

        # Call the crawl_one function
        result = await crawl_one("https://example.com", "/output/directory")

        # Assertions
        self.assertEqual(result, '/path/to/markdown/file.md')  # Check if the returned path is correct
        mock_save_markdown.assert_called_once()  # Check if save_markdown was called once
        mock_save_metadata.assert_called_once()  # Check if save_metadata was called once

    @patch('crawl4ai.AsyncWebCrawler')
    async def test_crawl_one_no_markdown(self, mock_crawler_class):
        # Set up the mock crawler to return an empty result
        mock_crawler_instance = mock_crawler_class.return_value.__aenter__.return_value
        mock_crawler_instance.arun = AsyncMock(return_value={})  # No markdown content

        result = await crawl_one("https://example.com", "/output/directory")

        # Assertions
        self.assertIsNone(result)  # Expect None if no markdown content is found

    @patch('crawl4ai.AsyncWebCrawler')
    async def test_crawl_one_error(self, mock_crawler_class):
        # Set up the mock crawler to raise an exception
        mock_crawler_instance = mock_crawler_class.return_value.__aenter__.return_value
        mock_crawler_instance.arun = AsyncMock(side_effect=Exception("Crawl error"))

        result = await crawl_one("https://example.com", "/output/directory")

        # Assertions
        self.assertIsNone(result)  # Expect None if there was an error
        # Optionally, you can check if the logger recorded the error
        # For checking log messages, you could tap on logging.captureWarnings() and validate the output


if __name__ == "__main__":
    unittest.main()
