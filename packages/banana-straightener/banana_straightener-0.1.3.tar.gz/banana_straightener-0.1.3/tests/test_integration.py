#!/usr/bin/env python3
"""
Integration tests for Banana Straightener.

Tests that verify the complete workflow and CLI functionality.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from dotenv import load_dotenv

from banana_straightener import BananaStraightener, Config


# Load environment variables
load_dotenv()


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_config_from_env(self):
        """Test configuration loading from environment."""
        config = Config.from_env()
        
        assert config is not None
        assert hasattr(config, 'api_key')
        assert hasattr(config, 'generator_model')
        assert hasattr(config, 'evaluator_model')
    
    def test_config_api_key_detection(self):
        """Test API key source detection."""
        config = Config.from_env()
        source = config.get_api_key_source()
        
        assert isinstance(source, str)
        assert len(source) > 0
    
    def test_banana_straightener_creation(self):
        """Test BananaStraightener can be created."""
        config = Config.from_env()
        
        # Skip if no API key in CI environment
        if not config.api_key and os.getenv("CI"):
            pytest.skip("API key not available in CI environment")
        
        # For CI without API keys, create a dummy config
        if not config.api_key:
            config.api_key = "dummy-key-for-testing"
            
        try:
            agent = BananaStraightener(config)
            
            assert agent is not None
            assert hasattr(agent, 'config')
            assert hasattr(agent, 'generator')
            assert hasattr(agent, 'evaluator')
        except Exception as e:
            if "API key" in str(e) and os.getenv("CI"):
                pytest.skip(f"Skipping due to API key requirement in CI: {e}")
            else:
                raise
    
    @pytest.mark.slow
    def test_complete_workflow(self):
        """Test complete image generation workflow."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "test-key-from-env-file":
            pytest.skip("No valid API key available")
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(
                api_key=api_key,
                output_dir=Path(temp_dir),
                default_max_iterations=2,  # Keep it fast
                success_threshold=0.7,     # Lower threshold for testing
                save_intermediates=True
            )
            
            agent = BananaStraightener(config)
            
            # Test straightening
            result = agent.straighten("A simple blue square")
            
            assert isinstance(result, dict)
            assert 'success' in result
            assert 'iterations' in result
            assert 'session_dir' in result
            assert result['iterations'] > 0
            
            # Check that files were created
            session_dir = Path(result['session_dir'])
            assert session_dir.exists()
            
            # Check for some expected files
            files = list(session_dir.glob('*'))
            assert len(files) > 0
    
    def test_cli_imports(self):
        """Test that CLI components can be imported."""
        from banana_straightener.cli import main
        from banana_straightener.ui import create_interface
        
        # Basic smoke test - just ensure imports work
        assert callable(main)
        assert callable(create_interface)