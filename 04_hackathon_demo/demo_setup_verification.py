#!/usr/bin/env python3
"""
IntelliPart Enhanced Demo - Setup Verification & Launch
=====================================================

This script verifies all components are properly set up and launches the enhanced demo.
Designed for hassle-free hackathon and executive presentations.

Usage: python demo_setup_verification.py
"""

import os
import sys
import subprocess
import webbrowser
import time
import json
from pathlib import Path

class DemoVerifier:
    def __init__(self):
        self.demo_dir = Path(__file__).parent
        self.required_files = [
            'enhanced_demo.html',
            'demo_server.py',
            'launch_demo.py',
            'requirements.txt',
            'ENHANCED_DEMO_PRESENTATION_SCRIPT.md',
            'ENHANCED_DEMO_README.md'
        ]
        self.issues = []
        self.warnings = []
    
    def print_banner(self):
        """Print professional banner"""
        print("=" * 70)
        print("🚀 IntelliPart Enhanced Demo - Setup Verification")
        print("=" * 70)
        print()
    
    def check_files(self):
        """Verify all required files exist"""
        print("📁 Checking Required Files...")
        missing_files = []
        
        for file in self.required_files:
            file_path = self.demo_dir / file
            if file_path.exists():
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file} - MISSING")
                missing_files.append(file)
        
        if missing_files:
            self.issues.append(f"Missing files: {', '.join(missing_files)}")
        
        print()
    
    def check_python_version(self):
        """Check Python version compatibility"""
        print("🐍 Checking Python Version...")
        version = sys.version_info
        
        if version.major >= 3 and version.minor >= 7:
            print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        else:
            print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requires 3.7+")
            self.issues.append("Python version too old (requires 3.7+)")
        
        print()
    
    def check_dependencies(self):
        """Check if required Python packages are available"""
        print("📦 Checking Dependencies...")
        
        required_packages = ['flask', 'flask_cors']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   ❌ {package} - NOT INSTALLED")
                missing_packages.append(package)
        
        if missing_packages:
            self.warnings.append(f"Missing packages: {', '.join(missing_packages)} (will be auto-installed)")
        
        print()
    
    def check_port_availability(self):
        """Check if demo port is available"""
        print("🌐 Checking Port Availability...")
        
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            
            if result == 0:
                print("   ⚠️  Port 5000 is in use - demo will try alternate port")
                self.warnings.append("Port 5000 occupied, will use alternate port")
            else:
                print("   ✅ Port 5000 available")
        except Exception as e:
            print(f"   ⚠️  Could not check port: {e}")
            self.warnings.append("Could not verify port availability")
        
        print()
    
    def check_browser_availability(self):
        """Check if a suitable browser is available"""
        print("🌍 Checking Browser Availability...")
        
        try:
            # Try to get default browser
            webbrowser.get()
            print("   ✅ Default browser detected")
        except webbrowser.Error:
            print("   ⚠️  No default browser found")
            self.warnings.append("No default browser detected - you may need to open manually")
        
        print()
    
    def verify_demo_structure(self):
        """Verify demo directory structure"""
        print("📋 Verifying Demo Structure...")
        
        # Check for data directory
        data_dir = self.demo_dir / 'data'
        if data_dir.exists():
            print("   ✅ Data directory found")
        else:
            print("   ⚠️  Data directory not found - creating...")
            data_dir.mkdir(exist_ok=True)
            self.warnings.append("Created missing data directory")
        
        # Check for templates directory
        templates_dir = self.demo_dir / 'templates'
        if templates_dir.exists():
            print("   ✅ Templates directory found")
        else:
            print("   ⚠️  Templates directory not found - creating...")
            templates_dir.mkdir(exist_ok=True)
            self.warnings.append("Created missing templates directory")
        
        print()
    
    def install_dependencies(self):
        """Install missing dependencies"""
        if any("Missing packages" in warning for warning in self.warnings):
            print("⚙️  Installing Missing Dependencies...")
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
                ], check=True, cwd=self.demo_dir)
                print("   ✅ Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install dependencies: {e}")
                self.issues.append("Could not install required dependencies")
            print()
    
    def generate_verification_report(self):
        """Generate verification report"""
        print("📊 Verification Report")
        print("-" * 30)
        
        if not self.issues and not self.warnings:
            print("🎉 All checks passed! Demo is ready to launch.")
            return True
        
        if self.warnings:
            print("⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()
        
        if self.issues:
            print("❌ Critical Issues:")
            for issue in self.issues:
                print(f"   • {issue}")
            print()
            print("❌ Demo cannot launch until issues are resolved.")
            return False
        
        print("✅ Demo can launch with warnings.")
        return True
    
    def launch_demo(self):
        """Launch the demo application"""
        print("🚀 Launching IntelliPart Enhanced Demo...")
        print()
        
        try:
            # Launch the demo using the launch script
            launch_script = self.demo_dir / 'launch_demo.py'
            if launch_script.exists():
                subprocess.run([sys.executable, str(launch_script)], cwd=self.demo_dir)
            else:
                # Fallback to direct server launch
                server_script = self.demo_dir / 'demo_server.py'
                subprocess.run([sys.executable, str(server_script)], cwd=self.demo_dir)
                
        except KeyboardInterrupt:
            print("\n🛑 Demo launch interrupted by user")
        except Exception as e:
            print(f"❌ Failed to launch demo: {e}")
    
    def run_verification(self):
        """Run complete verification process"""
        self.print_banner()
        
        # Run all checks
        self.check_files()
        self.check_python_version()
        self.check_dependencies()
        self.check_port_availability()
        self.check_browser_availability()
        self.verify_demo_structure()
        
        # Install dependencies if needed
        self.install_dependencies()
        
        # Generate report
        can_launch = self.generate_verification_report()
        
        print()
        
        # Launch if possible
        if can_launch:
            response = input("🚀 Ready to launch demo? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                self.launch_demo()
            else:
                print("Demo launch cancelled. Run 'python launch_demo.py' when ready.")
        else:
            print("Please resolve the issues above before launching the demo.")
        
        print()
        print("📚 For help, see:")
        print("   • ENHANCED_DEMO_README.md - Complete setup guide")
        print("   • ENHANCED_DEMO_PRESENTATION_SCRIPT.md - Presentation guide")

def main():
    """Main entry point"""
    verifier = DemoVerifier()
    verifier.run_verification()

if __name__ == "__main__":
    main()
