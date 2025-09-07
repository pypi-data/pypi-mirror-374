# core/repo_context.py
import os
from .environment_config import detect_environment
from .dependency_parser import extract_all_dependencies
from .env_var_parser import extract_env_variables
from .usage_instruction_builder import generate_usage_instruction

def build_repo_context(src_dir: str) -> dict:
    """
    Aggregates repository-level signals to improve summarization accuracy.

    Returns keys:
      - environment (str)
      - dependencies (dict[str, list[str]])
      - env_vars (dict[str, str])
      - usage (str)
      - project_name (str)
      - has_tests (bool)
      - has_docker (bool)
      - readme_present (bool)
    """
    environment = detect_environment(src_dir)
    dependencies = extract_all_dependencies(src_dir) or {}
    env_vars = extract_env_variables(src_dir) or {}
    usage = generate_usage_instruction(src_dir, environment=environment) or ""
    project_name = os.path.basename(os.path.abspath(src_dir)) or "Codebase"

    # lightweight extra signals
    has_tests = any(d.lower() == "tests" for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d)))
    has_docker = any(x in os.listdir(src_dir) for x in ["Dockerfile", "docker-compose.yml"])
    readme_present = any(x.lower() == "readme.md" for x in os.listdir(src_dir))

    return {
        "environment": environment,
        "dependencies": dependencies,
        "env_vars": env_vars,
        "usage": usage,
        "project_name": project_name,
        "has_tests": has_tests,
        "has_docker": has_docker,
        "readme_present": readme_present,
    }
