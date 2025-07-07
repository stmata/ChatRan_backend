import re
import asyncio
from utils.prompts import SYSTEM_PROMPT
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from starlette.concurrency import run_in_threadpool

# Loads variables from .env file into environment
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

def extract_sub_queries_and_answer(gpt_content: str):
    # 1. Extraire sub-queries numérotées
    sub_lines = re.findall(r'^\s*\d+\.\s*(.+)', gpt_content, flags=re.MULTILINE)
    sub_queries = [q.strip() for q in sub_lines][:5]

    # 2. Extraire la section Sources (même en fin de texte, avec ou sans ligne vide)
    citations = []
    sources_block = ""
    sources_match = re.search(r'Sources\s*:?\s*\n([\s\S]+)', gpt_content, flags=re.IGNORECASE)
    if sources_match:
        sources_block = sources_match.group(1).strip()
        # Prend tout jusqu’à un double saut de ligne OU fin du texte
        sources_block = re.split(r'\n\s*\n', sources_block)[0]
        citations = re.findall(r'https?://[^\s\)\]\}]+', sources_block)

    # 3. Nettoyage de la réponse
    cleaned = gpt_content

    # Supprimer sub-queries
    cleaned = re.sub(r'^\s*\d+\.\s*.+$', '', cleaned, flags=re.MULTILINE)

    # Supprimer Sources section
    cleaned = re.sub(r'Sources\s*:?\s*\n[\s\S]+', '', cleaned, flags=re.IGNORECASE)

    # Nettoyage final
    answer = cleaned.strip()

    return sub_queries, answer, citations

# def extract_out_of_scope_flag(answer: str) -> bool:
#     m = re.search(r'OUT_OF_SCOPE\s*:\s*(true|false)', answer, re.IGNORECASE)
#     if m:
#         return m.group(1).lower() == "true"
#     return False  # fallback value si la ligne est manquante

# def remove_links(text, citations):
#     # Enlève les liens markdown
#     text = re.sub(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', r'\1', text)
#     # Supprime tous les liens bruts
#     for url in citations:
#         text = text.replace(url, "")
#     text = re.sub(r'https?://[^\s\]\)]+', '', text)
#     # Supprime la section Sources s’il reste des traces
#     text = re.sub(r'Sources:\s*(.+?)(?:\n\s*\n|OUT_OF_SCOPE|$)', '', text, flags=re.DOTALL | re.IGNORECASE)
#     return text.strip()


async def run_in_threadpool_iterable(sync_iterable):
    loop = asyncio.get_running_loop()
    for item in sync_iterable:
        yield await loop.run_in_executor(None, lambda: item)

async def handle_chat_gptweb(
    question: str,
    language: str = "en",
    allowed_topics: list = None,
    conversation_history: list = None
):
    topics = allowed_topics or []
    domain_str = ", ".join(topics) if topics else "No topics provided"

    # Prompt système unique
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(domain=domain_str)}
    ]

    # Historique de la conversation (déjà au bon format avec MessageItem)
    if conversation_history:
        for item in conversation_history:
            messages.append({
                "role": item.role,
                "content": item.content
            })

    # Ajout de la nouvelle question (sans redondance)
    messages.append({
        "role": "user",
        "content": question
    })

    def gpt_call():
        return client.chat.completions.create(
            model='gpt-4o',
            messages=messages,
            temperature=0.3,
            max_tokens=1200
        )

    try:
        chat_response = await run_in_threadpool(gpt_call)
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'appel Azure OpenAI: {e}")

    gpt_output = chat_response.choices[0].message.content.strip()
    print(gpt_output)
    sub_queries, answer, citations = extract_sub_queries_and_answer(gpt_output)
    
    # out_of_scope = extract_out_of_scope_flag(answer)
    # sources_section = re.search(r'Sources:\s*(.+)', answer, re.DOTALL | re.IGNORECASE)
    # urls = []
    # if sources_section:
    #     urls = re.findall(r'https?://[^\s\)]+', sources_section.group(1))
    # citations = re.findall(r'https?://[^\s\'\"\)\]]+', answer)
    # citations += re.findall(r'\[.*?\]\((https?://[^\s\)]+)\)', answer)
    # citations += urls
    # top_citations = list(dict.fromkeys(citations))[:10]
    # cleaned_answer = remove_links(answer, top_citations)

    print("🧠 Question:", question)
    print(answer)
    # print("✅ Answer:", cleaned_answer.strip())
    # print(citations)
    # print(sub_queries)
    return {
        "original_question": question,
        "sub_queries": sub_queries,
        "response": answer.strip(),
        "citations": citations,
        "allowed_topics": topics
    }


