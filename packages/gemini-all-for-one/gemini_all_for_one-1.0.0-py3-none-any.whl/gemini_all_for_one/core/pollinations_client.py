"""
Pollinations AI Client Module
============================

This module provides high-quality image and text generation using the Pollinations.ai API,
featuring multiple models and no API key requirement.

Features:
- High-quality image generation using Flux models
- Multiple artistic styles and models (Flux, Flux-Realism, Flux-Anime, etc.)
- Text generation capabilities
- No API key required
- Customizable parameters (dimensions, seeds, enhancement)
- Serverless-ready with base64 output

Classes:
    PollinationsClient: Main client for Pollinations.ai API

Functions:
    generate_image_pollinations(): Generate images using Pollinations.ai
    generate_text_pollinations(): Generate text using Pollinations.ai
"""

import requests
import logging
import uuid
import base64
from datetime import datetime
from urllib.parse import quote
from typing import Dict, Any, Optional, List

# Configure logging
logger = logging.getLogger(__name__)

# Pollinations API endpoints
POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"
POLLINATIONS_TEXT_URL = "https://text.pollinations.ai"

# Available models
AVAILABLE_IMAGE_MODELS = [
    "flux",
    "flux-realism", 
    "flux-anime",
    "flux-3d",
    "any-dark",
    "flux-pro"
]

AVAILABLE_TEXT_MODELS = [
    "openai",
    "mistral",
    "claude"
]


class PollinationsClient:
    """
    High-quality image and text generation client using Pollinations.ai API.
    
    This client provides access to advanced Flux models for image generation
    and various language models for text generation, without requiring API keys.
    
    Attributes:
        base_url: Pollinations API base URL
        text_url: Pollinations text API URL
        
    Example:
        >>> client = PollinationsClient()
        >>> result = client.generate_image("A beautiful landscape")
        >>> image_data = result['image_base64']
    """
    
    def __init__(self):
        """Initialize the Pollinations AI Client."""
        self.base_url = POLLINATIONS_BASE_URL
        self.text_url = POLLINATIONS_TEXT_URL
        logger.info("Pollinations AI Client initialized successfully")

    def generate_image(self,
                      prompt: str,
                      width: int = 1024,
                      height: int = 1024,
                      seed: Optional[int] = None,
                      model: str = "flux",
                      enhance: bool = True,
                      safe: bool = True) -> Dict[str, Any]:
        """
        Generate high-quality images using Pollinations.ai API.
        
        Args:
            prompt (str): Text description for image generation
            width (int): Image width in pixels (default: 1024)
            height (int): Image height in pixels (default: 1024)
            seed (int, optional): Random seed for reproducible results
            model (str): Model to use (flux, flux-realism, flux-anime, etc.)
            enhance (bool): Whether to enhance the prompt automatically
            safe (bool): Whether to use safe content filtering
            
        Returns:
            Dict containing:
                - status (str): 'success' or 'error'
                - image_base64 (str): Base64 encoded image (if successful)
                - filename (str): Suggested filename
                - provider (str): 'pollinations.ai'
                - model (str): Model used
                - parameters (Dict): Generation parameters
                - error (str): Error message (if failed)
                
        Example:
            >>> result = client.generate_image("A serene mountain lake at sunset")
            >>> if result['status'] == 'success':
            ...     image_data = result['image_base64']
        """
        try:
            # URL encode the prompt
            encoded_prompt = quote(prompt)
            
            # Build the API URL
            api_url = f"{self.base_url}/{encoded_prompt}"
            
            # Prepare parameters
            params = {
                "width": width,
                "height": height,
                "model": model,
                "enhance": str(enhance).lower(),
                "safe": str(safe).lower()
            }
            
            if seed is not None:
                params["seed"] = seed
            
            logger.info(f"Generating image with Pollinations.ai: {prompt}")
            logger.info(f"Model: {model}, Dimensions: {width}x{height}")
            
            # Make request to Pollinations API
            response = requests.get(api_url, params=params, timeout=60)
            response.raise_for_status()
            
            # Generate unique identifier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            image_filename = f"pollinations_image_{timestamp}_{unique_id}.png"
            
            # Encode image to base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            
            logger.info(f"Image generated successfully with ID: {unique_id}")
            
            return {
                'status': 'success',
                'image_base64': image_base64,
                'filename': image_filename,
                'provider': 'pollinations.ai',
                'model': model,
                'prompt': prompt,
                'parameters': params
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f'Failed to generate image from Pollinations.ai: {str(e)}'
            logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'provider': 'pollinations.ai'
            }
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            logger.error(f"Error in generate_image: {error_msg}")
            return {
                'status': 'error', 
                'error': error_msg,
                'provider': 'pollinations.ai'
            }

    def generate_text(self,
                     prompt: str,
                     model: str = "openai",
                     system: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate text using Pollinations.ai text API.
        
        Args:
            prompt (str): Text prompt for generation
            model (str): Model to use (openai, mistral, claude)
            system (str, optional): System prompt for context
            
        Returns:
            Dict containing:
                - status (str): 'success' or 'error'
                - text (str): Generated text (if successful)
                - provider (str): 'pollinations.ai'
                - model (str): Model used
                - error (str): Error message (if failed)
                
        Example:
            >>> result = client.generate_text("Write a haiku about nature")
            >>> if result['status'] == 'success':
            ...     print(result['text'])
        """
        try:
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "model": model
            }
            
            if system:
                payload["messages"].insert(0, {"role": "system", "content": system})
            
            logger.info(f"Generating text with Pollinations.ai: {prompt[:50]}...")
            logger.info(f"Model: {model}")
            
            response = requests.post(
                self.text_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            
            result_text = response.text.strip()
            
            logger.info("Text generated successfully")
            
            return {
                'status': 'success',
                'text': result_text,
                'provider': 'pollinations.ai',
                'model': model,
                'prompt': prompt
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f'Failed to generate text from Pollinations.ai: {str(e)}'
            logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'provider': 'pollinations.ai'
            }
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            logger.error(f"Error in generate_text: {error_msg}")
            return {
                'status': 'error',
                'error': error_msg,
                'provider': 'pollinations.ai'
            }

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models for image and text generation."""
        return {
            "image_models": AVAILABLE_IMAGE_MODELS.copy(),
            "text_models": AVAILABLE_TEXT_MODELS.copy()
        }

    def get_aspect_ratio_dimensions(self, aspect_ratio: str) -> Dict[str, int]:
        """
        Convert aspect ratio string to width/height dimensions.
        
        Args:
            aspect_ratio (str): Aspect ratio (e.g., "16:9", "1:1")
            
        Returns:
            Dict with width and height dimensions
        """
        ratio_map = {
            "1:1": {"width": 1024, "height": 1024},
            "16:9": {"width": 1024, "height": 576},
            "9:16": {"width": 576, "height": 1024},
            "4:3": {"width": 1024, "height": 768},
            "3:4": {"width": 768, "height": 1024}
        }
        
        return ratio_map.get(aspect_ratio, {"width": 1024, "height": 1024})


def generate_image_pollinations(prompt: str,
                               width: int = 1024,
                               height: int = 1024,
                               seed: Optional[int] = None,
                               model: str = "flux",
                               enhance: bool = True,
                               safe: bool = True) -> Dict[str, Any]:
    """
    Convenience function to generate an image using Pollinations.ai.
    
    Args:
        prompt (str): Text description for image generation
        width (int): Image width (default: 1024)
        height (int): Image height (default: 1024)
        seed (int, optional): Random seed for reproducible results
        model (str): Model to use (default: "flux")
        enhance (bool): Whether to enhance the prompt
        safe (bool): Whether to use safe content filtering
        
    Returns:
        Dict containing generation results or error information
        
    Example:
        >>> result = generate_image_pollinations("A cosmic nebula in space")
        >>> print(result['status'])
    """
    client = PollinationsClient()
    return client.generate_image(prompt, width, height, seed, model, enhance, safe)


def generate_text_pollinations(prompt: str,
                              model: str = "openai",
                              system: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to generate text using Pollinations.ai.
    
    Args:
        prompt (str): Text prompt for generation
        model (str): Model to use (default: "openai")
        system (str, optional): System prompt for context
        
    Returns:
        Dict containing text generation results or error information
        
    Example:
        >>> result = generate_text_pollinations("Explain quantum computing")
        >>> print(result['text'])
    """
    client = PollinationsClient()
    return client.generate_text(prompt, model, system)


def get_available_models() -> Dict[str, List[str]]:
    """Get list of available models for Pollinations.ai."""
    return {
        "image_models": AVAILABLE_IMAGE_MODELS.copy(),
        "text_models": AVAILABLE_TEXT_MODELS.copy()
    }


def get_aspect_ratio_dimensions(aspect_ratio: str) -> Dict[str, int]:
    """Convert aspect ratio string to width/height dimensions."""
    client = PollinationsClient()
    return client.get_aspect_ratio_dimensions(aspect_ratio)