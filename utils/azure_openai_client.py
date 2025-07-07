import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


 
API_KEY = os.getenv("API_KEY")
API_VERSION = os.getenv("OPENAI_API_VERSION")
API_BASE = os.getenv("API_BASE")
 
if not API_KEY or not API_VERSION or not API_BASE:
    raise ValueError("Les variables d'environnement API_KEY, OPENAI_API_VERSION et API_BASE doivent être définies.")
 
try:
    client = AzureOpenAI(
        api_key=API_KEY,
        api_version=API_VERSION,
        azure_endpoint=API_BASE
    )
except Exception as e:
    raise RuntimeError(f"Erreur lors de l'initialisation du client Azure OpenAI : {e}")