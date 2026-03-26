import google.generativeai as genai

# Configure with your API key
genai.configure(api_key="AIzaSyB8a1qF4NqZIm0erF6kkRiHRJxL-zAcOnk")

# List all available models
models = genai.list_models()

# Print model name and supported methods
for m in models:
    print(m.name, "-", m.supported_methods)