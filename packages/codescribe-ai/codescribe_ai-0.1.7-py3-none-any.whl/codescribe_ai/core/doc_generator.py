# core/doc_generator.py
from jinja2 import Environment, FileSystemLoader
import os

def generate_section(file_path, summary):  # Formats a file-level summary block in markdown
    """
    Formats a markdown section for a single file's summary.

    Args:
        file_path (str): The file name or relative path.
        summary (str): The text summary from the LLM.

    Returns:
        str: A markdown-formatted section block.
    """
    return f"### `{file_path}`\n\n{summary.strip()}\n\n---\n"


from core.env_var_descriptions import ENV_VAR_DESCRIPTIONS

def generate_readme(
    summary_dict,
    dependencies,
    env_vars,
    usage,
    environment,
    project_name="Codebase",
    overview="This project was auto-documented by CodeScribe AI.",
    purpose="This project is designed to perform its core functionality.",
    system_deps=None,
):
    """
    Generate README content using Jinja2 templates.
    """
    from jinja2 import Environment, FileSystemLoader
    import os

    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("readme_template.md")

    rendered = template.render(
        project_name=project_name,
        overview=overview or "This project is auto-documented by CodeScribe AI.",
        purpose=purpose or "perform its main functionality as intended.",
        dependencies=dependencies or {},
        env_vars=env_vars or {},
        usage=usage or "",
        summary_dict=summary_dict or {},
        environment=environment or "generic",
        system_deps=system_deps or []  # 🔥 New param
    )

    return rendered

