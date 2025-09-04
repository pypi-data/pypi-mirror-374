"""
Test for structured_data.json_ld selector
Tests both xpath and regex methods
"""

import unittest
from webextractionhelper import extract


class TestStructuredDataJsonLd(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with JSON-LD structured data"""
        self.html_with_json_ld = '''
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "Test Product",
                "description": "A test product description"
            }
            </script>
        </head>
        <body>
            <div>Some content</div>
        </body>
        </html>
        '''

        self.html_without_json_ld = '''
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div>No JSON-LD here</div>
        </body>
        </html>
        '''

    def test_xpath_extraction_with_json_ld(self):
        """Test xpath extraction of JSON-LD structured data"""
        results = extract('structured_data.json_ld', self.html_with_json_ld, method='xpath')
        self.assertIsInstance(results, list)
        # Should find the script element
        self.assertGreater(len(results), 0)

    def test_xpath_extraction_without_json_ld(self):
        """Test xpath extraction when no JSON-LD is present"""
        results = extract('structured_data.json_ld', self.html_without_json_ld, method='xpath')
        self.assertIsInstance(results, list)
        # Should be empty or not find anything
        self.assertEqual(len(results), 0)

    def test_regex_extraction_with_json_ld(self):
        """Test regex extraction of JSON-LD structured data"""
        results = extract('structured_data.json_ld', self.html_with_json_ld, method='regex')
        self.assertIsInstance(results, list)
        # Should find the JSON content
        self.assertGreater(len(results), 0)
        # Should contain the product name
        content = ' '.join(results)
        self.assertIn('Test Product', content)

    def test_regex_extraction_without_json_ld(self):
        """Test regex extraction when no JSON-LD is present"""
        results = extract('structured_data.json_ld', self.html_without_json_ld, method='regex')
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
