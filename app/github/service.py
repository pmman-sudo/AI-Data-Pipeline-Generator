import os
from git import Repo, InvalidGitRepositoryError

def commit_and_push(task_description: str) -> str:
    try:
        repo = Repo(".")

        repo.git.add("generated/")

        if not repo.is_dirty(untracked_files=True):
            return "No changes"

        commit = repo.index.commit(
            f"Generate artifact via AI - task: {task_description}"
        )

        try:
            repo.remote("origin").push()
            return commit.hexsha[:7]
        except Exception:
            # Commit exists locally even if push fails
            return f"{commit.hexsha[:7]} (local)"

    except InvalidGitRepositoryError:
        return "Render deployment"