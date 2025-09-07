"""Configuration management for Banana Straightener."""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load .env file from current directory or parent directories
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

@dataclass
class Config:
    """Configuration for Banana Straightener."""
    
    api_key: Optional[str] = None
    generator_model: str = "gemini-2.5-flash-image-preview"
    evaluator_model: str = "gemini-2.5-flash-image-preview"
    
    default_max_iterations: int = 5
    success_threshold: float = 0.85
    save_intermediates: bool = False
    output_dir: Path = Path("./outputs")
    
    evaluation_prompt_template: str = """
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
    
    gradio_port: int = 7860
    gradio_share: bool = False
    
    def __post_init__(self):
        """Initialize configuration after dataclass creation."""
        if not self.api_key:
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables and .env files."""
        return cls(
            api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
            generator_model=os.getenv("GENERATOR_MODEL", "gemini-2.5-flash-image-preview"),
            evaluator_model=os.getenv("EVALUATOR_MODEL", "gemini-2.5-flash-image-preview"),
            default_max_iterations=int(os.getenv("MAX_ITERATIONS", "5")),
            success_threshold=float(os.getenv("SUCCESS_THRESHOLD", "0.85")),
            save_intermediates=os.getenv("SAVE_INTERMEDIATES", "false").lower() == "true",
            output_dir=Path(os.getenv("OUTPUT_DIR", "./outputs")),
            gradio_port=int(os.getenv("GRADIO_PORT", "7860")),
            gradio_share=os.getenv("GRADIO_SHARE", "false").lower() == "true",
        )
    
    def get_api_key_source(self) -> str:
        """Get information about where the API key was loaded from."""
        if not self.api_key:
            return "Not found"
        
        # Check if .env file exists and contains the API key
        dotenv_path = find_dotenv()
        if dotenv_path:
            try:
                with open(dotenv_path, 'r') as f:
                    content = f.read()
                    if 'GEMINI_API_KEY=' in content or 'GOOGLE_API_KEY=' in content:
                        # Check if the value from .env matches what we have
                        from dotenv import dotenv_values
                        env_values = dotenv_values(dotenv_path)
                        env_key = env_values.get('GEMINI_API_KEY') or env_values.get('GOOGLE_API_KEY')
                        if env_key and env_key == self.api_key:
                            return f".env file ({dotenv_path})"
            except Exception:
                pass
        
        # Check if it came from environment variables  
        if os.getenv("GEMINI_API_KEY") == self.api_key:
            return "Environment variable (GEMINI_API_KEY)"
        elif os.getenv("GOOGLE_API_KEY") == self.api_key:
            return "Environment variable (GOOGLE_API_KEY)"
        
        return "Configuration parameter"