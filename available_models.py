import google.generativeai as genai

genai.configure(api_key="AIzaSyBhrOZUVySN9Y6Ly7sg6SdTpiQsqlnoHLk")

# Retrieve the list of available models
models = genai.list_models()

# Open a text file to write the model names
with open("gemini_models.txt", "w") as file:
    for model in models:
        file.write(f"{model.name}\n")
        print(model.name)
