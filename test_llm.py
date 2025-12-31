import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load env manually just in case
load_dotenv(dotenv_path="c:\\sem6-real\\ai_verse\\.env")

async def test_llm():
    api_key = os.getenv('GOOGLE_API_KEY')
    print(f"Checking API Key: {'Found' if api_key else 'Missing'}")
    
    try:
        genai.configure(api_key=api_key)
        print("Listing available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
        
    except Exception as e:
        print(f"List Models Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
