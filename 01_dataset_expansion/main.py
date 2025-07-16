#!/usr/bin/env python3
"""
Production Dataset Generation - Main Entry Point
Generates 200,000+ automotive parts with 50+ attributes each
"""

import sys
import os
import time
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from production_dataset_generator import ProductionDatasetGenerator

def get_script_root():
    return Path(__file__).parent.resolve()

def main():
    """Main function for production dataset generation"""
    print("🚀 IntelliPart Production Dataset Generator")
    print("=" * 60)
    print("📊 Generating 200,000+ automotive parts with 50+ attributes each")
    print("🎯 Features: Images, Technical Specs, Supply Chain, Quality Metrics")
    print()
    
    # Always resolve output_dir relative to script location
    script_root = get_script_root()
    generator = ProductionDatasetGenerator(output_dir = script_root / "production_dataset")
    
    # Generate different dataset sizes for different use cases
    datasets = [
        {"name": "Sample Dataset", "parts": 1000, "description": "Quick testing and development"},
        {"name": "Medium Dataset", "parts": 25000, "description": "Demo and validation"},
        {"name": "Production Dataset", "parts": 200000, "description": "Full production environment"}
    ]
    
    print("Available dataset options:")
    for i, dataset in enumerate(datasets, 1):
        print(f"{i}. {dataset['name']}: {dataset['parts']:,} parts - {dataset['description']}")
    
    print()
    choice = input("Select dataset to generate (1-3) or 'all' for all datasets: ").strip().lower()
    
    start_time = time.time()
    
    if choice == 'all':
        # Generate all datasets
        for dataset in datasets:
            print(f"\n🔧 Generating {dataset['name']}...")
            generator.generate_dataset(
                num_parts=dataset['parts'],
                batch_size=min(1000, dataset['parts'] // 10)
            )
    else:
        try:
            dataset_idx = int(choice) - 1
            if 0 <= dataset_idx < len(datasets):
                dataset = datasets[dataset_idx]
                print(f"\n🔧 Generating {dataset['name']}...")
                generator.generate_dataset(
                    num_parts=dataset['parts'],
                    batch_size=min(1000, dataset['parts'] // 10)
                )
            else:
                print("❌ Invalid choice. Generating sample dataset...")
                generator.generate_dataset(num_parts=1000)
        except ValueError:
            print("❌ Invalid input. Generating sample dataset...")
            generator.generate_dataset(num_parts=1000)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n✅ Dataset generation completed in {duration:.2f} seconds")
    print(f"📁 Output directory: {generator.output_dir}")
    print("\n📋 Generated files:")
    print("  • Batch files: production_dataset/datasets/automotive_parts_batch_*.jsonl")
    print("  • Summary: production_dataset/dataset_summary.json")
    print("  • Images: production_dataset/images/")
    print("  • Technical drawings: production_dataset/technical_drawings/")
    print("  • Documentation: production_dataset/documentation/")
    
    print("\n🎯 Next Steps:")
    print("  1. Run deep analysis: python ../02_deep_analysis/main.py")
    print("  2. Start conversational AI: python ../03_conversational_chat/main.py")
    print("  3. Launch demo: python ../04_hackathon_demo/launch_demo.py")

if __name__ == "__main__":
    main()
