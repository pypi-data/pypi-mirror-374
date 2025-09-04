"""
Test for Google search feature selectors
Tests google.featured_snippet_title and related selectors
"""

import unittest
from webextractionhelper import extract


class TestGoogleSearchFeatures(unittest.TestCase):
    def setUp(self):
        """Set up test HTML simulating Google search results"""
        self.html_with_featured_snippet = '''
        <html>
        <body>
            <div class="g">
                <div class="xpdopen">
                    <span class="S3Uucc">Featured Snippet Title</span>
                    <span class="e24Kjd">This is the featured snippet text content.</span>
                    <ul class="i8Z77e">
                        <li>First bullet point</li>
                        <li>Second bullet point</li>
                    </ul>
                    <a href="https://example.com/source">Source Link</a>
                </div>
            </div>
            <g-accordion-expander>
                <h3>Related Question 1</h3>
                <span class="e24Kjd">Answer to question 1</span>
            </g-accordion-expander>
            <g-accordion-expander>
                <h3>Related Question 2</h3>
                <span class="e24Kjd">Answer to question 2</span>
            </g-accordion-expander>
        </body>
        </html>
        '''

        self.html_without_features = '''
        <html>
        <body>
            <div>Regular search result without special features</div>
        </body>
        </html>
        '''

    def test_featured_snippet_title_extraction(self):
        """Test extraction of featured snippet title"""
        results = extract('google.featured_snippet_title', self.html_with_featured_snippet)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn('Featured Snippet Title', results)

    def test_featured_snippet_title_no_featured(self):
        """Test extraction when no featured snippet is present"""
        results = extract('google.featured_snippet_title', self.html_without_features)
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)

    def test_featured_snippet_text_extraction(self):
        """Test extraction of featured snippet text"""
        results = extract('google.featured_snippet_text', self.html_with_featured_snippet)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn('This is the featured snippet text content.', results)

    def test_related_questions_extraction(self):
        """Test extraction of related questions"""
        results = extract('google.related_questions_all', self.html_with_featured_snippet)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIn('Related Question 1', results)
        self.assertIn('Related Question 2', results)

    def test_related_questions_no_questions(self):
        """Test extraction when no related questions are present"""
        results = extract('google.related_questions_all', self.html_without_features)
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
