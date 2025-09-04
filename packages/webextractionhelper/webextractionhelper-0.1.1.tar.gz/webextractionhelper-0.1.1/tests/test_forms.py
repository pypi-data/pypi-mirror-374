"""
Test for form selectors
Tests forms.all and forms.inputs
"""

import unittest
from webextractionhelper import extract


class TestForms(unittest.TestCase):
    def setUp(self):
        """Set up test HTML with forms and inputs"""
        self.html_with_forms = '''
        <html>
        <body>
            <form action="/submit" method="post">
                <input type="text" name="username" placeholder="Username">
                <input type="password" name="password" placeholder="Password">
                <input type="email" name="email" placeholder="Email">
                <input type="submit" value="Submit">
                <button type="submit">Login</button>
            </form>
            <form action="/search" method="get">
                <input type="text" name="query" placeholder="Search...">
                <input type="submit" value="Search">
            </form>
        </body>
        </html>
        '''

        self.html_without_forms = '''
        <html>
        <body>
            <div>No forms here</div>
            <p>Just regular content</p>
        </body>
        </html>
        '''



    def test_inputs_extraction(self):
        """Test extraction of all input elements"""
        results = extract('forms.inputs', self.html_with_forms)
        self.assertIsInstance(results, list)
        # Should find all input elements with their values/placeholders
        self.assertGreater(len(results), 0)
        # Check specific inputs
        results_str = ' '.join(results)
        self.assertIn('Username', results_str)  # placeholder
        self.assertIn('Password', results_str)  # placeholder
        self.assertIn('Email', results_str)     # placeholder
        self.assertIn('Submit', results_str)    # value

    def test_text_inputs_extraction(self):
        """Test extraction of text input elements"""
        results = extract('forms.text_inputs', self.html_with_forms)
        self.assertIsInstance(results, list)
        # Should find ONLY text inputs with type="text" (username and query)
        # Email input has type="email" so should NOT be captured
        self.assertEqual(len(results), 2)  # username and query inputs
        results_str = ' '.join(results)
        self.assertIn('Username', results_str)
        self.assertNotIn('Email', results_str)  # Email input is type="email", not "text"
        self.assertIn('Search', results_str)  # placeholder from second form




if __name__ == '__main__':
    unittest.main()
