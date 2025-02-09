import sys
import os
import unittest
import requests
from unittest.mock import patch

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from url_check import check_url, is_valid_format, exists, clean_url

class TestUrlChecker(unittest.TestCase):

    def test_is_valid_format(self):
        valid_url = "https://example.com"
        invalid_url = "htp://invalid.url"

        self.assertTrue(is_valid_format(valid_url))
        self.assertFalse(is_valid_format(invalid_url))

    @patch('requests.head')  # Mocking the requests.head call
    def test_exists(self, mock_head):
        # Test case for a valid URL
        mock_head.return_value.status_code = 200
        result = exists("https://example.com")
        self.assertTrue(result['exists'])

        # Test case for a 404 URL
        mock_head.return_value.status_code = 404
        result = exists("https://example.com/non-existent")
        self.assertFalse(result['exists'])

        # Test case for a connection error
        mock_head.side_effect = requests.ConnectionError
        result = exists("https://some-bad-url.com")
        self.assertFalse(result['exists'])
        self.assertEqual(result['error'], 'Connection error')


    def test_clean_url_valid_cases(self):
        # Test valid URLs
        valid_url = "https://example.com/path"
        sanitized_url = clean_url(valid_url)
        self.assertEqual(sanitized_url, "https://example.com/path")

        # Test URL with spaces
        url_with_spaces = "https://example.com/path with spaces"
        sanitized_url = clean_url(url_with_spaces)
        self.assertEqual(sanitized_url, "https://example.com/path%20with%20spaces")

    def test_clean_url_invalid_cases(self):
        # Test input that should raise a ValueError due to malicious content
        invalid_url_with_script = "https://example.com/<script>alert('xss')</script>"
        with self.assertRaises(ValueError):
            clean_url(invalid_url_with_script)  # Should raise ValueError for containing script

        # Test input with JavaScript
        invalid_url_js = "javascript:alert('xss')"
        with self.assertRaises(ValueError):
            clean_url(invalid_url_js)  # Should raise ValueError for JavaScript injection

        # Test malformed URL which is wholly invalid
        malformed_url = "htp://not.a.valid.url"
        with self.assertRaises(ValueError):
            clean_url(malformed_url)  # This should also raise a ValueError if is_valid_format fails

    def test_check_url(self):
        with patch('requests.head') as mock_head:
            mock_head.return_value.status_code = 200
            result = check_url("https://example.com")
            self.assertEqual(result['valid'], True)
            self.assertEqual(result['url'], "https://example.com") 

            mock_head.return_value.status_code = 404
            result = check_url("https://example.com/non-existent")
            self.assertEqual(result['valid'], False)
            self.assertIn("does not exist", result['message'])

if __name__ == "__main__":
    unittest.main()