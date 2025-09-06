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
from .utils import create_session_zip

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
                gr.update(interactive=True),  # button
                gr.update(visible=False),  # download_btn
                None,  # download_link
                gr.update(visible=False),  # comparison_tab
                None,  # comparison_input
                None,  # comparison_output
                gr.update(visible=False)  # comparison_slider
            )
            return
        
        # Update config for this run
        config.default_max_iterations = max_iterations
        config.success_threshold = threshold
        config.save_intermediates = save_intermediates
        
        try:
            # Initialize agent
            agent = BananaStraightener(config)
            
            # Update session data for UI functions
            session_data['prompt'] = prompt
            session_data['input_image'] = input_image
            session_data['agent'] = agent
            session_data['images'] = []
            session_data['evaluations'] = []
            
            # Track all iterations for gallery and history
            iteration_images = []
            iteration_info = []
            all_evaluations = []
            session_images = []  # Store actual PIL images for ZIP
            
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
                
                # Add to gallery (convert to format Gradio expects) and store for ZIP
                if current_image:
                    iteration_images.append((current_image, f"Iteration {iteration}"))
                    session_images.append(current_image)
                    session_data['images'].append(current_image)
                
                # Store evaluation data for ZIP
                all_evaluations.append(evaluation)
                session_data['evaluations'].append(evaluation)
                
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
                
                # Determine if we should show comparison tab
                show_comparison = input_image is not None
                
                # Yield current state
                yield (
                    current_image,  # Current result
                    iteration_images,  # Gallery of all iterations
                    status,  # Status message
                    eval_text,  # Current evaluation
                    "\n\n---\n\n".join(iteration_info),  # Full history
                    gr.update(interactive=False),  # Keep button disabled during processing
                    gr.update(visible=len(session_images) > 0),  # download_btn (show if we have images)
                    None,  # download_link (not ready during processing)
                    gr.update(visible=show_comparison),  # comparison_tab
                    input_image if show_comparison else None,  # comparison_input
                    current_image if show_comparison else None,  # comparison_output
                    gr.update(maximum=len(session_images), value=len(session_images), visible=len(session_images) > 1)  # comparison_slider
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
                        gr.update(interactive=True),  # Re-enable button
                        gr.update(visible=len(session_images) > 0),  # download_btn
                        None,  # download_link (ready after completion)
                        gr.update(visible=show_comparison),  # comparison_tab
                        input_image if show_comparison else None,  # comparison_input
                        current_image if show_comparison else None,  # comparison_output
                        gr.update(maximum=len(session_images), value=len(session_images), visible=len(session_images) > 1)  # comparison_slider
                    )
                    return
                
                # Small delay to make progress visible
                time.sleep(0.1)
            
            # If we reach here, max iterations were reached
            final_status = f"""**⚠️ Maximum iterations reached**  
Best result from {max_iterations} iteration(s)  
Best confidence: {confidence:.1%}  

The banana is straighter, but not quite perfect yet. Try increasing iterations or adjusting your prompt."""
            
            show_comparison = input_image is not None
            
            yield (
                current_image,
                iteration_images,
                final_status,
                eval_text,
                "\n\n---\n\n".join(iteration_info),
                gr.update(interactive=True),  # Re-enable button
                gr.update(visible=len(session_images) > 0),  # download_btn
                None,  # download_link
                gr.update(visible=show_comparison),  # comparison_tab
                input_image if show_comparison else None,  # comparison_input
                current_image if show_comparison else None,  # comparison_output
                gr.update(maximum=len(session_images), value=len(session_images), visible=len(session_images) > 1)  # comparison_slider
            )
            
        except Exception as e:
            error_msg = f"❌ **Error:** {str(e)}"
            yield (
                None,
                [],
                error_msg,
                "",
                "",
                gr.update(interactive=True),  # Re-enable button on error
                gr.update(visible=False),  # download_btn
                None,  # download_link
                gr.update(visible=False),  # comparison_tab
                None,  # comparison_input
                None,  # comparison_output
                gr.update(visible=False)  # comparison_slider
            )
    
    # Store session data globally for the UI functions to access
    session_data = {
        'images': [],
        'evaluations': [],
        'prompt': '',
        'input_image': None,
        'agent': None
    }
    
    def create_download_zip():
        """Create a ZIP file with all session artifacts."""
        try:
            if not session_data['images']:
                print("⚠️  No images available for download")
                return None
                
            print(f"📦 Creating ZIP with {len(session_data['images'])} images...")
            
            if session_data['agent'] and hasattr(session_data['agent'], 'session_dir'):
                zip_path = create_session_zip(
                    session_dir=session_data['agent'].session_dir,
                    images=session_data['images'],
                    evaluations=session_data['evaluations'],
                    prompt=session_data['prompt'],
                    input_image=session_data['input_image']
                )
                if zip_path.exists():
                    print(f"✅ Created ZIP at: {zip_path} (size: {zip_path.stat().st_size} bytes)")
                    return str(zip_path)
                else:
                    print(f"❌ ZIP file not found at: {zip_path}")
                    return None
            else:
                # Fallback: create a simple zip in the outputs directory
                from pathlib import Path
                import tempfile
                from datetime import datetime
                
                # Create outputs directory if it doesn't exist
                outputs_dir = Path("outputs")
                outputs_dir.mkdir(exist_ok=True)
                
                # Create timestamped zip file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_path = outputs_dir / f"banana_session_{timestamp}.zip"
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for i, image in enumerate(session_data['images'], 1):
                        if image:
                            img_buffer = io.BytesIO()
                            image.save(img_buffer, format='PNG', optimize=True, quality=95)
                            zipf.writestr(f"iteration_{i:02d}.png", img_buffer.getvalue())
                    
                    # Add input image if available
                    if session_data['input_image']:
                        img_buffer = io.BytesIO()
                        session_data['input_image'].save(img_buffer, format='PNG', optimize=True, quality=95)
                        zipf.writestr("input_image.png", img_buffer.getvalue())
                    
                    # Add basic session info
                    session_info = {
                        "prompt": session_data['prompt'],
                        "total_iterations": len(session_data['images']),
                        "has_input_image": session_data['input_image'] is not None,
                        "created_at": datetime.now().isoformat()
                    }
                    zipf.writestr("session_info.json", json.dumps(session_info, indent=2))
                
                if zip_path.exists():
                    print(f"✅ Created fallback ZIP at: {zip_path} (size: {zip_path.stat().st_size} bytes)")
                    return str(zip_path)
                else:
                    print(f"❌ Fallback ZIP file not found at: {zip_path}")
                    return None
        except Exception as e:
            print(f"❌ Error creating ZIP: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_comparison_slider(slider_value):
        """Update comparison images based on slider value."""
        try:
            slider_value = int(slider_value)
            if slider_value <= len(session_data['images']) and slider_value > 0:
                return session_data['images'][slider_value - 1]
        except (ValueError, IndexError):
            pass
        return None
    
    # Custom CSS for better styling, dark theme support, and mobile responsiveness
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
    .comparison-container {
        display: flex;
        gap: 20px;
        align-items: flex-start;
    }
    .comparison-item {
        flex: 1;
        text-align: center;
    }
    .download-section {
        padding: 15px;
        border-radius: 8px;
        background: var(--background-fill-secondary);
        margin-top: 15px;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .gradio-container {
            padding: 10px !important;
        }
        .main-header {
            padding: 15px;
            margin-bottom: 20px;
        }
        .main-header h1 {
            font-size: 1.5rem !important;
        }
        .main-header h3 {
            font-size: 1.1rem !important;
        }
        .comparison-container {
            flex-direction: column;
            gap: 15px;
        }
        /* Make tabs stack vertically on mobile */
        .tab-nav {
            flex-wrap: wrap !important;
        }
        /* Adjust button sizes for touch */
        button {
            min-height: 44px !important;
            padding: 12px 20px !important;
        }
        /* Gallery adjustments */
        .gallery {
            columns: 2 !important;
        }
    }
    
    @media (max-width: 480px) {
        .gallery {
            columns: 1 !important;
        }
        .main-header h1 {
            font-size: 1.3rem !important;
        }
        .gradio-container {
            padding: 5px !important;
        }
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
                        
                        # Download section
                        with gr.Row():
                            download_btn = gr.Button(
                                "📦 Download All Iterations as ZIP",
                                variant="secondary",
                                visible=False
                            )
                            download_link = gr.File(
                                visible=False,
                                interactive=False
                            )
                    
                    with gr.TabItem("🔍 Current Evaluation"):
                        evaluation_text = gr.Markdown(
                            value="No evaluation yet. Start the process to see detailed analysis!"
                        )
                    
                    with gr.TabItem("📋 Full History"):
                        history_text = gr.Markdown(
                            value="History will appear here as iterations complete."
                        )
                    
                    with gr.TabItem("🔄 Comparison", visible=False) as comparison_tab:
                        gr.HTML('<div class="comparison-container">')
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("### 📥 Input Image")
                                comparison_input = gr.Image(
                                    label="Original",
                                    type="pil",
                                    interactive=False,
                                    height=300
                                )
                            with gr.Column():
                                gr.Markdown("### 🎨 Final Result")
                                comparison_output = gr.Image(
                                    label="Result", 
                                    type="pil",
                                    interactive=False,
                                    height=300
                                )
                        gr.HTML('</div>')
                        
                        with gr.Row():
                            comparison_slider = gr.Slider(
                                minimum=1,
                                maximum=1,
                                step=1,
                                value=1,
                                label="Iteration Comparison",
                                info="Slide to compare different iterations",
                                visible=False
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
                generate_btn,  # For updating button state
                download_btn,  # Download button visibility
                download_link,  # Download file link
                comparison_tab,  # Comparison tab visibility
                comparison_input,  # Comparison input image
                comparison_output,  # Comparison output image  
                comparison_slider  # Comparison slider
            ],
            show_progress="full"
        )
        
        # Connect download button to update file link
        download_btn.click(
            fn=create_download_zip,
            outputs=download_link
        )
        
        # Connect comparison slider
        comparison_slider.change(
            fn=update_comparison_slider,
            inputs=comparison_slider,
            outputs=comparison_output
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