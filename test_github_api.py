from app.github.api import get_repo, encode_file
from app.github.api import get_file_sha
from app.github.api import commit_generated_artifact

sha = commit_generated_artifact(
    artifact_path="README.md",
    commit_message="Testing GitHub API"
)

print(sha)

print(get_repo()["full_name"])
print(len(encode_file("README.md")))
print(get_file_sha("README.md"))