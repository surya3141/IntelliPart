import shutil
from datetime import datetime
from pathlib import Path

src = Path("d:/OneDrive - Mahindra & Mahindra Ltd/Desktop/POC/Gemini/IntelliPart/IntelliPart/01_dataset_expansion/generate_car_parts_dataset.py")
dst_dir = Path("d:/OneDrive - Mahindra & Mahindra Ltd/Desktop/POC/Gemini/IntelliPart/IntelliPart/01_dataset_expansion/production_dataset/datasets/archived")
dst_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
dst = dst_dir / f"generate_car_parts_dataset_{timestamp}.py"
shutil.copy2(src, dst)
print(f"Archived script to {dst}")