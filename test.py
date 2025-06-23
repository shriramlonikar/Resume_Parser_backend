from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

# Configure the generative AI client
genai.configure(api_key=api_key)

# Create the model and start the chat
model = genai.GenerativeModel(model_name="gemini-2.0-flash")
chat = model.start_chat()

# Send a message and print the response
response = chat.send_message("Hi")
print(response.text)
