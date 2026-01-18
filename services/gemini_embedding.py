import os
import getpass
from langchain_google_genai import GoogleGenerativeAIEmbeddings

if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API key: ")

gemini_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", api_key=os.getenv("GOOGLE_API_KEY")
)
