# Uses AzureOpenAI (No longer my Key) to break down a user question into smaller, more precise sub-questions

from app.utils.azure_openai_client import client
from icecream import ic

async def rewrite_query(question: str, language: str = "en") -> list:
    """
    Uses the LLM to generate sub-questions for a given question.
    """
    prompt = f"Break down the following question into 3 smaller, precise sub-questions to fully answer it. Write each sub-question as a bullet point. Question: '{question}'"
    # prompt = (
    #     "Break down the following question into at most 3 smaller, precise sub-questions "
    #     "to fully answer it. Write each sub-question as a bullet point. "
    #     f"Question: '{question}'"
    # )
    # Call Azure OpenAI ChatCompletion API
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert at clarifying and reformulating research questions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=300,
        n=1
    )
    ic(question)
    # Extract the content, split by newlines, and clean up
    content = resp.choices[0].message.content.strip()
    subqs = [line.lstrip("- ").strip() for line in content.split('\n') if line.strip()]
    ic(subqs)
    return subqs
