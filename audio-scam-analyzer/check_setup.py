#!/usr/bin/env python3
# =============================================================================
# INSTALLATION & SETUP VERIFICATION SCRIPT
# =============================================================================
# This script helps debug setup issues

import subprocess
import sys
import os

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or version.minor < 8:
        print("⚠️  Python 3.8+ recommended")
        return False
    return True

def check_module(module_name, import_name=None):
    """Check if Python module is installed"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print(f"✅ {module_name}")
        return True
    except ImportError:
        print(f"❌ {module_name} - NOT INSTALLED")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg")
        return True
    except:
        print("❌ FFmpeg - NOT INSTALLED")
        print("   Install: brew install ffmpeg (Mac) or choco install ffmpeg (Windows)")
        return False

def check_ports():
    """Check if ports are available"""
    import socket
    
    ports = {8000: "Backend", 8001: "Frontend"}
    available = True
    
    for port, service in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  Port {port} ({service}) is already in use")
            available = False
        else:
            print(f"✅ Port {port} ({service}) available")
    
    return available

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🔐 Scam Analyzer - Installation Verification             ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print("📋 Checking Prerequisites...")
    print("-" * 60)
    
    checks = [
        ("Python", check_python),
        ("FFmpeg", check_ffmpeg),
        ("Ports", check_ports),
    ]
    
    all_passed = all(check[1]() for check in checks)
    
    print("\n📦 Checking Python Packages...")
    print("-" * 60)
    
    packages = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("Pydantic", "pydantic"),
        ("Librosa", "librosa"),
        ("SoundFile", "soundfile"),
        ("NumPy", "numpy"),
        ("Whisper", "whisper"),
    ]
    
    packages_ok = all(check_module(name, imp) for name, imp in packages)
    
    print("\n" + "=" * 60)
    
    if all_passed and packages_ok:
        print("✅ All checks passed! Ready to run.")
        print("\n🚀 Start with:")
        print("   cd backend && python app.py")
        return 0
    else:
        print("⚠️  Some checks failed. Please resolve above issues.")
        if not packages_ok:
            print("\n📦 To install missing packages:")
            print("   cd backend && pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
