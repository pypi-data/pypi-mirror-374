# import argparse
# import os
# import tempfile
# import shutil
# from codescribe_ai.scripts.run_pipeline import run_codescribe_pipeline
# from codescribe_ai.core.repo_downloader import download_and_extract_repo

# def main():
#     parser = argparse.ArgumentParser(description="AI-powered README generator")
#     parser.add_argument(
#         "source",
#         help="Path to local project folder or GitHub repo URL"
#     )
#     parser.add_argument(
#         "-o", "--output",
#         default="README.md",
#         help="Output README file path"
#     )
#     args = parser.parse_args()

#     # Check if source is GitHub URL
#     if args.source.startswith("http://") or args.source.startswith("https://"):
#         with tempfile.TemporaryDirectory() as tmpdir:
#             print(f"Downloading repository {args.source}...")
#             repo_path = download_and_extract_repo(args.source, tmpdir)
#             run_codescribe_pipeline(repo_path, args.output)
#     else:
#         # Local folder
#         src_path = os.path.abspath(args.source)
#         if not os.path.exists(src_path):
#             print(f"❌ Path does not exist: {src_path}")
#             return
#         run_codescribe_pipeline(src_path, args.output)

#     print(f"✅ README generated at: {args.output}")

# if __name__ == "__main__":
#     main()





import argparse
import os
import tempfile
import requests
import shutil
import zipfile
from codescribe_ai.scripts.run_pipeline import run_codescribe_pipeline
from codescribe_ai.core.repo_downloader import download_and_extract_repo

# 👇 Change this to your deployed Flask API base URL
FALLBACK_API = os.environ.get("CODESCRIBE_API_URL", "https://codescribe-ai.onrender.com")


def run_with_fallback(source, output):
    """
    Try local pipeline with GROQ_API_KEY.
    If not available, fallback to Flask API.
    """
    groq_key = os.getenv("GROQ_API_KEY")

    if groq_key:
        # ✅ Local mode with API key
        if source.startswith("http://") or source.startswith("https://"):
            with tempfile.TemporaryDirectory() as tmpdir:
                print(f"Downloading repository {source}...")
                repo_path = download_and_extract_repo(source, tmpdir)
                run_codescribe_pipeline(repo_path, output)
        else:
            src_path = os.path.abspath(source)
            if not os.path.exists(src_path):
                print(f"❌ Path does not exist: {src_path}")
                return
            run_codescribe_pipeline(src_path, output)

    else:
        # 🌍 Remote mode → use Flask API
        print("⚠️ No GROQ_API_KEY found. Falling back to remote API...")

        if source.startswith("http://") or source.startswith("https://"):
            # GitHub URL mode
            payload = {"github_url": source}
            resp = requests.post(f"{FALLBACK_API}/api/generate", json=payload)
        else:
            # Local folder → zip & upload
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, "project.zip")
                shutil.make_archive(zip_path.replace(".zip", ""), 'zip', source)
                with open(zip_path, "rb") as f:
                    files = {"code_zip": f}
                    resp = requests.post(f"{FALLBACK_API}/api/generate", files=files)

        if resp.status_code == 200:
            with open(output, "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"✅ README generated via remote API at: {output}")
        else:
            print(f"❌ Remote API failed: {resp.status_code} - {resp.text}")


def main():
    parser = argparse.ArgumentParser(description="AI-powered README generator")
    parser.add_argument(
        "source",
        help="Path to local project folder or GitHub repo URL"
    )
    parser.add_argument(
        "-o", "--output",
        default="README.md",
        help="Output README file path"
    )
    args = parser.parse_args()

    run_with_fallback(args.source, args.output)


if __name__ == "__main__":
    main()