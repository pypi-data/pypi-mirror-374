# core/summarizer.py using multiple models via direct Groq API calls
# core/summarizer.py

import os
import pathlib
import requests
from dotenv import load_dotenv, find_dotenv

from codescribe_ai.core.prompt_builder import build_prompt
from codescribe_ai.core.lang_detector import detect_language_from_extension

# --- Load API key safely ---
BASE_DIR = pathlib.Path(__file__).parents[2].resolve()
env_path = find_dotenv(usecwd=True)
load_dotenv(env_path, override=True)

raw = os.getenv("GROQ_API_KEY", "")
GROQ_API_KEY = (raw or "").strip().strip('"').strip("'").replace("\r", "").replace("\n", "")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY missing or invalid in .env")

API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Default model if none provided
DEFAULT_MODEL = "llama-3.3-70b-versatile"


def summarize_code(
    code_chunk: str,
    file_path: str | None = None,
    environment: str = "generic",
    repo_context: dict | None = None,
    model: str | None = None,
) -> str:
    """
    Summarize a code chunk using Groq API.

    Args:
        code_chunk (str): Code to summarize.
        file_path (str | None): Path for context.
        environment (str): Framework/language detected.
        repo_context (dict | None): Extra context (dependencies, env).
        model (str | None): Override model (if None, use DEFAULT_MODEL).

    Returns:
        str: AI-generated summary.
    """
    lang = detect_language_from_extension(file_path or "")
    prompt = build_prompt(
        code_chunk,
        file_path=file_path,
        environment=environment,
        repo_context=repo_context,
    )

    payload = {
        "model": model or DEFAULT_MODEL,   # 👈 dynamic model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }

    try:
        resp = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
            proxies={"http": None, "https": None},  # bypass proxies
        )
    except requests.RequestException as e:
        raise RuntimeError(f"🌐 Network error contacting Groq: {e}")

    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    else:
        raise RuntimeError(f"❌ Groq API error: {resp.status_code} - {resp.text}")


def summarize_file_from_chunks(
    chunk_summaries,
    file_path: str | None = None,
    environment: str = "generic",
    repo_context: dict | None = None,
    model: str | None = None,
) -> str:
    """
    Second-pass coherency summary for a file (summarize the summaries).
    """
    combined_summary = "\n".join(chunk_summaries)
    if not combined_summary.strip():
        return ""

    prompt = (
        "You are consolidating partial summaries into a single accurate file-level summary.\n"
        "Given these partial notes, produce a coherent, high-level explanation of the file:\n\n"
        f"{combined_summary}\n\n"
        "Keep it concise and precise."
    )

    return summarize_code(
        prompt,
        file_path=file_path,
        environment=environment,
        repo_context=repo_context,
        model=model,   # 👈 propagate model choice
    )

















# latest version using direct API calls with only one model (gemma2-9b-it)
# import os
# import pathlib
# import requests
# import re
# from dotenv import load_dotenv, find_dotenv

# from core.prompt_builder import build_prompt
# from core.lang_detector import detect_language_from_extension

# # --- Load and clean API key safely ---
# BASE_DIR = pathlib.Path(__file__).parents[2].resolve()
# env_path = find_dotenv(usecwd=True)
# load_dotenv(env_path, override=True)

# raw = os.getenv("GROQ_API_KEY", "")
# GROQ_API_KEY = (raw or "").strip().strip('"').strip("'").replace("\r", "").replace("\n", "")

# if not GROQ_API_KEY:
#     raise ValueError("❌ GROQ_API_KEY missing or invalid in .env")

# API_URL = "https://api.groq.com/openai/v1/chat/completions"
# MODEL = "gemma2-9b-it"


# def summarize_code(code_chunk: str, file_path: str | None = None, environment: str = "generic", repo_context: dict | None = None) -> str:
#     """
#     Summarize a code chunk using Groq API.
#     """
#     lang = detect_language_from_extension(file_path or "")
#     prompt = build_prompt(code_chunk, file_path=file_path, environment=environment, repo_context=repo_context)

#     payload = {
#         "model": MODEL,
#         "messages": [{"role": "user", "content": prompt}],
#         "temperature": 0.3,
#     }

#     try:
#         resp = requests.post(
#             API_URL,
#             headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
#             json=payload,
#             timeout=30,
#             proxies={"http": None, "https": None},  # bypass proxies
#         )
#     except requests.RequestException as e:
#         raise RuntimeError(f"🌐 Network error contacting Groq: {e}")

#     if resp.status_code == 200:
#         return resp.json()["choices"][0]["message"]["content"]
#     else:
#         raise RuntimeError(f"❌ Groq API error: {resp.status_code} - {resp.text}")


# def summarize_file_from_chunks(chunk_summaries, file_path=None, environment="generic",repo_context=None):
#     """
#     Second-pass coherency summary for a file (summarize the summaries).
#     Notes:
#     - Calls summarize_code() with a meta-prompt; passes repo_context through.
#     - Called by scripts/run_pipeline.py after chunk loop if you use a 2-pass flow.
#     """
#     combined_summary = "\n".join(chunk_summaries)
#     if not combined_summary.strip():
#         return ""

#     prompt = (
#         "You are consolidating partial summaries into a single accurate file-level summary.\n"
#         "Given these partial notes, produce a coherent, high-level explanation of the file:\n\n"
#         f"{combined_summary}\n\n"
#         "Keep it concise and precise."
#     )

#     # Reuse summarize_code to call Groq with cleaned key
#     return summarize_code(prompt, file_path=file_path, environment=environment,repo_context=repo_context)






















# import openai
# from core.prompt_builder import build_prompt

# def summarize_code(code_chunk, file_path=None):  # Summarizes code using OpenAI GPT-4 API
#     """
#     Sends a code chunk to OpenAI's GPT-4 API and returns a summary.

#     Args:
#         code_chunk (str): The code block to summarize.
#         file_path (str): Optional file path for prompt context.

#     Returns:
#         str: Summary generated by GPT-4.

#     Notes:
#         Uses build_prompt() to structure the LLM input.
#     """
#     openai.api_key = "your_openai_api_key_here"
#     MODEL = "gpt-4"

#     prompt = build_prompt(code_chunk, file_path)

#     response = openai.ChatCompletion.create(
#         model=MODEL,
#         messages=[
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.3
#     )

#     return response["choices"][0]["message"]["content"]






# print("🔎 Using summarizer at:", __file__)



# # codescribe_ai/core/summarizer.py (SDK version)
# import os
# from dotenv import load_dotenv, find_dotenv
# from groq import Groq

# from core.prompt_builder import build_prompt
# from core.lang_detector import detect_language_from_extension

# # Load .env robustly
# env_path = find_dotenv(usecwd=True)
# load_dotenv(env_path, override=True)

# def _clean(s: str | None) -> str:
#     s = s or ""
#     return s.strip().strip('"').strip("'").replace("\r", "").replace("\n", "")

# API_KEY = _clean(os.getenv("GROQ_API_KEY"))
# if not API_KEY:
#     raise ValueError("❌ GROQ_API_KEY missing/invalid")

# # Use same model you used in test_env
# MODEL = "llama3-8b-8192"

# # Create client (SDK handles headers/endpoint)
# client = Groq(api_key=API_KEY)

# def summarize_code(code_chunk: str, file_path: str | None = None, environment: str = "generic") -> str:
#     """
#     Summarize a raw code chunk with Groq SDK.
#     Note: build_prompt returns plain string; SDK expects messages list.
#     """
#     _ = detect_language_from_extension(file_path or "")
#     prompt = build_prompt(code_chunk, file_path=file_path, environment=environment)

#     resp = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": "You are a clear code documentation assistant."},
#             {"role": "user", "content": prompt},
#         ],
#         temperature=0.3,
#     )
#     return resp.choices[0].message.content

# def summarize_file_from_chunks(chunk_summaries: list[str], file_path: str | None = None, environment: str = "generic") -> str:
#     """
#     Second-pass summarization: do NOT call build_prompt again (avoid double wrapping).
#     """
#     combined = "\n".join(s for s in chunk_summaries if s and s.strip())
#     if not combined.strip():
#         return ""

#     final_prompt = (
#         "Generate a concise, high-level description of this file from the partial summaries below. "
#         "Prefer structure, mention cross-file context if hinted.\n\n"
#         f"{combined}"
#     )

#     resp = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": "You are a concise, accurate code documentation assistant."},
#             {"role": "user", "content": final_prompt},
#         ],
#         temperature=0.2,
#     )
#     return resp.choices[0].message.content
