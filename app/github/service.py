import os
from git import Repo

def commit_and_push(task_description: str) -> str:
    """Stages generated files, commits, and pushes to GitHub."""
    
    # Ensure token exists in environment
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is missing from .env")
        
    repo = Repo(".")
    
    # Stage all files in the generated/ directory
    repo.git.add("generated/")
    
    # Check if there are actually changes to commit
    if repo.is_dirty(untracked_files=True):
        # Commit with a descriptive message
        commit_message = f"Generate artifact via AI - task: {task_description}"
        commit = repo.index.commit(commit_message)
        
        # Push to the current branch (assumes local git is authenticated)
        origin = repo.remote(name="origin")
        origin.push()
        
        # Return the short commit hash
        return commit.hexsha[:7]
        
    return "pending"