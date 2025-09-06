# 🍌 Banana Straightener

> Self-correcting image generation using Gemini - iterate until it's right!

Banana Straightener is an AI agent that automatically refines image generation through iterative improvement. It generates images based on your prompt, evaluates them against your original intent, and keeps improving until the image matches what you actually wanted.

## ✨ Features

- 🔄 **Self-correcting loop**: Automatically evaluates and improves images with intelligent iteration strategies
- 🎨 **Gemini-powered**: Uses Gemini 2.5 Flash Image Preview for both generation and evaluation
- 🧠 **Smart iteration**: Advanced prompt engineering prevents repetitive loops and adapts strategies
- 💻 **Multiple interfaces**: CLI, Python API, and Web UI with dark theme support
- 📊 **Detailed feedback**: Get insights into what's working and what needs improvement
- 💾 **Session tracking**: Save all iterations and see the improvement process
- ⚙️ **Highly configurable**: Customize models, thresholds, and iteration limits
- 🚀 **Automated releases**: Easy version management and publishing

## 🚀 Quick Start

**Requirements**: Python 3.12+ (tested on Python 3.12 & 3.13)

> 💡 **New in v0.1.3**: Check your installed version with `straighten --version`

### For Local Development

If you're working with the source code locally (before the package is published):

```bash
# Clone the repository
git clone https://github.com/velvet-shark/banana-straightener.git
cd banana-straightener

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install in editable mode
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Set your API key (choose one method)

# Method 1: Create .env file (recommended for local development)
echo 'GEMINI_API_KEY=your-api-key-here' > .env

# Method 2: Set environment variable
export GEMINI_API_KEY="your-api-key-here"

# Test it works
uv run python -c "from banana_straightener import BananaStraightener; print('✅ Import successful!')"

# Test CLI (should show help)
uv run python -m banana_straightener.cli --help

# Run comprehensive local test
uv run python test_local.py
```

### For Production Use

Once published to PyPI:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Banana Straightener
uv pip install banana-straightener
```

### Get your API key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Set it up (choose one method):

**Option A: .env file (recommended)**

```bash
echo 'GEMINI_API_KEY=your-api-key-here' > .env
```

**Option B: Environment variable**

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### Basic Usage

**Command Line:**

```bash
# Generate from a prompt
straighten generate "a perfectly straight banana"

# Modify an existing image
straighten generate "add wings to the cat" --image cat.jpg

# With custom settings
straighten generate "futuristic city" --iterations 10 --save-all
```

**Python API:**

```python
from banana_straightener import BananaStraightener

agent = BananaStraightener()
result = agent.straighten("a dragon reading a book in a library")

if result['success']:
    result['final_image'].save('dragon_librarian.png')
    print(f"Success in {result['iterations']} iterations!")
```

**Web UI:**

```bash
straighten ui
# Opens http://localhost:7860 in your browser
```

## 🧠 How It Works

1. **Generate**: Create an initial image based on your prompt
2. **Evaluate**: Use Gemini to analyze if the image matches your intent
3. **Improve**: If needed, enhance the prompt with specific feedback
4. **Iterate**: Repeat until the image is right or max iterations reached
5. **Success**: Get your perfectly straightened banana! 🍌

## 🚀 Publishing & Releases

### For Contributors

To create a new release (maintainers only):

```bash
# Method 1: Use the automated bump script (recommended)
uv run python scripts/bump-version.py --patch --release
# or
uv run python scripts/bump-version.py 0.1.4 --release

# Method 2: Manual version update
# 1. Update version in pyproject.toml: version = "0.1.4"
# 2. Update version in src/banana_straightener/__init__.py: __version__ = "0.1.4"
# 3. Commit and push - GitHub Actions will automatically create the release

# Method 3: Manual release with script only (no auto-publish)
# python scripts/bump-version.py 0.1.4 (without --release flag)
```

The automated release system will:
- ✅ Update version files
- ✅ Create GitHub release with changelog
- ✅ Publish to PyPI automatically
- ✅ Run all tests before publishing

For detailed release instructions, see [RELEASE.md](RELEASE.md).

### For Users

To update to the latest version:

```bash
# Check current version
straighten --version

# Update to latest
uv pip install --upgrade banana-straightener

# Or with regular pip
pip install --upgrade banana-straightener
```

## 📖 Detailed Usage

### Command Line Interface

The CLI provides the most comprehensive control over the straightening process:

```bash
# Basic generation
straighten generate "your prompt here"

# All available options
straighten generate "a majestic dragon" \
  --image input.jpg \           # Starting image (optional)
  --iterations 10 \             # Max iterations (default: 5)
  --threshold 0.90 \            # Success threshold (default: 0.85)
  --output ./my_outputs \       # Output directory
  --save-all \                  # Save intermediate images
  --open                        # Open results folder when done

# Check version
straighten --version

# Other useful commands
straighten examples             # Show example prompts
straighten config              # Show current configuration
straighten ui --port 8080      # Launch web UI on custom port
straighten --version           # Show installed version
```

### Python API

For integration into your own applications:

```python
from banana_straightener import BananaStraightener, Config
from PIL import Image

# Basic usage
agent = BananaStraightener()
result = agent.straighten("a sunset over mountains")

# Custom configuration
config = Config(
    api_key="your-key",
    default_max_iterations=8,
    success_threshold=0.90,
    save_intermediates=True
)
agent = BananaStraightener(config)

# With input image
input_img = Image.open("photo.jpg")
result = agent.straighten(
    prompt="make this photo look like a painting",
    input_image=input_img,
    max_iterations=5
)

# Process results
if result['success']:
    print(f"✅ Success after {result['iterations']} iterations!")
    result['final_image'].save('output.png')
else:
    print(f"⚠️ Best attempt: {result['best_confidence']:.1%} confidence")

# Real-time processing with generator
for iteration in agent.straighten_iterative("abstract art"):
    print(f"Iteration {iteration['iteration']}: {iteration['evaluation']['confidence']:.1%}")
    if iteration['success']:
        break
```

### Web Interface

The Gradio web UI provides an intuitive interface for interactive use:

- **Real-time progress**: Watch iterations happen live
- **Gallery view**: See all attempts side-by-side
- **Detailed evaluation**: Understand what the AI sees
- **Easy sharing**: Generate public links with `--share`

Launch with: `straighten ui`

## ⚙️ Configuration

### Configuration Options

**Recommended: Create a `.env` file in your project directory:**

```env
# Required
GEMINI_API_KEY=your_api_key_here

# Optional - Model Selection
GENERATOR_MODEL=gemini-2.5-flash
EVALUATOR_MODEL=gemini-2.5-flash

# Optional - Generation Settings
MAX_ITERATIONS=5
SUCCESS_THRESHOLD=0.85
SAVE_INTERMEDIATES=false
OUTPUT_DIR=./outputs

# Optional - UI Settings
GRADIO_PORT=7860
GRADIO_SHARE=false
```

**Alternative: Environment variables (useful for deployment)**

```bash
export GEMINI_API_KEY="your_api_key_here"
export MAX_ITERATIONS=5
export SUCCESS_THRESHOLD=0.85
# ... etc
```

The system will check for API keys in this order:

1. `.env` file in current or parent directories
2. `GEMINI_API_KEY` environment variable
3. `GOOGLE_API_KEY` environment variable

### Python Configuration

```python
from banana_straightener import Config

config = Config(
    api_key="your-key",
    generator_model="gemini-2.5-flash",
    evaluator_model="gemini-2.5-flash",
    default_max_iterations=5,
    success_threshold=0.85,
    save_intermediates=True,
    output_dir=Path("./my_outputs")
)
```

## 🎨 Example Prompts

### Creative Prompts

- "A majestic dragon reading a book in an ancient library"
- "A steampunk robot tending a garden of mechanical flowers"
- "A cozy coffee shop on a rainy evening with warm lighting"
- "Abstract art inspired by the sound of ocean waves"

### Technical/Specific

- "A perfectly straight banana on a white background"
- "Technical diagram of a spaceship engine with labels"
- "Logo design for a tech startup, minimalist, blue and white"
- "Architectural blueprint of a modern sustainable house"

### Photo Editing

- "Add a rainbow to this landscape photo"
- "Make this portrait look like an oil painting"
- "Remove the background and add a sunset sky"
- "Convert this photo to black and white with dramatic lighting"

## 🔧 Advanced Usage

### Custom Evaluation Criteria

```python
# Modify evaluation prompt template
config = Config()
config.evaluation_prompt_template = """
Analyze this image for: "{target_prompt}"

Rate on these specific criteria:
1. Technical quality (composition, lighting)
2. Prompt adherence (how well it matches)
3. Artistic appeal (creativity, style)

Provide scores 0.0-1.0 for each...
"""
```

### Batch Processing

```python
prompts = [
    "a red car on a mountain road",
    "a cat wearing sunglasses",
    "abstract geometric patterns"
]

results = []
agent = BananaStraightener()

for prompt in prompts:
    result = agent.straighten(prompt, max_iterations=3)
    results.append(result)
    print(f"Completed: {prompt}")
```

### Integration with Other Tools

```python
# Use with image preprocessing
from PIL import Image, ImageEnhance

def preprocess_image(img):
    """Enhance image before straightening."""
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(1.2)

# Apply preprocessing
input_img = Image.open("photo.jpg")
enhanced_img = preprocess_image(input_img)

result = agent.straighten(
    "improve the lighting in this photo",
    input_image=enhanced_img
)
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/velvet-shark/banana-straightener.git
cd banana-straightener

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all dependencies
uv pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

**⚠️ Note**: Most tests require a valid `GEMINI_API_KEY` for full functionality.

```bash
# Run quick tests (no API calls required)
uv run pytest tests/test_quick.py -v

# Run all tests (requires API key)
uv run pytest

# Run tests excluding slow API-dependent tests
uv run pytest -m "not slow"

# Run only fast integration tests
uv run pytest tests/test_integration.py -m "not slow"

# Run image generation tests (requires API key)
uv run pytest tests/test_image_generation.py -v

# Local development testing (comprehensive check)
uv run python test_local.py

# Quick manual image generation test
uv run python tests/test_quick_manual.py

# With coverage
uv run pytest --cov=banana_straightener --cov-report=term-missing

# Run specific test files
uv run pytest tests/test_quick.py tests/test_integration.py -v
```

**Test Categories:**

- `test_quick.py` - Fast tests, no API calls required
- `test_image_generation.py` - Core image generation functionality (requires API key)
- `test_integration.py` - End-to-end workflow tests (requires API key)
- `test_local.py` - Comprehensive local development validation script
- `test_quick_manual.py` - Simple manual test for image generation

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Check style
uv run flake8 src/ tests/

# Type checking
uv run mypy src/banana_straightener/
```

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Ensure code quality**: Run `black`, `flake8`, and `mypy`
5. **Test thoroughly**: `pytest` should pass
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Areas for Contribution

- 🎨 **New model integrations** (DALL-E, Midjourney, etc.)
- 🔧 **Evaluation improvements** (custom metrics, multi-modal)
- 🌐 **UI enhancements** (mobile support, themes)
- 📚 **Documentation** (tutorials, examples, guides)
- 🧪 **Testing** (more test cases, integration tests)
- 🚀 **CI/CD improvements** (release automation, testing)

### Development Workflow

All changes automatically trigger CI/CD:
- ✅ **Tests run** on Python 3.12 & 3.13
- ✅ **Code quality** checks (black, flake8, mypy)
- ✅ **Automated releases** when version changes
- ✅ **PyPI publishing** for tagged releases

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/velvet-shark/banana-straightener/issues)
- **Discussions**: [GitHub Discussions](https://github.com/velvet-shark/banana-straightener/discussions)

## 🙏 Acknowledgments

- **Google Gemini** for the powerful multimodal AI
- **Gradio** for the amazing web UI framework
- **Rich** for beautiful command-line interfaces
- **The open-source community** for inspiration and support

---

<div align="center">

**Made with 🍌 and ❤️**

_Straightening bananas, one pixel at a time_

[⭐ Star us on GitHub](https://github.com/velvet-shark/banana-straightener) • [🐦 Follow updates](https://twitter.com/velvet_shark) • [📧 Get support](mailto:mail@velvetshark.com)

</div>
