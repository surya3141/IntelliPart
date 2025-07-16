import os
import json
from typing import List, Dict

def load_all_parts(datasets_dir: str = None) -> List[Dict]:
    """
    Loads and combines all .jsonl files from the given datasets directory.
    If no directory is provided, uses the default production dataset path.
    Returns a list of part dictionaries.
    """
    if datasets_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        datasets_dir = os.path.abspath(os.path.join(script_dir, '..', '01_dataset_expansion', 'production_dataset', 'datasets'))
    all_parts = []
    if os.path.isdir(datasets_dir):
        for fname in os.listdir(datasets_dir):
            if fname.endswith('.jsonl'):
                fpath = os.path.join(datasets_dir, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                all_parts.append(json.loads(line))
                            except Exception as e:
                                print(f"Error parsing line in {fname}: {e}")
    else:
        print(f"Datasets directory not found: {datasets_dir}")
    return all_parts
