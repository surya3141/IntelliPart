import os
from google import genai
import ssl

# Disable SSL verification globally
ssl._create_default_https_context = ssl._create_unverified_context

def authenticate_json():
    json_key_path = "D://OneDrive - Mahindra & Mahindra Ltd//Desktop//POC//Gemini//gemini_v1//scripts//mdp-ad-parts-dev-api-json-key.json"
    if not os.path.exists(json_key_path):
        raise FileNotFoundError(f"Service account key file '{json_key_path}' not found.")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_path

def connect_to_google_genai():
    authenticate_json()
    client = genai.Client(
        vertexai=True,
        project="mdp-ad-parts-dev-338172",
        location="global"
    )
    return client

def ask_llm(query, context=None):
    client = connect_to_google_genai()
    prompt = f"User query: {query}\nContext: {context or ''}\nAnswer:"
    # Assuming the model name is 'gemini-1.0-pro' (update if needed)
    model = client.get_model("gemini-1.0-pro")
    response = model.generate_content(prompt)
    return response.text.strip() if hasattr(response, 'text') else str(response)