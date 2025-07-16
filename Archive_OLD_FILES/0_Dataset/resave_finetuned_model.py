from sentence_transformers import SentenceTransformer

# Path to your fine-tuned model directory (update if needed)
model_path = "0_Dataset/fine_tuned_model"

# Load the model
model = SentenceTransformer(model_path)

# Re-save the model to ensure all required files are present (including model.safetensors or pytorch_model.bin)
model.save(model_path)

print(f"Model re-saved successfully to: {model_path}")
#Would you like to try deleting/renaming model.safetensors and then re-running the scrip