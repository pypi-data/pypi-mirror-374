"""
WebExtractionHelper - A comprehensive web scraping helper package

This package provides XPath selectors, regex patterns, and CSS selectors
for extracting various web content including Google search features,
featured snippets, related questions, and other SERP elements.

Author: Jens Verneuer
Email: Jens@Aristotle.ventures
"""

from .selectors import Selectors, extract

__version__ = "0.1.1"
__author__ = "Jens Verneuer"
__email__ = "Jens@Aristotle.ventures"

__all__ = ["Selectors", "extract"]
