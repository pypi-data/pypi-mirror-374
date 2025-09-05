"""Public API endpoints that don't require authentication."""

from typing import List, Optional
from fastapi import APIRouter, Query

from ..services.filesystem_thoughts import get_filesystem_thoughts

router = APIRouter()


@router.get("/thoughts/local")
async def list_local_thoughts(
    search: Optional[str] = Query(None, description="Search in title and content"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    repository: Optional[str] = Query(None, description="Filter by repository"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of thoughts to return"),
):
    """List thoughts directly from local filesystem (no authentication required)."""
    
    thoughts = get_filesystem_thoughts(
        search=search,
        tags=tags,
        repository=repository,
        limit=limit
    )
    
    from pathlib import Path
    current_dir = Path.cwd()
    
    # Use the same path detection logic as get_filesystem_thoughts
    if current_dir.name == "backend":
        parent_dir = current_dir.parent
    elif current_dir.name == "src":  # Docker: running from /app/backend/src
        # In Docker, check if thoughts are mounted at /app/thoughts
        docker_thoughts = Path("/app/thoughts")
        if docker_thoughts.exists():
            parent_dir = Path("/app")
        else:
            # Fallback to going up two levels: /app/backend/src -> /app
            parent_dir = current_dir.parent.parent
    else:
        parent_dir = current_dir
    
    return {
        "thoughts": thoughts,
        "total": len(thoughts),
        "source": "local-filesystem",
        "repositories_found": list(set(t.get("repository", "unknown") for t in thoughts)),
        "debug_info": {
            "current_working_directory": str(current_dir),
            "search_directory": str(parent_dir),
            "thoughts_directory_exists": (parent_dir / "thoughts").exists(),
            "thoughts_directory_contents": list(str(p) for p in (parent_dir / "thoughts").iterdir()) if (parent_dir / "thoughts").exists() else [],
            "hot_reload_test": "working_after_restart"
        }
    }