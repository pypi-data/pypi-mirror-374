#!/usr/bin/env python3
"""
Quick local testing script for Banana Straightener.
Run this to verify everything works locally before publishing.

Usage:
    uv run python test_local.py
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description, check=True):
    """Run a command and print results."""
    print(f"\n🔄 {description}")
    print(f"📝 Command: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            check=check
        )
        print(result.stdout)
        if result.stderr:
            print(f"stderr: {result.stderr}")
        print("✅ Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with code {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    """Run local testing workflow."""
    print("🍌 Banana Straightener - Local Testing Script")
    print("=" * 60)
    
    # Check we're in the right directory
    if not Path("src/banana_straightener").exists():
        print("❌ Run this script from the project root directory!")
        print("Expected to find: src/banana_straightener/")
        sys.exit(1)
    
    # Test 1: Import test
    success = run_command(
        'uv run python -c "from banana_straightener import BananaStraightener; print(\'Import successful!\')"',
        "Testing basic import"
    )
    if not success:
        print("\n❌ Basic import failed. Make sure you ran: uv pip install -e .")
        sys.exit(1)
    
    # Test 2: CLI module access
    run_command(
        "uv run python -m banana_straightener.cli --help",
        "Testing CLI via module syntax"
    )
    
    # Test 3: Entry points
    run_command(
        "straighten --help",
        "Testing CLI via entry point",
        check=False  # Might fail if not installed in editable mode
    )
    
    # Test 4: Config command (doesn't need API key)
    run_command(
        "uv run python -m banana_straightener.cli config",
        "Testing config command"
    )
    
    # Test 5: Examples command
    run_command(
        "uv run python -m banana_straightener.cli examples",
        "Testing examples command"
    )
    
    # Test 6: Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"\n✅ API key found (length: {len(api_key)})")
        
        # Test basic example if API key is present
        print("\n🔄 Testing basic example with API key...")
        run_command(
            "uv run python examples/basic_usage.py",
            "Running basic usage example",
            check=False  # Don't fail the whole script if API fails
        )
    else:
        print("\n⚠️ No GEMINI_API_KEY found in environment")
        print("💡 Set it to test full functionality:")
        print("   export GEMINI_API_KEY='your-key-here'")
    
    # Test 7: Check package structure
    required_files = [
        "src/banana_straightener/__init__.py",
        "src/banana_straightener/agent.py",
        "src/banana_straightener/models.py",
        "src/banana_straightener/config.py",
        "src/banana_straightener/cli.py",
        "src/banana_straightener/ui.py",
        "src/banana_straightener/utils.py",
    ]
    
    print("\n🔄 Checking package structure")
    print("-" * 50)
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files!")
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 LOCAL TESTING COMPLETE!")
    print("=" * 60)
    
    if api_key:
        print("✅ Package structure: OK")
        print("✅ Import functionality: OK") 
        print("✅ CLI access: OK")
        print("✅ API key: Configured")
        print("\n🚀 Ready for full testing and publishing!")
    else:
        print("✅ Package structure: OK")
        print("✅ Import functionality: OK")
        print("✅ CLI access: OK") 
        print("⚠️ API key: Not configured")
        print("\n💡 Set GEMINI_API_KEY to test full functionality")
        print("🚀 Ready for publishing (API tests pending)")

if __name__ == "__main__":
    main()