# 01_dataset_expansion: Production Dataset Generation

## Purpose
Generate and maintain the unified production dataset for IntelliPart, supporting 200,000+ automotive parts and 50+ technical attributes per part. All modules use this dataset via the shared loader.

## Features
- 200K+ parts, 50+ attributes, images, drawings
- Output: `production_dataset/datasets/*.jsonl` (used by all modules)
- CLI tools for dataset generation and validation

## Usage
```bash
cd 01_dataset_expansion
pip install -r requirements.txt
python main.py  # Follow prompts to generate or validate dataset
```

## Output Structure
```
production_dataset/
├── datasets/
│   ├── automotive_parts_batch_0001.jsonl
│   ├── ...
├── images/
│   ├── ...
```

## Integration
- All analytics and conversational modules load data from `production_dataset/datasets/` using the shared loader.
- Keep this dataset up to date for best results in downstream modules.

---
**🏆 Production-Ready | 📊 Enterprise-Scale | 🚀 Mahindra Innovation**
