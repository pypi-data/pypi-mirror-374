"""
Image Editing Module
===================

This module provides AI-powered image editing and composition capabilities
using Google's Gemini AI, including prompt-based editing and multi-image composition.

Features:
- Prompt-based image editing and transformation
- Multi-image composition and blending
- Style transfer and artistic effects
- Aspect ratio adjustment and format conversion
- Serverless-ready implementation with base64 I/O

Classes:
    ImageEditor: Main class for image editing operations

Functions:
    edit_image_with_prompt(): Edit images using text prompts
    compose_images_with_prompt(): Compose multiple images into one
"""

import os
import logging
import base64
import uuid
import io
from datetime import datetime
from typing import Dict, Any, Optional, List
from PIL import Image
import google.genai as genai
from google.genai import types

# Configure logging
logger = logging.getLogger(__name__)

# Available styles for image editing
AVAILABLE_STYLES = {
    "photorealistic": "photorealistic style",
    "cartoon": "cartoon style", 
    "abstract": "abstract art style",
    "impressionistic": "impressionist painting style",
    "cyberpunk": "cyberpunk art style",
    "anime": "anime style",
    "oil_painting": "oil painting style",
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


class ImageEditor:
    """
    AI-powered image editing client using Google Gemini AI.
    
    This class provides comprehensive image editing capabilities including
    prompt-based transformations, style transfer, and multi-image composition.
    
    Attributes:
        api_key: Google Gemini API key
        client: Configured Gemini client
        
    Example:
        >>> editor = ImageEditor()
        >>> result = editor.edit_image(image_bytes, "Make it look like a painting")
        >>> edited_image = result['image_base64']
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Image Editor.
        
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
        logger.info("Image Editor initialized successfully")

    def edit_image(self, 
                  image_data: bytes,
                  edit_prompt: str,
                  style: str = "photorealistic",
                  aspect_ratio: str = "1:1",
                  edit_strength: float = 0.7,
                  model: str = "gemini-2.0-flash-preview-image-generation") -> Dict[str, Any]:
        """
        Edit an image using a text prompt.
        
        Args:
            image_data (bytes): Raw image data to edit
            edit_prompt (str): Description of desired edits
            style (str): Target artistic style (default: "photorealistic")
            aspect_ratio (str): Target aspect ratio (default: "1:1")
            edit_strength (float): Edit intensity (0.0-1.0, default: 0.7)
            model (str): Gemini model for editing
            
        Returns:
            Dict containing:
                - status (str): 'success' or 'error'
                - image_base64 (str): Edited image as base64 (if successful)
                - response_text (str): AI description of edits made
                - filename (str): Suggested filename
                - error (str): Error message (if failed)
                
        Example:
            >>> result = editor.edit_image(image_bytes, "Add a rainbow in the sky")
            >>> if result['status'] == 'success':
            ...     edited_image = result['image_base64']
        """
        try:
            # Get style and ratio descriptions
            style_desc = AVAILABLE_STYLES.get(style, AVAILABLE_STYLES["photorealistic"])
            ratio_desc = AVAILABLE_RATIOS.get(aspect_ratio, AVAILABLE_RATIOS["1:1"])
            
            # Create enhanced editing prompt that preserves the original object
            enhanced_prompt = f"Edit this image: {edit_prompt}, {style_desc}, {ratio_desc}"
            
            logger.info(f"Starting image editing with prompt: {edit_prompt}")
            logger.info(f"Style: {style} ({style_desc})")
            logger.info(f"Aspect ratio: {aspect_ratio} ({ratio_desc})")
            logger.info(f"Edit strength: {edit_strength}")
            
            # Generate unique identifier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            image_filename = f"edited_image_{timestamp}_{unique_id}.png"
            
            # Call Gemini API for image editing with proper image passing
            response = self.client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type="image/jpeg",
                    ),
                    enhanced_prompt
                ],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE'],
                    temperature=0.8,
                    max_output_tokens=16384
                )
            )
            
            if not response.candidates:
                logger.error("No candidates returned from Gemini API for image editing")
                return {
                    'status': 'error',
                    'error': 'No edited image generated by the API. Please try a different prompt or image.'
                }
            
            # Process the response
            content = response.candidates[0].content
            if not content or not content.parts:
                logger.error("No content or parts in API response for image editing")
                return {
                    'status': 'error',
                    'error': 'Invalid response from image editing API'
                }
            
            image_data_bytes = None
            response_text = None
            
            # Extract image data and text from response
            for part in content.parts:
                if part.text:
                    response_text = part.text
                    logger.info(f"API response text: {part.text}")
                elif part.inline_data and part.inline_data.data:
                    image_data_bytes = part.inline_data.data
                    logger.info(f"Edited image generated successfully with ID: {unique_id}")
            
            if image_data_bytes is None:
                logger.error("No image data found in API response for editing")
                return {
                    'status': 'error',
                    'error': 'No edited image data received from the API. The model may not support this edit.'
                }
            
            # Encode the image data to Base64
            image_base64 = base64.b64encode(image_data_bytes).decode('utf-8')
            
            return {
                'status': 'success',
                'image_base64': image_base64,
                'response_text': response_text,
                'filename': image_filename,
                'edit_prompt': edit_prompt,
                'style': style,
                'aspect_ratio': aspect_ratio
            }
            
        except Exception as e:
            logger.error(f"Error in edit_image: {str(e)}")
            
            # Provide specific error messages
            if "API_KEY" in str(e).upper():
                error_msg = "Invalid or missing Gemini API key. Please check your GEMINI_API_KEY."
            elif "quota" in str(e).lower() or "limit" in str(e).lower():
                error_msg = "API quota exceeded or rate limit reached. Please try again later."
            elif "permission" in str(e).lower() or "forbidden" in str(e).lower():
                error_msg = "Permission denied. Please check your API key permissions."
            else:
                error_msg = f"Failed to edit image: {str(e)}"
            
            return {
                'status': 'error',
                'error': error_msg
            }

    def compose_images(self, 
                      images_data: List[bytes],
                      composition_prompt: str,
                      style: str = "photorealistic",
                      aspect_ratio: str = "1:1",
                      model: str = "gemini-2.5-flash") -> Dict[str, Any]:
        """
        Compose multiple images into one using AI guidance.
        
        Args:
            images_data (List[bytes]): List of image data to compose
            composition_prompt (str): Description of how to combine images
            style (str): Target artistic style
            aspect_ratio (str): Target aspect ratio
            model (str): Gemini model for composition
            
        Returns:
            Dict containing composition results or error information
            
        Example:
            >>> result = editor.compose_images([img1_bytes, img2_bytes], 
            ...                               "Blend these images together")
        """
        try:
            # Get style and ratio descriptions
            style_desc = AVAILABLE_STYLES.get(style, AVAILABLE_STYLES["photorealistic"])
            ratio_desc = AVAILABLE_RATIOS.get(aspect_ratio, AVAILABLE_RATIOS["1:1"])
            
            # Create enhanced composition prompt
            enhanced_prompt = f"Analyze and describe how to compose these {len(images_data)} images: {composition_prompt}. Style: {style_desc}. Format: {ratio_desc}."
            
            logger.info(f"Starting image composition with prompt: {composition_prompt}")
            logger.info(f"Number of input images: {len(images_data)}")
            logger.info(f"Style: {style} ({style_desc})")
            
            # Generate unique identifier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            image_filename = f"composed_image_{timestamp}_{unique_id}.png"
            
            # Convert all images to PIL Images
            pil_images = []
            for image_data in images_data:
                pil_image = Image.open(io.BytesIO(image_data))
                pil_images.append(pil_image)
            
            # Create content for Gemini API
            content_parts = [enhanced_prompt] + pil_images
            
            # Use the client to generate composition analysis
            response = self.client.models.generate_content(
                model=model,
                contents=content_parts
            )
            
            if not response or not response.text:
                logger.error("No response from Gemini API for image composition")
                return {
                    'status': 'error',
                    'error': 'No composition analysis generated by the API. Please try different images or prompt.'
                }
            
            return {
                'status': 'success',
                'analysis': response.text,
                'filename': image_filename,
                'composition_prompt': composition_prompt,
                'style': style,
                'aspect_ratio': aspect_ratio,
                'num_images': len(images_data)
            }
            
        except Exception as e:
            logger.error(f"Error in compose_images: {str(e)}")
            
            # Provide specific error messages
            if "API_KEY" in str(e).upper():
                error_msg = "Invalid or missing Gemini API key. Please check your GEMINI_API_KEY."
            elif "quota" in str(e).lower() or "limit" in str(e).lower():
                error_msg = "API quota exceeded or rate limit reached. Please try again later."
            elif "permission" in str(e).lower() or "forbidden" in str(e).lower():
                error_msg = "Permission denied. Please check your API key permissions."
            else:
                error_msg = f"Failed to compose images: {str(e)}"
            
            return {
                'status': 'error',
                'error': error_msg
            }

    def get_available_styles(self) -> Dict[str, str]:
        """Get available artistic styles for image editing."""
        return AVAILABLE_STYLES.copy()

    def get_available_ratios(self) -> Dict[str, str]:
        """Get available aspect ratios for image editing."""
        return AVAILABLE_RATIOS.copy()


def edit_image_with_prompt(image_data: bytes, 
                          edit_prompt: str,
                          style: str = "photorealistic",
                          aspect_ratio: str = "1:1",
                          edit_strength: float = 0.7,
                          api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to edit an image with a text prompt.
    
    Args:
        image_data (bytes): Image data to edit
        edit_prompt (str): Description of desired edits
        style (str): Target artistic style
        aspect_ratio (str): Target aspect ratio
        edit_strength (float): Edit intensity (0.0-1.0)
        api_key (str, optional): API key for authentication
        
    Returns:
        Dict containing editing results or error information
        
    Example:
        >>> result = edit_image_with_prompt(image_bytes, "Make it more colorful")
        >>> print(result['status'])
    """
    try:
        editor = ImageEditor(api_key)
        return editor.edit_image(image_data, edit_prompt, style, aspect_ratio, edit_strength)
    except Exception as e:
        logger.error(f"Error in edit_image_with_prompt: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


def compose_images_with_prompt(images_data: List[bytes],
                              composition_prompt: str,
                              style: str = "photorealistic",
                              aspect_ratio: str = "1:1",
                              api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to compose multiple images using AI guidance.
    
    Args:
        images_data (List[bytes]): List of image data to compose
        composition_prompt (str): Description of how to combine images
        style (str): Target artistic style
        aspect_ratio (str): Target aspect ratio
        api_key (str, optional): API key for authentication
        
    Returns:
        Dict containing composition results or error information
        
    Example:
        >>> result = compose_images_with_prompt([img1, img2], "Merge into collage")
        >>> print(result['analysis'])
    """
    try:
        editor = ImageEditor(api_key)
        return editor.compose_images(images_data, composition_prompt, style, aspect_ratio)
    except Exception as e:
        logger.error(f"Error in compose_images_with_prompt: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }