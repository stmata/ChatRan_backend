import re

def extract_sub_queries_and_answer(gpt_content: str):
    """
    Extrait les sous-questions et la réponse à partir du texte brut du modèle.
    Format attendu :
    Sub-questions:
    1. ...
    2. ...
    
    Answer:
    ...
    """
    sub_queries = []
    answer = gpt_content
    parts = re.split(r'(?i)answer\s*:', gpt_content, maxsplit=1)
    if len(parts) == 2:
        sub_block, answer = parts
    else:
        sub_block, answer = gpt_content, gpt_content
    sub_lines = re.findall(r'\d+\.\s*(.+)', sub_block)
    sub_queries = [q.strip() for q in sub_lines][:3]
    return sub_queries, answer.strip()


def extract_out_of_scope_flag(answer: str) -> bool:
    """
    Détecte s'il y a une ligne OUT_OF_SCOPE: true|false à la fin du texte.
    """
    m = re.search(r'OUT_OF_SCOPE\s*:\s*(true|false)', answer, re.IGNORECASE)
    if m:
        return m.group(1).lower() == "true"
    return False


def remove_out_of_scope_line(answer: str) -> str:
    """
    Supprime la ligne OUT_OF_SCOPE: true|false s’il y en a une.
    """
    return re.sub(r'OUT_OF_SCOPE\s*:\s*(true|false)\s*$', '', answer, flags=re.IGNORECASE).strip()


def remove_links(text: str, citations: list) -> str:
    """
    Supprime les liens (Markdown ou bruts) dans le texte, en se basant sur les citations listées.
    """
    # Supprime les liens Markdown [text](url)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', r'\1', text)
    # Supprime tous les liens listés
    for url in citations:
        text = text.replace(url, "")
    # Supprime les URLs restantes
    text = re.sub(r'https?://[^\s\]\)]+', '', text)
    return text
