"""
Test for analytics.google_analytics_id selector
Tests both xpath and regex methods
"""

import unittest
from webextractionhelper import extract


class TestAnalyticsGoogleAnalyticsId(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with Google Analytics tracking code"""
        self.html_with_ga = '''
        <html>
        <head>
            <script>
            (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
            (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
            m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
            })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

            ga('create', 'UA-123456789-1', 'auto');
            ga('send', 'pageview');
            </script>
        </head>
        <body>
            <div>Page content</div>
        </body>
        </html>
        '''

        self.html_without_ga = '''
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div>No analytics here</div>
        </body>
        </html>
        '''

    def test_xpath_extraction_with_ga(self):
        """Test xpath extraction of Google Analytics script"""
        results = extract('analytics.google_analytics_id', self.html_with_ga, method='xpath')
        self.assertIsInstance(results, list)
        # Should find the script element containing UA-
        self.assertGreater(len(results), 0)

    def test_xpath_extraction_without_ga(self):
        """Test xpath extraction when no GA is present"""
        results = extract('analytics.google_analytics_id', self.html_without_ga, method='xpath')
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)

    def test_regex_extraction_with_ga(self):
        """Test regex extraction of Google Analytics UA ID"""
        results = extract('analytics.google_analytics_id', self.html_with_ga, method='regex')
        self.assertIsInstance(results, list)
        # Should find the UA ID
        self.assertGreater(len(results), 0)
        # Should contain the UA ID
        ua_ids = [r for r in results if r.startswith('UA-')]
        self.assertGreater(len(ua_ids), 0)
        self.assertIn('UA-123456789-1', ua_ids)

    def test_regex_extraction_without_ga(self):
        """Test regex extraction when no GA is present"""
        results = extract('analytics.google_analytics_id', self.html_without_ga, method='regex')
        self.assertIsInstance(results, list)
        # Should be empty
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
