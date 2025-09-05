"""Git worktree management functionality."""

import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

def create_worktree(ticket_id: str, branch_name: str, base_dir: Path) -> Path:
    """Create a git worktree for ticket implementation."""
    from .utils import get_git_info
    
    # Get current repository info
    git_info = get_git_info()
    if not git_info['is_git_repo']:
        raise ValueError("Not in a git repository")
    
    repo_name = git_info['repo_root'].name
    worktree_path = base_dir / repo_name / ticket_id
    
    # Create base directory
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create worktree
    cmd = ["git", "worktree", "add", str(worktree_path), "-b", branch_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Git worktree creation failed: {result.stderr}")
    
    return worktree_path


def list_worktrees() -> List[Dict[str, Any]]:
    """List existing git worktrees."""
    cmd = ["git", "worktree", "list", "--porcelain"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to list worktrees: {result.stderr}")
    
    worktrees = []
    current_worktree = {}
    
    for line in result.stdout.strip().split('\n'):
        if not line:
            if current_worktree:
                worktrees.append(current_worktree)
                current_worktree = {}
            continue
            
        if line.startswith('worktree '):
            current_worktree['path'] = line[9:]  # Remove 'worktree ' prefix
        elif line.startswith('HEAD '):
            current_worktree['commit'] = line[5:]  # Remove 'HEAD ' prefix
        elif line.startswith('branch '):
            current_worktree['branch'] = line[7:]  # Remove 'branch ' prefix
        elif line == 'bare':
            current_worktree['bare'] = True
        elif line == 'detached':
            current_worktree['detached'] = True
    
    # Add the last worktree if it exists
    if current_worktree:
        worktrees.append(current_worktree)
    
    return worktrees


def remove_worktree(worktree_path: Path, force: bool = False) -> None:
    """Remove a git worktree."""
    cmd = ["git", "worktree", "remove", str(worktree_path)]
    if force:
        cmd.append("--force")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to remove worktree: {result.stderr}")


def get_worktree_status(worktree_path: Path) -> Dict[str, Any]:
    """Get status information for a specific worktree."""
    if not worktree_path.exists():
        return {"exists": False}
    
    # Change to worktree directory and get git status
    cmd = ["git", "-C", str(worktree_path), "status", "--porcelain"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return {
            "exists": True,
            "valid": False,
            "error": result.stderr
        }
    
    # Count changes
    lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
    
    # Get current branch
    branch_cmd = ["git", "-C", str(worktree_path), "branch", "--show-current"]
    branch_result = subprocess.run(branch_cmd, capture_output=True, text=True)
    current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
    
    return {
        "exists": True,
        "valid": True,
        "path": str(worktree_path),
        "branch": current_branch,
        "changes": len(lines) if lines != [''] else 0,
        "is_clean": len(lines) == 0 or lines == ['']
    }


def find_worktrees_for_repo(repo_name: str, base_dir: Path) -> List[Path]:
    """Find all worktrees for a specific repository in the base directory."""
    repo_dir = base_dir / repo_name
    if not repo_dir.exists():
        return []
    
    worktrees = []
    for item in repo_dir.iterdir():
        if item.is_dir():
            # Check if this looks like a worktree (has .git file pointing to main repo)
            git_file = item / '.git'
            if git_file.exists():
                worktrees.append(item)
    
    return worktrees