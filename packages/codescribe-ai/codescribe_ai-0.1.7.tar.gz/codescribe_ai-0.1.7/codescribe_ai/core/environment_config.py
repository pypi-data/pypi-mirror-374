# core/environment_config.py

import os
import json

def detect_environment(project_path: str) -> str:
    """
    Detects the environment/framework of a codebase by scanning key files.
    Returns one of ['django', 'flask', 'react', 'node', 'java', 'go', 'python', 'generic'].
    """

    # Normalize file list
    found_files = []
    for root, _, files in os.walk(project_path):
        for file in files:
            found_files.append(file.lower())

    # --- Priority checks ---
    # Django
    if "manage.py" in found_files or "settings.py" in found_files:
        return "django"

    # Flask
    if "app.py" in found_files or "wsgi.py" in found_files:
        with open(os.path.join(project_path, "requirements.txt"), "r", encoding="utf-8", errors="ignore") as f:
            reqs = f.read().lower()
        if "flask" in reqs:
            return "flask"

    # React
    if "package.json" in found_files:
        try:
            pkg_path = os.path.join(project_path, "package.json")
            with open(pkg_path, "r", encoding="utf-8", errors="ignore") as f:
                pkg = json.load(f)
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if any("react" in dep for dep in deps.keys()):
                return "react"
        except Exception:
            pass

    # Node.js (generic backend, not React)
    if "package.json" in found_files:
        return "node"

    # Java (look for Maven/Gradle)
    if "pom.xml" in found_files or "build.gradle" in found_files:
        return "java"

    # Go
    if "go.mod" in found_files or any(f.endswith(".go") for f in found_files):
        return "go"

    # Python (fallback if .py files exist and no higher-priority env matched)
    if any(f.endswith(".py") for f in found_files):
        return "python"

    # Default
    return "generic"
