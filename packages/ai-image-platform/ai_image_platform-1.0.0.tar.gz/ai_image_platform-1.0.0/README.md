# AI Image Platform

A comprehensive Python library for AI-powered image processing, generation, editing, and multimodal chat capabilities.

[![PyPI version](https://badge.fury.io/py/ai-image-platform.svg)](https://badge.fury.io/py/ai-image-platform)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

🎨 **Multi-Provider Image Generation**
- High-quality image generation with Pollinations.ai (Flux models)
- Creative image generation with Google Gemini AI
- Multiple artistic styles and aspect ratios
- Real-time generation with base64 encoding

✏️ **AI-Powered Image Editing**
- Prompt-based image transformations
- Style transfer and artistic effects
- Multi-image composition capabilities
- Advanced editing with customizable strength

🔍 **Intelligent Image Analysis**
- Detailed image descriptions and scene understanding
- Object detection and recognition
- Support for multiple input formats (base64, bytes, URLs)
- Advanced AI analysis with Google Gemini

💬 **Multimodal Chat**
- Chat with 6 different Gemini AI models
- Support for both text and image inputs
- Conversation history management
- Real-time responses with streaming support

🌐 **RESTful API**
- Complete Flask-based web API
- Interactive web interface included
- Comprehensive API documentation
- Health monitoring and status endpoints

☁️ **Serverless Ready**
- Zero file system dependencies
- Pure base64 I/O operations
- Environment variable configuration
- Production-ready with Gunicorn

## Quick Start

### Installation

```bash
pip install ai-image-platform
```

### Basic Usage

#### Python Library

```python
from ai_image_platform import (
    GeminiChatClient, 
    ImageGenerator, 
    ImageAnalyzer, 
    PollinationsClient
)

# Set your API key
import os
os.environ['GEMINI_API_KEY'] = 'your-gemini-api-key'

# Generate images with Pollinations
pollinations = PollinationsClient()
result = pollinations.generate_image(
    "A serene mountain landscape at sunset",
    style="photorealistic",
    model="flux-pro"
)

# Chat with Gemini AI
chat = GeminiChatClient()
response = chat.ask_question(
    "What's the weather like?",
    model="gemini-2.5-flash-lite"
)

# Analyze images
analyzer = ImageAnalyzer()
analysis = analyzer.analyze_image_bytes(image_bytes)
```

#### Flask Web Application

```python
from ai_image_platform import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Web Interface

The library includes a complete web interface accessible at `http://localhost:5000` with tabs for:
- 🎨 Image Generation
- ✏️ Image Editing  
- 🔍 Image Analysis
- 💬 AI Chat

## API Reference

### Core Classes

#### `PollinationsClient`
High-quality image generation using Pollinations.ai API.

```python
client = PollinationsClient()
result = client.generate_image(
    prompt="A futuristic cityscape",
    style="cyberpunk",
    aspect_ratio="16:9",
    model="flux-pro"
)
```

#### `GeminiChatClient`
Multimodal chat with Google Gemini AI models.

```python
chat = GeminiChatClient()

# Text-only chat
response = chat.ask_question("Hello, how are you?")

# Chat with image
with open('image.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()
response = chat.ask_question("What's in this image?", image_data=image_data)
```

#### `ImageGenerator`
Creative image generation with Gemini AI.

```python
generator = ImageGenerator()
result = generator.generate_image(
    "An abstract painting of emotions",
    style="abstract",
    aspect_ratio="1:1"
)
```

#### `ImageAnalyzer`
Intelligent image analysis and understanding.

```python
analyzer = ImageAnalyzer()

# Analyze from bytes
result = analyzer.analyze_image_bytes(image_bytes)

# Analyze from URL
result = analyzer.analyze_image_url("https://example.com/image.jpg")
```

#### `ImageEditor`
AI-powered image editing and transformation.

```python
editor = ImageEditor()
result = editor.edit_image(
    image_bytes,
    "Add a rainbow in the sky",
    style="photorealistic",
    edit_strength=0.7
)
```

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Service health check |
| `/api/chat` | POST | Multimodal chat with AI |
| `/api/generate-image` | POST | Generate images with Gemini |
| `/api/pollinations/generate-image` | POST | Generate images with Pollinations |
| `/api/analyze-image` | POST | Analyze images |
| `/api/edit-image` | POST | Edit images with AI |
| `/docs` | GET | Interactive API documentation |

## Configuration

### Environment Variables

```bash
# Required for Gemini AI features
GEMINI_API_KEY=your-gemini-api-key-here

# Optional Flask configuration
SECRET_KEY=your-secret-key
```

### Available Models

**Gemini Chat Models:**
- `gemini-2.5-flash-lite` (Fastest)
- `gemini-1.5-flash` (Fast)
- `gemini-2.5-flash` (Advanced)
- `gemini-2.0-flash` (Next-gen)
- `gemini-2.5-pro` (Professional)
- `gemini-1.5-flash-8b` (Lightweight)

**Image Generation Models:**
- Pollinations: `flux-pro`, `flux-dev`, `flux-realism`
- Gemini: `gemini-2.0-flash-preview-image-generation`

### Supported Styles

- Photorealistic
- Cartoon
- Abstract Art
- Impressionistic
- Cyberpunk
- Anime
- Oil Painting
- Watercolor
- Sketch
- Digital Art

## Examples

### Generate High-Quality Images

```python
from ai_image_platform import PollinationsClient

client = PollinationsClient()

# Generate a professional photo
result = client.generate_image(
    prompt="Professional headshot of a business woman",
    style="photorealistic",
    aspect_ratio="3:4",
    model="flux-pro",
    enhance=True
)

if result['status'] == 'success':
    # Save the image
    import base64
    image_data = base64.b64decode(result['image_base64'])
    with open('generated_image.png', 'wb') as f:
        f.write(image_data)
```

### Multimodal AI Chat

```python
from ai_image_platform import GeminiChatClient
import base64

chat = GeminiChatClient()

# Load an image
with open('photo.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

# Ask AI about the image
response = chat.ask_question(
    "Describe this image in detail and suggest improvements",
    image_data=image_data,
    model="gemini-2.5-flash"
)

print(response['answer'])
```

### Batch Image Analysis

```python
from ai_image_platform import ImageAnalyzer

analyzer = ImageAnalyzer()

image_urls = [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
]

for url in image_urls:
    result = analyzer.analyze_image_url(url)
    if result['status'] == 'success':
        print(f"Analysis: {result['analysis']}")
```

## Deployment

### Local Development

```bash
git clone <your-repo>
cd ai-image-platform
pip install -e .
export GEMINI_API_KEY=your-key-here
python main.py
```

### Production with Gunicorn

```bash
pip install ai-image-platform
export GEMINI_API_KEY=your-key-here
gunicorn --bind 0.0.0.0:8000 --workers 4 "ai_image_platform:create_app()"
```

### Serverless Deployment

The library is designed for serverless environments with:
- No file system dependencies
- Environment-based configuration
- Stateless operations
- Base64 I/O handling

## Requirements

- Python 3.8+
- Flask 2.3+
- Google GenAI 1.33+
- Pillow 10.0+
- Requests 2.31+

## API Keys

### Google Gemini AI
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Set `GEMINI_API_KEY` environment variable

### Pollinations AI
No API key required - free to use!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- 📧 Email: contact@ai-image-platform.dev
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/ai-image-platform/issues)
- 📖 Documentation: [Full API Documentation](http://localhost:5000/docs)

## Changelog

### v1.0.0
- Initial release
- Multi-provider image generation
- Gemini AI chat integration
- Complete web interface
- RESTful API
- Serverless deployment support

---

**Built with ❤️ for the AI community**