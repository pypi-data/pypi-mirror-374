"""
Test for generic selectors with parameters
Tests generic.elements_by_class and generic.elements_by_id
"""

import unittest
from webextractionhelper import extract


class TestGenericSelectors(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with various elements for generic selectors"""
        self.html_with_elements = '''
        <html>
        <body>
            <div id="header" class="header-class">Header content</div>
            <div class="product-card">Product 1</div>
            <div class="product-card">Product 2</div>
            <div class="product-card">Product 3</div>
            <div id="footer" class="footer-class">Footer content</div>
            <span class="highlight">Highlighted text</span>
            <span class="highlight">Another highlight</span>
        </body>
        </html>
        '''

    def test_elements_by_class_extraction(self):
        """Test extraction of elements by class name"""
        results = extract('generic.elements_by_class', self.html_with_elements, class_name='product-card')
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # Should find all product-card elements
        self.assertGreaterEqual(len(results), 3)
        all_text = ' '.join(results)
        self.assertIn('Product 1', all_text)
        self.assertIn('Product 2', all_text)
        self.assertIn('Product 3', all_text)

    def test_elements_by_class_no_matches(self):
        """Test extraction when no elements match the class"""
        results = extract('generic.elements_by_class', self.html_with_elements, class_name='nonexistent')
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)

    def test_elements_by_id_extraction(self):
        """Test extraction of element by ID"""
        results = extract('generic.elements_by_id', self.html_with_elements, id_value='header')
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # Should find the header element
        self.assertIn('Header content', results)

    def test_elements_by_id_no_matches(self):
        """Test extraction when no element matches the ID"""
        results = extract('generic.elements_by_id', self.html_with_elements, id_value='nonexistent')
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)

    def test_elements_by_attribute_extraction(self):
        """Test extraction of elements by attribute"""
        results = extract('generic.elements_by_attribute',
                         self.html_with_elements,
                         attribute_name='id',
                         attribute_value='footer')
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        # Should find the footer element
        self.assertIn('Footer content', results)


if __name__ == '__main__':
    unittest.main()
