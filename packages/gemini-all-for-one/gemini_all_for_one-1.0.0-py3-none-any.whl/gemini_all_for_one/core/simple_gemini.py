"""
Simple Gemini Client for direct API calls
"""
import os
import logging
import base64
import io
from typing import Dict, Any, Optional, Union
from PIL import Image
import google.genai as genai

logger = logging.getLogger(__name__)

class SimpleGeminiClient:
    """Simple Gemini client that works with the current API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided")
        self.client = genai.Client(api_key=self.api_key)
        logger.info("Simple Gemini client initialized")
    
    def chat(self, message: str, model: str = "gemini-2.5-flash-lite", image_data: Optional[str] = None) -> Dict[str, Any]:
        """Simple chat method"""
        try:
            contents = [message]
            
            if image_data:
                # Handle image data
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                pil_image = Image.open(io.BytesIO(image_bytes))
                contents.append(pil_image)
            
            response = self.client.models.generate_content(
                model=model,
                contents=contents
            )
            
            if response and response.text:
                return {
                    'status': 'success',
                    'answer': response.text,
                    'model_used': model
                }
            else:
                return {
                    'status': 'error',
                    'error': 'No response from AI'
                }
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                'status': 'error',
                'error': f'Chat failed: {str(e)}'
            }
    
    def analyze_image(self, image_data: Union[str, bytes], prompt: str = "Analyze this image in detail") -> Dict[str, Any]:
        """Simple image analysis"""
        try:
            if isinstance(image_data, str):
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, pil_image]
            )
            
            if response and response.text:
                return {
                    'status': 'success',
                    'analysis': response.text
                }
            else:
                return {
                    'status': 'error',
                    'error': 'No analysis result'
                }
                
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {
                'status': 'error',
                'error': f'Analysis failed: {str(e)}'
            }

    def edit_image(self, image_bytes: bytes, edit_prompt: str, edit_strength: float = 0.7) -> Dict[str, Any]:
        """Simple image editing"""
        try:
            # For now, return an error since Gemini image editing requires specific models
            return {
                'status': 'error',
                'error': 'Image editing with Gemini requires specialized model setup that is not available in this demo'
            }
        except Exception as e:
            logger.error(f"Edit error: {e}")
            return {
                'status': 'error',
                'error': f'Edit failed: {str(e)}'
            }