import openai
from app.utils.azure_openai_client import client


async def check_scope_llm(question: str, allowed_topics: list) -> bool:
    """
    Uses LLM to check if question is about one of the allowed topics.
    """
    topics_str = "; ".join(allowed_topics)
    prompt = (
        "You are a strict classifier. "
        "Is the following question about / related any of these topics: "
        f"[{topics_str}]? "
        "Reply only with 'True' or 'False'.\n\n"
        f"Question: {question}"
    )
    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages=[
            {"role": "system", "content": "You classify questions as in-scope or out-of-scope based on a list of topics."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=5,
        n=1
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer.startswith("true")
