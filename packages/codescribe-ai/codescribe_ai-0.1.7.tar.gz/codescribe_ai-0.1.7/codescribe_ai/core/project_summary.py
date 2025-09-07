# core/project_summary.py

import os
from core.summarizer import summarize_code

def generate_project_overview(src_dir, environment="generic"):
    """
    Generate a high-level project overview and purpose statement.
    Uses file structure + main file context + summarizer.
    """
    files = []
    for root, _, filenames in os.walk(src_dir):
        for f in filenames:
            if f.endswith((".py", ".js", ".ts", ".java", ".go", ".rb")):
                files.append(os.path.relpath(os.path.join(root, f), src_dir))

    # Build context from file list
    context = f"This project contains the following source files:\n" + "\n".join(files[:20])  # limit 20 files
    if len(files) > 20:
        context += f"\n(and {len(files)-20} more files...)"

    # Try to read entrypoint files
    main_candidates = ["main.py", "app.py", "index.js", "server.js"]
    for candidate in main_candidates:
        candidate_path = os.path.join(src_dir, candidate)
        if os.path.exists(candidate_path):
            try:
                with open(candidate_path, "r", encoding="utf-8") as f:
                    code_sample = f.read()[:2000]  # only first 2k chars
                context += f"\n\nSample from {candidate}:\n{code_sample}"
                break
            except Exception:
                continue

    # Ask LLM for overview
    overview_prompt = (
        "You are analyzing a software project. Based on the following file list and sample code, "
        "generate a clear and informative project overview (2-4 sentences):\n\n"
        f"{context}"
    )
    overview = summarize_code(overview_prompt, file_path="PROJECT_OVERVIEW", environment=environment)

    # Ask LLM for purpose
    purpose_prompt = (
        "Summarize the main purpose of this project in one concise sentence, "
        "as if writing the 'What this project does' section of a README.\n\n"
        f"{context}"
    )
    purpose = summarize_code(purpose_prompt, file_path="PROJECT_PURPOSE", environment=environment)

    return {"overview": overview.strip(), "purpose": purpose.strip()}
