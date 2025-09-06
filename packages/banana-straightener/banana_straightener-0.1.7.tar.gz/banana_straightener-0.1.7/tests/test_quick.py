#!/usr/bin/env python3
"""
Quick tests that can run without API key.

These tests verify basic functionality and imports without making API calls.
"""

import pytest
from PIL import Image

from banana_straightener import Config
from banana_straightener.models import GeminiModel, BaseModel


class TestQuick:
    """Quick tests that don't require API calls."""
    
    def test_imports(self):
        """Test that all main imports work."""
        from banana_straightener import BananaStraightener, Config
        from banana_straightener.models import GeminiModel
        from banana_straightener.cli import main
        from banana_straightener.ui import create_interface
        
        # Basic checks
        assert BananaStraightener is not None
        assert Config is not None
        assert GeminiModel is not None
        assert callable(main)
        assert callable(create_interface)
    
    def test_config_creation(self):
        """Test Config creation with defaults."""
        config = Config()
        
        assert config.generator_model == "gemini-2.5-flash-image-preview"
        assert config.evaluator_model == "gemini-2.5-flash-image-preview"
        assert config.default_max_iterations == 5
        assert config.success_threshold == 0.85
        assert config.gradio_port == 7860
    
    def test_config_with_params(self):
        """Test Config creation with custom parameters."""
        config = Config(
            api_key="test-key",
            default_max_iterations=3,
            success_threshold=0.9
        )
        
        assert config.api_key == "test-key"
        assert config.default_max_iterations == 3
        assert config.success_threshold == 0.9
    
    def test_model_inheritance(self):
        """Test model class hierarchy."""
        assert issubclass(GeminiModel, BaseModel)
        
        # Test abstract methods exist
        assert hasattr(BaseModel, 'generate_image')
        assert hasattr(BaseModel, 'evaluate_image')
    
    def test_model_creation_with_dummy_key(self):
        """Test model creation with dummy key (no API calls)."""
        model = GeminiModel(api_key="dummy-key-for-testing")
        
        assert hasattr(model, 'api_key')
        assert hasattr(model, 'model')
        assert hasattr(model, 'generation_config')
        assert model.api_key == "dummy-key-for-testing"
    
    def test_placeholder_image_creation(self):
        """Test placeholder image creation."""
        model = GeminiModel(api_key="dummy-key")
        
        # Test the private method that creates placeholder images
        placeholder = model._create_placeholder_image("test prompt")
        
        assert isinstance(placeholder, Image.Image)
        assert placeholder.size == (512, 512)
        assert placeholder.mode == 'RGB'
    
    def test_external_libraries_available(self):
        """Test that required external libraries are available."""
        # Test Google libraries
        import google.generativeai as genai
        from google import genai as new_genai
        from google.genai import types
        
        # Test other dependencies  
        import click
        import gradio as gr
        import rich
        from PIL import Image
        from tenacity import retry
        from dotenv import load_dotenv