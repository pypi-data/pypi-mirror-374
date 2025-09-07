# import os
# import json

# def detect_python_entry(project_path):
#     for name in ["app.py", "main.py"]:
#         if os.path.exists(os.path.join(project_path, name)):
#             return f"python {name}"
    
#     for root, _, files in os.walk(project_path):
#         for file in files:
#             if file == "manage.py":
#                 return "python manage.py runserver"
#             if file == "wsgi.py":
#                 return "gunicorn app:app"

#     return None

# def detect_node_entry(project_path):
#     package_path = os.path.join(project_path, "package.json")
#     if not os.path.exists(package_path):
#         return None

#     try:
#         with open(package_path, "r", encoding="utf-8") as f:
#             data = json.load(f)

#         if "scripts" in data:
#             if "start" in data["scripts"]:
#                 return "npm start"
#             elif "dev" in data["scripts"]:
#                 return "npm run dev"

#         # fallback: look for server.js or app.js
#         for entry in ["server.js", "app.js"]:
#             if os.path.exists(os.path.join(project_path, entry)):
#                 return f"node {entry}"

#     except Exception:
#         return None

#     return None

# def generate_usage_instruction(project_path, environment="generic"):
#     """
#     Returns a suggested way to run the project (CLI).

#     Args:
#         project_path (str): Path to project
#         environment (str): Detected environment (django, flask, react, etc.)

#     Returns:
#         str: A usage command or instructions
#     """
#     if environment in ["flask", "django"]:
#         cmd = detect_python_entry(project_path)
#         if cmd:
#             return cmd

#     if environment in ["node", "react"]:
#         cmd = detect_node_entry(project_path)
#         if cmd:
#             return cmd

#     # Try both methods as fallback
#     return detect_python_entry(project_path) or detect_node_entry(project_path) or "Check documentation or main file."








# core/usage_instruction_builder.py
import os

def generate_usage_instruction(project_path: str, environment: str = "generic") -> str:
    """
    Generates installation + run instructions depending on detected environment.
    Falls back to generic instructions if environment not recognized.
    """

    instructions = []

    # --- Clone step ---
    project_name = os.path.basename(os.path.abspath(project_path))
    instructions.append("## Clone the repository")
    instructions.append(f"git clone <your-repo-url>")
    instructions.append(f"cd {project_name}\n")

    # --- Install + Run per environment ---
    if environment == "django":
        instructions.append("## Install dependencies")
        instructions.append("pip install -r requirements.txt\n")
        instructions.append("## Run migrations & start server")
        instructions.append("python manage.py migrate")
        instructions.append("python manage.py runserver")

    elif environment == "flask":
        instructions.append("## Install dependencies")
        instructions.append("pip install -r requirements.txt\n")
        instructions.append("## Run the Flask app")
        instructions.append("export FLASK_APP=app.py  # or set FLASK_APP=app.py on Windows")
        instructions.append("flask run")

    elif environment == "react":
        instructions.append("## Install dependencies")
        instructions.append("npm install\n")
        instructions.append("## Start the development server")
        instructions.append("npm start")

    elif environment == "node":
        instructions.append("## Install dependencies")
        instructions.append("npm install\n")
        instructions.append("## Run the server")
        if os.path.exists(os.path.join(project_path, "server.js")):
            instructions.append("node server.js")
        elif os.path.exists(os.path.join(project_path, "app.js")):
            instructions.append("node app.js")
        else:
            instructions.append("npm run start")

    elif environment == "java":
        instructions.append("## Build with Maven/Gradle")
        if os.path.exists(os.path.join(project_path, "pom.xml")):
            instructions.append("mvn clean install")
        elif os.path.exists(os.path.join(project_path, "build.gradle")):
            instructions.append("gradle build")
        instructions.append("## Run the app")
        instructions.append("java -jar target/<your-app>.jar")

    elif environment == "go":
        instructions.append("## Install dependencies")
        instructions.append("go mod tidy\n")
        instructions.append("## Run the app")
        instructions.append("go run main.go")

    elif environment == "python":
        instructions.append("## Install dependencies")
        instructions.append("pip install -r requirements.txt\n")
        instructions.append("## Run the app")
        instructions.append("python main.py")

    else:  # generic fallback
        instructions.append("#### (Update this section based on your project setup)")
        instructions.append("## Example: install dependencies")
        instructions.append("pip install -r requirements.txt")
        instructions.append("## Example: run the project")
        instructions.append("python main.py")

    return "\n".join(instructions)
