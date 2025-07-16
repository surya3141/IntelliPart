#!/usr/bin/env python3
"""
IntelliPart Enhanced Demo Launcher
One-click demo startup with browser integration
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['flask', 'flask-cors']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\n💡 Install with: pip install flask flask-cors")
        return False
    
    return True

def start_demo_server():
    """Start the Flask demo server"""
    try:
        print("🚀 Starting IntelliPart Enhanced Demo Server...")
        
        # Start server in background
        server_process = subprocess.Popen([
            sys.executable, 'demo_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give server time to start
        time.sleep(3)
        
        return server_process
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def open_demo_in_browser():
    """Open the demo in the default browser"""
    # Try to find which port the server is running on
    import socket
    
    ports_to_check = [5000, 5001, 5002, 5003, 8000, 8080]
    server_port = None
    
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:  # Port is in use (server is running)
                server_port = port
                break
        except Exception:
            continue
    
    if server_port:
        demo_url = f'http://localhost:{server_port}'
    else:
        demo_url = f'file:///{Path("enhanced_demo.html").absolute()}'
    
    try:
        print(f"🌐 Opening demo at: {demo_url}")
        webbrowser.open(demo_url)
        return True
    except Exception as e:
        print(f"⚠️ Could not open {demo_url}: {e}")
        return False

def main():
    """Main launcher function"""
    print("=" * 70)
    print("🏆 IntelliPart Enhanced Demo Launcher")
    print("   Advanced AI-Powered Automotive Parts Intelligence")
    print("=" * 70)
    
    # Check if HTML demo file exists
    if not Path("enhanced_demo.html").exists():
        print("❌ Demo file 'enhanced_demo.html' not found!")
        print("💡 Please ensure the demo file is in the current directory.")
        return False
    
    # Check Python requirements
    if not check_requirements():
        print("\n🔧 Installing required packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', 'flask-cors'])
            print("✅ Packages installed successfully!")
        except Exception as e:
            print(f"❌ Failed to install packages: {e}")
            print("📝 Please install manually: pip install flask flask-cors")
            
    print("\n📋 Demo Options:")
    print("1. 🚀 Full Interactive Demo (with live data server)")
    print("2. 📄 Standalone Demo (HTML only)")
    print("3. 🔧 Development Mode (with server logs)")
    
    try:
        choice = input("\n🎯 Select option (1-3): ").strip()
        
        if choice == '1':
            print("\n🚀 Starting full interactive demo...")
            server_process = start_demo_server()
            if server_process:
                time.sleep(2)
                open_demo_in_browser()
                print("\n✅ Demo is running!")
                print("📊 Features available:")
                print("   • Real-time metrics updates")
                print("   • Interactive AI demonstrations")
                print("   • Live data simulation")
                print("   • Full API integration")
                print("\n🛑 Press Ctrl+C to stop the server")
                
                try:
                    server_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down demo server...")
                    server_process.terminate()
                    print("✅ Demo server stopped.")
            
        elif choice == '2':
            print("\n📄 Opening standalone demo...")
            demo_path = Path("enhanced_demo.html").absolute()
            webbrowser.open(f'file:///{demo_path}')
            print("✅ Standalone demo opened in browser!")
            print("📝 Note: Live data features require option 1")
            
        elif choice == '3':
            print("\n🔧 Starting development mode...")
            os.system(f'"{sys.executable}" demo_server.py')
            
        else:
            print("❌ Invalid option. Please choose 1, 2, or 3.")
            
    except KeyboardInterrupt:
        print("\n👋 Demo launcher cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n🎉 Thank you for using IntelliPart Demo!")
    return True

if __name__ == "__main__":
    main()
