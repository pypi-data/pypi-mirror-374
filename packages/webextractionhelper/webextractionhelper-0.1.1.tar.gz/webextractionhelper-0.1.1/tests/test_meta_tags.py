"""
Test for meta tag selectors
Tests meta.title and meta.description
"""

import unittest
from webextractionhelper import extract


class TestMetaTags(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with meta tags"""
        self.html_with_meta = '''
        <html>
        <head>
            <title>Test Page Title</title>
            <meta name="description" content="This is a test page description for SEO">
            <meta name="keywords" content="test, page, seo">
        </head>
        <body>
            <h1>Test Heading</h1>
            <p>Test content</p>
        </body>
        </html>
        '''

        self.html_without_meta = '''
        <html>
        <head>
            <title>No Meta Page</title>
        </head>
        <body>
            <div>No meta tags here</div>
        </body>
        </html>
        '''

    def test_meta_title_extraction(self):
        """Test extraction of page title"""
        results = extract('meta.title', self.html_with_meta)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn('Test Page Title', results)

    def test_meta_title_extraction_no_title(self):
        """Test extraction when no title is present"""
        results = extract('meta.title', self.html_without_meta)
        self.assertIsInstance(results, list)
        # Should still find the title tag
        self.assertGreater(len(results), 0)

    def test_meta_description_extraction(self):
        """Test extraction of meta description"""
        results = extract('meta.description', self.html_with_meta)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn('This is a test page description for SEO', results)

    def test_meta_description_extraction_no_description(self):
        """Test extraction when no meta description is present"""
        results = extract('meta.description', self.html_without_meta)
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
