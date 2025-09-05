"""Command-line interface for Banana Straightener."""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from PIL import Image
import sys
import webbrowser

from .agent import BananaStraightener
from .config import Config
from .utils import load_image
from . import __version__

console = Console()

def show_banner():
    """Display the Banana Straightener banner."""
    banner = Text("🍌 BANANA STRAIGHTENER", style="bold yellow")
    subtitle = Text("Self-correcting image generation - iterate until it's right!", style="dim")
    console.print(Panel.fit(f"{banner}\n{subtitle}", border_style="yellow"))

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def main(ctx, version):
    """🍌 Banana Straightener - Iterate until your image is just right!"""
    if version:
        console.print(f"🍌 Banana Straightener v{__version__}")
        sys.exit(0)
    
    if ctx.invoked_subcommand is None:
        show_banner()
        console.print("\n[dim]Use 'straighten --help' to see available commands[/dim]")
        console.print("[dim]Quick start: straighten generate \"your image description here\"[/dim]\n")

@main.command()
@click.argument('prompt')
@click.option('--image', '-i', type=click.Path(exists=True), 
              help='Input image to modify (PNG, JPG, etc.)')
@click.option('--iterations', '-n', type=int, default=5, 
              help='Maximum iterations (default: 5)')
@click.option('--threshold', '-t', type=float, default=0.85, 
              help='Success threshold 0.0-1.0 (default: 0.85)')
@click.option('--output', '-o', type=click.Path(), default='./outputs', 
              help='Output directory (default: ./outputs)')
@click.option('--save-all', is_flag=True, 
              help='Save all intermediate images')
@click.option('--api-key', envvar='GEMINI_API_KEY', 
              help='Gemini API key (or set GEMINI_API_KEY env var)')
@click.option('--open', 'open_result', is_flag=True, 
              help='Open result directory when done')
def generate(prompt, image, iterations, threshold, output, save_all, api_key, open_result):
    """Generate or modify an image until it matches your prompt."""
    
    show_banner()
    console.print(f"\n[bold]Target:[/bold] {prompt}")
    if image:
        console.print(f"[dim]Starting from: {image}[/dim]")
    console.print(f"[dim]Max iterations: {iterations} | Success threshold: {threshold:.0%}[/dim]\n")
    
    # Load configuration
    config = Config(
        api_key=api_key,
        default_max_iterations=iterations,
        success_threshold=threshold,
        save_intermediates=save_all,
        output_dir=Path(output)
    )
    
    # Load input image if provided
    input_image = None
    if image:
        try:
            input_image = load_image(image)
            console.print(f"✅ Loaded input image: {Path(image).name}")
        except Exception as e:
            console.print(f"[red]❌ Failed to load image: {e}[/red]")
            sys.exit(1)
    
    # Initialize agent
    try:
        agent = BananaStraightener(config)
    except ValueError as e:
        console.print(f"[red]❌ Configuration error:[/red] {e}")
        console.print("[dim]💡 Get your API key from: https://aistudio.google.com/app/apikey[/dim]")
        console.print("[dim]💡 Set via environment: export GEMINI_API_KEY='your-key-here'[/dim]")
        console.print("[dim]💡 Or create .env file: echo 'GEMINI_API_KEY=your-key-here' > .env[/dim]")
        sys.exit(1)
    
    # Progress tracking
    iteration_results = []
    
    def progress_callback(iteration, current_image, evaluation):
        """Callback to track progress for final summary."""
        iteration_results.append({
            'iteration': iteration,
            'matches': evaluation['matches_intent'],
            'confidence': evaluation['confidence'],
            'improvements': evaluation.get('improvements', '')
        })
    
    # Run the straightening process
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("🍌 Straightening your banana...", total=iterations)
            
            result = agent.straighten(
                prompt=prompt,
                input_image=input_image,
                max_iterations=iterations,
                success_threshold=threshold,
                callback=lambda i, img, eval: (
                    progress_callback(i, img, eval),
                    progress.update(task, advance=1, description=f"🔄 Iteration {i}/{iterations}")
                )
            )
            
            progress.update(task, completed=iterations)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Error during processing: {e}[/red]")
        sys.exit(1)
    
    # Display detailed results
    console.print("\n" + "="*60 + "\n")
    
    # Create results summary table
    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    
    if result['success']:
        summary_table.add_row("Status:", "[bold green]✅ Success![/bold green]")
        summary_table.add_row("Iterations:", f"{result['iterations']}")
        summary_table.add_row("Final confidence:", f"{result['confidence']:.1%}")
    else:
        summary_table.add_row("Status:", "[bold yellow]⚠️ Max iterations reached[/bold yellow]")
        summary_table.add_row("Best confidence:", f"{result.get('best_confidence', 0):.1%}")
        summary_table.add_row("Total iterations:", f"{result['iterations']}")
    
    summary_table.add_row("Output directory:", f"[link]{result['session_dir']}[/link]")
    if result.get('final_image_path'):
        summary_table.add_row("Final image:", f"[link]{Path(result['final_image_path']).name}[/link]")
    
    console.print(Panel(
        summary_table,
        title="[bold]🍌 Results[/bold]",
        border_style="green" if result['success'] else "yellow"
    ))
    
    # Show iteration progress if we have results
    if iteration_results:
        console.print("\n[bold]Iteration Progress:[/bold]")
        progress_table = Table()
        progress_table.add_column("Iter", style="cyan", width=4)
        progress_table.add_column("Match", width=5)
        progress_table.add_column("Confidence", width=10)
        progress_table.add_column("Next Steps", style="dim")
        
        for iter_result in iteration_results:
            match_icon = "✅" if iter_result['matches'] else "❌"
            confidence = f"{iter_result['confidence']:.1%}"
            improvements = iter_result['improvements'][:50] + "..." if len(iter_result['improvements']) > 50 else iter_result['improvements']
            
            progress_table.add_row(
                str(iter_result['iteration']),
                match_icon,
                confidence,
                improvements or "Looking good!"
            )
        
        console.print(progress_table)
    
    # Open result directory if requested
    if open_result and result.get('session_dir'):
        try:
            import subprocess
            import platform
            
            path = Path(result['session_dir'])
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(path)])
            elif platform.system() == "Windows":
                subprocess.run(["explorer", str(path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(path)])
            
            console.print(f"\n[dim]📂 Opened {path}[/dim]")
        except Exception:
            console.print(f"\n[dim]💡 View results at: {result['session_dir']}[/dim]")
    
    console.print()

@main.command()
@click.option('--port', '-p', type=int, default=7860, help='Port for web UI')
@click.option('--share', is_flag=True, help='Create public shareable link')
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key')
@click.option('--no-browser', is_flag=True, help="Don't open browser automatically")
def ui(port, share, api_key, no_browser):
    """Launch the Gradio web interface."""
    show_banner()
    console.print(f"[dim]Starting web UI on port {port}...[/dim]\n")
    
    try:
        from .ui import launch_ui
        
        config = Config(
            api_key=api_key, 
            gradio_port=port, 
            gradio_share=share
        )
        
        if not no_browser:
            console.print(f"🌐 Opening browser at http://localhost:{port}")
        
        launch_ui(config, open_browser=not no_browser)
        
    except ImportError:
        console.print("[red]❌ Gradio not installed.[/red]")
        console.print("[dim]Install with: uv pip install gradio[/dim]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Failed to start web UI: {e}[/red]")
        sys.exit(1)

@main.command()
def examples():
    """Show example prompts and usage patterns."""
    show_banner()
    
    examples_content = """[bold]🎨 Example Prompts:[/bold]

• A perfectly straight banana on a white background
• A majestic dragon reading a book in an ancient library
• A cozy coffee shop on a rainy day with warm lighting
• Futuristic cityscape with flying cars at sunset
• A cat wearing a monocle and top hat, oil painting style
• A spiral staircase made of books floating in space
• A steampunk robot tending a garden of mechanical flowers

[bold]💻 Example Commands:[/bold]

[dim]# Generate from scratch[/dim]
straighten generate "a majestic dragon reading a book"

[dim]# Modify existing image[/dim]  
straighten generate "add a rainbow in the sky" --image sunset.jpg

[dim]# High-quality with more iterations[/dim]
straighten generate "perfect circle" --iterations 10 --threshold 0.95

[dim]# Save all steps for review[/dim]
straighten generate "abstract art" --save-all --open

[dim]# Launch web interface[/dim]
straighten ui

[bold]🔑 Setup:[/bold]

1. Get API key: https://aistudio.google.com/app/apikey
2. Set environment: export GEMINI_API_KEY='your-key-here'
3. Start creating: straighten generate "your prompt here"
"""
    
    console.print(Panel(
        examples_content,
        title="[bold]🍌 Banana Straightener Examples[/bold]",
        border_style="yellow"
    ))

@main.command()
def config():
    """Show current configuration and environment."""
    show_banner()
    
    config_obj = Config.from_env()
    
    config_table = Table(title="Current Configuration")
    config_table.add_column("Setting", style="cyan", width=20)
    config_table.add_column("Value", style="green")
    config_table.add_column("Source", style="dim")
    
    # API Key
    api_status = "✅ Set" if config_obj.api_key else "❌ Missing"
    api_source = config_obj.get_api_key_source()
    config_table.add_row("API Key", api_status, api_source)
    
    # Models
    config_table.add_row("Generator Model", config_obj.generator_model, "Config")
    config_table.add_row("Evaluator Model", config_obj.evaluator_model, "Config")
    
    # Settings
    config_table.add_row("Max Iterations", str(config_obj.default_max_iterations), "Config")
    config_table.add_row("Success Threshold", f"{config_obj.success_threshold:.0%}", "Config")
    config_table.add_row("Output Directory", str(config_obj.output_dir), "Config")
    config_table.add_row("Save Intermediates", str(config_obj.save_intermediates), "Config")
    
    console.print(config_table)
    
    if not config_obj.api_key:
        console.print(f"\n[red]⚠️ API key not found![/red]")
        console.print("[dim]Get your key: https://aistudio.google.com/app/apikey[/dim]")
        console.print("[dim]Set via environment: export GEMINI_API_KEY='your-key-here'[/dim]")
        console.print("[dim]Or create .env file: echo 'GEMINI_API_KEY=your-key-here' > .env[/dim]")

if __name__ == "__main__":
    main()