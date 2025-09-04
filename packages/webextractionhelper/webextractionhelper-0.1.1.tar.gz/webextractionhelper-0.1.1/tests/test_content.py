"""
Test for content selectors
Tests content.paragraphs and content.lists
"""

import unittest
from webextractionhelper import extract


class TestContent(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with various content elements"""
        self.html_with_content = '''
        <html>
        <body>
            <p>First paragraph with some text.</p>
            <p>Second paragraph with different content.</p>
            <div>Some div content</div>
            <ul>
                <li>List item 1</li>
                <li>List item 2</li>
                <li>List item 3</li>
            </ul>
            <ol>
                <li>Ordered item 1</li>
                <li>Ordered item 2</li>
            </ol>
            <table>
                <tr><td>Cell 1</td><td>Cell 2</td></tr>
                <tr><td>Cell 3</td><td>Cell 4</td></tr>
            </table>
        </body>
        </html>
        '''

        self.html_without_content = '''
        <html>
        <body>
            <div>No paragraphs or lists here</div>
        </body>
        </html>
        '''

    def test_paragraphs_extraction(self):
        """Test extraction of paragraphs"""
        results = extract('content.paragraphs', self.html_with_content)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # Should contain both paragraphs
        all_text = ' '.join(results)
        self.assertIn('First paragraph', all_text)
        self.assertIn('Second paragraph', all_text)

    def test_paragraphs_extraction_no_paragraphs(self):
        """Test extraction when no paragraphs are present"""
        results = extract('content.paragraphs', self.html_without_content)
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)

    def test_lists_extraction(self):
        """Test extraction of lists"""
        results = extract('content.lists', self.html_with_content)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # Should find both ul and ol elements with their list items
        self.assertEqual(len(results), 2)  # One ul and one ol
        # Check that list items are properly extracted
        ul_result = results[0]
        ol_result = results[1]
        self.assertIn('List item 1', ul_result)
        self.assertIn('List item 2', ul_result)
        self.assertIn('List item 3', ul_result)
        self.assertIn('Ordered item 1', ol_result)
        self.assertIn('Ordered item 2', ol_result)

    def test_list_items_extraction(self):
        """Test extraction of list items"""
        results = extract('content.list_items', self.html_with_content)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # Should find all li elements
        all_text = ' '.join(results)
        self.assertIn('List item 1', all_text)
        self.assertIn('List item 2', all_text)
        self.assertIn('Ordered item 1', all_text)


if __name__ == '__main__':
    unittest.main()
