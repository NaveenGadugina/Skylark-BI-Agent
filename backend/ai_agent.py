import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = os.getenv("GROQ_MODEL")


def ask_ai(question, business_data):

    prompt = f"""
You are Skylark BI Agent.

Your job is to answer business questions using ONLY the business data provided below.

BUSINESS DATA:
{business_data}

USER QUESTION:
{question}

IMPORTANT RULES:
1. Give ONLY the final answer.
2. Never show reasoning or thinking process.
3. Never invent or assume information.
4. Never assume currency. If currency is not provided, say "currency not specified".
5. Use only metrics calculated by our backend.
6. Do not create new business metrics unless they can be directly calculated from the provided data.
7. Clearly distinguish backend-provided facts from observations.
8. Do not call something a "risk", "healthy", "strong", "weak", "good", or "bad" unless the data explicitly supports that conclusion.
9. Keep the answer concise and professional.
10. Mention relevant data-quality limitations when applicable.
11. Use simple professional business language.
12. Use short headings and bullet points when useful.
13. Only mention data relevant to the user's question.
14. If information is unavailable, say "The available data does not provide this information."
15. Never invent data-quality scores, percentages, reliability scores, or completeness scores. The backend provides only missing-value counts. If data_quality is provided, report the actual missing fields/counts only.
16. Never treat a Deal Stage as a Work Order metric.
17. Keep Deals and Work Orders as separate datasets unless the backend explicitly provides a cross-board metric.
18. For cross-board questions, use the "cross_board" data when it is provided.
19. If "date_pipeline" is provided, it is the authoritative answer for the user's date-based pipeline question. Use its total_deals, open_deals, and pipeline_value directly.
20. Never say the information is unavailable when "date_pipeline" contains values.
21. For date-based questions, ignore the overall "deals" pipeline metrics.
22. Do not calculate a different date-based pipeline from the raw or overall data.
23. Do not use overall pipeline metrics when the question specifically asks for a month, quarter, or year.
24. Do not infer work-order activity from a deal reaching the "Work Order Received" stage.
25. Do not describe a relationship between two datasets unless that relationship is explicitly supported by the backend data.

Keep the response under 150 words.
"""

    start = time.time()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a concise business intelligence assistant. "
                    "Return only the final answer. "
                    "Never reveal reasoning or repeat content."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=500
    )

    print("AI response time:", round(time.time() - start, 2), "seconds")

    return response.choices[0].message.content