"""Core agent for iterative image improvement."""

from typing import Optional, Dict, Any, List, Generator, Callable
from pathlib import Path
from datetime import datetime
import json
from PIL import Image

from .models import GeminiModel
from .config import Config
from .utils import (
    save_image, 
    create_iteration_report, 
    enhance_prompt_with_feedback,
    create_session_summary,
    sanitize_filename,
    validate_image,
    resize_image_if_needed
)

class BananaStraightener:
    """Self-correcting image generation agent."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the Banana Straightener agent."""
        self.config = config or Config.from_env()
        
        if not self.config.api_key:
            raise ValueError(
                "API key not found. Please set GEMINI_API_KEY environment variable "
                "or pass it in the configuration."
            )
        
        self.generator = GeminiModel(
            api_key=self.config.api_key,
            model_name=self.config.generator_model
        )
        
        if self.config.evaluator_model == self.config.generator_model:
            self.evaluator = self.generator
        else:
            self.evaluator = GeminiModel(
                api_key=self.config.api_key,
                model_name=self.config.evaluator_model
            )
        
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.config.output_dir / self.session_id
        self.session_start_time = datetime.now()
        self.session_input_image = None  # Store input image for comparison
        
        if self.config.save_intermediates:
            self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def straighten(
        self,
        prompt: str,
        input_image: Optional[Image.Image] = None,
        max_iterations: Optional[int] = None,
        success_threshold: Optional[float] = None,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Iteratively improve image generation until it matches the prompt.
        
        Args:
            prompt: Target description of what the image should show
            input_image: Optional starting image to modify
            max_iterations: Maximum number of iterations (default from config)
            success_threshold: Confidence threshold for success (default from config)
            callback: Optional callback function called after each iteration
        
        Returns:
            Dictionary containing results and metadata
        """
        max_iterations = max_iterations or self.config.default_max_iterations
        success_threshold = success_threshold or self.config.success_threshold
        
        # Store input image for comparison in UI
        self.session_input_image = input_image
        
        history = []
        current_image = input_image
        current_prompt = prompt
        
        # Validate and resize input image if provided
        if current_image and not validate_image(current_image):
            print("⚠️ Invalid input image provided, starting from scratch")
            current_image = None
        elif current_image:
            current_image = resize_image_if_needed(current_image)
        
        for iteration in range(1, max_iterations + 1):
            print(f"\n🍌 Iteration {iteration}/{max_iterations}")
            
            try:
                # Generate or improve image
                if iteration == 1 and not input_image:
                    print("  📝 Generating initial image...")
                    current_image = self.generator.generate_image(prompt)
                else:
                    if history:
                        feedback = history[-1]['evaluation']['improvements']
                        if feedback and feedback.lower() not in ['none', 'n/a', 'none needed!']:
                            current_prompt = enhance_prompt_with_feedback(
                                original_prompt=prompt,
                                feedback=feedback,
                                iteration=iteration,
                                previous_history=history
                            )
                            print(f"  📝 Enhanced prompt based on feedback")
                    
                    print("  🎨 Generating improved image...")
                    current_image = self.generator.generate_image(
                        current_prompt,
                        base_image=current_image
                    )
                
                if not validate_image(current_image):
                    print(f"  ❌ Failed to generate valid image for iteration {iteration}")
                    continue
                
                # Save intermediate image if configured
                image_path = None
                if self.config.save_intermediates:
                    image_filename = f"iteration_{iteration:02d}.png"
                    image_path = self.session_dir / image_filename
                    save_image(current_image, image_path)
                    print(f"  💾 Saved to {image_path.name}")
                
                # Evaluate the generated image
                print("  🔍 Evaluating image...")
                evaluation = self.evaluator.evaluate_image(current_image, prompt)
                
                # Create iteration record
                iteration_data = {
                    'iteration': iteration,
                    'prompt_used': current_prompt,
                    'evaluation': evaluation,
                    'image_path': str(image_path) if image_path else None,
                    'timestamp': datetime.now().isoformat()
                }
                history.append(iteration_data)
                
                # Call callback if provided
                if callback:
                    try:
                        callback(iteration, current_image, evaluation)
                    except Exception as e:
                        print(f"  ⚠️ Callback error: {e}")
                
                # Display evaluation results
                match_status = "✅ YES" if evaluation['matches_intent'] else "❌ NO"
                print(f"  🎯 Match: {match_status}")
                print(f"  📊 Confidence: {evaluation['confidence']:.2%}")
                
                if not evaluation['matches_intent'] and evaluation['improvements']:
                    print(f"  💡 Next: {evaluation['improvements'][:100]}...")
                
                # Check for success
                if evaluation['matches_intent'] and evaluation['confidence'] >= success_threshold:
                    print(f"\n🎉 Success! Image matches the prompt after {iteration} iteration(s)")
                    
                    # Save final image
                    final_filename = f"final_image_{sanitize_filename(prompt[:30])}.png"
                    final_path = self.session_dir / final_filename
                    save_image(current_image, final_path)
                    
                    result = {
                        'success': True,
                        'final_image': current_image,
                        'final_image_path': str(final_path),
                        'iterations': iteration,
                        'history': history,
                        'session_dir': str(self.session_dir),
                        'confidence': evaluation['confidence'],
                        'session_id': self.session_id
                    }
                    
                    # Save session report
                    self._save_session_report(result, prompt)
                    print(create_session_summary(prompt, result, self.session_start_time))
                    
                    return result
                    
            except Exception as e:
                print(f"  ❌ Error in iteration {iteration}: {e}")
                continue
        
        # Max iterations reached without success
        print(f"\n⚠️ Maximum iterations ({max_iterations}) reached")
        
        # Find best attempt
        if history:
            best_iteration = max(history, key=lambda x: x['evaluation']['confidence'])
            best_confidence = best_iteration['evaluation']['confidence']
        else:
            best_confidence = 0.0
        
        # Save final image
        final_filename = f"best_attempt_{sanitize_filename(prompt[:30])}.png"
        final_path = self.session_dir / final_filename
        if current_image and validate_image(current_image):
            save_image(current_image, final_path)
        
        result = {
            'success': False,
            'final_image': current_image,
            'final_image_path': str(final_path) if current_image else None,
            'iterations': max_iterations,
            'history': history,
            'session_dir': str(self.session_dir),
            'best_confidence': best_confidence,
            'session_id': self.session_id,
            'message': f"Best result: {best_confidence:.2%} confidence"
        }
        
        # Save session report
        self._save_session_report(result, prompt)
        print(create_session_summary(prompt, result, self.session_start_time))
        
        return result
    
    def straighten_iterative(
        self,
        prompt: str,
        input_image: Optional[Image.Image] = None,
        max_iterations: Optional[int] = None,
        success_threshold: Optional[float] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generator version that yields results after each iteration.
        Useful for real-time UI updates.
        """
        max_iterations = max_iterations or self.config.default_max_iterations
        success_threshold = success_threshold or self.config.success_threshold
        
        history = []
        current_image = input_image
        current_prompt = prompt
        
        # Validate input image
        if current_image:
            current_image = resize_image_if_needed(current_image)
            if not validate_image(current_image):
                current_image = None
        
        for iteration in range(1, max_iterations + 1):
            try:
                # Generate or improve image
                if iteration == 1 and not input_image:
                    current_image = self.generator.generate_image(prompt)
                else:
                    if history:
                        feedback = history[-1]['evaluation']['improvements']
                        if feedback and feedback.lower() not in ['none', 'n/a', 'none needed!']:
                            current_prompt = enhance_prompt_with_feedback(
                                original_prompt=prompt,
                                feedback=feedback,
                                iteration=iteration,
                                previous_history=history
                            )
                    
                    current_image = self.generator.generate_image(
                        current_prompt,
                        base_image=current_image
                    )
                
                if not validate_image(current_image):
                    continue
                
                # Evaluate the generated image
                evaluation = self.evaluator.evaluate_image(current_image, prompt)
                
                # Create iteration record
                iteration_data = {
                    'iteration': iteration,
                    'current_image': current_image,
                    'prompt_used': current_prompt,
                    'evaluation': evaluation,
                    'success': evaluation['matches_intent'] and evaluation['confidence'] >= success_threshold,
                    'timestamp': datetime.now().isoformat()
                }
                history.append(iteration_data)
                
                # Yield current state
                yield iteration_data
                
                # Stop if successful
                if iteration_data['success']:
                    break
                    
            except Exception as e:
                # Yield error state
                yield {
                    'iteration': iteration,
                    'current_image': current_image,
                    'prompt_used': current_prompt,
                    'evaluation': {
                        'matches_intent': False,
                        'confidence': 0.0,
                        'improvements': f'Error: {e}'
                    },
                    'success': False,
                    'error': str(e)
                }
    
    def _save_session_report(self, result: Dict[str, Any], original_prompt: str) -> Path:
        """Save a detailed report of the straightening session."""
        report_data = {
            'session_id': self.session_id,
            'timestamp': self.session_start_time.isoformat(),
            'original_prompt': original_prompt,
            'success': result['success'],
            'total_iterations': result['iterations'],
            'final_confidence': result.get('confidence', result.get('best_confidence', 0)),
            'config': {
                'generator_model': self.config.generator_model,
                'evaluator_model': self.config.evaluator_model,
                'success_threshold': self.config.success_threshold
            },
            'history': result['history']
        }
        
        report_path = self.session_dir / "session_report.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"📄 Session report saved: {report_path}")
        except Exception as e:
            print(f"⚠️ Failed to save session report: {e}")
        
        return report_path