import time
from google import genai
from google.genai import errors, types
from app.config import settings

MODELS = ["gemini-3.8-flash"]
RETRY_CODES = {429, 500, 503}

SYSTEM_PROMPT = (
    "You are a research assistant. Answer the question using ONLY the numbered "
    "sources provided. Cite sources inline like [1] or [2][3]. If the sources do "
    "not contain the answer, say you could not find it in the papers. "
    "Be concise and accurate."
)


def generate_text(
    system_prompt: str,
    contents: str,
    max_tokens: int = 800,
    json_mode: bool = False,
) -> str:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is missing in .env")

    client = genai.Client(api_key=settings.gemini_api_key)
    config_args = {
        "system_instruction": system_prompt,
        "max_output_tokens": max_tokens,
    }
    if json_mode:
        config_args["response_mime_type"] = "application/json"
    config = types.GenerateContentConfig(**config_args)

    last_error = None
    for model in MODELS:
        for attempt in range(4):
            try:
                response = client.models.generate_content(
                    model=model, contents=contents, config=config
                )
                return response.text
            except errors.APIError as e:
                last_error = e
                if e.code in RETRY_CODES:
                    time.sleep(2 ** attempt)  # waits 1s, 2s, 4s, 8s
                    continue
                raise

    raise RuntimeError(f"Model is busy, please try again shortly. ({last_error})")


def answer_question(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{i}] (page {c['page']})\n{c['text']}" for i, c in enumerate(chunks, start=1)
    )
    return generate_text(
        SYSTEM_PROMPT,
        f"Sources:\n{context}\n\nQuestion: {question}",
        max_tokens=800,
    )