#!/usr/bin/env python3
"""
IntelliPart Demo Launcher
"""

import subprocess
import webbrowser
import time
import sys
import os

def main():
    """
    Launches the IntelliPart Flask server and opens the web interface.
    """
    print("=======================================")
    print("🚀 Starting IntelliPart Demo Server...")
    print("=======================================")

    # This script is in the root, the app is in 03_conversational_chat
    app_path = os.path.join(os.path.dirname(__file__), "03_conversational_chat", "conversational_web_app.py")
    
    if not os.path.exists(app_path):
        print(f"❌ ERROR: Could not find the application at {app_path}")
        print("Please ensure the script is run from the project's root directory.")
        sys.exit(1)

    # Launch the Flask server as a separate process
    # Use sys.executable to ensure we're using the same python interpreter
    try:
        # Start the server. On Windows, Popen is non-blocking.
        print(f"🐍 Running: {sys.executable} {app_path}")
        server_process = subprocess.Popen([sys.executable, app_path])
        print(f"✅ Server process started with PID: {server_process.pid}")
    except Exception as e:
        print(f"❌ ERROR: Failed to start the Flask server: {e}")
        sys.exit(1)

    # Wait a few seconds for the server to initialize
    print("⏳ Waiting for server to initialize...")
    time.sleep(5) # Increased wait time for stability

    # The Flask app serves the template at the root URL
    url = "http://127.0.0.1:5000"
    print(f"🌐 Opening web browser to {url}")
    
    try:
        webbrowser.open(url)
        print("✅ Browser launched successfully.")
    except Exception as e:
        print(f"⚠️ WARNING: Could not open web browser automatically: {e}")
        print(f"💡 Please manually open this URL: {url}")

    print("\n🎉 IntelliPart Demo is now running.")
    print("   The server is running in a separate window.")
    print("   Close the server window or press Ctrl+C in it to stop the demo.")
    
    # This script can now exit, as the server is an independent process.
    print("\nLauncher script has finished. The server is running in the background.")


if __name__ == "__main__":
    main()
