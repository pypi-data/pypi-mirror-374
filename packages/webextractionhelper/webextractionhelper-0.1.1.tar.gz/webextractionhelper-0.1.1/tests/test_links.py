"""
Test for link selectors
Tests links.all and links.to_domain
"""

import unittest
from webextractionhelper import extract


class TestLinks(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with various links"""
        self.html_with_links = '''
        <html>
        <body>
            <a href="https://example.com/page1">Link 1</a>
            <a href="https://google.com/search">Link 2</a>
            <a href="/internal/page">Internal Link</a>
            <a href="mailto:test@example.com">Email Link</a>
            <div>
                <a href="https://example.com/page2">Another Example Link</a>
            </div>
        </body>
        </html>
        '''

        self.html_without_links = '''
        <html>
        <body>
            <div>No links here</div>
            <p>Just text content</p>
        </body>
        </html>
        '''

    def test_all_links_extraction(self):
        """Test extraction of all links"""
        results = extract('links.all', self.html_with_links)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # Should find all link href attributes
        self.assertEqual(len(results), 5)  # 5 links total
        results_str = ' '.join(results)
        self.assertIn('https://example.com/page1', results_str)
        self.assertIn('https://google.com/search', results_str)
        self.assertIn('/internal/page', results_str)
        self.assertIn('mailto:test@example.com', results_str)
        self.assertIn('https://example.com/page2', results_str)

    def test_all_links_extraction_no_links(self):
        """Test extraction when no links are present"""
        results = extract('links.all', self.html_without_links)
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)






if __name__ == '__main__':
    unittest.main()
