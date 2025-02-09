import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import logging

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from robots_parser import fetch_robots_txt, parse_robots_txt, is_url_allowed, filter_allowed_urls

# Setup logging for tests
logging.basicConfig(level=logging.DEBUG)

class TestUrlChecker(unittest.TestCase):

    @patch('robots_parser.requests.get')  # Mock requests.get to prevent actual HTTP calls
    def test_fetch_robots_txt(self, mock_get):
        # Simulate the response content for a robots.txt file
        mock_response_content = """
        User-agent: *
        Disallow: /private
        Allow: /public
        Sitemap: https://example.com/sitemap.xml
        """

        # Set up the mock to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_response_content
        mock_get.return_value = mock_response

        # Test the function
        url = "https://example.com"
        robots_rules = fetch_robots_txt(url)

        expected_rules = {
            'allow': ['/public'],
            'disallow': ['/private'],
            'sitemap': ['https://example.com/sitemap.xml']
        }

        self.assertEqual(robots_rules, expected_rules)

    def test_parse_robots_txt(self):
        # Test content of robots.txt
        robots_txt_content = """
        User-agent: *
        Disallow: /private
        Allow: /public
        Sitemap: https://example.com/sitemap.xml
        """

        expected_rules = {
            'allow': ['/public'],
            'disallow': ['/private'],
            'sitemap': ['https://example.com/sitemap.xml']
        }

        parsed_rules = parse_robots_txt(robots_txt_content)
        self.assertEqual(parsed_rules, expected_rules)

    def test_is_url_allowed(self):
        robots_rules = {
            'allow': ['/public'],
            'disallow': ['/private']
        }

        # Test a URL that should be allowed
        self.assertTrue(is_url_allowed("https://example.com/public/page", robots_rules))

        # Test a URL that should be disallowed
        self.assertFalse(is_url_allowed("https://example.com/private/page", robots_rules))

        # Test a URL with no matching rules (default to allow)
        self.assertTrue(is_url_allowed("https://example.com/other/page", robots_rules))

    def test_filter_allowed_urls(self):
        robots_rules = {
            'allow': ['/public'],
            'disallow': ['/private']
        }
        
        # List of URLs to filter
        urls = [
            "https://example.com/public/page",
            "https://example.com/private/page",
            "https://example.com/another/page"
        ]

        allowed_urls = filter_allowed_urls(urls, robots_rules)
        expected_allowed_urls = ["https://example.com/public/page", "https://example.com/another/page"]

        self.assertEqual(allowed_urls, expected_allowed_urls)

if __name__ == "__main__":
    unittest.main()