# # core/prompt_builder.py

# import os
# from core.lang_detector import detect_language_from_extension

# def build_prompt(code_chunk, file_path=None, environment="generic", language="python"):
#     """
#     Builds a prompt to summarize code with contextual awareness.

#     Args:
#         code_chunk (str): The code snippet or chunk.
#         file_path (str): Optional file path to include in the prompt.
#         environment (str): Detected environment/framework (e.g., 'flask', 'react').
#         language (str): Language of the file (e.g., 'python', 'javascript').

#     Returns:
#         str: Formatted prompt string.
#     """

#     header = "You are an intelligent AI that helps developers understand code easily."

#     # Language-aware code block (for formatting)
#     language = language.lower()
#     code_lang_tag = {
#         "python": "python",
#         "javascript": "javascript",
#         "typescript": "typescript",
#         "java": "java",
#         "go": "go",
#         "c": "c",
#         "cpp": "cpp",
#         "csharp": "csharp",
#         "ruby": "ruby",
#         "php": "php",
#         "html": "html",
#         "css": "css",
#         "bash": "bash",
#         "json": "json",
#         "yaml": "yaml",
#         "rust": "rust",
#     }.get(language, "")  # fallback to empty if unknown

#     # Environment-specific note
#     env_note = ""
#     match environment.lower():
#         case "django":
#             env_note = "This is a Django backend project. Look for models, views, URLs, and app configuration.\n"
#         case "flask":
#             env_note = "This is a Flask backend project. Focus on routes, decorators, and app factory structure.\n"
#         case "react":
#             env_note = "This is a React frontend project. Explain components, props, hooks, and JSX structure.\n"
#         case "node":
#             env_note = "This is a Node.js project (likely using Express). Explain API routes, middleware, and logic.\n"
#         case "spring":
#             env_note = "This is a Java Spring Boot project. Explain services, controllers, and configurations.\n"
#         case _:
#             env_note = ""  # Generic fallback

#     # Prompt instructions
#     instructions = (
#         f"{env_note}"
#         "Summarize the following code clearly for a developer audience:\n"
#         "- Explain the main purpose of the file\n"
#         "- Describe functions, classes, and key logic\n"
#         "- Use simple but technical language\n"
#         "- Keep the summary concise and readable"
#     )

#     # Add file context if available
#     context = f"File: {file_path}\n\n" if file_path else ""

#     # Format code with correct markdown tag
#     code_block = f"```{code_lang_tag}\n{code_chunk.strip()}\n```"

#     return f"{header}\n\n{instructions}\n\n{context}{code_block}"




# core/prompt_builder.py
import os
from .lang_detector import detect_language_from_extension

def _environment_hint(env: str) -> str:
    if env == "django":
        return "Django backend (models, views, urls, settings)."
    if env == "flask":
        return "Flask app (routes, blueprints, app factory)."
    if env == "react":
        return "React frontend (components, hooks, props/state)."
    if env == "node":
        return "Node/Express backend (routes, middleware, controllers)."
    return "Generic project."

def build_prompt(
    code_chunk: str,
    file_path: str | None = None,
    environment: str = "generic",
    repo_context: dict | None = None,
) -> str:
    """
    Builds a prompt for high-accuracy code summarization.
    Notes beside function:
    - Uses detect_language_from_extension() from core.lang_detector.
    - Called by core.summarizer.summarize_code().
    """
    # Language hint from filename
    lang = detect_language_from_extension(file_path or "") or "plaintext"

    # Repo-level context (safe to be empty)
    rc = repo_context or {}
    deps = rc.get("dependencies") or {}
    env_vars = rc.get("env_vars") or {}
    usage = (rc.get("usage") or "").strip()
    project_name = rc.get("project_name") or "Codebase"

    env_hint = _environment_hint(environment)

    # Shorten deps/env_vars in the prompt (prevent bloat)
    dep_lines = []
    for k, v in deps.items():
        if not v: 
            continue
        sample = ", ".join(v[:6])
        more = " …" if len(v) > 6 else ""
        dep_lines.append(f"- {k}: {sample}{more}")
    deps_block = "\n".join(dep_lines) if dep_lines else "None detected."

    env_lines = []
    for k, v in list(env_vars.items())[:10]:
        env_lines.append(f"- {k}: {v or '(no description)'}")
    env_block = "\n".join(env_lines) if env_lines else "None detected."

    usage_block = usage if usage else "Not inferred."

    header = (
        "You are a senior software engineer producing accurate, concise documentation for code.\n"
        "Follow the rules strictly:\n"
        "1) Be correct over confident. If unsure, say 'uncertain'.\n"
        "2) Include purpose, key functions/classes, inputs/outputs, side-effects.\n"
        "3) Mention important dependencies or framework patterns if relevant.\n"
        "4) Avoid restating code; summarize behavior and intent.\n"
        "5) Keep it readable for engineers (bullet points welcome).\n"
    )

    repo_context_block = (
        f"Project: {project_name}\n"
        f"Detected environment: {environment} ({env_hint})\n"
        f"Top dependencies:\n{deps_block}\n"
        f"Environment variables (if any):\n{env_block}\n"
        f"How to run (inferred):\n{usage_block}\n"
    )

    file_note = f"File Path: {file_path or '(unknown)'}\nLanguage: {lang}\n"

    instructions = (
        "Summarize the following code chunk in the above project context.\n"
        "Output a clear, technical explanation suitable for a README 'Code File Summaries' section."
    )

    fenced = f"```{lang}\n{code_chunk}\n```"

    return f"{header}\n{repo_context_block}\n{file_note}\n{instructions}\n\n{fenced}\n"
