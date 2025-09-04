"""
Test for heading selectors
Tests headings.h1, headings.h2, headings.all
"""

import unittest
from webextractionhelper import extract


class TestHeadings(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with various headings"""
        self.html_with_headings = '''
        <html>
        <body>
            <h1>Main Heading 1</h1>
            <p>Some content</p>
            <h2>Sub Heading 2.1</h2>
            <p>More content</p>
            <h2>Sub Heading 2.2</h2>
            <h3>Sub Sub Heading 3</h3>
            <h4>Heading Level 4</h4>
        </body>
        </html>
        '''

        self.html_without_headings = '''
        <html>
        <body>
            <div>Content without headings</div>
            <p>Just paragraphs</p>
        </body>
        </html>
        '''

    def test_h1_extraction(self):
        """Test extraction of H1 headings"""
        results = extract('headings.h1', self.html_with_headings)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn('Main Heading 1', results)

    def test_h1_extraction_no_h1(self):
        """Test H1 extraction when no H1 is present"""
        results = extract('headings.h1', self.html_without_headings)
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)

    def test_h2_extraction(self):
        """Test extraction of H2 headings"""
        results = extract('headings.h2', self.html_with_headings)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn('Sub Heading 2.1', results)
        self.assertIn('Sub Heading 2.2', results)

    def test_h2_extraction_no_h2(self):
        """Test H2 extraction when no H2 is present"""
        results = extract('headings.h2', self.html_without_headings)
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)

    def test_all_headings_extraction(self):
        """Test extraction of all headings"""
        results = extract('headings.all', self.html_with_headings)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # Should contain all heading levels
        all_headings = ' '.join(results)
        self.assertIn('Main Heading 1', all_headings)
        self.assertIn('Sub Heading 2.1', all_headings)
        self.assertIn('Sub Sub Heading 3', all_headings)


if __name__ == '__main__':
    unittest.main()
