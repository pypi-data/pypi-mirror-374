"""
Test for analytics.google_tag_manager_id selector
Tests both xpath and regex methods
"""

import unittest
from webextractionhelper import extract


class TestAnalyticsGoogleTagManagerId(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with Google Tag Manager code"""
        self.html_with_gtm = '''
        <html>
        <head>
            <script>
            (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
            new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
            j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
            'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
            })(window,document,'script','dataLayer','GTM-ABCDEFGH');
            </script>
        </head>
        <body>
            <div>Page content</div>
        </body>
        </html>
        '''

        self.html_without_gtm = '''
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div>No GTM here</div>
        </body>
        </html>
        '''

    def test_xpath_extraction_with_gtm(self):
        """Test xpath extraction of Google Tag Manager script"""
        results = extract('analytics.google_tag_manager_id', self.html_with_gtm, method='xpath')
        self.assertIsInstance(results, list)
        # Should find the script element containing GTM-
        self.assertGreater(len(results), 0)

    def test_xpath_extraction_without_gtm(self):
        """Test xpath extraction when no GTM is present"""
        results = extract('analytics.google_tag_manager_id', self.html_without_gtm, method='xpath')
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)

    def test_regex_extraction_with_gtm(self):
        """Test regex extraction of Google Tag Manager GTM ID"""
        results = extract('analytics.google_tag_manager_id', self.html_with_gtm, method='regex')
        self.assertIsInstance(results, list)
        # Should find the GTM ID
        self.assertGreater(len(results), 0)
        # Should contain the GTM ID
        gtm_ids = [r for r in results if r.startswith('GTM-')]
        self.assertGreater(len(gtm_ids), 0)
        self.assertIn('GTM-ABCDEFGH', gtm_ids)

    def test_regex_extraction_without_gtm(self):
        """Test regex extraction when no GTM is present"""
        results = extract('analytics.google_tag_manager_id', self.html_without_gtm, method='regex')
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
