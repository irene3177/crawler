import asyncio
import unittest
from unittest.mock import patch, AsyncMock
import logging
from src.scrap_static import fetch_links, scrap_website, get_domain, is_page_url  # Adjust import based on your structure

# Setup logging for tests (optional)
logging.basicConfig(level=logging.DEBUG)

class TestSitemapParser(unittest.TestCase):

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)  # Mock the GET request
    async def test_fetch_links(self, mock_get):
        # Simulated HTML response content
        html_content = """
        <html>
            <body>
                <a href="https://example.com/page1">Page 1</a>
                <a href="https://example.com/page2">Page 2</a>
                <a href="https://example.com/image.jpg">Image</a>
            </body>
        </html>
        """
        # Set up the mock response
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value=html_content)
        mock_get.return_value.__aenter__.return_value.status = 200

        async with aiohttp.ClientSession() as session:
            links = await fetch_links(session, "https://example.com")

        # Check the URLs fetched
        expected_links = {
            'https://example.com/page1',
            'https://example.com/page2',
        }
        self.assertEqual(links, expected_links)  # Ensure it doesn't include non-page URLs

    def test_get_domain(self):
        url = "https://example.com/some/path"
        expected_domain = "example.com"
        self.assertEqual(get_domain(url), expected_domain)

    def test_is_page_url(self):
        # URLs that should be considered page URLs
        self.assertTrue(is_page_url("https://example.com/public/page"))
        self.assertTrue(is_page_url("https://example.com/path.html"))
        
        # URLs that should not be considered page URLs
        self.assertFalse(is_page_url("https://example.com/private/page.jpg"))
        self.assertFalse(is_page_url("https://example.com/static/resource.zip"))

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)  # Mock the GET request
    async def test_scrap_website(self, mock_get):
        # Mock the initial URL fetching
        mock_html_content = """
        <html>
            <body>
                <a href="https://example.com/public/page1">Page 1</a>
                <a href="https://example.com/private/page">Private Page</a>
            </body>
        </html>
        """
        # Set up the mock response
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value=mock_html_content)
        mock_get.return_value.__aenter__.return_value.status = 200

        # Proceed to test scraping
        visited_urls = await scrap_website("https://example.com", max_depth=1)

        expected_visited_urls = {"https://example.com/public/page1"}
        self.assertEqual(visited_urls, expected_visited_urls)

if __name__ == "__main__":
    unittest.main()