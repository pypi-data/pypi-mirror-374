import os
import re
import sys
import importlib.util

# 🔧 Map of keywords → installation instructions
SYSTEM_DEP_MAP = {
    "ollama": "Install Ollama from https://ollama.ai (required for running local LLMs).",
    "tesseract": "Install Tesseract OCR (e.g., `sudo apt-get install tesseract-ocr`).",
    "poppler": "Install Poppler (e.g., `sudo apt-get install poppler-utils`).",
    "cuda": "Install NVIDIA CUDA Toolkit (required for GPU acceleration).",
    "torch": "PyTorch may require GPU drivers. See https://pytorch.org/get-started/locally/",
    "tensorflow": "TensorFlow may require GPU/CUDA support. See https://www.tensorflow.org/install",
    "docker": "Install Docker to build and run containerized apps.",
    "postgres": "Install PostgreSQL (e.g., `sudo apt-get install postgresql`).",
    "redis": "Install Redis (e.g., `sudo apt-get install redis`).",
    "java": "Install Java JDK (required for JVM-based projects like Spring/Gradle).",
    "maven": "Install Apache Maven (Java dependency manager).",
    "gradle": "Install Gradle (Java build tool).",
    "go": "Install Go (https://golang.org/doc/install).",
    "rust": "Install Rust via rustup (https://www.rust-lang.org/tools/install).",
    "node": "Install Node.js and npm (https://nodejs.org/).",
    "yarn": "Install Yarn (JavaScript dependency manager).",
}


def is_stdlib(module: str) -> bool:
    """Check if a module is from the Python standard library."""
    if module in sys.builtin_module_names:
        return True
    spec = importlib.util.find_spec(module)
    if spec is None:
        return False
    return "site-packages" not in (spec.origin or "")


def extract_all_dependencies(project_path):
    """
    Detects dependencies for Python, Node, and common system dependencies.
    Returns a dict of {language: [dependencies]}.
    """
    dependencies = {"python": [], "node": [], "system": []}

    # --- Python deps from requirements.txt ---
    req_file = os.path.join(project_path, "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file, "r", encoding="utf-8") as f:
            dependencies["python"].extend(
                [line.strip() for line in f if line.strip() and not line.startswith("#")]
            )

    # --- Node deps from package.json ---
    package_json = os.path.join(project_path, "package.json")
    if os.path.exists(package_json):
        try:
            import json

            with open(package_json, "r", encoding="utf-8") as f:
                pkg = json.load(f)
            node_deps = list(pkg.get("dependencies", {}).keys()) + list(pkg.get("devDependencies", {}).keys())
            dependencies["node"].extend(node_deps)
        except Exception:
            pass

    # --- Scan source files for Python imports + system keywords ---
    py_imports = set()
    for root, _, files in os.walk(project_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Python imports
            if file.endswith(".py"):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            match = re.match(r"^\s*(?:from|import)\s+([a-zA-Z0-9_\.]+)", line)
                            if match:
                                module = match.group(1).split(".")[0]  # top-level package
                                if not is_stdlib(module):
                                    py_imports.add(module)
                except Exception:
                    continue

            # System deps
            if file.endswith((".py", ".js", ".ts", ".java", ".go", ".rs", ".md", "Dockerfile", "Makefile")):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        for keyword, instruction in SYSTEM_DEP_MAP.items():
                            if keyword in content and instruction not in dependencies["system"]:
                                dependencies["system"].append(instruction)
                except Exception:
                    continue

    # Add discovered Python imports
    dependencies["python"].extend(sorted(py_imports))

    # Remove duplicates
    dependencies = {lang: sorted(set(deps)) for lang, deps in dependencies.items()}

    return dependencies
