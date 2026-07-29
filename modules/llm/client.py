# this file is used to create a client for the Groq API using the provided API key and model name.
# It loads environment variables from a .env file and raises an error if the API key is not found.
# The default model name is set to "qwen/qwen3.6-27b" if not specified in the environment variables.

from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if api_key is None:
    raise ValueError("GROQ_API_KEY not found in .env")

MODEL_NAME: str = os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")

client = Groq(api_key=api_key)
