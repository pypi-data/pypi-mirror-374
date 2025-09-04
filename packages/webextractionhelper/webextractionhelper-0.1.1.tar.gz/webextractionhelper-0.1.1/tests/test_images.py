"""
Test for image selectors
Tests images.all, images.with_alt, images.without_alt
"""

import unittest
from webextractionhelper import extract


class TestImages(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with various images"""
        self.html_with_images = '''
        <html>
        <body>
            <img src="https://example.com/image1.jpg" alt="Image 1 description">
            <img src="https://example.com/image2.png">
            <img src="/local/image3.gif" alt="Local image">
            <div>
                <img src="https://cdn.example.com/image4.jpg" alt="CDN image">
            </div>
        </body>
        </html>
        '''

        self.html_without_images = '''
        <html>
        <body>
            <div>No images here</div>
            <p>Just text content</p>
        </body>
        </html>
        '''

    def test_all_images_extraction(self):
        """Test extraction of all images"""
        results = extract('images.all', self.html_with_images)
        self.assertIsInstance(results, list)
        # Should find all images and return their src attributes
        self.assertGreater(len(results), 0)
        self.assertEqual(len(results), 4)  # 4 img elements
        # Should contain src URLs
        results_str = ' '.join(results)
        self.assertIn('https://example.com/image1.jpg', results_str)
        self.assertIn('https://example.com/image2.png', results_str)
        self.assertIn('/local/image3.gif', results_str)
        self.assertIn('https://cdn.example.com/image4.jpg', results_str)

    def test_all_images_extraction_no_images(self):
        """Test extraction when no images are present"""
        results = extract('images.all', self.html_without_images)
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)

    def test_images_with_alt_extraction(self):
        """Test extraction of images that have alt text"""
        results = extract('images.with_alt', self.html_with_images)
        self.assertIsInstance(results, list)
        # Should find images with alt text and return their src attributes
        self.assertGreater(len(results), 0)
        self.assertEqual(len(results), 3)  # 3 images have alt text
        results_str = ' '.join(results)
        self.assertIn('https://example.com/image1.jpg', results_str)
        self.assertIn('/local/image3.gif', results_str)
        self.assertIn('https://cdn.example.com/image4.jpg', results_str)

    def test_images_without_alt_extraction(self):
        """Test extraction of images that don't have alt text"""
        results = extract('images.without_alt', self.html_with_images)
        self.assertIsInstance(results, list)
        # Should find images without alt text and return their src attributes
        self.assertEqual(len(results), 1)  # 1 image without alt text
        self.assertIn('https://example.com/image2.png', results)


if __name__ == '__main__':
    unittest.main()
