"""
Image Generation Module
======================

This module provides text-to-image generation capabilities using Google's Gemini AI,
with support for multiple styles and aspect ratios.

Features:
- High-quality text-to-image generation
- Multiple artistic styles (photorealistic, cartoon, abstract, etc.)
- Customizable aspect ratios
- Serverless-ready implementation with base64 output
- Comprehensive error handling and logging

Classes:
    ImageGenerator: Main class for image generation operations

Functions:
    generate_image_from_text(): Generate images from text prompts
"""

import os
import logging
import base64
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import google.genai as genai

# Configure logging
logger = logging.getLogger(__name__)

# Available styles for image generation
AVAILABLE_STYLES = {
    "photorealistic": "photorealistic and detailed",
    "cartoon": "cartoon style and animated",
    "abstract": "abstract art style",
    "impressionistic": "impressionist painting style",
    "cyberpunk": "cyberpunk and futuristic art",
    "anime": "anime and manga style",
    "oil_painting": "oil painting technique",
    "watercolor": "watercolor painting style",
    "sketch": "pencil sketch style",
    "digital_art": "digital art style"
}

# Available aspect ratios
AVAILABLE_RATIOS = {
    "1:1": "square format",
    "16:9": "landscape widescreen format",
    "9:16": "portrait vertical format",
    "4:3": "standard landscape format",
    "3:4": "standard portrait format"
}


class ImageGenerator:
    """
    High-quality text-to-image generation client using Google Gemini AI.
    
    This class provides comprehensive image generation capabilities with
    support for multiple styles, aspect ratios, and quality settings.
    
    Attributes:
        api_key: Google Gemini API key
        client: Configured Gemini client
        
    Example:
        >>> generator = ImageGenerator()
        >>> result = generator.generate_image("A beautiful sunset over mountains")
        >>> image_data = result['image_base64']
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Image Generator.
        
        Args:
            api_key (str, optional): Google Gemini API key. If not provided,
                                   will use GEMINI_API_KEY environment variable.
        
        Raises:
            ValueError: If no API key is provided or found in environment
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment variables")
        
        # Configure Gemini API
        self.client = genai.Client(api_key=self.api_key)
        logger.info("Image Generator initialized successfully")

    def generate_image(self, 
                      prompt_text: str,
                      style: str = "photorealistic",
                      aspect_ratio: str = "1:1",
                      model: str = "gemini-2.0-flash-preview-image-generation",
                      temperature: float = 0.8,
                      max_tokens: int = 8192) -> Dict[str, Any]:
        """
        Generate an image from text prompt.
        
        Args:
            prompt_text (str): The text description for image generation
            style (str): Artistic style (default: "photorealistic")
            aspect_ratio (str): Image aspect ratio (default: "1:1")
            model (str): Gemini model to use for generation
            temperature (float): Generation creativity (0.0-1.0)
            max_tokens (int): Maximum output tokens for high quality
            
        Returns:
            Dict containing:
                - status (str): 'success' or 'error'
                - image_base64 (str): Base64 encoded image data (if successful)
                - response_text (str): AI description of generated image
                - filename (str): Suggested filename
                - error (str): Error message (if failed)
                
        Example:
            >>> result = generator.generate_image("A majestic lion in the savanna")
            >>> if result['status'] == 'success':
            ...     image_data = result['image_base64']
        """
        try:
            # Get style and ratio descriptions
            style_desc = AVAILABLE_STYLES.get(style, AVAILABLE_STYLES["photorealistic"])
            ratio_desc = AVAILABLE_RATIOS.get(aspect_ratio, AVAILABLE_RATIOS["1:1"])
            
            # Create enhanced prompt
            enhanced_prompt = f"{prompt_text}, {style_desc}, {ratio_desc}"
            
            logger.info(f"Starting image generation for prompt: {prompt_text}")
            logger.info(f"Style: {style} ({style_desc})")
            logger.info(f"Aspect ratio: {aspect_ratio} ({ratio_desc})")
            
            # Generate unique identifier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            image_filename = f"generated_image_{timestamp}_{unique_id}.png"
            
            # Generate image using Gemini API
            response = self.client.models.generate_content(
                model=model,
                contents=enhanced_prompt,
                config={
                    'response_modalities': ['TEXT', 'IMAGE'],
                    'temperature': temperature,
                    'max_output_tokens': max_tokens
                }
            )
            
            if not response.candidates:
                logger.error("No candidates returned from Gemini API")
                return {
                    'status': 'error',
                    'error': 'No image generated by the API. Please try a different prompt.'
                }
            
            # Process response
            content = response.candidates[0].content
            if not content or not content.parts:
                logger.error("No content or parts in API response")
                return {
                    'status': 'error',
                    'error': 'Invalid response from image generation API'
                }
            
            image_data_bytes = None
            response_text = None
            
            # Extract image data and text
            for part in content.parts:
                if part.text:
                    response_text = part.text
                    logger.info(f"API response text: {part.text}")
                elif part.inline_data and part.inline_data.data:
                    image_data_bytes = part.inline_data.data
                    logger.info(f"Image generated successfully with ID: {unique_id}")
            
            if image_data_bytes is None:
                logger.error("No image data found in API response")
                return {
                    'status': 'error',
                    'error': 'No image data received from the API. The model may not support this prompt.'
                }
            
            # Encode to base64
            image_base64 = base64.b64encode(image_data_bytes).decode('utf-8')
            
            return {
                'status': 'success',
                'image_base64': image_base64,
                'response_text': response_text,
                'filename': image_filename,
                'prompt': prompt_text,
                'style': style,
                'aspect_ratio': aspect_ratio
            }
            
        except Exception as e:
            logger.error(f"Error in generate_image: {str(e)}")
            
            # Provide specific error messages
            if "API_KEY" in str(e).upper():
                error_msg = "Invalid or missing Gemini API key. Please check your GEMINI_API_KEY."
            elif "quota" in str(e).lower() or "limit" in str(e).lower():
                error_msg = "API quota exceeded or rate limit reached. Please try again later."
            elif "permission" in str(e).lower() or "forbidden" in str(e).lower():
                error_msg = "Permission denied. Please check your API key permissions."
            else:
                error_msg = f"Failed to generate image: {str(e)}"
            
            return {
                'status': 'error',
                'error': error_msg
            }

    def get_available_styles(self) -> Dict[str, str]:
        """Get available artistic styles for image generation."""
        return AVAILABLE_STYLES.copy()

    def get_available_ratios(self) -> Dict[str, str]:
        """Get available aspect ratios for image generation."""
        return AVAILABLE_RATIOS.copy()


def generate_image_from_text(prompt_text: str, 
                           style: str = "photorealistic",
                           aspect_ratio: str = "1:1",
                           api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to generate an image from text prompt.
    
    Args:
        prompt_text (str): The text description for image generation
        style (str): Artistic style (default: "photorealistic")
        aspect_ratio (str): Image aspect ratio (default: "1:1")
        api_key (str, optional): API key for authentication
        
    Returns:
        Dict containing generation results or error information
        
    Example:
        >>> result = generate_image_from_text("A serene mountain landscape")
        >>> if result['status'] == 'success':
        ...     print(f"Generated: {result['filename']}")
    """
    try:
        generator = ImageGenerator(api_key)
        return generator.generate_image(prompt_text, style, aspect_ratio)
    except Exception as e:
        logger.error(f"Error in generate_image_from_text: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }