"""Utility functions for Banana Straightener."""

from typing import Union, Optional, List
from pathlib import Path
from PIL import Image
import base64
import io
import zipfile
import json
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
    iteration: int,
    previous_history: list = None
) -> str:
    """
    Enhance the prompt based on evaluation feedback and previous attempts.
    
    This function creates a more specific prompt by incorporating
    the feedback from the previous iteration and tracking what's been tried before.
    """
    if not feedback or feedback.lower() in ['none', 'n/a', 'none needed!']:
        return original_prompt
    
    previous_history = previous_history or []
    
    # Check for repetitive feedback patterns
    if len(previous_history) > 1:
        recent_feedback = [h.get('evaluation', {}).get('improvements', '') for h in previous_history[-3:]]
        if _is_feedback_repetitive(feedback, recent_feedback):
            # Try alternative approaches when stuck in loops
            return _create_alternative_approach(original_prompt, feedback, iteration, previous_history)
    
    # Build enhanced prompt with cumulative learnings
    enhanced_parts = [f"Original request: {original_prompt}"]
    
    # Add iteration-specific strategy
    strategy = _get_iteration_strategy(iteration, len(previous_history))
    enhanced_parts.append(f"\nIteration {iteration} strategy: {strategy}")
    
    # Add current specific improvements
    enhanced_parts.append(f"\nSpecific improvements needed:\n{feedback}")
    
    # Add learnings from previous attempts if available
    if previous_history:
        attempted_approaches = _extract_attempted_approaches(previous_history)
        if attempted_approaches:
            enhanced_parts.append(f"\nPrevious attempts tried: {attempted_approaches}")
            enhanced_parts.append("Try a different approach from those listed above.")
    
    enhanced_parts.append("\nGenerate an image that addresses these specific issues while maintaining the original intent.")
    
    return "\n".join(enhanced_parts).strip()

def _is_feedback_repetitive(current_feedback: str, recent_feedback: list) -> bool:
    """Check if current feedback is too similar to recent feedback."""
    if not recent_feedback:
        return False
    
    current_words = set(current_feedback.lower().split())
    
    for past_feedback in recent_feedback:
        if not past_feedback:
            continue
        past_words = set(past_feedback.lower().split())
        
        # Calculate similarity
        if current_words and past_words:
            intersection = current_words & past_words
            union = current_words | past_words
            similarity = len(intersection) / len(union) if union else 0
            
            if similarity > 0.8:  # 80% similarity threshold
                return True
    
    return False

def _create_alternative_approach(original_prompt: str, feedback: str, iteration: int, history: list) -> str:
    """Create alternative approaches when stuck in repetitive loops."""
    alternatives = []
    
    # Add creative alternatives based on iteration number
    if iteration <= 3:
        alternatives.append("Try adding more specific visual details and descriptive language.")
    elif iteration <= 6:
        alternatives.append("Use negative prompting - explicitly state what should NOT appear.")
        alternatives.append("Break down the request into smaller, more specific components.")
    else:
        alternatives.append("Try a completely different artistic style or approach.")
        alternatives.append("Use metaphorical or comparative language (e.g., 'like a ruler', 'similar to a photograph').")
    
    # Analyze what's been tried from history
    tried_approaches = _extract_attempted_approaches(history)
    
    enhanced = f"""
    Original request: {original_prompt}
    
    ITERATION {iteration} - ALTERNATIVE APPROACH NEEDED
    Previous attempts have been repetitive. Trying a new strategy:
    
    Current issue: {feedback}
    
    Alternative approaches to try:
    {chr(10).join(['• ' + alt for alt in alternatives])}
    
    Previously attempted: {tried_approaches}
    
    Use a fundamentally different approach than before. Be creative and specific.
    """
    
    return enhanced.strip()

def _get_iteration_strategy(iteration: int, history_length: int) -> str:
    """Get strategy based on iteration number."""
    if iteration == 1:
        return "First attempt - try the straightforward approach with clear, specific instructions."
    elif iteration <= 3:
        return "Early iteration - add more visual details and specific positioning/sizing instructions."
    elif iteration <= 6:
        return "Mid-stage - try technical/photographic terms and negative prompting (what to avoid)."
    else:
        return "Late stage - use creative alternatives, metaphors, or completely different artistic approaches."

def _extract_attempted_approaches(history: list) -> str:
    """Extract what approaches have been tried from the history."""
    approaches = []
    
    for entry in history:
        prompt_used = entry.get('prompt_used', '')
        if 'negative prompting' in prompt_used.lower():
            approaches.append("negative prompting")
        if 'artistic style' in prompt_used.lower() or 'style' in prompt_used.lower():
            approaches.append("style modification")
        if 'metaphor' in prompt_used.lower() or 'like a' in prompt_used.lower():
            approaches.append("metaphorical descriptions")
        if 'technical' in prompt_used.lower() or 'photographic' in prompt_used.lower():
            approaches.append("technical terminology")
    
    return ", ".join(set(approaches)) if approaches else "basic descriptions only"

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

def create_session_zip(
    session_dir: Path, 
    images: List[Image.Image], 
    evaluations: List[dict],
    prompt: str,
    input_image: Optional[Image.Image] = None
) -> Path:
    """Create a ZIP file with all session artifacts."""
    # Ensure the session directory exists
    session_dir.mkdir(parents=True, exist_ok=True)
    zip_path = session_dir / f"session_{session_dir.name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all iteration images
        for i, image in enumerate(images, 1):
            if image and validate_image(image):
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG', optimize=True, quality=95)
                zipf.writestr(f"iteration_{i:02d}.png", img_buffer.getvalue())
        
        # Add input image if provided
        if input_image and validate_image(input_image):
            img_buffer = io.BytesIO()
            input_image.save(img_buffer, format='PNG', optimize=True, quality=95)
            zipf.writestr("input_image.png", img_buffer.getvalue())
        
        # Add evaluation data
        session_data = {
            "prompt": prompt,
            "total_iterations": len(images),
            "has_input_image": input_image is not None,
            "evaluations": evaluations,
            "created_at": datetime.now().isoformat()
        }
        zipf.writestr("session_data.json", json.dumps(session_data, indent=2))
        
        # Add text summary
        summary_text = f"""Banana Straightener Session Summary
================================

Prompt: {prompt}
Total Iterations: {len(images)}
Input Image: {'Yes' if input_image else 'No'}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Iteration Details:
"""
        for i, eval_data in enumerate(evaluations, 1):
            confidence = eval_data.get('confidence', 0)
            improvements = eval_data.get('improvements', 'N/A')
            summary_text += f"\nIteration {i}:\n"
            summary_text += f"  Confidence: {confidence:.1%}\n"
            summary_text += f"  Improvements: {improvements}\n"
        
        zipf.writestr("session_summary.txt", summary_text)
    
    return zip_path