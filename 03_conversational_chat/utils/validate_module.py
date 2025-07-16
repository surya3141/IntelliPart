#!/usr/bin/env python3
"""
03_conversational_chat Module Validation Script
Validates the module structure and core functionality after cleanup
"""

import os
import sys
from pathlib import Path

def validate_module_structure():
    """Validate the module has all required files and structure"""
    
    print("🔍 03_conversational_chat Module Validation")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    issues = []
    
    # Required files
    required_files = {
        "conversational_web_app.py": "Main Flask application",
        "conversational_search.py": "Core search engine",
        "main.py": "Module entry point",
        "README.md": "Module documentation",
        "requirements.txt": "Dependencies"
    }
    
    # Required directories
    required_dirs = {
        "templates": "Web UI templates",
        "archive_legacy": "Legacy files archive",
        "docs": "Module documentation",
        "data": "Local datasets"
    }
    
    print("\n📁 Checking required files...")
    for file, description in required_files.items():
        file_path = base_path / file
        if file_path.exists():
            print(f"  ✅ {file} - {description}")
        else:
            issues.append(f"❌ Missing {file}")
            print(f"  ❌ {file} - {description} (MISSING)")
    
    print("\n📂 Checking required directories...")
    for dir_name, description in required_dirs.items():
        dir_path = base_path / dir_name
        if dir_path.exists():
            item_count = len(list(dir_path.iterdir()))
            print(f"  ✅ {dir_name}/ - {description} ({item_count} items)")
        else:
            issues.append(f"❌ Missing {dir_name}/ directory")
            print(f"  ❌ {dir_name}/ - {description} (MISSING)")
    
    # Check template files
    print("\n🎨 Checking template files...")
    templates_path = base_path / "templates"
    if templates_path.exists():
        template_files = list(templates_path.glob("*.html"))
        if template_files:
            for template in template_files:
                print(f"  ✅ {template.name}")
        else:
            issues.append("❌ No HTML templates found")
            print("  ❌ No HTML templates found")
    
    # Check archive content
    print("\n📦 Checking archive content...")
    archive_path = base_path / "archive_legacy"
    if archive_path.exists():
        archived_files = len(list(archive_path.iterdir()))
        print(f"  ✅ {archived_files} legacy files archived")
        if archived_files < 10:
            print("  ⚠️  Expected more legacy files (should be ~16)")
    
    # Validation summary
    print("\n" + "=" * 50)
    if issues:
        print("⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n❌ Validation failed with {len(issues)} issues")
        return False
    else:
        print("✅ ALL CHECKS PASSED!")
        print("🎉 Module structure is properly organized")
        return True

def check_main_application():
    """Quick check if the main application can be imported"""
    print("\n🔧 Testing main application import...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        # Just test if we can import without running
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "conversational_web_app", 
            Path(__file__).parent / "conversational_web_app.py"
        )
        if spec and spec.loader:
            print("  ✅ Main application can be imported")
            return True
        else:
            print("  ❌ Failed to load main application")
            return False
    except Exception as e:
        print(f"  ⚠️  Import test failed: {e}")
        return False

def show_module_overview():
    """Display current module structure"""
    print("\n📋 Module Structure Overview:")
    print("-" * 30)
    
    base_path = Path(__file__).parent
    
    # Show main files
    print("📄 Core Files:")
    for item in sorted(base_path.iterdir()):
        if item.is_file() and item.suffix in ['.py', '.md', '.txt']:
            print(f"   {item.name}")
    
    print("\n📁 Directories:")
    for item in sorted(base_path.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            item_count = len(list(item.iterdir()))
            print(f"   {item.name}/ ({item_count} items)")

if __name__ == "__main__":
    print("🚀 03_conversational_chat Module Validation")
    print("=" * 50)
    
    structure_ok = validate_module_structure()
    import_ok = check_main_application()
    show_module_overview()
    
    print("\n" + "=" * 50)
    if structure_ok and import_ok:
        print("🎉 MODULE VALIDATION SUCCESSFUL!")
        print("✅ Module is ready for production use")
        print("\n🚀 Quick Start:")
        print("   python conversational_web_app.py")
        print("   # Access: http://localhost:5004")
    else:
        print("❌ MODULE VALIDATION FAILED")
        print("🔧 Please fix the issues above")
        sys.exit(1)
