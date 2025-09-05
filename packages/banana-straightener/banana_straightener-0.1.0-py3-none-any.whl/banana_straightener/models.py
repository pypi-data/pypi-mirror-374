"""Model interfaces and implementations for image generation and evaluation."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
from PIL import Image
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import io
import base64

class BaseModel(ABC):
    """Abstract base class for models."""
    
    @abstractmethod
    def generate_image(self, prompt: str, base_image: Optional[Image.Image] = None) -> Image.Image:
        """Generate an image based on prompt."""
        pass
    
    @abstractmethod
    def evaluate_image(self, image: Image.Image, target_prompt: str) -> Dict[str, Any]:
        """Evaluate if image matches the target prompt."""
        pass

class GeminiModel(BaseModel):
    """Gemini model implementation for generation and evaluation."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-image-preview"):
        """Initialize Gemini model."""
        self.api_key = api_key  # Store API key for new library
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_image(self, prompt: str, base_image: Optional[Image.Image] = None) -> Image.Image:
        """Generate an image using Imagen 3 through Gemini."""
        
        try:
            if base_image:
                generation_prompt = f"""
                Modify this image according to the following instructions: {prompt}
                
                Generate an improved version that better matches the desired outcome.
                Focus on making the specific changes requested while maintaining the overall quality.
                """
                
                response = self.model.generate_content(
                    [generation_prompt, base_image],
                    generation_config=self.generation_config
                )
                
                if hasattr(response, 'images') and response.images:
                    return response.images[0]._pil_image
                else:
                    return self._generate_with_imagen(f"{prompt} (enhanced version)")
            else:
                return self._generate_with_imagen(prompt)
                
        except Exception as e:
            print(f"Generation error: {e}")
            return self._generate_with_imagen(prompt)
    
    def _generate_with_imagen(self, prompt: str) -> Image.Image:
        """Generate image using Gemini 2.5 Flash Image Preview."""
        try:
            # Try the new google-genai approach first
            return self._generate_with_new_api(prompt)
        except ImportError:
            print("google-genai library not available, trying fallback...")
            return self._generate_fallback(prompt)
        except Exception as e:
            print(f"Imagen generation error: {e}")
            return self._create_placeholder_image(prompt)
    
    def _generate_with_new_api(self, prompt: str) -> Image.Image:
        """Generate image using the new google-genai library."""
        from google import genai as new_genai
        from google.genai import types
        import mimetypes
        from io import BytesIO
        
        # Create client with the stored API key
        client = new_genai.Client(api_key=self.api_key)
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )
        
        # Generate and stream response
        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash-image-preview",
            contents=contents,
            config=config,
        ):
            if (chunk.candidates and chunk.candidates[0].content and 
                chunk.candidates[0].content.parts):
                
                part = chunk.candidates[0].content.parts[0]
                if part.inline_data and part.inline_data.data:
                    # Convert bytes back to PIL Image
                    image_data = BytesIO(part.inline_data.data)
                    return Image.open(image_data)
        
        raise Exception("No image data received")
    
    def _generate_fallback(self, prompt: str) -> Image.Image:
        """Fallback method when new library is not available."""
        # For now, create a placeholder that explains the issue
        return self._create_placeholder_image(f"Image generation requires google-genai library. Prompt: {prompt}")
    
    def _create_placeholder_image(self, prompt: str) -> Image.Image:
        """Create a placeholder image when generation fails."""
        from PIL import Image, ImageDraw, ImageFont
        
        width, height = 512, 512
        image = Image.new('RGB', (width, height), color='lightgray')
        draw = ImageDraw.Draw(image)
        
        text = f"Failed to generate:\n{prompt[:50]}..."
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='black', font=font)
        return image
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def evaluate_image(self, image: Image.Image, target_prompt: str) -> Dict[str, Any]:
        """Evaluate if the image matches the target prompt using Gemini."""
        
        evaluation_prompt = f"""
        Analyze this image and determine if it successfully shows: "{target_prompt}"
        
        Provide a structured evaluation:
        1. MATCH: Does it match the intent? (YES/NO)
        2. CONFIDENCE: Rate your confidence from 0.0 to 1.0
        3. CORRECT_ELEMENTS: List what elements are correctly represented
        4. MISSING_ELEMENTS: List what's missing or incorrect
        5. IMPROVEMENTS: Specific improvements needed (be very specific)
        
        Format your response as:
        MATCH: [YES/NO]
        CONFIDENCE: [0.0-1.0]
        CORRECT_ELEMENTS: [list]
        MISSING_ELEMENTS: [list]
        IMPROVEMENTS: [detailed feedback]
        """
        
        try:
            response = self.model.generate_content(
                [evaluation_prompt, image],
                generation_config={"temperature": 0.2}
            )
            
            return self._parse_evaluation(response.text, target_prompt)
        except Exception as e:
            print(f"Evaluation error: {e}")
            return {
                'matches_intent': False,
                'confidence': 0.0,
                'correct_elements': 'Error during evaluation',
                'missing_elements': 'Unable to analyze',
                'improvements': 'Please try again',
                'raw_feedback': f'Evaluation failed: {e}'
            }
    
    def _parse_evaluation(self, response_text: str, target_prompt: str) -> Dict[str, Any]:
        """Parse the evaluation response into structured data."""
        lines = response_text.strip().split('\n')
        evaluation = {
            'matches_intent': False,
            'confidence': 0.0,
            'correct_elements': [],
            'missing_elements': [],
            'improvements': '',
            'raw_feedback': response_text
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('MATCH:'):
                evaluation['matches_intent'] = 'YES' in line.upper()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence_str = line.split(':', 1)[1].strip()
                    confidence_str = confidence_str.replace('%', '')
                    evaluation['confidence'] = min(1.0, max(0.0, float(confidence_str)))
                except (ValueError, IndexError):
                    evaluation['confidence'] = 0.5
            elif line.startswith('CORRECT_ELEMENTS:'):
                evaluation['correct_elements'] = line.split(':', 1)[1].strip()
            elif line.startswith('MISSING_ELEMENTS:'):
                evaluation['missing_elements'] = line.split(':', 1)[1].strip()
            elif line.startswith('IMPROVEMENTS:'):
                evaluation['improvements'] = line.split(':', 1)[1].strip()
        
        if not evaluation['improvements'] and not evaluation['matches_intent']:
            evaluation['improvements'] = f"Please regenerate the image to better match: {target_prompt}"
        
        return evaluation