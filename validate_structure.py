#!/usr/bin/env python3
"""
IntelliPart Structure Validation Script
Validates that all core modules are accessible after restructuring
"""

import os
import sys
from pathlib import Path

def check_module_structure():
    """Check if all core modules have their essential files"""
    
    print("🔍 IntelliPart Structure Validation")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    issues = []
    
    # Define expected module structure
    modules = {
        "01_dataset_expansion": ["main.py", "README.md"],
        "02_deep_analysis": ["main.py", "README.md"], 
        "03_conversational_chat": ["conversational_web_app.py", "README.md"],
        "04_hackathon_demo": ["README.md"],
        "05_new_features": ["README.md"]
    }
    
    # Check each module
    for module, required_files in modules.items():
        module_path = base_path / module
        print(f"\n📁 Checking {module}...")
        
        if not module_path.exists():
            issues.append(f"❌ Module {module} not found")
            continue
            
        print(f"  ✅ Module directory exists")
        
        for file in required_files:
            file_path = module_path / file
            if file_path.exists():
                print(f"  ✅ {file} found")
            else:
                issues.append(f"❌ {module}/{file} missing")
                print(f"  ❌ {file} missing")
    
    # Check documentation folder
    print(f"\n📁 Checking docs folder...")
    docs_path = base_path / "docs"
    if docs_path.exists():
        print(f"  ✅ docs/ directory exists")
        doc_files = list(docs_path.glob("*.md"))
        print(f"  ✅ Found {len(doc_files)} documentation files")
    else:
        issues.append("❌ docs/ folder missing")
    
    # Check archive folder  
    print(f"\n📁 Checking Archive_OLD_FILES...")
    archive_path = base_path / "Archive_OLD_FILES"
    if archive_path.exists():
        print(f"  ✅ Archive_OLD_FILES/ directory exists")
        archived_items = len(list(archive_path.iterdir()))
        print(f"  ✅ Contains {archived_items} archived items")
    else:
        issues.append("❌ Archive_OLD_FILES/ folder missing")
    
    # Check root files
    print(f"\n📁 Checking root files...")
    root_files = ["README.md", "requirements.txt", "launch_demo.py", "production_demo.py"]
    for file in root_files:
        file_path = base_path / file
        if file_path.exists():
            print(f"  ✅ {file} found")
        else:
            issues.append(f"❌ {file} missing")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print("⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n❌ Validation failed with {len(issues)} issues")
        return False
    else:
        print("✅ ALL CHECKS PASSED!")
        print("🎉 IntelliPart structure is properly organized")
        return True

def show_structure_overview():
    """Display the current folder structure"""
    print("\n📋 Current Structure Overview:")
    print("-" * 30)
    
    base_path = Path(__file__).parent
    
    # Show main folders only
    for item in sorted(base_path.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            print(f"📁 {item.name}/")
        elif item.is_file() and item.suffix in ['.py', '.md', '.txt']:
            print(f"📄 {item.name}")

if __name__ == "__main__":
    success = check_module_structure()
    show_structure_overview()
    
    if success:
        print("\n🚀 Ready to launch IntelliPart!")
        print("   Run: python launch_demo.py")
    else:
        print("\n🔧 Please fix the issues above before proceeding")
        sys.exit(1)
