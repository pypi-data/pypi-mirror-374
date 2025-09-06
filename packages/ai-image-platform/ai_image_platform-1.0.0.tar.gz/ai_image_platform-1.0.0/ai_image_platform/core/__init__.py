"""
Core AI Processing Modules
==========================

This package contains the core AI processing modules for the AI Image Platform:

- gemini_chat: Multimodal chat with Gemini AI models
- image_analysis: Intelligent image analysis and description  
- image_generation: Text-to-image generation with multiple providers
- image_editing: AI-powered image editing and composition
- pollinations_client: High-quality image generation via Pollinations.ai
"""

from .gemini_chat import GeminiChatClient
from .image_analysis import ImageAnalyzer
from .image_generation import ImageGenerator
from .image_editing import ImageEditor
from .pollinations_client import PollinationsClient

__all__ = [
    'GeminiChatClient',
    'ImageAnalyzer',
    'ImageGenerator', 
    'ImageEditor',
    'PollinationsClient'
]