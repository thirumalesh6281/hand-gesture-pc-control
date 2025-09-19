#!/usr/bin/env python3
"""
Windows Setup Script for Hand Gesture Control Project
Helps resolve common MediaPipe installation issues on Windows
"""

import subprocess
import sys
import platform
import os

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    elif version.major == 3 and version.minor > 11:
        print("⚠️  Warning: Python 3.12+ may have compatibility issues with MediaPipe")
        print("   Consider using Python 3.9-3.11 for best compatibility")
    else:
        print("✅ Python version is compatible")
    
    return True

def install_package(package_name, specific_version=None):
    """Install a package with pip"""
    if specific_version:
        cmd = [sys.executable, "-m", "pip", "install", f"{package_name}=={specific_version}"]
    else:
        cmd = [sys.executable, "-m", "pip", "install", package_name]
    
    print(f"Installing {package_name}...")
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print(f"✅ {package_name} installed successfully")
        return True
    else:
        print(f"❌ Failed to install {package_name}")
        print(f"Error: {stderr}")
        return False

def test_imports():
    """Test if all required packages can be imported"""
    packages = {
        'cv2': 'OpenCV',
        'mediapipe': 'MediaPipe',
        'pyautogui': 'PyAutoGUI',
        'numpy': 'NumPy'
    }
    
    all_good = True
    
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✅ {name} imports successfully")
        except (ImportError, OSError) as e:
            print(f"❌ {name} failed to import: {e}")
            if "DLL" in str(e).upper():
                print("   This looks like a DLL error - install Visual C++ Redistributable")
            all_good = False
    
    return all_good

def main():
    print("=== Hand Gesture Control - Windows Setup ===")
    print(f"Operating System: {platform.system()} {platform.release()}")
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    print("\n--- Upgrading pip and tools ---")
    upgrade_success, _, _ = run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    if upgrade_success:
        print("✅ pip, setuptools, and wheel upgraded")
    else:
        print("⚠️  Warning: Failed to upgrade pip tools")
    
    print("\n--- Installing Dependencies ---")
    
    # Install packages with specific versions that work well on Windows
    packages = [
        ("opencv-python", "4.8.1.78"),
        ("numpy", "1.24.3"),
        ("pyautogui", "0.9.54"),
        ("mediapipe", "0.10.0")
    ]
    
    for package, version in packages:
        if not install_package(package, version):
            print(f"\nTrying to install {package} without specific version...")
            if not install_package(package):
                print(f"❌ Failed to install {package}")
                print("\nTroubleshooting steps:")
                print("1. Update pip: python -m pip install --upgrade pip")
                print("2. Try: pip install --upgrade setuptools wheel")
                print("3. Install Visual C++ Redistributable from:")
                print("   https://aka.ms/vs/17/release/vc_redist.x64.exe")
                input("Press Enter to continue...")
    
    print("\n--- Testing Imports ---")
    if test_imports():
        print("\n🎉 All packages installed successfully!")
        print("You can now run: python gesture_control.py")
    else:
        print("\n❌ Some packages failed to import")
        print("Try the troubleshooting steps mentioned above")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()