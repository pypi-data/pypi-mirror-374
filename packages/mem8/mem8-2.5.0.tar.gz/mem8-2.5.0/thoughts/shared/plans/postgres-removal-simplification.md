---
date: 2025-09-02T18:24:19-05:00
author: killerapp
status: proposed
priority: high
complexity: medium
estimated_effort: 1-2 days
tags: [refactoring, simplification, architecture, postgres, docker, cli]
---

# Plan: Remove PostgreSQL/Docker Dependencies and Simplify to Local CLI

## Objective
Transform mem8 from a complex PostgreSQL/Docker-based system to a streamlined local CLI tool focused on managing Claude Code customizations via cookiecutter templates.

## Key Findings from Research
- **Thoughts are shared via Windows file junctions** at `C:\Users\vaski\mem8-shared`, NOT through PostgreSQL
- **PostgreSQL is only used for** web UI, team collaboration, and advanced search indexing
- **Core CLI functionality works without database** - all essential features are file-based
- **Docker/PostgreSQL adds ~50+ files** of unnecessary complexity for local use case

## Implementation Steps

### Phase 1: Backup and Verification (30 min)
1. Create full backup of current mem8 repository
2. Test core commands work without backend:
   ```bash
   mem8 status
   mem8 sync
   mem8 search "test"
   mem8 init --dry-run
   ```
3. Document current functionality for rollback reference

### Phase 2: Remove Database/Docker Infrastructure (1 hour)
1. **Delete directories:**
   ```
   rm -rf backend/
   rm -rf frontend/
   rm -rf scripts/deploy.sh
   rm -rf scripts/dev-setup.sh
   ```

2. **Delete Docker files:**
   ```
   rm docker-compose.yml
   rm docker-compose.dev.yml
   rm Makefile  # Contains Docker commands
   rm DOCKER.md
   ```

3. **Delete database-related files:**
   ```
   rm load_thoughts.py  # Database loader
   rm hack/run_postgres.sh
   ```

### Phase 3: Clean Dependencies (30 min)
1. **Update root pyproject.toml** - Remove:
   - sqlalchemy
   - psycopg2-binary
   - fastapi
   - uvicorn
   - pydantic
   - httpx
   - websockets
   - redis
   - alembic

2. **Keep essential dependencies:**
   - typer
   - rich
   - cookiecutter
   - gitpython
   - pyyaml
   - pathlib
   - importlib-resources

3. **Regenerate lock file:**
   ```bash
   uv lock
   uv sync
   ```

### Phase 4: Remove Team Mode from CLI (1 hour)
1. **Edit mem8/cli_typer.py:**
   - Remove team_app (lines 1079-1121)
   - Remove deploy_app if present
   - Remove WebSocket sync references
   - Remove API client imports

2. **Clean configuration:**
   - Remove team-related config from `mem8/core/config.py`
   - Remove API URL configurations
   - Keep file-based shared directory settings

3. **Update help text:**
   - Remove references to team features
   - Update command descriptions to focus on local usage

### Phase 5: Simplify Project Structure (30 min)
1. **Move files to root where appropriate:**
   ```
   mem8/
   ├── __init__.py
   ├── cli.py
   ├── cli_typer.py
   ├── core/
   │   ├── config.py
   │   ├── memory.py
   │   ├── sync.py
   │   ├── utils.py
   │   ├── smart_setup.py
   │   ├── thought_entity.py
   │   ├── thought_actions.py
   │   └── thought_discovery.py
   ├── templates/
   │   ├── claude-dot-md-template/
   │   └── shared-thoughts-template/
   └── legacy/  # Keep for now, review later
   ```

2. **Clean example configs:**
   - Remove team collaboration examples
   - Keep local-only examples

### Phase 6: Add Optional SQLite for Local Search (2 hours)
1. **Create mem8/core/local_db.py:**
   ```python
   import sqlite3
   from pathlib import Path
   
   class LocalSearchIndex:
       def __init__(self, db_path: Path = None):
           self.db_path = db_path or Path.home() / ".mem8" / "search.db"
           self.init_db()
       
       def init_db(self):
           # Create thoughts table with FTS5
           pass
       
       def index_thought(self, path: Path, content: str):
           # Add to search index
           pass
       
       def search(self, query: str):
           # Full-text search
           pass
   ```

2. **Make it optional:**
   - Default to ripgrep-based search
   - Use SQLite only if explicitly enabled
   - No additional dependencies required (sqlite3 is built-in)

### Phase 7: Update Documentation (1 hour)
1. **Update README.md:**
   - Remove Docker/PostgreSQL setup instructions
   - Simplify installation to just `uv tool install mem8`
   - Focus on Claude Code customization features
   - Add migration guide for existing users

2. **Update CLAUDE.md:**
   - Remove references to backend/frontend
   - Update memory commands
   - Clarify that sharing is file-based

3. **Create MIGRATION.md:**
   - Document removed features
   - Provide alternatives for team users
   - Explain simplified architecture

### Phase 8: Testing and Validation (1 hour)
1. **Test core commands:**
   ```bash
   mem8 init
   mem8 status
   mem8 sync
   mem8 search "test query"
   mem8 find all
   ```

2. **Test template generation:**
   ```bash
   mem8 init --template claude-config
   mem8 init --template thoughts-repo
   ```

3. **Verify cross-repository discovery:**
   - Check that thoughts are still discovered from sibling repos
   - Confirm Windows junction to `C:\Users\vaski\mem8-shared` works

### Phase 9: Package and Release (30 min)
1. **Update version in pyproject.toml** to 3.0.0 (breaking changes)
2. **Update changelog** with removed features
3. **Test installation:**
   ```bash
   uv build
   uv tool install ./dist/mem8-3.0.0-py3-none-any.whl
   ```
4. **Tag and release**

## Expected Outcomes
- **70% reduction in codebase size** (~50+ files removed)
- **90% reduction in dependencies**
- **Instant installation** (no Docker/PostgreSQL setup)
- **Focused functionality** on Claude Code customization
- **Maintained file-based sharing** that already works

## Rollback Plan
If issues arise:
1. Git reset to backup commit
2. Restore backend/frontend directories
3. Restore Docker configurations
4. Revert pyproject.toml changes

## Alternative Approach (If Gradual Migration Preferred)
1. **Create mem8-lite** as separate package
2. Extract core CLI functionality
3. Maintain original mem8 for team users
4. Deprecate team features over time

## Next Steps
1. Get approval for this plan
2. Create feature branch: `git checkout -b simplify-to-local-cli`
3. Execute phases with commits after each phase
4. Test thoroughly before merging

## Questions to Resolve
- [ ] Keep legacy CLI code or fully remove?
- [ ] Maintain any backward compatibility?
- [ ] Create mem8-lite or modify existing package?
- [ ] Add SQLite search index or stay pure file-based?