#!/usr/bin/env python3
"""
Setup script for Option Pricing Platform.

This script checks dependencies and sets up the environment.
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_python_version():
    """Check Python version is 3.9+."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ ERROR: Python 3.9 or higher required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print("✅ Python version OK")
    return True


def install_dependencies():
    """Install required dependencies."""
    print_header("Installing Dependencies")
    
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    print("Installing packages from requirements.txt...")
    print("(This may take a few minutes)\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("\n✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to install dependencies: {e}")
        return False


def check_imports():
    """Check if key modules can be imported."""
    print_header("Checking Module Imports")
    
    required_modules = [
        ("numpy", "NumPy"),
    ]
    
    optional_modules = [
        ("pandas", "Pandas"),
        ("openpyxl", "OpenPyXL"),
        ("matplotlib", "Matplotlib"),
    ]
    
    all_ok = True
    
    print("\nRequired modules:")
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {display_name}")
        except ImportError:
            print(f"  ❌ {display_name} - NOT FOUND")
            all_ok = False
    
    print("\nOptional modules (recommended):")
    for module_name, display_name in optional_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {display_name}")
        except ImportError:
            print(f"  ⚠️  {display_name} - not installed (optional)")
    
    return all_ok


def check_files():
    """Check if all required files exist."""
    print_header("Checking Project Files")
    
    required_files = [
        "main.py",
        "utils.py",
        "interfaces.py",
        "models.py",
        "pricing_strategies.py",
        "greeks_mixin.py",
        "options.py",
        "jump_diffusion.py",
        "trade_blotter.py",
        "context_managers.py",
        "data_io.py",
        "factory.py",
        "sample_trades.csv",
        "test_option_platform.py",
        "README.md"
    ]
    
    all_present = True
    
    for filename in required_files:
        file_path = Path(filename)
        if file_path.exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} - MISSING")
            all_present = False
    
    return all_present


def run_quick_test():
    """Run a quick import test."""
    print_header("Running Quick Test")
    
    print("Testing module imports...")
    
    try:
        import utils
        import interfaces
        import models
        import factory
        print("✅ All core modules import successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def main():
    """Main setup function."""
    print_header("Option Pricing Platform - Setup")
    print("Bank XYZ Quantitative Development")
    print()
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version too old")
        sys.exit(1)
    
    # Check files
    if not check_files():
        print("\n⚠️  Warning: Some files are missing")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Install dependencies
    print("\nWould you like to install dependencies now?")
    response = input("Install from requirements.txt? (y/n): ")
    
    if response.lower() == 'y':
        if not install_dependencies():
            print("\n❌ Setup failed: Could not install dependencies")
            sys.exit(1)
    
    # Check imports
    if not check_imports():
        print("\n❌ Setup incomplete: Some required modules missing")
        print("\nTry running: pip install -r requirements.txt")
        sys.exit(1)
    
    # Quick test
    if not run_quick_test():
        print("\n⚠️  Warning: Module import test failed")
    
    # Success
    print_header("Setup Complete!")
    print("""
✅ All checks passed!

Next steps:
1. Review the README.md file
2. Run the main demo:
   
   python main.py

3. Run tests (optional):
   
   python test_option_platform.py
   
4. Check the output files generated by main.py

For questions, see DESIGN_MEMO.md or contact the development team.
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
