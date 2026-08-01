import os
import requests
from dotenv import load_dotenv
import base64
from pathlib import Path

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

OWNER = "pmman-sudo"
REPO = "AI-Data-Pipeline-Generator"
BRANCH = "master"

BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"


def github_headers():
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN not configured.")

    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def get_repo():
    response = requests.get(
        BASE_URL,
        headers=github_headers(),
        timeout=30,
    ) 
    
    response.raise_for_status()

    return response.json()

def encode_file(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8") 

def get_file_sha(path: str):
    """
    Returns the SHA of a file if it already exists in GitHub.
    Returns None if the file doesn't exist.
    """

    url = f"{BASE_URL}/contents/{path}"

    response = requests.get(
        url,
        headers=github_headers(),
        timeout=30,
        params={"ref": BRANCH},
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.json()["sha"]    

def commit_generated_artifact(artifact_path: str, commit_message: str) -> str:
    """
    Uploads a generated artifact to GitHub using the Contents API.
    Returns the short commit SHA.
    """

    path = Path(artifact_path)

    try:
        # Running on Render
        github_path = path.relative_to("/opt/render/project/src").as_posix()
    except ValueError:
        # Running locally
        github_path = path.as_posix()

    # Ensure GitHub receives a repository-relative path
    github_path = Path(github_path).as_posix()

    if "generated/" in github_path:
        github_path = "generated/" + github_path.split("generated/", 1)[1]

    url = f"{BASE_URL}/contents/{github_path}"

    payload = {
        "message": commit_message,
        "content": encode_file(artifact_path),
        "branch": BRANCH,
    }

    existing_sha = get_file_sha(github_path)

    if existing_sha:
        payload["sha"] = existing_sha
    
    print(f"Uploading to GitHub path: {github_path}")

    response = requests.put(
        url,
        headers=github_headers(),
        json=payload,
        timeout=60,
    )

    if not response.ok:
        print("GitHub response:", response.text)
        response.raise_for_status()

    data = response.json()

    return data["commit"]["sha"][:7]        