#!/usr/bin/env python3
"""
Test image generation functionality.

This module contains tests for the core image generation capabilities
of the Banana Straightener.
"""

import os
import pytest
from dotenv import load_dotenv
from PIL import Image

from banana_straightener.models import GeminiModel


# Load environment variables
load_dotenv()


class TestImageGeneration:
    """Test image generation functionality."""
    
    def test_api_key_available(self):
        """Test that API key is available."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        assert api_key is not None, "API key must be set for testing"
        assert api_key != "test-key-from-env-file", "Must use real API key"
        assert len(api_key) > 10, "API key seems too short"
    
    def test_model_creation(self):
        """Test that GeminiModel can be created."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "test-key-from-env-file":
            pytest.skip("No valid API key available")
        
        model = GeminiModel(api_key=api_key)
        assert hasattr(model, 'api_key')
        assert hasattr(model, 'model')
        assert model.api_key == api_key
    
    def test_imports_work(self):
        """Test that required imports work."""
        # Test old library
        import google.generativeai as genai
        
        # Test new library
        from google import genai as new_genai
        from google.genai import types
        
        # Test our classes
        from banana_straightener.models import GeminiModel, BaseModel
    
    @pytest.mark.slow
    def test_image_generation(self):
        """Test actual image generation (slow test)."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "test-key-from-env-file":
            pytest.skip("No valid API key available")
        
        model = GeminiModel(api_key=api_key)
        
        # Generate a simple image
        image = model.generate_image("A simple red circle on white background")
        
        assert isinstance(image, Image.Image)
        assert image.size[0] > 0 and image.size[1] > 0
        
        # Save for manual inspection if needed
        image.save("test_output_circle.png")
    
    @pytest.mark.slow  
    def test_image_evaluation(self):
        """Test image evaluation functionality."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "test-key-from-env-file":
            pytest.skip("No valid API key available")
        
        model = GeminiModel(api_key=api_key)
        
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), 'red')
        
        # Evaluate it
        result = model.evaluate_image(test_image, "a red square")
        
        assert isinstance(result, dict)
        assert 'matches_intent' in result
        assert 'confidence' in result
        assert 'improvements' in result
        assert isinstance(result['confidence'], float)
        assert 0.0 <= result['confidence'] <= 1.0