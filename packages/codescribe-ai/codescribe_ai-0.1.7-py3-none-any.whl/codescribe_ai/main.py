
import sys, os

# Make sure the *project root* is first on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# After sys.path fix, import and print the module paths
import requests, os, pathlib
from codescribe_ai.scripts.run_pipeline import run_codescribe_pipeline
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import os, zipfile, uuid, shutil
from git import Repo
from markdown import markdown
import pathlib
from dotenv import load_dotenv
from codescribe_ai.core.summarizer import summarize_code





try:
    import codescribe_ai.core.summarizer as sm
    print("🔎 Using summarizer at:", sm.__file__)
except Exception as e:
    print("⚠️ Could not import codescribe_ai.core.summarizer:", repr(e))
    # fallback: legacy import path if you had bare 'core'
    try:
        import core.summarizer as sm2
        print("🔎 Using summarizer (legacy) at:", sm2.__file__)
    except Exception as e2:
        print("❌ Could not import legacy core.summarizer:", repr(e2))



app = Flask(__name__)

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
UPLOADS = os.path.join(BASE_DIR, "uploads")
OUTPUTS = os.environ.get("OUTPUT_DIR", os.path.join(BASE_DIR, "generated"))

dotenv_path = BASE_DIR / ".env"
print("Loading .env from:", dotenv_path)
load_dotenv(dotenv_path)  # Load environment variables from .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")
else:
    print("GROQ_API_KEY loaded successfully.")

Key=os.getenv("GROQ_API_KEY")
resp=requests.get("https://api.groq.com/v1/chat/completions", 
                  headers={"Authorization": f"Bearer {Key}", "Content-Type":"application/json"},
                  json= {"model":"llama3-8b-8192", "messages":[{"role":"user","content":"ping"}]})
print("GROQ API response status:", resp.status_code)

# 🔹 Configurable base directories

UPLOADS = os.path.join(BASE_DIR, "uploads")
OUTPUTS = os.environ.get("OUTPUT_DIR", os.path.join(BASE_DIR, "generated"))

# Ensure folders exist
os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(OUTPUTS, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        project_id = str(uuid.uuid4())
        extract_path = os.path.join(UPLOADS, project_id)

        zip_file = request.files.get("code_zip")
        github_url = request.form.get("github_url")
        output_ext = request.form.get("format", "md")
        model_choice = request.form.get("model", None)
        output_file = os.path.join(OUTPUTS, f"{project_id}_README.{output_ext}")

        # Handle ZIP upload
        if zip_file and zip_file.filename.endswith(".zip"):
            zip_path = os.path.join(UPLOADS, f"{project_id}.zip")
            zip_file.save(zip_path)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)

        # Handle GitHub repo
        elif github_url:
            try:
                Repo.clone_from(github_url.strip(), extract_path)
            except Exception as e:
                return f"❌ GitHub error: {e}"

        else:
            return "❌ Provide a ZIP or GitHub URL."

        # Run Codescribe pipeline
        run_codescribe_pipeline(extract_path, output_file,model=model_choice)

        # Cleanup
        shutil.rmtree(extract_path, ignore_errors=True)

        return redirect(url_for("preview", filename=os.path.basename(output_file)))

    return render_template("index.html")

@app.route("/preview/<filename>")
def preview(filename):
    filepath = os.path.join(OUTPUTS, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        html = markdown(f.read(), extensions=["fenced_code", "tables"])
    return render_template(
        "preview.html",
        html_content=html,
        download_link=url_for("download", filename=filename),
    )

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(OUTPUTS, filename), as_attachment=True)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    API endpoint for CLI fallback.
    Accepts:
      - JSON: {"github_url": "..."}
      - Form-data: file upload (zip)
    Returns:
      - README content (plain text)
    """
    project_id = str(uuid.uuid4())
    extract_path = os.path.join(UPLOADS, project_id)
    os.makedirs(extract_path, exist_ok=True)

    output_file = os.path.join(OUTPUTS, f"{project_id}_README.md")

    # Case 1: GitHub URL (JSON)
    if request.is_json and request.json.get("github_url"):
        github_url = request.json["github_url"].strip()
        try:
            Repo.clone_from(github_url, extract_path)
        except Exception as e:
            return jsonify({"error": f"❌ GitHub clone failed: {e}"}), 400

    # Case 2: ZIP upload (form-data)
    elif "code_zip" in request.files:
        zip_file = request.files["code_zip"]
        if not zip_file.filename.endswith(".zip"):
            return jsonify({"error": "❌ Uploaded file must be a .zip"}), 400
        zip_path = os.path.join(UPLOADS, f"{project_id}.zip")
        zip_file.save(zip_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

    else:
        return jsonify({"error": "❌ Provide either github_url (JSON) or code_zip (form-data)"}), 400

    # Run Codescribe pipeline
    try:
        run_codescribe_pipeline(extract_path, output_file)
        with open(output_file, "r", encoding="utf-8") as f:
            readme_content = f.read()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        shutil.rmtree(extract_path, ignore_errors=True)

    return readme_content, 200, {"Content-Type": "text/plain; charset=utf-8"}


if __name__ == "__main__":
    app.run(debug=True)
