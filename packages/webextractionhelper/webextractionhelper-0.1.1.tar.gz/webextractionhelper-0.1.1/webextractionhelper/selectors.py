"""
Google Search XPath Selectors Helper
Extracted from: https://www.screamingfrog.co.uk/blog/how-to-scrape-google-search-features-using-xpath/

This module provides XPath selectors for extracting various Google search features
including featured snippets, related questions, and other SERP elements.
"""

from typing import Dict, Any, List, Optional
from lxml import html, etree
import re

class Selectors:
    """Unified Selectors for web scraping using XPath, Regex, and CSS."""

    def __init__(self):
        self.selectors = {
            # Featured Snippets
            'google.featured_snippet_title': {
                'explanation': 'Featured snippet page title (Text) - extracts the main title of the featured snippet',
                'xpath': '(//span[@class="S3Uucc"])[1]'
            },
            'google.featured_snippet_text': {
                'explanation': 'Featured snippet text paragraph (Text) - extracts the main description text',
                'xpath': '(//span[@class="e24Kjd"])[1]'
            },
            'google.featured_snippet_bullet_points': {
                'explanation': 'Featured snippet bullet point text (Text) - extracts all bullet points from unordered lists',
                'xpath': '//ul[@class="i8Z77e"]/li'
            },
            'google.featured_snippet_numbered_list': {
                'explanation': 'Featured snippet numbered list (Text) - extracts all items from ordered lists',
                'xpath': '//ol[@class="X5LH0c"]/li'
            },
            'google.featured_snippet_table': {
                'explanation': 'Featured snippet table (Text) - extracts all table rows',
                'xpath': '//table//tr'
            },
            'google.featured_snippet_url': {
                'explanation': 'Featured snippet URL (Inner HTML) - extracts the source URL of the featured snippet',
                'xpath': '(//div[@class="xpdopen"]//a/@href)[2]'
            },
            'google.featured_snippet_image': {
                'explanation': 'Featured snippet image source (Text) - extracts the title/alt text of featured snippet images',
                'xpath': '(//img[@id="dimg_7"]//@title)'
            },

            # Related Questions (People Also Ask)
            'google.related_question_1': {
                'explanation': 'Related question 1 text (Text) - extracts the first "People also ask" question',
                'xpath': '(//g-accordion-expander//h3)[1]'
            },
            'google.related_question_2': {
                'explanation': 'Related question 2 text (Text) - extracts the second "People also ask" question',
                'xpath': '(//g-accordion-expander//h3)[2]'
            },
            'google.related_question_3': {
                'explanation': 'Related question 3 text (Text) - extracts the third "People also ask" question',
                'xpath': '(//g-accordion-expander//h3)[3]'
            },
            'google.related_question_4': {
                'explanation': 'Related question 4 text (Text) - extracts the fourth "People also ask" question',
                'xpath': '(//g-accordion-expander//h3)[4]'
            },
            'google.related_questions_all': {
                'explanation': 'All related question texts (Text) - extracts all "People also ask" questions',
                'xpath': '//g-accordion-expander//h3'
            },
            'google.related_question_snippets': {
                'explanation': 'Related question snippet text for all questions (Text) - extracts answer snippets',
                'xpath': '//g-accordion-expander//span[@class="e24Kjd"]'
            },
            'google.related_question_titles': {
                'explanation': 'Related question page titles for all questions (Text) - extracts source page titles',
                'xpath': '//g-accordion-expander//h3'
            },
            'google.related_question_urls': {
                'explanation': 'Related question page URLs for all questions (Inner HTML) - extracts source URLs',
                'xpath': '//g-accordion-expander//div[@class="r"]//a/@href'
            },

            # Alternative/Updated Selectors from Comments
            'google.related_questions_alternative': {
                'explanation': 'Alternative selector for related questions (working as of August 2021) - extracts question containers',
                'xpath': '//div[@class="iDjcJe IX9Lgd wwB5gf"]'
            },
            'google.related_questions_aria': {
                'explanation': 'Alternative selector using aria-expanded attribute - extracts all question answers',
                'xpath': '//*[@aria-expanded]/div[2]/span'
            },

            # General Search Results
            'google.search_results_containers': {
                'explanation': 'Main search result containers - extracts the primary search result divs',
                'xpath': '//div[@class="g"]'
            },
            'google.search_result_links': {
                'explanation': 'Search result links - extracts all href attributes from search results',
                'xpath': '//div[@class="g"]//a[@href]'
            },
            'google.search_result_titles': {
                'explanation': 'Search result titles - extracts all h3 titles from search results',
                'xpath': '//div[@class="g"]//h3'
            },
            'google.search_result_snippets': {
                'explanation': 'Search result snippets - extracts the description text below titles',
                'xpath': '//div[@class="g"]//span[@class="st"]'
            },

            # Generic Web Scraping Selectors
            # Meta Tags
            'meta.title': {
                'explanation': 'Page title from title tag',
                'xpath': '//title'
            },
            'meta.description': {
                'explanation': 'Meta description content',
                'xpath': '//meta[@name="description"]/@content'
            },
            'meta.keywords': {
                'explanation': 'Meta keywords content',
                'xpath': '//meta[@name="keywords"]/@content'
            },
            'meta.viewport': {
                'explanation': 'Viewport meta tag content',
                'xpath': '//meta[@name="viewport"]/@content'
            },
            'meta.news_keywords': {
                'explanation': 'News keywords meta tag content',
                'xpath': '//meta[@name="news_keywords"]/@content'
            },

            # Open Graph (og:) Meta Tags
            'og.title': {
                'explanation': 'Open Graph title',
                'xpath': '//meta[@property="og:title"]/@content'
            },
            'og.description': {
                'explanation': 'Open Graph description',
                'xpath': '//meta[@property="og:description"]/@content'
            },
            'og.image': {
                'explanation': 'Open Graph image URL',
                'xpath': '//meta[@property="og:image"]/@content'
            },
            'og.url': {
                'explanation': 'Open Graph canonical URL',
                'xpath': '//meta[@property="og:url"]/@content'
            },
            'og.type': {
                'explanation': 'Open Graph content type',
                'xpath': '//meta[@property="og:type"]/@content'
            },
            'og.site_name': {
                'explanation': 'Open Graph site name',
                'xpath': '//meta[@property="og:site_name"]/@content'
            },

            # Twitter (x:) Meta Tags
            'x.card': {
                'explanation': 'Twitter card type',
                'xpath': '//meta[@name="twitter:card"]/@content'
            },
            'x.title': {
                'explanation': 'Twitter title',
                'xpath': '//meta[@name="twitter:title"]/@content'
            },
            'x.description': {
                'explanation': 'Twitter description',
                'xpath': '//meta[@name="twitter:description"]/@content'
            },
            'x.image': {
                'explanation': 'Twitter image URL',
                'xpath': '//meta[@name="twitter:image"]/@content'
            },
            'x.creator': {
                'explanation': 'Twitter creator handle',
                'xpath': '//meta[@name="twitter:creator"]/@content'
            },
            'x.site': {
                'explanation': 'Twitter site handle',
                'xpath': '//meta[@name="twitter:site"]/@content'
            },

            # Structured Data
            'structured_data.json_ld': {
                'explanation': 'JSON-LD structured data scripts',
                'xpath': '//script[@type="application/ld+json"]',
                'regex': r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>'
            },
            'structured_data.microdata': {
                'explanation': 'Microdata structured data elements',
                'xpath': '//*[@itemtype]'
            },
            'structured_data.product': {
                'explanation': 'Product name from JSON-LD structured data',
                'regex': r'"product":\s*"(.*?)"'
            },
            'structured_data.rating': {
                'explanation': 'Rating value from JSON-LD structured data',
                'regex': r'"ratingValue":\s*"(.*?)"'
            },
            'structured_data.review_count': {
                'explanation': 'Review count from JSON-LD structured data',
                'regex': r'"reviewCount":\s*"(.*?)"'
            },

            # Links and Navigation
            'links.all': {
                'explanation': 'All links - returns href attributes',
                'xpath': '//a[@href]',
                'extract': 'attribute',
                'attribute': 'href'
            },
            'links.external': {
                'explanation': 'External links (not from same domain) - returns href attributes',
                'xpath': '//a[not(contains(@href, "//" + substring-after(//meta[@property="og:url"]/@content, "://")))]',
                'extract': 'attribute',
                'attribute': 'href'
            },
            'links.internal': {
                'explanation': 'Internal links (same domain) - returns href attributes',
                'xpath': '//a[contains(@href, "//" + substring-after(//meta[@property="og:url"]/@content, "://"))]',
                'extract': 'attribute',
                'attribute': 'href'
            },
            'links.images': {
                'explanation': 'Links containing images - returns href attributes',
                'xpath': '//a[img]',
                'extract': 'attribute',
                'attribute': 'href'
            },
            'links.containing_text': {
                'explanation': 'Links containing specific text (case sensitive) - requires text_content parameter',
                'xpath': '//a[contains(., "{text_content}")]/@href'
            },
            'links.containing_text_insensitive': {
                'explanation': 'Links containing specific text (case insensitive) - requires text_content parameter',
                'xpath': '//a[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{text_content}")]/@href'
            },


            # Images
            'images.all': {
                'explanation': 'All images - returns src URLs',
                'xpath': '//img',
                'extract': 'attribute',
                'attribute': 'src'
            },
            'images.with_alt': {
                'explanation': 'Images with alt text - returns src URLs',
                'xpath': '//img[@alt]',
                'extract': 'attribute',
                'attribute': 'src'
            },
            'images.without_alt': {
                'explanation': 'Images without alt text - returns src URLs',
                'xpath': '//img[not(@alt)]',
                'extract': 'attribute',
                'attribute': 'src'
            },
            'images.src': {
                'explanation': 'Image source URLs',
                'xpath': '//img/@src'
            },
            'images.alt': {
                'explanation': 'Image alt text attributes',
                'xpath': '//img/@alt'
            },

            # Headings
            'headings.all': {
                'explanation': 'All heading elements',
                'xpath': '//h1 | //h2 | //h3 | //h4 | //h5 | //h6'
            },
            'headings.h1': {
                'explanation': 'H1 headings',
                'xpath': '//h1'
            },
            'headings.h2': {
                'explanation': 'H2 headings',
                'xpath': '//h2'
            },
            'headings.h3': {
                'explanation': 'H3 headings',
                'xpath': '//h3'
            },

            # Content
            'content.paragraphs': {
                'explanation': 'All paragraph elements',
                'xpath': '//p',
                'extract': 'text'
            },
            'content.lists': {
                'explanation': 'All list elements (ordered and unordered) - extracts list items',
                'xpath': '//ul | //ol',
                'extract': 'list_items'
            },
            'content.list_items': {
                'explanation': 'All list item elements',
                'xpath': '//li',
                'extract': 'text'
            },
            'content.tables': {
                'explanation': 'All table elements',
                'xpath': '//table'
            },
            'content.table_rows': {
                'explanation': 'All table rows',
                'xpath': '//table//tr'
            },
            'content.table_cells': {
                'explanation': 'All table cells (data and header)',
                'xpath': '//table//td | //table//th'
            },

            # Forms
            'forms.inputs': {
                'explanation': 'All input elements - returns placeholder/value/name',
                'xpath': '//input',
                'extract': 'attribute',
                'attribute': 'placeholder'  # Will fallback to value, then name, then type
            },
            'forms.text_inputs': {
                'explanation': 'Text input elements - returns placeholder/value',
                'xpath': '//input[@type="text"]',
                'extract': 'attribute',
                'attribute': 'placeholder'  # Will fallback to value, then name
            },

            # Media
            'media.videos': {
                'explanation': 'All video elements',
                'xpath': '//video'
            },
            'media.iframes': {
                'explanation': 'All iframe source URLs',
                'xpath': '//iframe/@src'
            },
            'media.youtube_iframes': {
                'explanation': 'YouTube embedded iframes',
                'xpath': '//iframe[contains(@src, "www.youtube.com/embed/")]'
            },
            'media.exclude_gtm': {
                'explanation': 'Iframes excluding Google Tag Manager',
                'xpath': '//iframe[not(contains(@src, "https://www.googletagmanager.com/"))]/@src'
            },
            'media.first_iframe': {
                'explanation': 'First iframe source URL',
                'xpath': '(//iframe/@src)[1]'
            },

            # AMP and Mobile
            'amp.url': {
                'explanation': 'AMP version URL',
                'xpath': '//head/link[@rel="amphtml"]/@href'
            },

            # Analytics and Tracking
            'analytics.google_analytics_id': {
                'explanation': 'Google Analytics UA tracking ID',
                'xpath': '//script[contains(text(), "UA-")]',
                'regex': r'["\'](UA-.*?)["\']'
            },
            'analytics.google_tag_manager_id': {
                'explanation': 'Google Tag Manager GTM ID',
                'xpath': '//script[contains(text(), "GTM-")]',
                'regex': r'["\'](GTM-.*?)["\']'
            },
             'analytics.google_analytics_ga4': {
                'explanation': 'Google Analytics 4 measurement ID',
                'regex': r'["\'](G-[A-Z0-9]{10})["\']'
            },

            # Specific Content Areas
            'content.blog_posts': {
                'explanation': 'Blog post links within specific container class - requires class_name parameter',
                'xpath': '//div[@class="{class_name}"]//a'
            },
            'content.blog_titles': {
                'explanation': 'Blog titles within specific container class - requires class_name parameter',
                'xpath': '//div[contains(@class, "{class_name}")]//h3'
            },
            'content.comments_links': {
                'explanation': 'Comment links with specific class - requires class_name parameter',
                'xpath': '//a[@class="{class_name}"]'
            },

            # Multiple Elements (Pipe separated)
            'content.blog_titles_and_comments': {
                'explanation': 'Blog titles and comment links combined (pipe separated) - requires class_name and comments_link_class parameters',
                'xpath': '//div[contains(@class, "{class_name}")]//h3|//a[@class="comments_link_class"]'
            },

            # Generic dynamic selectors
            'generic.elements_by_class': {
                'explanation': 'All elements with specific class - requires class_name parameter',
                'xpath': '//*[@class="{class_name}"]'
            },
            'generic.elements_by_id': {
                'explanation': 'Element with specific ID - requires id_value parameter',
                'xpath': '//*[@id="{id_value}"]'
            },
            'generic.elements_by_attribute': {
                'explanation': 'Elements with specific attribute value - requires attribute_name and attribute_value parameters',
                'xpath': '//*[@{attribute_name}="{attribute_value}"]'
            },
            'generic.links_to_domain': {
                'explanation': 'All links to specific domain - requires domain parameter',
                'xpath': '//a[contains(@href, "{domain}")]'
            },
            'generic.images_from_domain': {
                'explanation': 'All images from specific domain - requires domain parameter',
                'xpath': '//img[contains(@src, "{domain}")]'
            },
            'generic.text_containing': {
                'explanation': 'Elements containing specific text - requires text_content parameter',
                'xpath': '//*[contains(text(), "{text_content}")]'
            },

            # General Regex Patterns
             'general.email': {
                'explanation': 'Strict email address pattern (requires domain extension)',
                'regex': r'[a-zA-Z0-9-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
            },
            'general.phone_us': {
                'explanation': 'US phone number format (XXX) XXX-XXXX',
                'regex': r'\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})'
            },
            'general.url': {
                'explanation': 'HTTP/HTTPS URLs',
                'regex': r'https?://[^\s<>"{}|\\^`\[\]]+'
            },
            'general.twitter_handle': {
                'explanation': 'Twitter/X handle format',
                'regex': r'@[a-zA-Z0-9_]{1,15}'
            },
             'general.date_iso': {
                'explanation': 'ISO date format (YYYY-MM-DD)',
                'regex': r'\d{4}-\d{2}-\d{2}'
            },
             'general.price_usd': {
                'explanation': 'US Dollar price format',
                'regex': r'\$\d+(?:\.\d{2})?'
            },
             'general.ipv4': {
                'explanation': 'IPv4 address format',
                'regex': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            }
        }

    def get(self, selector_name: str, method: str = 'xpath') -> Optional[str]:
        """
        Get selector by name and method
        
        Args:
            selector_name: Name of the selector to retrieve
            method: Extraction method ('xpath', 'regex', 'css')
            
        Returns:
            Selector string or None if not found
        """
        if selector_name in self.selectors and method in self.selectors[selector_name]:
            return self.selectors[selector_name][method]
        return None

    def get_explanation(self, selector_name: str) -> Optional[str]:
        """
        Get explanation for a selector by name
        
        Args:
            selector_name: Name of the selector to get explanation for
            
        Returns:
            Explanation string or None if not found
        """
        if selector_name in self.selectors:
            return self.selectors[selector_name].get('explanation')
        return None
    
    def get_all_selectors(self) -> Dict[str, Dict[str, str]]:
        """
        Get all available selectors and their methods
        
        Returns:
            Dictionary of selectors
        """
        return self.selectors

    def extract(self, selector_name: str, html_string: str, method: str = 'xpath', **kwargs) -> List[str]:
        """
        Apply a selector to an HTML string and return results.
        
        Args:
            selector_name: Name of the selector to apply
            html_string: HTML string to parse
            method: Extraction method ('xpath', 'regex')
            **kwargs: Additional parameters for dynamic selectors
            
        Returns:
            List of extracted string values
        """
        pattern = self.get(selector_name, method)
        if not pattern:
            print(f"Selector '{selector_name}' with method '{method}' not found.")
            return []

        # Process dynamic parameters
        pattern = self._process_dynamic_pattern(pattern, **kwargs)

        try:
            if method == 'xpath':
                tree = html.fromstring(html_string)
                elements = tree.xpath(pattern)

                results = []
                for element in elements:
                    # Handle string results (attributes, attribute values, etc.)
                    if isinstance(element, str):
                        results.append(element.strip())
                    # Handle lxml elements
                    elif hasattr(element, 'tag'):
                        # Check if selector specifies what to extract
                        selector_config = self.selectors.get(selector_name, {})
                        extract_type = selector_config.get('extract', 'text')

                        if extract_type == 'text':
                            extracted_value = self._extract_text_content(element)
                        elif extract_type == 'attribute':
                            attr_name = selector_config.get('attribute')
                            if attr_name:
                                # Try the specified attribute first
                                extracted_value = element.get(attr_name)
                                if not extracted_value:
                                    # Try fallback attributes based on selector
                                    if selector_name.startswith('forms.inputs') or selector_name.startswith('forms.text_inputs'):
                                        for fallback_attr in ['value', 'name', 'type']:
                                            if fallback_attr != attr_name:
                                                extracted_value = element.get(fallback_attr)
                                                if extracted_value:
                                                    break
                                    elif selector_name.startswith('images.'):
                                        # For images, fallback to alt if src is empty
                                        if attr_name == 'src':
                                            extracted_value = element.get('alt')
                            else:
                                # No specific attribute specified, try common ones
                                for attr in ['src', 'href', 'alt', 'value', 'content']:
                                    extracted_value = element.get(attr)
                                    if extracted_value:
                                        break
                        elif extract_type == 'html':
                            extracted_value = etree.tostring(element, encoding='unicode')
                        elif extract_type == 'list_items':
                            extracted_value = self._extract_list_items(element)
                        else:
                            # Fallback to text content
                            extracted_value = self._extract_text_content(element)

                        if extracted_value:
                            results.append(extracted_value.strip() if isinstance(extracted_value, str) else str(extracted_value))
                    # Handle other types
                    else:
                        results.append(str(element).strip())
                return results
            elif method == 'regex':
                return re.findall(pattern, html_string, re.DOTALL)
            
            # Add CSS selector logic if needed in the future
            # elif method == 'css':
            #     ...

            else:
                print(f"Unsupported extraction method: {method}")
                return []

        except Exception as e:
            print(f"Error applying selector {selector_name} with method {method}: {e}")
            return []
    
    def _extract_element_value(self, element, selector_name: str) -> Optional[str]:
        """
        Extract the most relevant value from an HTML element based on its type and the selector.

        Args:
            element: lxml element object
            selector_name: Name of the selector being used

        Returns:
            Extracted string value or None
        """
        # Handle different element types
        if element.tag == 'img':
            return self._extract_image_value(element, selector_name)
        elif element.tag in ['input', 'textarea', 'select']:
            return self._extract_form_value(element, selector_name)
        elif element.tag in ['ul', 'ol']:
            return self._extract_list_value(element, selector_name)
        elif element.tag == 'a':
            return self._extract_link_value(element, selector_name)
        else:
            return self._extract_generic_value(element)

    def _extract_image_value(self, element, selector_name: str) -> Optional[str]:
        """Extract value from img element."""
        if 'src' in selector_name:
            return element.get('src')
        elif 'alt' in selector_name:
            return element.get('alt')
        else:
            # For general image selectors, return src if available, otherwise alt
            src = element.get('src')
            if src:
                return src
            return element.get('alt')

    def _extract_form_value(self, element, selector_name: str) -> Optional[str]:
        """Extract value from form elements."""
        # Priority: value > placeholder > name > type
        value = element.get('value')
        if value:
            return value

        placeholder = element.get('placeholder')
        if placeholder:
            return placeholder

        name = element.get('name')
        if name:
            return name

        input_type = element.get('type')
        if input_type:
            return input_type

        return None

    def _extract_list_value(self, element, selector_name: str) -> Optional[str]:
        """Extract text content from list elements (ul, ol)."""
        # Get all list items and join their text
        list_items = element.xpath('.//li')
        if list_items:
            texts = []
            for li in list_items:
                text = ''.join(li.itertext()).strip()
                if text:
                    texts.append(text)
            return ' | '.join(texts)

        # Fallback to all text content
        text = ''.join(element.itertext()).strip()
        return text if text else None

    def _extract_link_value(self, element, selector_name: str) -> Optional[str]:
        """Extract value from anchor elements."""
        if 'href' in selector_name or 'url' in selector_name:
            return element.get('href')
        elif 'links.' in selector_name:
            # For link selectors, return href attribute
            return element.get('href')
        else:
            # For general link selectors, return text content
            text = ''.join(element.itertext()).strip()
            return text if text else element.get('href')

    def _extract_generic_value(self, element) -> Optional[str]:
        """Extract value from generic elements."""
        # First try direct text content
        if hasattr(element, 'text') and element.text:
            return element.text.strip()

        # Then try all text content from children
        text = ''.join(element.itertext()).strip()
        if text:
            return text

        # Finally try to get a meaningful attribute
        for attr in ['value', 'content', 'title', 'alt', 'src', 'href']:
            value = element.get(attr)
            if value:
                return value

        return None

    def _extract_text_content(self, element) -> Optional[str]:
        """Extract text content from an element."""
        # First try direct text content
        if hasattr(element, 'text') and element.text:
            return element.text.strip()

        # Then try all text content from children
        text = ''.join(element.itertext()).strip()
        return text if text else None

    def _extract_list_items(self, element) -> Optional[str]:
        """Extract text content from list elements (ul, ol)."""
        # Get all list items and join their text
        list_items = element.xpath('.//li')
        if list_items:
            texts = []
            for li in list_items:
                text = ''.join(li.itertext()).strip()
                if text:
                    texts.append(text)
            return ' | '.join(texts)

        # Fallback to all text content
        text = ''.join(element.itertext()).strip()
        return text if text else None

    def _process_dynamic_pattern(self, pattern: str, **kwargs) -> str:
        """
        Replace placeholders in a pattern with actual values from kwargs.
        """
        for key, value in kwargs.items():
            pattern = pattern.replace(f'{{{key}}}', str(value))
        return pattern


# Create global instance
selectors_instance = Selectors()

# Convenience functions
def get_selector(name: str, method: str = 'xpath') -> Optional[str]:
    """Get selector by name and method"""
    return selectors_instance.get(name, method)

def get_explanation(name: str) -> Optional[str]:
    """Get explanation for selector by name"""
    return selectors_instance.get_explanation(name)

def extract(selector_name: str, html_string: str, method: str = 'xpath', **kwargs) -> List[str]:
    """Extract data from HTML using a named selector"""
    return selectors_instance.extract(selector_name, html_string, method, **kwargs)
