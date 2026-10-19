import os
from dotenv import load_dotenv

load_dotenv()

Google_Api_Key = os.getenv('Google_Api_Key')
Tavily_Api_Key = os.getenv('Tavily_Api_Key')

Gemini_Model = os.getenv(
    'Gemini_Model',
    'gemini-3.6-flash'
)

Chroma_Path = os.getenv(
    'ChromaDB_Path',
    './chroma_db'
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")