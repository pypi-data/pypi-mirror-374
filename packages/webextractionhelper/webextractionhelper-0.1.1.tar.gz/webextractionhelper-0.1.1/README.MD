# WebExtractionHelper

A comprehensive Python package providing XPath selectors, regex patterns, and CSS selectors for web scraping various web content including Google search features, featured snippets, related questions, and other SERP elements.

## 🚀 Features

- **95+ Pre-built Selectors**: Comprehensive collection of XPath selectors for web scraping
- **Google Search Support**: Specialized selectors for Google SERP features
- **Multiple Content Types**: Support for featured snippets, related questions, images, links, and more
- **Easy to Use**: Simple API with clear explanations for each selector
- **Well Documented**: Each selector includes detailed explanations and usage examples

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install webextractionhelper
```

### From Source
```bash
git clone https://github.com/Artistotle-ai/webextractionhelper.git
cd webextractionhelper
pip install -e .
```

## 🔧 Requirements

- Python 3.7+
- lxml >= 4.6.0

## 📚 Quick Start

```python
from webextractionhelper import Selectors

# Create a Selectors instance
selectors = Selectors()

# Access Google featured snippet selectors
featured_title_xpath = selectors.selectors['google.featured_snippet_title']['xpath']
featured_text_xpath = selectors.selectors['google.featured_snippet_text']['xpath']

# Access related questions selectors
related_questions_xpath = selectors.selectors['google.related_questions_all']['xpath']

print(f"Featured snippet title XPath: {featured_title_xpath}")
print(f"Featured snippet text XPath: {featured_text_xpath}")
print(f"Related questions XPath: {related_questions_xpath}")
```

## 🎯 Available Selector Categories

### Google Search Selectors (21 selectors)
- **Featured Snippets**: Title, text, bullet points, numbered lists, tables, URLs, images
- **Related Questions**: Individual questions, all questions, answer snippets, source titles/URLs
- **Search Results**: Main containers, links, titles, descriptions

### Meta & Open Graph Selectors (11 selectors)
- **Meta Tags**: Title, description, keywords, robots, viewport
- **Open Graph**: Title, description, image, URL, type, site name

### Social Media Selectors (6 selectors)
- **Twitter/X**: Card type, title, description, image, creator, site

### Content Selectors (10 selectors)
- **Headings**: H1, H2, H3, H4
- **Text Content**: Paragraphs, lists, blockquotes
- **Forms**: Input fields, buttons, labels

### Media Selectors (5 selectors)
- **Images**: Source, alt text, title, dimensions
- **Videos**: Source, poster, dimensions

### Link Selectors (7 selectors)
- **Navigation**: Main nav, footer links, breadcrumbs
- **Content Links**: Internal, external, download links

## 🔍 Usage Examples

### Example 1: Extract Google Featured Snippet
```python
from webextractionhelper import Selectors
import requests
from lxml import html

selectors = Selectors()

# Get the page content
url = "https://www.google.com/search?q=python+programming"
response = requests.get(url)
tree = html.fromstring(response.content)

# Extract featured snippet title
title_xpath = selectors.selectors['google.featured_snippet_title']['xpath']
title_elements = tree.xpath(title_xpath)

if title_elements:
    title = title_elements[0].text_content()
    print(f"Featured snippet title: {title}")
```

### Example 2: Extract All Related Questions
```python
# Get all related questions
questions_xpath = selectors.selectors['google.related_questions_all']['xpath']
question_elements = tree.xpath(questions_xpath)

for i, question in enumerate(question_elements, 1):
    print(f"Question {i}: {question.text_content()}")
```

### Example 3: Extract Meta Information
```python
# Get page meta description
meta_desc_xpath = selectors.selectors['meta.description']['xpath']
meta_desc_elements = tree.xpath(meta_desc_xpath)

if meta_desc_elements:
    description = meta_desc_elements[0].get('content')
    print(f"Meta description: {description}")
```

## 📋 Selector Structure

Each selector in the package follows this structure:

```python
{
    'explanation': 'Human-readable description of what this selector extracts',
    'xpath': 'The XPath expression to extract the content',
    'regex': 'Optional regex pattern for text processing',
    'css': 'Optional CSS selector alternative'
}
```

## 🛠️ Development

### Setting up development environment
```bash
git clone https://github.com/Artistotle-ai/webextractionhelper.git
cd webextractionhelper
pip install -e ".[dev]"
```

### Running tests
```bash
python test_package.py
python example_usage.py
```

### Building the package
```bash
python -m build
```

## 📄 License

This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License - see the [LICENSE.txt](LICENSE.txt) file for details.

## 👨‍💻 Author

**Jens Verneuer**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📞 Support

If you have any questions or need help, please:
1. Check the [GitHub Issues](https://github.com/Artistotle-ai/webextractionhelper/issues)
2. Create a new issue if your problem isn't already addressed

## 🔗 Links

- **GitHub Repository**: [https://github.com/Artistotle-ai/webextractionhelper](https://github.com/Artistotle-ai/webextractionhelper)
- **PyPI Package**: [https://pypi.org/project/webextractionhelper/](https://pypi.org/project/webextractionhelper/)
- **Documentation**: [https://github.com/Artistotle-ai/webextractionhelper#readme](https://github.com/Artistotle-ai/webextractionhelper#readme)

## 📈 Version History

- **0.1.0** - Initial release with 95+ selectors for web scraping

---

**Note**: This package is designed to help with web scraping tasks. Please ensure you comply with the terms of service of the websites you're scraping and respect robots.txt files.
