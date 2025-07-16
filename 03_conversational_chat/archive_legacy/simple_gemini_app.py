"""
Simple Gemini Test App - Diagnose Connection Issues
"""

from flask import Flask, jsonify, request
import json
import os
import time

# Test if Google AI is available
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
    print("✅ Google AI library imported successfully")
except ImportError as e:
    GEMINI_AVAILABLE = False
    print(f"❌ Google AI library not available: {e}")
    genai = None

app = Flask(__name__)

# Gemini Configuration
GEMINI_JSON_PATH = "D:/OneDrive - Mahindra & Mahindra Ltd/Desktop/POC/Gemini/gemini_v1/scripts/mdp-ad-parts-dev-api-json-key.json"
GEMINI_MODEL_NAME = "gemini-2.0-flash-exp"

def test_gemini_connection():
    """Test Gemini connection"""
    if not GEMINI_AVAILABLE:
        return {"status": "error", "message": "Google AI library not installed"}
    
    try:
        # Check if JSON file exists
        if not os.path.exists(GEMINI_JSON_PATH):
            return {"status": "error", "message": f"JSON key not found at: {GEMINI_JSON_PATH}"}
        
        # Try to set up credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GEMINI_JSON_PATH
        
        # Try to initialize model
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        
        # Try a simple test
        response = model.generate_content("Say 'Hello from Gemini'")
        
        if response.candidates and response.candidates[0].content:
            return {
                "status": "success", 
                "message": "Gemini 2.0 Pro connected successfully!",
                "test_response": response.candidates[0].content.parts[0].text
            }
        else:
            return {"status": "error", "message": "No response from Gemini"}
            
    except Exception as e:
        return {"status": "error", "message": f"Gemini connection failed: {str(e)}"}

@app.route('/')
def home():
    """Simple test page"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Gemini Connection Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        #result { margin-top: 20px; }
    </style>
</head>
<body>
    <h1>🔧 IntelliPart - Gemini Connection Test</h1>
    
    <div class="status info">
        <strong>Status:</strong> Testing Gemini 2.0 Pro connection...
    </div>
    
    <button onclick="testConnection()">Test Gemini Connection</button>
    
    <div id="result"></div>
    
    <script>
        async function testConnection() {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<div class="status info">Testing connection...</div>';
            
            try {
                const response = await fetch('/test-gemini');
                const data = await response.json();
                
                if (data.status === 'success') {
                    resultDiv.innerHTML = `
                        <div class="status success">
                            <strong>✅ Success!</strong><br>
                            ${data.message}<br>
                            <strong>Test Response:</strong> ${data.test_response || 'N/A'}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="status error">
                            <strong>❌ Error:</strong><br>
                            ${data.message}
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="status error">
                        <strong>❌ Connection Error:</strong><br>
                        ${error.message}
                    </div>
                `;
            }
        }
        
        // Test on page load
        testConnection();
    </script>
</body>
</html>
    '''

@app.route('/test-gemini')
def test_gemini():
    """Test Gemini API endpoint"""
    result = test_gemini_connection()
    return jsonify(result)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Simple chat endpoint"""
    if not GEMINI_AVAILABLE:
        return jsonify({"error": "Gemini not available"})
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "No message provided"})
        
        # Set up credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GEMINI_JSON_PATH
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        
        # Generate response
        response = model.generate_content(f"You are a helpful automotive parts assistant. User says: {message}")
        
        if response.candidates and response.candidates[0].content:
            return jsonify({
                "success": True,
                "response": response.candidates[0].content.parts[0].text
            })
        else:
            return jsonify({"error": "No response generated"})
            
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    print("🚀 Starting Simple Gemini Test App...")
    print("📋 Checking configuration...")
    print(f"   JSON Path: {GEMINI_JSON_PATH}")
    print(f"   JSON Exists: {os.path.exists(GEMINI_JSON_PATH)}")
    print(f"   Gemini Available: {GEMINI_AVAILABLE}")
    print("🌐 Access at: http://127.0.0.1:5003")
    print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5003)
