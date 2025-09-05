"""Utility functions for Banana Straightener."""

from typing import Union, Optional
from pathlib import Path
from PIL import Image
import base64
import io
from datetime import datetime

def load_image(image_path: Union[str, Path]) -> Image.Image:
    """Load an image from file path."""
    return Image.open(image_path).convert("RGB")

def save_image(image: Image.Image, path: Union[str, Path]) -> Path:
    """Save an image to file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG", optimize=True, quality=95)
    return path

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def base64_to_image(base64_string: str) -> Image.Image:
    """Convert base64 string to PIL Image."""
    image_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_data))

def enhance_prompt_with_feedback(
    original_prompt: str,
    feedback: str,
    iteration: int
) -> str:
    """
    Enhance the prompt based on evaluation feedback.
    
    This function creates a more specific prompt by incorporating
    the feedback from the previous iteration.
    """
    if not feedback or feedback.lower() in ['none', 'n/a', 'none needed!']:
        return original_prompt
    
    enhanced = f"""
    Original request: {original_prompt}
    
    Iteration {iteration} - Please address these specific improvements:
    {feedback}
    
    Generate an image that fixes these issues while maintaining the original intent.
    Focus particularly on correcting the identified problems.
    """.strip()
    
    return enhanced

def create_iteration_report(
    iteration: int,
    evaluation: dict,
    prompt_used: str
) -> str:
    """Create a human-readable report for an iteration."""
    status = "✅ SUCCESS" if evaluation.get('matches_intent', False) else "⚠️ NEEDS WORK"
    confidence = evaluation.get('confidence', 0.0)
    
    report = f"""
    🔄 Iteration {iteration} - {status}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📝 Prompt: {prompt_used[:100]}{'...' if len(prompt_used) > 100 else ''}
    📊 Confidence: {confidence:.1%}
    
    ✓ Correct Elements:
    {evaluation.get('correct_elements', 'N/A')}
    
    ✗ Missing/Incorrect:
    {evaluation.get('missing_elements', 'N/A')}
    
    💡 Next Steps:
    {evaluation.get('improvements', 'None - looks perfect!')}
    """
    return report.strip()

def calculate_prompt_similarity(prompt1: str, prompt2: str) -> float:
    """Calculate similarity between two prompts (simple version)."""
    words1 = set(prompt1.lower().split())
    words2 = set(prompt2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union) if union else 0.0

def format_time_elapsed(start_time: datetime) -> str:
    """Format elapsed time in a human-readable way."""
    elapsed = datetime.now() - start_time
    total_seconds = int(elapsed.total_seconds())
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    import re
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename[:50]  # Limit length
    return filename.strip()

def create_session_summary(
    prompt: str,
    result: dict,
    start_time: datetime
) -> str:
    """Create a summary of the straightening session."""
    duration = format_time_elapsed(start_time)
    status = "🎉 SUCCESS" if result.get('success', False) else "⏱️ MAX ITERATIONS"
    
    summary = f"""
    🍌 BANANA STRAIGHTENER SESSION SUMMARY
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    📝 Original Prompt: {prompt}
    📊 Status: {status}
    ⏱️ Duration: {duration}
    🔄 Iterations: {result.get('iterations', 0)}
    📈 Final Confidence: {result.get('confidence', result.get('best_confidence', 0)):.1%}
    
    💾 Output Location: {result.get('session_dir', 'Not saved')}
    🖼️ Final Image: {result.get('final_image_path', 'Not saved')}
    
    {'🎯 Goal achieved! The image now matches your description.' if result.get('success') else '🎯 Reached maximum iterations. Best attempt saved.'}
    """
    
    return summary.strip()

def validate_image(image: Image.Image) -> bool:
    """Validate that an image is usable."""
    if image is None:
        return False
    
    try:
        width, height = image.size
        return width > 0 and height > 0 and image.mode in ['RGB', 'RGBA', 'L']
    except Exception:
        return False

def resize_image_if_needed(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """Resize image if it's too large, maintaining aspect ratio."""
    width, height = image.size
    
    if max(width, height) <= max_size:
        return image
    
    if width > height:
        new_width = max_size
        new_height = int((height * max_size) / width)
    else:
        new_height = max_size
        new_width = int((width * max_size) / height)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)