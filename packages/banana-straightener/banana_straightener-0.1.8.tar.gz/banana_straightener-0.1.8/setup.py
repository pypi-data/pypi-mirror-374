from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="banana-straightener",
    version="0.1.0",
    author="Radek Sienkiewicz",
    author_email="mail@velvetshark.com",
    description="Self-correcting image generation using Gemini - iterate until it's right!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/velvet-shark/banana-straightener",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "google-generativeai>=0.8.0",
        "Pillow>=10.0.0",
        "click>=8.0.0",
        "gradio>=5.0.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "tenacity>=8.0.0",
        "google-genai>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "straighten=banana_straightener.cli:main",
            "banana-straightener=banana_straightener.cli:main",
        ],
    },
)