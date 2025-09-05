"""Gradio web interface for Banana Straightener."""

import gradio as gr
from PIL import Image
from typing import Optional, List, Tuple, Generator
import json
import webbrowser
import threading
import time

from .agent import BananaStraightener
from .config import Config

def create_interface(config: Optional[Config] = None):
    """Create and return the Gradio interface without launching it."""
    config = config or Config.from_env()
    
    if not config.api_key:
        raise ValueError("API key not found. Please set GEMINI_API_KEY environment variable.")
    
    # This function exists for testing/programmatic access
    # The actual interface creation is in launch_ui()
    return None

def launch_ui(config: Optional[Config] = None, open_browser: bool = True):
    """Launch the Gradio web interface."""
    
    config = config or Config.from_env()
    
    if not config.api_key:
        raise ValueError("API key not found. Please set GEMINI_API_KEY environment variable.")
    
    def straighten_image_generator(
        prompt: str,
        input_image: Optional[Image.Image],
        max_iterations: int,
        threshold: float,
        save_intermediates: bool,
        progress=gr.Progress()
    ):
        """Process image straightening with live updates."""
        
        if not prompt.strip():
            yield (
                None,  # current_image
                [],    # gallery
                "❌ Please enter a prompt",  # status
                "",    # evaluation
                "",    # history
                gr.update(interactive=True)  # button
            )
            return
        
        # Update config for this run
        config.default_max_iterations = max_iterations
        config.success_threshold = threshold
        config.save_intermediates = save_intermediates
        
        try:
            # Initialize agent
            agent = BananaStraightener(config)
            
            # Track all iterations for gallery and history
            iteration_images = []
            iteration_info = []
            
            # Initialize progress for Gradio 5.0+
            
            # Run straightening with generator for live updates
            for iteration_data in agent.straighten_iterative(
                prompt=prompt,
                input_image=input_image,
                max_iterations=max_iterations,
                success_threshold=threshold
            ):
                current_image = iteration_data['current_image']
                evaluation = iteration_data['evaluation']
                iteration = iteration_data['iteration']
                
                # Update progress for Gradio 5.0+
                progress(iteration / max_iterations, f"🔄 Iteration {iteration}/{max_iterations}")
                
                # Add to gallery (convert to format Gradio expects)
                if current_image:
                    iteration_images.append((current_image, f"Iteration {iteration}"))
                
                # Create status message
                match_status = "✅ Match" if evaluation['matches_intent'] else "❌ No match"
                confidence = evaluation['confidence']
                
                status = f"""**Iteration {iteration}**
{match_status} | Confidence: {confidence:.1%}
                
{f"🎉 **Success!** Goal achieved!" if iteration_data.get('success') else "🔄 Continuing..."}"""
                
                # Create detailed evaluation
                eval_text = f"""### Iteration {iteration} Evaluation
                
**Match Intent:** {match_status}  
**Confidence:** {confidence:.1%}

**✅ Correct Elements:**  
{evaluation.get('correct_elements', 'N/A')}

**❌ Missing/Issues:**  
{evaluation.get('missing_elements', 'N/A')}

**💡 Improvements Needed:**  
{evaluation.get('improvements', 'None - looks perfect!')}
"""
                
                iteration_info.append(eval_text)
                
                # Yield current state
                yield (
                    current_image,  # Current result
                    iteration_images,  # Gallery of all iterations
                    status,  # Status message
                    eval_text,  # Current evaluation
                    "\n\n---\n\n".join(iteration_info),  # Full history
                    gr.update(interactive=False)  # Keep button disabled during processing
                )
                
                # Stop if successful
                if iteration_data.get('success'):
                    final_status = f"""**🎉 SUCCESS!**  
Achieved perfect result in {iteration} iteration(s)  
Final confidence: {confidence:.1%}  

Your banana has been straightened! 🍌✨"""
                    
                    yield (
                        current_image,
                        iteration_images,
                        final_status,
                        eval_text,
                        "\n\n---\n\n".join(iteration_info),
                        gr.update(interactive=True)  # Re-enable button
                    )
                    return
                
                # Small delay to make progress visible
                time.sleep(0.1)
            
            # If we reach here, max iterations were reached
            final_status = f"""**⚠️ Maximum iterations reached**  
Best result from {max_iterations} iteration(s)  
Best confidence: {confidence:.1%}  

The banana is straighter, but not quite perfect yet. Try increasing iterations or adjusting your prompt."""
            
            yield (
                current_image,
                iteration_images,
                final_status,
                eval_text,
                "\n\n---\n\n".join(iteration_info),
                gr.update(interactive=True)  # Re-enable button
            )
            
        except Exception as e:
            error_msg = f"❌ **Error:** {str(e)}"
            yield (
                None,
                [],
                error_msg,
                "",
                "",
                gr.update(interactive=True)  # Re-enable button on error
            )
    
    # Custom CSS for better styling and dark theme support
    css = """
    .gradio-container {
        max-width: 1200px !important;
    }
    .main-header {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        border: 2px solid var(--color-accent);
    }
    .main-header h1 {
        color: var(--body-text-color) !important;
        margin-bottom: 10px;
    }
    .main-header h3 {
        color: var(--body-text-color) !important;
        margin-bottom: 10px;
        opacity: 0.8;
    }
    .main-header p {
        color: var(--body-text-color) !important;
        opacity: 0.7;
    }
    .spaced-section {
        margin: 30px 0;
    }
    """
    
    # Create Gradio interface
    with gr.Blocks(
        title="🍌 Banana Straightener", 
        theme=gr.themes.Soft(),
        css=css
    ) as interface:
        
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1>🍌 Banana Straightener</h1>
            <h3>Self-correcting image generation - iterate until it's just right!</h3>
            <p>Upload an image to modify or leave empty to generate from scratch.</p>
        </div>
        """)
        
        with gr.Row():
            # Left column - Inputs
            with gr.Column(scale=1):
                prompt_input = gr.Textbox(
                    label="✏️ What do you want?",
                    placeholder="Describe the image you want to create or modify...",
                    lines=3,
                    value="A perfectly straight banana on a white background"
                )
                
                image_input = gr.Image(
                    label="🖼️ Starting Image (optional)",
                    type="pil",
                    height=300
                )
                
                with gr.Accordion("⚙️ Advanced Settings", open=False):
                    iterations_slider = gr.Slider(
                        minimum=1,
                        maximum=20,
                        value=5,
                        step=1,
                        label="🔄 Maximum Iterations",
                        info="How many improvement cycles to attempt"
                    )
                    
                    threshold_slider = gr.Slider(
                        minimum=0.5,
                        maximum=1.0,
                        value=0.85,
                        step=0.05,
                        label="🎯 Success Threshold",
                        info="Confidence level required to consider the task complete"
                    )
                    
                    save_check = gr.Checkbox(
                        label="💾 Save all intermediate images",
                        value=False,
                        info="Keep all iterations for review"
                    )
                
                generate_btn = gr.Button(
                    "🍌 Start Straightening!",
                    variant="primary",
                    size="lg"
                )
                
            
            # Right column - Outputs
            with gr.Column(scale=2):
                # Main result display
                current_image = gr.Image(
                    label="🎨 Current Result",
                    type="pil",
                    height=400
                )
                
                # Status display
                status_text = gr.Markdown(
                    label="📊 Status",
                    value="Ready to straighten your banana! Enter a prompt and click start."
                )
                
                # Tabbed additional info
                with gr.Tabs():
                    with gr.TabItem("🖼️ All Iterations"):
                        gallery = gr.Gallery(
                            label="Iteration Gallery",
                            columns=4,
                            height="400px",
                            object_fit="contain"
                        )
                    
                    with gr.TabItem("🔍 Current Evaluation"):
                        evaluation_text = gr.Markdown(
                            value="No evaluation yet. Start the process to see detailed analysis!"
                        )
                    
                    with gr.TabItem("📋 Full History"):
                        history_text = gr.Markdown(
                            value="History will appear here as iterations complete."
                        )
        
        # Example inputs with tips
        with gr.Accordion("🎨 Examples & Tips", open=False):
            gr.Markdown("""
            **Pro tips:**
            • Be specific about style, lighting, and composition
            • Mention colors, mood, and atmosphere you want  
            • If modifying an image, describe the changes clearly
            • Higher thresholds = stricter quality requirements
            """)
            
            gr.Examples(
                examples=[
                    ["A perfectly straight banana on a white background", None, 5, 0.85, False],
                    ["A majestic dragon reading a book in an ancient library", None, 7, 0.80, True],
                    ["A cozy coffee shop on a rainy evening with warm lighting", None, 5, 0.85, False],
                    ["Futuristic cityscape with flying cars at sunset", None, 6, 0.90, False],
                    ["A cat wearing a monocle and top hat, oil painting style", None, 8, 0.85, True],
                ],
                inputs=[prompt_input, image_input, iterations_slider, threshold_slider, save_check]
            )
        
        # Footer with helpful links  
        gr.HTML("""
        <div style="text-align: center; padding: 15px; margin-top: 40px; border-top: 1px solid var(--block-border-color); opacity: 0.7;">
            <p>🔑 <strong>Need an API key?</strong> 
            <a href="https://aistudio.google.com/app/apikey" target="_blank">Get it from Google AI Studio</a></p>
            <p style="font-size: 0.9em;">Powered by Gemini 2.5 Flash</p>
        </div>
        """)
        
        # Connect the generation function
        generate_btn.click(
            fn=straighten_image_generator,
            inputs=[
                prompt_input,
                image_input,
                iterations_slider,
                threshold_slider,
                save_check
            ],
            outputs=[
                current_image,
                gallery,
                status_text,
                evaluation_text,
                history_text,
                generate_btn  # For updating button state
            ],
            show_progress="full"
        )
    
    # Launch the interface
    print(f"🍌 Starting Banana Straightener Web UI...")
    print(f"🌐 URL: http://localhost:{config.gradio_port}")
    print(f"🔗 Share: {config.gradio_share}")
    
    # Open browser in a separate thread after a short delay
    if open_browser:
        def open_browser_delayed():
            time.sleep(2)  # Wait for server to start
            webbrowser.open(f"http://localhost:{config.gradio_port}")
        
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    interface.launch(
        server_port=config.gradio_port,
        share=config.gradio_share,
        server_name="0.0.0.0",
        show_error=True,
        quiet=False
    )