# IntelliPart Project Structure Guide

## Overview
The IntelliPart project has been restructured for better organization and maintainability. This document explains the new folder structure and what each component contains.

## Main Directory Structure

### Core Modules (Production-Ready)
- **`01_dataset_expansion/`** - Production dataset generation system supporting 200K+ automotive parts
- **`02_deep_analysis/`** - Advanced analytics engine with predictive capabilities and BI dashboards  
- **`03_conversational_chat/`** - Main AI conversational interface with Gemini LLM integration
- **`04_hackathon_demo/`** - Modern demo and presentation platform for stakeholders
- **`05_new_features/`** - Innovation lab for rapid prototyping and new feature development

### Documentation & Resources
- **`docs/`** - All documentation, presentations, user guides, and solution documents
  - `USER_GUIDE.md` - User manual for the platform
  - `COMPREHENSIVE_SOLUTION_DOCUMENT.md` - Complete technical documentation
  - `HACKATHON_DEMO_GUIDE.md` - Demo presentation guide
  - `*.pdf`, `*.pptx` - Presentation materials

### Archive & Legacy
- **`Archive_OLD_FILES/`** - All legacy files, old versions, logs, and deprecated code
  - Contains old demo files, test scripts, backup configurations
  - Legacy datasets and models
  - Previous implementation versions

### Root Files
- **`launch_demo.py`** - Quick launch script for the web interface
- **`production_demo.py`** - Production system demonstration script  
- **`README.md`** - Main project overview and quick start guide
- **`requirements.txt`** - Core Python dependencies

### System Folders
- **`.git/`** - Git version control
- **`.model_cache/`** - Cached AI models
- **`.venv/`** - Python virtual environment

## Quick Navigation

### To Start Using IntelliPart:
1. Run `python launch_demo.py` for instant access
2. Read `docs/USER_GUIDE.md` for detailed usage

### For Development:
1. Check module-specific READMEs in `01_dataset_expansion/`, `02_deep_analysis/`, etc.
2. Use `production_demo.py` for system overview

### For Documentation:
1. All user-facing docs are in `docs/`
2. Technical specifications in `docs/COMPREHENSIVE_SOLUTION_DOCUMENT.md`

### For Legacy Reference:
1. All old files preserved in `Archive_OLD_FILES/`
2. Previous implementations in `Archive_OLD_FILES/archived_legacy/`

## Benefits of New Structure
- **Clean separation** between active code and legacy files
- **Logical organization** with numbered modules showing workflow
- **Centralized documentation** in dedicated docs folder
- **Preserved history** with comprehensive archive
- **Quick access** via root-level launch scripts

---
*Last Updated: July 16, 2025*
