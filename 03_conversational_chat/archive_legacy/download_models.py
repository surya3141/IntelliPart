"""
Model Download Script for Corporate Environment

This script helps download and cache Hugging Face models when you have network access
(e.g., from home or with proper IT permissions). Once downloaded, the models can be
used offline in corporate environments.

Usage:
1. Run this script when you have unrestricted internet access
2. It will download and cache the models locally
3. Your main application will then use the cached models

Run with: python download_models.py
"""

import os
import ssl
from pathlib import Path
from sentence_transformers import SentenceTransformer

def setup_ssl_bypass():
    """Setup SSL bypass for downloading (only for model download, not production)"""
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['CURL_CA_BUNDLE'] = ''
        print("✅ SSL bypass configured for model download")
    except Exception as e:
        print(f"⚠️ SSL bypass setup failed: {e}")

def download_models():
    """Download and cache the required models"""
    
    models_to_download = [
        'all-MiniLM-L6-v2',           # Primary model (small, fast)
        'paraphrase-MiniLM-L3-v2',    # Fallback model (even smaller)
        'all-mpnet-base-v2'           # High-quality option
    ]
    
    # Create local models directory
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    print("🔄 Starting model download process...")
    print(f"📁 Models will be saved to: {models_dir}")
    
    successful_downloads = []
    failed_downloads = []
    
    for model_name in models_to_download:
        try:
            print(f"\n🚀 Downloading {model_name}...")
            
            # Download and cache the model
            model = SentenceTransformer(model_name)
            
            # Save to local directory
            local_path = models_dir / model_name
            model.save(str(local_path))
            
            print(f"✅ Successfully downloaded and saved {model_name}")
            successful_downloads.append(model_name)
            
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")
            failed_downloads.append((model_name, str(e)))
    
    # Summary
    print(f"\n📊 Download Summary:")
    print(f"✅ Successful: {len(successful_downloads)}")
    print(f"❌ Failed: {len(failed_downloads)}")
    
    if successful_downloads:
        print(f"\n🎉 Successfully downloaded models:")
        for model in successful_downloads:
            print(f"   - {model}")
        print(f"\n💡 These models are now available for offline use!")
        print(f"📁 Location: {models_dir}")
    
    if failed_downloads:
        print(f"\n⚠️ Failed downloads:")
        for model, error in failed_downloads:
            print(f"   - {model}: {error}")
    
    return successful_downloads

def test_cached_models():
    """Test that cached models work correctly"""
    models_dir = Path(__file__).parent / "models"
    
    print(f"\n🧪 Testing cached models in {models_dir}...")
    
    # Find downloaded models
    cached_models = [d.name for d in models_dir.iterdir() if d.is_dir()]
    
    if not cached_models:
        print("❌ No cached models found")
        return
    
    for model_name in cached_models:
        try:
            model_path = models_dir / model_name
            model = SentenceTransformer(str(model_path))
            
            # Test encoding
            test_text = "Test automotive part search"
            embedding = model.encode([test_text])
            
            print(f"✅ {model_name}: Working (embedding shape: {embedding.shape})")
            
        except Exception as e:
            print(f"❌ {model_name}: Failed - {e}")

if __name__ == "__main__":
    print("🏢 Hugging Face Model Downloader for Corporate Environment")
    print("=" * 60)
    
    # Check if we should bypass SSL (only for downloading)
    response = input("\n⚠️ Bypass SSL verification for download? (y/N): ").lower().strip()
    if response in ['y', 'yes']:
        setup_ssl_bypass()
        print("🔓 SSL verification bypassed for this session")
    
    # Download models
    successful_models = download_models()
    
    # Test cached models
    if successful_models:
        test_response = input("\n🧪 Test cached models? (Y/n): ").lower().strip()
        if test_response not in ['n', 'no']:
            test_cached_models()
    
    print(f"\n✨ Done! You can now use the models offline in your corporate environment.")
    print(f"💡 The main application will automatically detect and use cached models.")
