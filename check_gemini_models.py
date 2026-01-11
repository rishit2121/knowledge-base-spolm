"""Check available Gemini models."""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available Gemini models for embeddings:")
print("=" * 70)

# List all models
for model in genai.list_models():
    if 'embedContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Methods: {model.supported_generation_methods}")
        print()

print("\nAvailable Gemini models for chat:")
print("=" * 70)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Methods: {model.supported_generation_methods}")
        print()

