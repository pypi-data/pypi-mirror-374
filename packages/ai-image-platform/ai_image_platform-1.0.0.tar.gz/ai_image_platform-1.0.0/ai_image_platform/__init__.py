"""
AI Image Platform Library
========================

A comprehensive Python library for AI-powered image processing, generation, 
editing, and analysis with multimodal chat capabilities.

Features:
- Multi-provider image generation (Pollinations.ai, Gemini AI)
- Advanced image editing and composition
- Intelligent image analysis and segmentation
- Multimodal chat with multiple Gemini models
- RESTful API with Flask backend
- Serverless deployment ready

Author: AI Image Platform Team
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AI Image Platform Team"
__license__ = "MIT"

# Core modules
from .core.gemini_chat import GeminiChatClient
from .core.image_analysis import ImageAnalyzer
from .core.image_generation import ImageGenerator
from .core.image_editing import ImageEditor
from .core.pollinations_client import PollinationsClient

# API module
from .api.flask_app import create_app

# Constants
AVAILABLE_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash", 
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-pro",
    "gemini-1.5-flash-8b"
]

AVAILABLE_STYLES = {
    'photorealistic': 'Photorealistic and detailed',
    'cartoon': 'Cartoon and animated style',
    'abstract': 'Abstract artistic style',
    'impressionistic': 'Impressionist painting style',
    'cyberpunk': 'Cyberpunk and futuristic',
    'anime': 'Anime and manga style',
    'oil_painting': 'Oil painting technique',
    'watercolor': 'Watercolor painting',
    'sketch': 'Pencil sketch style',
    'digital_art': 'Digital art style'
}

AVAILABLE_RATIOS = {
    '1:1': 'Square format',
    '16:9': 'Widescreen landscape', 
    '9:16': 'Mobile portrait',
    '4:3': 'Standard landscape',
    '3:4': 'Standard portrait'
}

__all__ = [
    'GeminiChatClient',
    'ImageAnalyzer', 
    'ImageGenerator',
    'ImageEditor',
    'PollinationsClient',
    'create_app',
    'AVAILABLE_MODELS',
    'AVAILABLE_STYLES', 
    'AVAILABLE_RATIOS'
]