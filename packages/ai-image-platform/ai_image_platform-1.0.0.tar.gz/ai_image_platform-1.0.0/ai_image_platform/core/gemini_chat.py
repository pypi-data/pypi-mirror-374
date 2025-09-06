"""
Gemini Chat Client Module
=========================

This module provides a comprehensive client for interacting with Google's Gemini AI models,
supporting both text-only and multimodal (text + image) conversations.

Features:
- Multiple Gemini model support (2.5 Flash Lite, 1.5 Flash, 2.5 Flash, etc.)
- Multimodal conversations with image upload capability
- Conversation history management
- Automatic session handling
- Error handling and retry logic

Classes:
    GeminiChatClient: Main client class for Gemini AI interactions
    
Functions:
    get_available_models(): Returns list of available Gemini models
    get_model_descriptions(): Returns detailed model descriptions
"""

import os
import logging
import base64
import io
from typing import Dict, List, Optional, Union, Tuple, Any
from PIL import Image
import google.genai as genai

# Configure logging
logger = logging.getLogger(__name__)


class GeminiChatClient:
    """
    A comprehensive client for Google Gemini AI models with multimodal capabilities.
    
    This client supports text-only and image+text conversations across multiple
    Gemini model variants, with automatic session management and error handling.
    
    Attributes:
        current_chat: Active chat session
        current_model: Currently selected model name
        api_key: Google Gemini API key
        
    Example:
        >>> client = GeminiChatClient()
        >>> response = client.ask_question("Hello, how are you?")
        >>> print(response['answer'])
        
        >>> # With image
        >>> with open('image.jpg', 'rb') as f:
        ...     image_data = base64.b64encode(f.read()).decode()
        >>> response = client.ask_question("What's in this image?", image_data=image_data)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini Chat Client.
        
        Args:
            api_key (str, optional): Google Gemini API key. If not provided,
                                   will use GEMINI_API_KEY environment variable.
        
        Raises:
            ValueError: If no API key is provided or found in environment
        """
        self.current_chat = None
        self.current_model = None
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment variables")
            
        # Initialize Gemini API client
        logger.info("Gemini Chat Client initialized successfully")

    def ask_question(self, 
                    user_question: str, 
                    selected_model: str = "gemini-2.5-flash-lite",
                    image_data: Optional[Union[str, bytes]] = None) -> Dict[str, Any]:
        """
        Ask a question to Gemini AI with optional image input.
        
        Args:
            user_question (str): The text question to ask
            selected_model (str): Model to use (default: gemini-2.5-flash-lite)
            image_data (Union[str, bytes], optional): Base64 string or raw bytes of image
            
        Returns:
            Dict containing:
                - status (str): 'success' or 'error'
                - question (str): Original question
                - answer (str): AI response (if successful)
                - model_used (str): Model that generated the response
                - error (str): Error message (if failed)
                
        Example:
            >>> response = client.ask_question("Explain quantum physics")
            >>> if response['status'] == 'success':
            ...     print(response['answer'])
        """
        try:
            logger.info(f"Processing question with model: {selected_model}")
            logger.info(f"Question: {user_question[:100]}...")
            
            # Create new chat session if needed or model changed
            if self.current_chat is None or self.current_model != selected_model:
                logger.info(f"Creating new chat session with model: {selected_model}")
                model = genai.GenerativeModel(selected_model)
                self.current_chat = model.start_chat(history=[])
                self.current_model = selected_model
            
            # Prepare content for sending - handle text and optional image
            if image_data:
                content_parts = [user_question]
                
                try:
                    # Process image for multimodal input
                    if isinstance(image_data, str):
                        # Remove data URL prefix if present
                        if image_data.startswith('data:image'):
                            image_data = image_data.split(',')[1]
                        
                        # Decode base64 to bytes
                        img_bytes = base64.b64decode(image_data)
                        
                        # Create PIL Image for Gemini
                        pil_image = Image.open(io.BytesIO(img_bytes))
                        content_parts.append(pil_image)
                        
                    elif isinstance(image_data, bytes):
                        # Handle raw bytes - convert to PIL Image
                        pil_image = Image.open(io.BytesIO(image_data))
                        content_parts.append(pil_image)
                        
                except Exception as img_error:
                    logger.error(f"Error processing image: {str(img_error)}")
                    return {
                        'status': 'error',
                        'error': f'Failed to process image: {str(img_error)}'
                    }
                
                # Send multimodal message
                response = self.current_chat.send_message(content_parts)
            else:
                # Send text-only message
                response = self.current_chat.send_message(user_question)
            
            if response.text:
                logger.info(f"Response received: {response.text[:100]}...")
                return {
                    'status': 'success',
                    'question': user_question,
                    'answer': response.text,
                    'model_used': selected_model
                }
            else:
                return {
                    'status': 'error',
                    'error': 'No response generated. Please try a different question.'
                }
                
        except Exception as e:
            logger.error(f"Error in ask_question: {str(e)}")
            
            # Reset chat session on error
            self.current_chat = None
            self.current_model = None
            
            # Provide more specific error messages
            if "API_KEY" in str(e).upper() or "Invalid API key" in str(e) or "api_key" in str(e).lower():
                error_msg = "Invalid or missing Gemini API key. Please check your GEMINI_API_KEY."
            elif "quota" in str(e).lower() or "limit" in str(e).lower() or "429" in str(e):
                error_msg = "API quota exceeded or rate limit reached. Please try again later."
            elif "permission" in str(e).lower() or "forbidden" in str(e).lower():
                error_msg = "Permission denied. Please check your API key permissions."
            else:
                error_msg = f"Failed to process question: {str(e)}"
            
            return {
                'status': 'error',
                'error': error_msg
            }

    def get_chat_history(self) -> Dict[str, Any]:
        """
        Get the current chat conversation history.
        
        Returns:
            Dict containing:
                - status (str): 'success' or 'error'
                - history (List): List of conversation messages
                - error (str): Error message (if failed)
        """
        try:
            if self.current_chat is None:
                return {
                    'status': 'success',
                    'history': []
                }
            
            history = []
            for message in self.current_chat.history:
                history.append({
                    'role': message.role,
                    'text': message.parts[0].text
                })
            
            return {
                'status': 'success',
                'history': history
            }
            
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return {
                'status': 'error',
                'error': f"Failed to get chat history: {str(e)}"
            }

    def reset_chat_session(self) -> Dict[str, str]:
        """
        Reset the current chat session.
        
        Returns:
            Dict with status message
        """
        self.current_chat = None
        self.current_model = None
        logger.info("Chat session reset")
        return {'status': 'success', 'message': 'Chat session reset'}

    def check_api_health(self) -> Dict[str, Any]:
        """
        Check if the Gemini API is accessible and working.
        
        Returns:
            Dict containing health status and API capabilities
        """
        try:
            if not self.api_key:
                return {
                    "status": "unhealthy",
                    "message": "Gemini API client not initialized",
                    "gemini_api": "unavailable"
                }
            
            # Test with a simple generation
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content("Hello, are you working?")
            
            if response.text:
                return {
                    "status": "healthy",
                    "message": "Gemini Chat API is running",
                    "gemini_api": "available",
                    "capabilities": {
                        "text_chat": [
                            "question answering",
                            "multiple model support", 
                            "natural language processing",
                            "conversation memory",
                            "multimodal input"
                        ]
                    },
                    "models": get_available_models(),
                    "model_descriptions": get_model_descriptions()
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Gemini API not responding properly",
                    "gemini_api": "limited"
                }
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"API health check failed: {str(e)}",
                "gemini_api": "error"
            }


def get_available_models() -> List[str]:
    """
    Get list of available Gemini models ordered by performance.
    
    Returns:
        List of model names ordered from fastest to most capable
    """
    return [
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash",
        "gemini-2.5-flash", 
        "gemini-2.0-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash-8b"
    ]


def get_model_descriptions() -> Dict[str, str]:
    """
    Get detailed descriptions for each available model.
    
    Returns:
        Dictionary mapping model names to their descriptions
    """
    return {
        "gemini-2.5-flash-lite": "🚀 Gemini 2.5 Flash Lite (Fastest) - Most optimized for speed and efficiency",
        "gemini-1.5-flash": "⚡ Gemini 1.5 Flash (Fastest) - High-speed, lightweight version",
        "gemini-2.5-flash": "⚡ Gemini 2.5 Flash (Faster) - Advanced model with excellent speed", 
        "gemini-2.0-flash": "💨 Gemini 2.0 Flash (Fast) - Next-gen model with good performance",
        "gemini-2.5-pro": "🧠 Gemini 2.5 Pro (Fast) - Optimized for performance and quality",
        "gemini-1.5-flash-8b": "💨 Gemini 1.5 Flash 8B (Fast) - 8 billion parameter lightweight model"
    }