#!/usr/bin/env python3
"""
Quick isolated test of just the image generation command.
"""

import os
import pytest
from dotenv import load_dotenv

load_dotenv()

def test_image_generation_isolated():
    """Test just the image generation part."""
    print("🎨 QUICK IMAGE GENERATION TEST")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "test-key-from-env-file":
        print("❌ No valid API key found")
        print("🔧 Get one at: https://aistudio.google.com/app/apikey")
        print("💡 Set with: export GEMINI_API_KEY='your-key-here'")
        
        # Skip if running in CI environment without API key
        if os.getenv("CI"):
            pytest.skip("API key not available in CI environment")
        else:
            assert False, "No valid API key found for testing"
    
    print(f"✅ API key found (length: {len(api_key)})")
    
    try:
        from banana_straightener.models import GeminiModel
        model = GeminiModel(api_key=api_key)
        print("✅ Model created successfully")
        
        # Test image generation
        print("🎨 Testing image generation...")
        image = model.generate_image("A simple red circle")
        
        if image:
            image.save("test_generated_image.png")
            print("✅ Image generated and saved as test_generated_image.png")
            assert True  # Test passed
        else:
            print("❌ No image returned")
            assert False, "No image returned from generation"
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        assert False, f"Generation failed: {e}"

if __name__ == "__main__":
    success = test_image_generation_isolated()
    
    if success:
        print("\n🎉 Image generation works!")
    else:
        print("\n⚠️ Image generation needs a real API key to test")
        print("🔗 Get one at: https://aistudio.google.com/app/apikey")