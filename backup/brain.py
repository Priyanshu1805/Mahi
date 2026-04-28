
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are MAHI, a smart, fast, and professional AI assistant.
Keep answers short, clear, and helpful.
Act like an intelligent assistant from Iron Man.
"""

def ask_mahi(user_input):
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content