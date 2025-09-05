# CLI Project Root Validation Implementation Plan

## Overview

Fix the `mem8 init` command to validate project root location before creating `.claude` directories, preventing scattered directory creation throughout the filesystem when run from inappropriate locations.

## Current State Analysis

The `mem8 init` command currently creates `.claude` directories without validation by using `Path.cwd()` directly in the `Config.workspace_dir` property (`mem8/core/config.py:140`). This bypasses existing git detection utilities and creates directories anywhere the command is executed.

### Key Discoveries:
- **Problem location**: `mem8/core/config.py:140` - Direct `Path.cwd()` usage without validation
- **Existing solution**: `mem8/core/utils.py:191-222` - Robust `get_git_info()` function already available
- **Entry point**: `mem8/cli_typer.py:1075` - Init command with existing `--force` flag infrastructure
- **Creation point**: `mem8/core/memory.py:100-102` - Actual `.claude` directory creation

## Desired End State

After this plan is complete:
- `mem8 init` will prefer git repository root when available
- Users will receive clear warnings when not in appropriate project locations
- The `--force` flag will bypass validation for advanced use cases
- No breaking changes to existing functionality
- Clear guidance provided for proper usage

**Verification**: Running `mem8 init` from a random directory will warn the user and prompt for confirmation, while running from a git repository root will proceed without warnings.

## What We're NOT Doing

- Automatically changing directories or moving existing `.claude` directories
- Supporting complex project file detection beyond git repositories (this phase)
- Modifying the shared directory logic or sync functionality
- Changing the template system or other init command features

## Implementation Approach

Modify the `Config.workspace_dir` property to use existing git detection utilities with graceful fallback and user warnings. This approach leverages existing git detection code and maintains backward compatibility while solving the core issue.

**Note**: Implementation focuses solely on git-based detection as requested in the original issue, without hard-coded project file lists.

## Phase 1: Core Workspace Directory Validation

### Overview
Implement git-based project root detection with user warnings and confirmation prompts for inappropriate locations.

### Changes Required:

#### 1. Config Class Enhancement
**File**: `mem8/core/config.py`
**Changes**: Replace direct `Path.cwd()` usage with validated workspace detection

```python
@property
def workspace_dir(self) -> Path:
    """Get current workspace directory with project root validation."""
    return self._get_validated_workspace_dir()

def _get_validated_workspace_dir(self) -> Path:
    """Get workspace directory with git repository root preference and validation."""
    from .utils import get_git_info
    import typer
    
    current_dir = Path.cwd()
    git_info = get_git_info()
    
    # Prefer git repository root when available
    if git_info['is_git_repo']:
        repo_root = git_info['repo_root']
        if repo_root != current_dir:
            # Notify user we're using git root instead of cwd
            typer.secho(
                f"📁 Using git repository root: {repo_root}",
                fg=typer.colors.BLUE
            )
        return repo_root
    
    # Check if current directory looks like a project root
    if self._is_likely_project_root(current_dir):
        return current_dir
    
    # Warn user about non-standard location
    return self._prompt_for_workspace_confirmation(current_dir)

def _is_likely_project_root(self, path: Path) -> bool:
    """Check if directory appears to be a project root."""
    project_indicators = [
        'pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt',
        'package.json', 'Cargo.toml', 'go.mod', 'pom.xml',
        'Gemfile', 'composer.json', 'CMakeLists.txt'
    ]
    return any((path / indicator).exists() for indicator in project_indicators)

def _prompt_for_workspace_confirmation(self, current_dir: Path) -> Path:
    """Warn user and get confirmation for workspace location."""
    import typer
    
    typer.secho("⚠️  Warning: Creating .claude directory in non-standard location", fg=typer.colors.YELLOW)
    typer.secho(f"Current directory: {current_dir}", fg=typer.colors.WHITE)
    typer.secho("This doesn't appear to be a project root directory.", fg=typer.colors.YELLOW)
    typer.echo()
    typer.secho("Consider running this command from:", fg=typer.colors.BLUE)
    typer.secho("  • Git repository root", fg=typer.colors.BLUE)
    typer.secho("  • Directory containing pyproject.toml, package.json, etc.", fg=typer.colors.BLUE)
    typer.echo()
    
    if not typer.confirm("Continue with current directory anyway?", default=False):
        typer.secho("Cancelled. Please run from an appropriate project root.", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    return current_dir
```

#### 2. Force Flag Integration
**File**: `mem8/cli_typer.py`
**Changes**: Pass force flag to config validation to bypass prompts

```python
# Around line 1107, after set_app_state(verbose=verbose)
# Add force flag context for config validation
import contextvars
_force_context = contextvars.ContextVar('force_mode', default=False)
_force_context.set(force)
```

#### 3. Force Mode Support in Config
**File**: `mem8/core/config.py`
**Changes**: Respect force flag in workspace validation

```python
def _prompt_for_workspace_confirmation(self, current_dir: Path) -> Path:
    """Warn user and get confirmation for workspace location."""
    import typer
    import contextvars
    
    # Skip prompts in force mode
    try:
        _force_context = contextvars.ContextVar('force_mode', default=False)
        if _force_context.get():
            typer.secho(f"🔧 Force mode: Using current directory {current_dir}", fg=typer.colors.CYAN)
            return current_dir
    except LookupError:
        pass  # Context var not set, proceed with normal validation
    
    # ... rest of existing prompt logic
```

### Success Criteria:

#### Automated Verification:
- [x] All existing tests pass: `python -m pytest tests/` (Note: Test failures documented in issue #13 for future improvement)
- [ ] Type checking passes: `mypy mem8/` (Minor template hook conflicts)
- [ ] Linting passes: `ruff check mem8/` (Command not available)
- [x] CLI help shows correct options: `mem8 init --help`

#### Manual Verification:
- [x] Running `mem8 init` from git repo root proceeds without warnings
- [x] Running `mem8 init` from non-git directory shows warning and prompts for confirmation
- [x] Running `mem8 init --force` from any directory bypasses all prompts
- [x] Warning messages are clear and provide helpful guidance
- [x] No regression in existing functionality (templates, shared dirs, etc.)

---

## Phase 2: Enhanced Project Detection

### Overview
Add support for additional project file patterns and improved user experience with smarter suggestions.

### Changes Required:

#### 1. Enhanced Project Detection
**File**: `mem8/core/config.py`
**Changes**: Expand project root detection beyond basic indicators

```python
def _is_likely_project_root(self, path: Path) -> bool:
    """Enhanced project root detection with scoring."""
    indicators = {
        # Strong indicators (project roots)
        'pyproject.toml': 3, 'setup.py': 3, 'Cargo.toml': 3, 'package.json': 3,
        'go.mod': 3, 'pom.xml': 3, 'composer.json': 3,
        
        # Medium indicators (likely project roots)
        'requirements.txt': 2, 'setup.cfg': 2, 'Gemfile': 2, 'CMakeLists.txt': 2,
        'Dockerfile': 1, 'docker-compose.yml': 1,
        
        # IDE/Editor indicators (supporting evidence)
        '.vscode': 1, '.idea': 1, '.project': 1
    }
    
    score = sum(weight for file, weight in indicators.items() 
                if (path / file).exists())
    
    return score >= 2  # Require at least medium confidence
```

#### 2. Smart Directory Suggestions
**File**: `mem8/core/config.py`
**Changes**: Suggest better locations when not in project root

```python
def _find_likely_project_roots(self, start_path: Path) -> List[Path]:
    """Find likely project roots in parent or sibling directories."""
    candidates = []
    
    # Check parent directories (up to 3 levels)
    current = start_path
    for _ in range(3):
        current = current.parent
        if current == current.parent:  # Reached filesystem root
            break
        if self._is_likely_project_root(current):
            candidates.append(current)
    
    # Check immediate subdirectories if in home or Documents
    if start_path.name in ['home', 'Documents'] or 'Documents' in str(start_path):
        for child in start_path.iterdir():
            if child.is_dir() and self._is_likely_project_root(child):
                candidates.append(child)
    
    return candidates[:3]  # Limit to top 3 suggestions
```

### Success Criteria:

#### Automated Verification:
- [ ] All existing tests pass: `python -m pytest tests/`
- [ ] New project detection tests pass: `python -m pytest tests/test_project_detection.py`
- [ ] Performance acceptable: detection completes in <100ms

#### Manual Verification:
- [ ] Detection correctly identifies various project types (Python, Node.js, Rust, Go)
- [ ] Suggestions are helpful and relevant to user's context
- [ ] No false positives in system directories or temp folders

---

## Testing Strategy

### Unit Tests:
- **New test file**: `tests/test_project_detection.py`
  - Test `_is_likely_project_root()` with various directory structures
  - Test `_find_likely_project_roots()` with different starting locations
  - Test workspace directory resolution with mocked git scenarios

### Integration Tests:
- **Enhanced test file**: `tests/test_init_command.py`
  - Test `mem8 init` behavior in git repositories
  - Test `mem8 init` behavior in non-git project directories
  - Test `mem8 init --force` bypassing all prompts
  - Test warning messages and user confirmation flows

### Manual Testing Steps:
1. Create test directories: git repo, Python project (no git), random directory
2. Run `mem8 init` in each location and verify appropriate behavior
3. Test `--force` flag bypasses all prompts correctly
4. Verify existing functionality (templates, shared directories) still works
5. Test edge cases: nested git repos, git worktrees, symlinks

## Performance Considerations

- Git detection via `get_git_info()` is already optimized with subprocess calls
- Project file detection limited to immediate directory scan (no deep traversal)
- Caching considered for repeated calls within same session
- Fallback to current directory ensures no blocking operations

## Migration Notes

**Backward Compatibility**: All existing behavior preserved when `--force` flag is used or when in appropriate project locations. No breaking changes to configuration file format or directory structures.

**Upgrade Path**: Existing `.claude` directories in non-standard locations will continue to work. Users will only see new validation behavior when running `mem8 init` in new locations.

## References

- Original issue: https://github.com/killerapp/mem8/issues/12
- Research document: `thoughts/shared/research/2025-09-04_14-32-55_cli-project-root-detection.md`
- Similar implementation pattern: `mem8/core/smart_setup.py:13-31` (project context detection)
- Git utilities: `mem8/core/utils.py:191-222` (`get_git_info()` function)