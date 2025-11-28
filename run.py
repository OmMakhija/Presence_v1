#!/usr/bin/env python3
"""
PRESENCE System Launcher
Quick start script for running the PRESENCE Attendance System
"""
import os
import sys
import subprocess
import time

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_virtual_env():
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment active")
        return True
    else:
        print("⚠️  Warning: Not running in virtual environment")
        print("   Consider activating venv: venv\\Scripts\\activate (Windows)")
        return True  # Don't block, just warn

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import torch
        import cv2
        import numpy
        from facenet_pytorch import MTCNN, InceptionResnetV1
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r backend/requirements.txt")
        return False

def check_database():
    """Check if database is initialized"""
    db_path = os.path.join('instance', 'presence.db')
    if os.path.exists(db_path):
        print("✅ Database initialized")
        return True
    else:
        print("⚠️  Database not found, initializing...")
        try:
            subprocess.run([sys.executable, 'backend/init_db.py'], check=True)
            print("✅ Database initialized")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to initialize database")
            return False

def start_server():
    """Start the Flask development server"""
    print("\n🚀 Starting PRESENCE Attendance System...")
    print("=" * 50)
    print("📱 Web Interface: http://127.0.0.1:5000")
    print("🔐 Default Admin: Register with role 'Teacher'")
    print("👤 Student Access: Register with role 'Student'")
    print("=" * 50)
    print("Press Ctrl+C to stop the server\n")

    try:
        # Start Flask development server
        subprocess.run([sys.executable, 'backend/app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 PRESENCE server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False

    return True

def main():
    """Main launcher function"""
    print("🎯 PRESENCE Attendance System Launcher")
    print("=" * 50)

    # Pre-flight checks
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("Dependencies", check_dependencies),
        ("Database", check_database),
    ]

    all_passed = True
    for check_name, check_func in checks:
        print(f"🔍 Checking {check_name}...")
        if not check_func():
            all_passed = False

    if not all_passed:
        print("\n❌ Pre-flight checks failed. Please resolve issues above.")
        print("📖 See DEPLOYMENT.md for detailed setup instructions.")
        return False

    print("\n✅ All checks passed! Starting PRESENCE...")

    # Start the server
    return start_server()

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 PRESENCE launcher interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
