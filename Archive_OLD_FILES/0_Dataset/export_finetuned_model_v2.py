from sentence_transformers import SentenceTransformer
import shutil
import os

# Path to your current fine-tuned model directory
old_model_path = "0_Dataset/fine_tuned_model"
# Path to the new model directory
new_model_path = "0_Dataset/fine_tuned_model_v2"

# Load the model from the old directory
model = SentenceTransformer(old_model_path)

# Remove the new directory if it exists (to avoid file lock issues)
if os.path.exists(new_model_path):
    shutil.rmtree(new_model_path)

# Save the model to the new directory
model.save(new_model_path)

print(f"Model saved successfully to: {new_model_path}")
