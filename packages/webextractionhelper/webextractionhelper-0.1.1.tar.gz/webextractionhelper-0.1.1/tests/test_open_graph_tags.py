"""
Test for Open Graph meta tag selectors
Tests og.title and og.description
"""

import unittest
from webextractionhelper import extract


class TestOpenGraphTags(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with Open Graph meta tags"""
        self.html_with_og = '''
        <html>
        <head>
            <title>Test Page</title>
            <meta property="og:title" content="Open Graph Title" />
            <meta property="og:description" content="Open Graph description for social sharing" />
            <meta property="og:image" content="https://example.com/image.jpg" />
            <meta property="og:url" content="https://example.com/page" />
            <meta property="og:type" content="website" />
        </head>
        <body>
            <h1>Test Heading</h1>
            <p>Test content</p>
        </body>
        </html>
        '''

        self.html_without_og = '''
        <html>
        <head>
            <title>No OG Page</title>
        </head>
        <body>
            <div>No Open Graph tags here</div>
        </body>
        </html>
        '''

    def test_og_title_extraction(self):
        """Test extraction of Open Graph title"""
        results = extract('og.title', self.html_with_og)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn('Open Graph Title', results)

    def test_og_title_extraction_no_og(self):
        """Test extraction when no OG title is present"""
        results = extract('og.title', self.html_without_og)
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)

    def test_og_description_extraction(self):
        """Test extraction of Open Graph description"""
        results = extract('og.description', self.html_with_og)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn('Open Graph description for social sharing', results)

    def test_og_description_extraction_no_og(self):
        """Test extraction when no OG description is present"""
        results = extract('og.description', self.html_without_og)
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
