import google.generativeai as genai
import os
genai.configure(api_key="AIzaSyBhrOZUVySN9Y6Ly7sg6SdTpiQsqlnoHLk") # Or however you configure it
model_name = "gemini-2.5-flash-preview-04-17-thinking"
try:
    model = genai.GenerativeModel(model_name=model_name)
    print(model)
    print(type(model))
    print(hasattr(model, 'generate_content'))
except Exception as e:
    print(f"Error during direct test: {e}")