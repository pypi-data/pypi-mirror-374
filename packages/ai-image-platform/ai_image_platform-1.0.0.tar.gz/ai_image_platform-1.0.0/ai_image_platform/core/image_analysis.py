"""
Image Analysis Module
====================

This module provides comprehensive image analysis capabilities using Google's Gemini AI,
including detailed image descriptions, object detection, and scene understanding.

Features:
- Advanced image description and analysis
- Support for multiple input formats (base64, bytes, URLs)
- Segmentation mask extraction (placeholder for future implementation)
- Detailed object and scene recognition
- Multimodal AI analysis with contextual understanding

Classes:
    ImageAnalyzer: Main class for image analysis operations

Functions:
    analyze_base64_image(): Analyze base64 encoded images
    analyze_url_image(): Analyze images from URLs
"""

import os
import logging
import base64
import io
import requests
from typing import Dict, Any, Optional, List, Union
from PIL import Image
import google.genai as genai

# Configure logging
logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """
    Advanced image analysis client using Google Gemini AI.
    
    This class provides comprehensive image analysis capabilities including
    object detection, scene understanding, and detailed descriptions.
    
    Attributes:
        api_key: Google Gemini API key
        client: Configured Gemini client
        
    Example:
        >>> analyzer = ImageAnalyzer()
        >>> result = analyzer.analyze_image_bytes(image_bytes)
        >>> print(result['analysis'])
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Image Analyzer.
        
        Args:
            api_key (str, optional): Google Gemini API key. If not provided,
                                   will use GEMINI_API_KEY environment variable.
        
        Raises:
            ValueError: If no API key is provided or found in environment
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment variables")
        
        # Initialize Gemini API client
        logger.info("Image Analyzer initialized successfully")

    def analyze_image_bytes(self, 
                           image_bytes: bytes, 
                           prompt: str = "What is this image? Provide a detailed description including objects, people, scenes, colors, and any notable details.",
                           model: str = "gemini-2.5-flash") -> str:
        """
        Analyze image from bytes data using Gemini AI.
        
        Args:
            image_bytes (bytes): Raw image data
            prompt (str): Analysis prompt for the AI
            model (str): Gemini model to use for analysis
            
        Returns:
            str: Detailed analysis of the image
            
        Raises:
            Exception: If analysis fails
        """
        try:
            # Convert bytes to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Create Gemini model
            gemini_model = genai.GenerativeModel(model)
            
            # Generate analysis
            response = gemini_model.generate_content([prompt, pil_image])
            
            if response.text:
                logger.info("Image analysis completed successfully")
                return response.text
            
            return "Unable to analyze the image."
            
        except Exception as e:
            logger.error(f"Error in analyze_image_bytes: {str(e)}")
            raise Exception(f"Error analyzing image: {str(e)}")

    def analyze_pil_image(self, 
                         image: Image.Image,
                         prompt: str = "What is this image? Provide a detailed description.",
                         model: str = "gemini-2.5-flash") -> str:
        """
        Analyze PIL Image object using Gemini AI.
        
        Args:
            image (PIL.Image): PIL Image object
            prompt (str): Analysis prompt
            model (str): Gemini model to use
            
        Returns:
            str: Analysis result
        """
        try:
            # Convert PIL image to bytes
            image_buffer = io.BytesIO()
            image.save(image_buffer, format='JPEG')
            image_bytes = image_buffer.getvalue()
            
            return self.analyze_image_bytes(image_bytes, prompt, model)
            
        except Exception as e:
            logger.error(f"Error in analyze_pil_image: {str(e)}")
            raise Exception(f"Error analyzing PIL image: {str(e)}")

    def extract_segmentation_masks(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Extract segmentation masks from image.
        
        Note: This is a placeholder implementation. Full segmentation would require
        specialized models and additional processing.
        
        Args:
            image (PIL.Image): PIL Image object
            
        Returns:
            List[Dict]: List of segmentation mask data (currently empty)
        """
        try:
            # Placeholder for future segmentation implementation
            logger.info("Segmentation mask extraction requested (placeholder implementation)")
            return []
            
        except Exception as e:
            logger.error(f"Error in extract_segmentation_masks: {str(e)}")
            return []


def analyze_base64_image(base64_image: str, 
                        extract_masks: bool = False, 
                        api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a base64 encoded image.
    
    Args:
        base64_image (str): Base64 encoded image data
        extract_masks (bool): Whether to extract segmentation masks
        api_key (str, optional): API key for authentication
        
    Returns:
        Dict containing analysis results or error information
        
    Example:
        >>> result = analyze_base64_image(base64_data)
        >>> print(result['analysis'])
    """
    try:
        # Initialize analyzer
        analyzer = ImageAnalyzer(api_key)
        
        # Remove data URL prefix if present
        if base64_image.startswith('data:image'):
            base64_image = base64_image.split(',')[1]
        
        # Decode base64 to image
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))
        
        # Get analysis
        analysis = analyzer.analyze_pil_image(image)
        
        # Get segmentation masks if requested
        segmentation_results = []
        if extract_masks:
            segmentation_results = analyzer.extract_segmentation_masks(image)
        
        return {
            "status": "success",
            "analysis": analysis,
            "segmentation_masks": segmentation_results,
            "image_format": image.format,
            "image_size": image.size
        }
        
    except Exception as e:
        logger.error(f"Error analyzing base64 image: {str(e)}")
        return {"error": str(e), "status": "error"}


def analyze_url_image(image_url: str, 
                     extract_masks: bool = False,
                     api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze an image from URL.
    
    Args:
        image_url (str): URL of the image to analyze
        extract_masks (bool): Whether to extract segmentation masks
        api_key (str, optional): API key for authentication
        
    Returns:
        Dict containing analysis results or error information
        
    Example:
        >>> result = analyze_url_image("https://example.com/image.jpg")
        >>> print(result['analysis'])
    """
    try:
        logger.info(f"Analyzing image from URL: {image_url}")
        
        # Initialize analyzer
        analyzer = ImageAnalyzer(api_key)
        
        # Download image from URL
        response = requests.get(image_url, timeout=30, stream=True)
        response.raise_for_status()
        
        # Verify content type
        content_type = response.headers.get('content-type', 'image/jpeg')
        if 'image/' not in content_type:
            content_type = 'image/jpeg'  # Default fallback
        
        # Analyze the image bytes
        analysis = analyzer.analyze_image_bytes(
            image_bytes=response.content,
            prompt="What is this image? Provide a detailed description, including objects, people, scenes, colors, and any notable details."
        )
        
        # Get segmentation masks if requested
        segmentation_results = []
        if extract_masks:
            # Open image for segmentation
            image = Image.open(io.BytesIO(response.content))
            segmentation_results = analyzer.extract_segmentation_masks(image)
        
        return {
            "status": "success",
            "analysis": analysis,
            "image_url": image_url,
            "content_type": content_type,
            "segmentation_masks": segmentation_results
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to download image from {image_url}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "status": "error"}
    except Exception as e:
        error_msg = f"Error analyzing URL image: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "status": "error"}