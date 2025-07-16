#!/usr/bin/env python3
"""
Hackathon Demo Cleanup Script
Moves duplicate/older files to archive and keeps only enhanced versions
"""

import os
import shutil
from pathlib import Path

def main():
    """Main cleanup function"""
    
    # Define paths
    demo_dir = Path("d:/OneDrive - Mahindra & Mahindra Ltd/Desktop/POC/Gemini/IntelliPart/IntelliPart/04_hackathon_demo")
    archive_dir = Path("d:/OneDrive - Mahindra & Mahindra Ltd/Desktop/POC/Gemini/IntelliPart/IntelliPart/archived")
    
    # Create archive subdirectory for hackathon files
    hackathon_archive = archive_dir / "04_hackathon_demo_original"
    hackathon_archive.mkdir(exist_ok=True)
    
    print("🧹 IntelliPart Hackathon Demo Cleanup")
    print("=" * 50)
    
    # Files to move to archive (older/duplicate versions)
    files_to_archive = [
        "hackathon_demo.py",
        "hackathon_web_demo.py", 
        "main.py",
        "advanced_analytics.py",  # May be used by others, check first
        "HACKATHON_PRESENTATION_SCRIPT.md",
        "README.md"  # Will be replaced
    ]
    
    # Directories to move to archive
    dirs_to_archive = [
        "templates"
    ]
    
    # Enhanced files to keep (verify they exist)
    enhanced_files = [
        "enhanced_demo.html",
        "demo_server.py",
        "launch_demo.py",
        "demo_setup_verification.py",
        "ENHANCED_DEMO_PRESENTATION_SCRIPT.md",
        "ENHANCED_DEMO_README.md",
        "FINAL_PACKAGE_SUMMARY.md"
    ]
    
    print("📁 Enhanced files found:")
    missing_enhanced = []
    for file in enhanced_files:
        file_path = demo_dir / file
        if file_path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_enhanced.append(file)
    
    if missing_enhanced:
        print(f"\n⚠️  Missing enhanced files: {missing_enhanced}")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    print(f"\n📦 Moving old files to: {hackathon_archive}")
    
    # Move files to archive
    for file in files_to_archive:
        file_path = demo_dir / file
        if file_path.exists():
            try:
                shutil.move(str(file_path), str(hackathon_archive / file))
                print(f"   📦 Moved: {file}")
            except Exception as e:
                print(f"   ❌ Error moving {file}: {e}")
        else:
            print(f"   ⚠️  Not found: {file}")
    
    # Move directories to archive
    for dir_name in dirs_to_archive:
        dir_path = demo_dir / dir_name
        if dir_path.exists():
            try:
                shutil.move(str(dir_path), str(hackathon_archive / dir_name))
                print(f"   📦 Moved directory: {dir_name}")
            except Exception as e:
                print(f"   ❌ Error moving {dir_name}: {e}")
    
    # Create new README.md pointing to enhanced version
    readme_content = """# 🚀 IntelliPart Enhanced Demo

## Quick Start

This folder contains the enhanced, modern demo of IntelliPart designed for hackathon and executive presentations.

### Launch the Demo

```powershell
python demo_setup_verification.py
```

Or for quick launch:

```powershell
python launch_demo.py
```

### Key Files

- `enhanced_demo.html` - Modern UI with glassmorphism design
- `demo_server.py` - Flask backend with live API endpoints
- `launch_demo.py` - One-click launcher
- `ENHANCED_DEMO_PRESENTATION_SCRIPT.md` - Complete presentation guide
- `ENHANCED_DEMO_README.md` - Detailed documentation

### Demo URL
http://localhost:5000

### Original Files
Original hackathon demo files have been moved to `../archived/04_hackathon_demo_original/`

---
**Ready for Hackathon Success! 🏆**
"""
    
    readme_path = demo_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"   ✅ Created new README.md")
    
    print(f"\n✅ Cleanup completed!")
    print(f"📊 Summary:")
    print(f"   • Enhanced files: {len(enhanced_files)} files kept")
    print(f"   • Archived files: {len(files_to_archive)} files moved")
    print(f"   • Archived directories: {len(dirs_to_archive)} directories moved")
    print(f"   • Archive location: {hackathon_archive}")
    
    print(f"\n🚀 Ready to launch enhanced demo:")
    print(f"   cd \"{demo_dir}\"")
    print(f"   python demo_setup_verification.py")

if __name__ == "__main__":
    main()
