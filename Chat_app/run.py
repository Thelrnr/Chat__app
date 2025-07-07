#!/usr/bin/env python3
"""
Simple Chat App Startup Script
Run this to start the chat application
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import flask
        import flask_socketio
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    print("🚀 Starting Simple Chat App...")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("✗ app.py not found!")
        sys.exit(1)
    
    print("✓ Starting Flask application...")
    print("✓ Server will be available at: http://localhost:5000")
    print("✓ Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        # Run the Flask app
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Chat app stopped. Goodbye!")
    except Exception as e:
        print(f"✗ Error starting app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 