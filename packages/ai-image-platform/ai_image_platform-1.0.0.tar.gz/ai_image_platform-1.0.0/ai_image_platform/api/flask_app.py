"""
Flask API Application
====================

Main Flask application providing RESTful API endpoints for the AI Image Platform.
Supports image analysis, generation, editing, and multimodal chat capabilities.

This module creates a comprehensive Flask application with:
- Multi-provider image generation (Gemini AI, Pollinations.ai)
- Advanced image analysis and understanding
- AI-powered image editing and composition
- Multimodal chat with conversation history
- Health monitoring and status endpoints
- Comprehensive error handling and logging
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, session
from werkzeug.middleware.proxy_fix import ProxyFix
import base64
import io

# Import core modules
from ..core.gemini_chat import GeminiChatClient
from ..core.image_analysis import ImageAnalyzer, analyze_base64_image, analyze_url_image
from ..core.image_generation import ImageGenerator, generate_image_from_text
from ..core.image_editing import ImageEditor, edit_image_with_prompt, compose_images_with_prompt
from ..core.pollinations_client import PollinationsClient, generate_image_pollinations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config (dict, optional): Configuration dictionary
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai_image_platform_secret_key_2024')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Apply configuration if provided
    if config:
        app.config.update(config)
    
    # Add proxy fix for production deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Initialize clients
    try:
        gemini_chat_client = GeminiChatClient()
        image_analyzer = ImageAnalyzer()
        image_generator = ImageGenerator()
        image_editor = ImageEditor()
        pollinations_client = PollinationsClient()
        logger.info("All AI clients initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing AI clients: {str(e)}")
        # Continue without clients - they'll be initialized per request if needed

    @app.route('/')
    def index():
        """Serve the main application interface."""
        return render_template('index.html')

    @app.route('/docs')
    def documentation():
        """Serve the API documentation."""
        return render_template('docs.html')

    @app.route('/api/health')
    def health_check():
        """
        Health check endpoint for monitoring service status.
        
        Returns:
            JSON response with service health information
        """
        try:
            # Check Gemini API health
            try:
                chat_client = GeminiChatClient()
                gemini_health = chat_client.check_api_health()
            except:
                gemini_health = {"status": "unhealthy", "gemini_api": "unavailable"}
            
            # Check Pollinations API health (simple ping)
            try:
                pollinations_health = {
                    "status": "healthy",
                    "pollinations_api": "available",
                    "message": "Pollinations API is accessible"
                }
            except:
                pollinations_health = {"status": "unhealthy", "pollinations_api": "unavailable"}
            
            return jsonify({
                "status": "healthy",
                "message": "AI Image Platform API is running",
                "services": {
                    "gemini": gemini_health,
                    "pollinations": pollinations_health
                },
                "endpoints": {
                    "chat": "/api/chat",
                    "image_analysis": "/api/analyze-image",
                    "image_generation": {
                        "gemini": "/api/generate-image",
                        "pollinations": "/api/pollinations/generate-image"
                    },
                    "image_editing": "/api/edit-image"
                }
            })
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 500

    @app.route('/api/chat', methods=['POST'])
    def chat_endpoint():
        """
        Multimodal chat endpoint supporting text and image inputs.
        
        Expected JSON payload:
            {
                "question": "Your question here",
                "model": "gemini-2.5-flash-lite",
                "image_data": "base64_image_data" (optional)
            }
            
        Returns:
            JSON response with chat answer or error
        """
        try:
            data = request.get_json()
            if not data or 'question' not in data:
                return jsonify({'error': 'Question is required'}), 400
            
            question = data['question']
            selected_model = data.get('model', 'gemini-2.5-flash-lite')
            image_data = data.get('image_data')
            
            # Initialize chat client
            chat_client = GeminiChatClient()
            
            # Ask question with optional image
            result = chat_client.ask_question(question, selected_model, image_data)
            
            if result['status'] == 'success':
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analyze-image', methods=['POST'])
    def analyze_image_endpoint():
        """
        Image analysis endpoint supporting base64 and URL inputs.
        
        Expected JSON payload:
            {
                "image_data": "base64_image_data",
                "image_url": "http://example.com/image.jpg",
                "extract_masks": false
            }
            
        Returns:
            JSON response with image analysis
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request data is required'}), 400
            
            extract_masks = data.get('extract_masks', False)
            
            if 'image_data' in data:
                # Analyze base64 image
                result = analyze_base64_image(data['image_data'], extract_masks)
            elif 'image_url' in data:
                # Analyze image from URL
                result = analyze_url_image(data['image_url'], extract_masks)
            else:
                return jsonify({'error': 'Either image_data or image_url is required'}), 400
            
            if result.get('status') == 'success':
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"Error in analyze_image endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate-image', methods=['POST'])
    def generate_image_endpoint():
        """
        Gemini image generation endpoint.
        
        Expected JSON payload:
            {
                "prompt": "A beautiful landscape",
                "style": "photorealistic",
                "aspect_ratio": "16:9"
            }
            
        Returns:
            JSON response with generated image (base64)
        """
        try:
            data = request.get_json()
            if not data or 'prompt' not in data:
                return jsonify({'error': 'Prompt is required'}), 400
            
            prompt = data['prompt']
            style = data.get('style', 'photorealistic')
            aspect_ratio = data.get('aspect_ratio', '1:1')
            
            # Generate image using Gemini
            result = generate_image_from_text(prompt, style, aspect_ratio)
            
            if result['status'] == 'success':
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"Error in generate_image endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/pollinations/generate-image', methods=['POST'])
    def pollinations_generate_image_endpoint():
        """
        Pollinations.ai image generation endpoint.
        
        Expected JSON payload:
            {
                "prompt": "A cosmic nebula",
                "width": 1024,
                "height": 1024,
                "model": "flux",
                "enhance": true,
                "seed": 12345 (optional)
            }
            
        Returns:
            JSON response with generated image (base64)
        """
        try:
            data = request.get_json()
            if not data or 'prompt' not in data:
                return jsonify({'error': 'Prompt is required'}), 400
            
            prompt = data['prompt']
            width = data.get('width', 1024)
            height = data.get('height', 1024)
            model = data.get('model', 'flux')
            enhance = data.get('enhance', True)
            seed = data.get('seed')
            
            # Generate image using Pollinations.ai
            result = generate_image_pollinations(prompt, width, height, seed, model, enhance)
            
            if result['status'] == 'success':
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"Error in pollinations generate_image endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/edit-image', methods=['POST'])
    def edit_image_endpoint():
        """
        AI image editing endpoint.
        
        Expected JSON payload:
            {
                "image_data": "base64_image_data",
                "edit_prompt": "Make it more colorful",
                "style": "photorealistic",
                "aspect_ratio": "1:1"
            }
            
        Returns:
            JSON response with edited image or analysis
        """
        try:
            data = request.get_json()
            if not data or 'image_data' not in data or 'edit_prompt' not in data:
                return jsonify({'error': 'image_data and edit_prompt are required'}), 400
            
            image_data = data['image_data']
            edit_prompt = data['edit_prompt']
            style = data.get('style', 'photorealistic')
            aspect_ratio = data.get('aspect_ratio', '1:1')
            
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Edit image
            result = edit_image_with_prompt(image_bytes, edit_prompt, style, aspect_ratio)
            
            if result.get('status') in ['success', 'partial_success']:
                return jsonify(result)
            else:
                return jsonify(result), 500
                
        except Exception as e:
            logger.error(f"Error in edit_image endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({'error': 'Internal server error'}), 500

    return app


# For backwards compatibility with existing main.py
app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)