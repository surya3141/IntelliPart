"""
Download HuggingFace SentenceTransformer model for offline use.

This script downloads a specified SentenceTransformer model and saves it to a local directory for use in offline semantic search.

Usage:
    python download_model.py --model_name sentence-transformers/all-MiniLM-L6-v2 --output_dir ./.model_cache/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf

Requirements:
    pip install sentence-transformers

Note:
    - This script requires internet access to download the model.
    - After download, copy the output folder to your offline machine if needed.
"""
import argparse
import os
from sentence_transformers import SentenceTransformer

def download_model(model_name, output_dir):
    print(f"Downloading model '{model_name}' to '{output_dir}'...")
    model = SentenceTransformer(model_name)
    os.makedirs(output_dir, exist_ok=True)
    model.save(output_dir)
    print(f"Model saved to '{output_dir}'. You can now use this folder for offline semantic search.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a HuggingFace SentenceTransformer model for offline use.")
    parser.add_argument('--model_name', type=str, default='sentence-transformers/all-MiniLM-L6-v2', help='Model name or path (HuggingFace Hub)')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory to save the model')
    args = parser.parse_args()
    download_model(args.model_name, args.output_dir)
