import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def generate(prompt: str) -> str:
    """Sends a prompt to the Groq API and returns the generated response."""
    
    # Initialize the Groq client. 
    # It automatically looks for GROQ_API_KEY in your environment variables.
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY")
    )
    
    # Generate the chat completion using Llama 3
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        # Using the recommended model for versatile tasks
        model="llama-3.3-70b-versatile",
    )
    
    # Extract and return the text content from the response
    return chat_completion.choices[0].message.content