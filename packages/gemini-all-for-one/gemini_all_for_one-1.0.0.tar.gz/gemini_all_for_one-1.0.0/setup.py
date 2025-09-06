"""
Setup configuration for Gemini All-for-One package.
"""

from setuptools import setup, find_packages
import os

# Read README if available
long_description = """
# Gemini All-for-One

A comprehensive AI image platform powered by Google's Gemini AI. Provides image generation, analysis, editing, and multimodal chat capabilities.

## Features

- **High-Quality Image Generation**: Text-to-image generation with multiple artistic styles and aspect ratios
- **Advanced Image Analysis**: Intelligent image understanding and detailed descriptions
- **AI-Powered Image Editing**: Edit images while preserving the same object using text prompts
- **Multimodal Chat**: Conversations with text and image support using Gemini AI
- **Free Image Generation**: Alternative image generation via Pollinations.ai (no API key required)
- **Serverless Ready**: Base64 I/O implementation perfect for serverless deployments

## Quick Start

```python
from gemini_all_for_one import ImageGenerator, ImageAnalyzer, ImageEditor, GeminiChatClient

# Generate images
generator = ImageGenerator()
result = generator.generate_image("A beautiful sunset over mountains")
image_data = result['image_base64']

# Analyze images  
analyzer = ImageAnalyzer()
analysis = analyzer.analyze_image(image_bytes)

# Edit images (preserves same object)
editor = ImageEditor()
edited = editor.edit_image(image_bytes, "add sunglasses")

# Multimodal chat
chat = GeminiChatClient()
response = chat.send_message("What's in this image?", image=image_bytes)
```

## Requirements

- Python 3.8+
- Google Gemini API key (get one at https://aistudio.google.com/app/apikey)
- Set `GEMINI_API_KEY` environment variable

## Installation

```bash
pip install gemini-all-for-one
```

## License

MIT License - see LICENSE file for details.
"""

setup(
    name="gemini-all-for-one",
    version="1.0.0",
    author="AI Image Platform Team",
    author_email="support@ai-image-platform.com",
    description="A comprehensive AI image platform powered by Google's Gemini AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-image-platform/gemini-all-for-one",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.3.0",
        "google-genai>=1.33.0", 
        "google-generativeai>=0.8.5",
        "pillow>=10.0.0",
        "requests>=2.31.0",
        "werkzeug>=2.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0", 
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    include_package_data=True,
    package_data={
        'gemini_all_for_one': [
            'templates/*.html',
            'static/*',
        ],
    },
    entry_points={
        'console_scripts': [
            'gemini-all-for-one=gemini_all_for_one.api.flask_app:main',
        ],
    },
    keywords="ai artificial-intelligence image-generation image-analysis image-editing gemini google multimodal chat",
    project_urls={
        "Bug Reports": "https://github.com/ai-image-platform/gemini-all-for-one/issues",
        "Source": "https://github.com/ai-image-platform/gemini-all-for-one",
        "Documentation": "https://gemini-all-for-one.readthedocs.io/",
    },
)