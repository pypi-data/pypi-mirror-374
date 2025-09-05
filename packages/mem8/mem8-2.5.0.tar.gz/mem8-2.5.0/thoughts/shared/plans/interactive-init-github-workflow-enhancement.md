# Interactive Init Enhancement with GitHub Workflow Integration

## Overview

Enhance `mem8 init --template claude-config` with interactive mode that allows user choice-based configuration, replace Linear/Ralph workflow automation with GitHub Issues integration (defaulting to free GitHub tools), and integrate missing 'hack' command functionality into the mem8 CLI with proper command naming alignment.

## Current State Analysis

The mem8 CLI has a solid foundation but several key limitations:

- **Non-interactive templates**: Current `cookiecutter(..., no_input=True)` at `mem8/cli_typer.py:986` prevents user interaction
- **Missing CLI commands**: Two hack scripts referenced in templates need CLI integration:
  - `hack/create_worktree.sh` → needs `mem8 worktree create` command  
  - `hack/spec_metadata.sh` → needs `mem8 metadata research` command
- **Linear/Ralph complexity**: Current Linear integration is complex and Ralph commands assume specific workflow
- **Template conditionals exist**: `cookiecutter.json` already has boolean flags for `include_linear_integration` and `include_ralph_commands`
- **Post-generation hooks work**: `hooks/post_gen_project.py` removes unused files based on configuration

### Key Discoveries:
- CLI follows consistent kebab-case for commands, snake_case for files: `mem8/cli_typer.py:568-1125`
- Interactive patterns exist: `typer.confirm()` used at lines 505 and 876
- Template system works: Both templates properly packaged at `mem8/templates/`
- Agent naming pattern: `domain-action.md` (like `codebase-analyzer.md`)
- Command naming pattern: `action_object.md` (like `create_plan.md`)

## Desired End State

After completion:
1. **Interactive Init**: `mem8 init --interactive` guides users through template configuration choices
2. **GitHub Workflow Default**: Templates default to GitHub Issues instead of Linear (free/open source)
3. **Integrated Commands**: All hack script functionality available as proper CLI commands
4. **Consistent Naming**: All commands and agents follow established naming conventions
5. **Backward Compatible**: All existing init parameters continue to work unchanged

### Verification:
- `mem8 init --interactive` prompts for workflow choices and generates appropriate templates
- `mem8 worktree create ENG-1234 feature-branch` creates git worktree
- `mem8 metadata research "topic"` generates research document metadata
- GitHub workflow commands work with `gh` CLI instead of Linear MCP tools

## What We're NOT Doing

- Not removing Linear integration entirely (still available as option)
- Not changing existing non-interactive init behavior (backward compatibility)
- Not modifying core cookiecutter template structure (only expanding configuration)
- Not implementing full GitHub Projects API integration (keeping it simple with gh CLI)
- Not automating complex Linear-style state progression (GitHub has simpler workflow)

## Implementation Approach

Phase-based approach that maintains backward compatibility while adding new functionality:
1. **Template Enhancement**: Add interactive cookiecutter parameters and GitHub-focused templates
2. **CLI Command Integration**: Add missing worktree and metadata command groups
3. **Interactive Init**: Enhance init command with user choice gathering
4. **Template Content**: Replace Ralph automation with simpler GitHub workflow commands

## Phase 1: Template System Enhancement

### Overview
Expand cookiecutter configuration with choice-based parameters and create GitHub-focused templates to replace Linear/Ralph dependencies.

### Changes Required:

#### 1. Claude Template Configuration Enhancement
**File**: `mem8/templates/claude-dot-md-template/cookiecutter.json`
**Changes**: Replace Linear/Ralph focus with GitHub-centric choices

```json
{
  "project_name": "Claude AI Memory",
  "project_slug": ".claude",
  "project_description": "AI memory configuration for Claude Code",
  "include_agents": true,
  "include_commands": true,
  "workflow_provider": ["github", "linear", "none"],
  "include_github_integration": "{% if cookiecutter.workflow_provider == 'github' %}true{% else %}false{% endif %}",
  "include_linear_integration": "{% if cookiecutter.workflow_provider == 'linear' %}true{% else %}false{% endif %}",
  "include_workflow_automation": ["standard", "advanced", "none"],
  "include_web_search": true,
  "default_tools": "Read, Grep, Glob, LS",
  "organization_name": "My Organization",
  "github_org": "your-org",
  "github_repo": "your-repo",
  "repository_path": "/shared/"
}
```

#### 2. Post-Generation Hook Enhancement
**File**: `mem8/templates/claude-dot-md-template/hooks/post_gen_project.py`
**Changes**: Add GitHub workflow conditional logic

```python
# Add after existing removals (around line 46)
workflow_provider = '{{ cookiecutter.workflow_provider }}'
include_workflow_automation = '{{ cookiecutter.include_workflow_automation }}'

# Remove unused workflow files
if workflow_provider != 'github':
    remove_files([
        'commands/github_issues.md',
        'commands/repo_setup.md',
        'commands/workflow_automation.md'
    ])

if workflow_provider != 'linear':
    remove_files(['commands/linear.md'])

# Remove Ralph automation commands entirely
remove_files([
    'commands/ralph_impl.md',
    'commands/ralph_plan.md', 
    'commands/ralph_research.md'
])

# Remove advanced workflow if not selected
if include_workflow_automation == 'none':
    remove_files(['commands/workflow_automation.md'])
```

#### 3. GitHub Issues Command Template
**File**: `mem8/templates/claude-dot-md-template/{{cookiecutter.project_slug}}/commands/github_issues.md`
**Changes**: Create new GitHub Issues management command (simplified Linear equivalent)

```markdown
# GitHub Issues - Issue Management

You are tasked with managing GitHub Issues, including creating issues from thoughts documents, updating existing issues, and following GitHub-based workflow patterns.

## Initial Setup

Verify that gh CLI is available:
```bash
gh --version
```

If not available, respond:
```
I need the GitHub CLI (gh) to help with issue management. Please install it:
- macOS: `brew install gh` 
- Windows: `winget install GitHub.cli`
- Linux: See https://cli.github.com/

Then authenticate with: `gh auth login`
```

## Workflow Labels

This command uses GitHub labels to represent workflow stages:
- `needs-triage` - Initial review needed
- `needs-research` - Investigation required
- `ready-for-plan` - Research complete, needs implementation plan
- `ready-for-dev` - Plan approved, ready for development
- `in-development` - Active development
- `ready-for-review` - PR submitted

## Action-Specific Instructions

### Creating Issues from Thoughts

1. **Locate and read the thoughts document**
2. **Analyze the document content** for core problem and implementation details
3. **Draft the issue summary** with clear title and description
4. **Create GitHub issue**:
   ```bash
   gh issue create --title "Title" --body "Description" --label "needs-triage"
   ```
5. **Update thoughts document** with issue reference

### Managing Issue Workflow

Update issue labels to represent workflow progression:
```bash
gh issue edit ISSUE_NUMBER --add-label "ready-for-dev" --remove-label "ready-for-plan"
```

Default to "needs-triage" for new issues and progress through workflow as appropriate.
```

#### 4. Workflow Automation Command Template  
**File**: `mem8/templates/claude-dot-md-template/{{cookiecutter.project_slug}}/commands/workflow_automation.md`
**Changes**: Create simplified GitHub workflow automation (replaces Ralph commands)

```markdown
# Workflow Automation - GitHub Issues

Simplified workflow automation for GitHub Issues using gh CLI, replacing complex Linear workflow automation.

## Commands

### Research Issues
Find and work on issues labeled `needs-research`:
```bash
gh issue list --label "needs-research" --limit 10
```

### Plan Issues  
Find and work on issues labeled `ready-for-plan`:
```bash
gh issue list --label "ready-for-plan" --limit 10
```

### Implementation Issues
Find and work on issues labeled `ready-for-dev`:  
```bash
gh issue list --label "ready-for-dev" --limit 10
```

Much simpler than Linear's complex state machine - GitHub Issues focus on labels and simplicity.
```

#### 5. Repository Setup Command Template
**File**: `mem8/templates/claude-dot-md-template/{{cookiecutter.project_slug}}/commands/repo_setup.md`
**Changes**: Create GitHub repository integration setup

```markdown
# Repository Setup - GitHub Integration

Set up GitHub repository integration for mem8 workflow.

## Setup Steps

1. **Verify GitHub CLI**: `gh auth status`
2. **Set default repository**: `gh repo set-default`
3. **Create workflow labels**:
   ```bash
   gh label create "needs-triage" --color "d73a4a" --description "Needs initial review"
   gh label create "needs-research" --color "fbca04" --description "Investigation required"
   gh label create "ready-for-plan" --color "0e8a16" --description "Ready for implementation plan"
   gh label create "ready-for-dev" --color "1d76db" --description "Ready for development"
   gh label create "in-development" --color "5319e7" --description "Active development"
   gh label create "ready-for-review" --color "f9d0c4" --description "Ready for code review"
   ```

4. **Configure repository settings** for mem8 integration
```

### Success Criteria:

#### Automated Verification:
- [x] Templates generate without errors: `cookiecutter mem8/templates/claude-dot-md-template --no-input`
- [x] Post-generation hooks run successfully
- [x] All template references resolve correctly: `grep -r "{{" .claude/` returns no unresolved variables
- [x] JSON validation passes: `python -m json.tool cookiecutter.json`

#### Manual Verification:
- [x] Interactive cookiecutter prompts work correctly when `no_input=False`
- [x] Different workflow_provider choices generate appropriate files
- [x] Ralph commands are completely removed from generated templates
- [x] GitHub workflow files are created when github is selected
- [x] Existing Linear integration still works when selected

---

## Phase 2: CLI Command Integration

### Overview  
Add missing CLI command groups for worktree and metadata management that replace hack script functionality.

### Changes Required:

#### 1. Worktree Command Group
**File**: `mem8/cli_typer.py`  
**Changes**: Add worktree subcommand group after line 1158 (following deploy_app pattern)

```python
# Create worktree subcommand app
worktree_app = typer.Typer(name="worktree", help="Git worktree management for development workflows")
typer_app.add_typer(worktree_app, name="worktree")

@worktree_app.command("create")
def worktree_create(
    ticket_id: Annotated[str, typer.Argument(help="Ticket ID (e.g., ENG-1234, GH-123)")],
    branch_name: Annotated[str, typer.Argument(help="Git branch name")],
    base_dir: Annotated[Path, typer.Option(
        "--base-dir", help="Base directory for worktrees"
    )] = Path.home() / "wt",
    auto_launch: Annotated[bool, typer.Option(
        "--launch", help="Auto-launch mem8 dashboard in worktree"
    )] = True,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Create a git worktree for ticket implementation (replaces hack/create_worktree.sh)."""
    from .core.worktree import create_worktree
    
    set_app_state(verbose=verbose)
    
    try:
        worktree_path = create_worktree(ticket_id, branch_name, base_dir)
        console.print(f"✅ [green]Created worktree: {worktree_path}[/green]")
        
        if auto_launch:
            launch_cmd = f'mem8 dashboard -w {worktree_path} "/implement_plan and when done, read ./claude/commands/commit.md and create commit, then read ./claude/commands/describe_pr.md and create PR"'
            console.print(f"🚀 [cyan]Launching: {launch_cmd}[/cyan]")
            
            import subprocess
            subprocess.run(launch_cmd, shell=True)
            
    except Exception as e:
        console.print(f"❌ [bold red]Error creating worktree: {e}[/bold red]")
        if verbose:
            console.print_exception()

@worktree_app.command("list")
def worktree_list():
    """List existing worktrees."""
    # Implementation here

@worktree_app.command("remove")  
def worktree_remove():
    """Remove a worktree."""
    # Implementation here
```

#### 2. Metadata Command Group
**File**: `mem8/cli_typer.py`
**Changes**: Add metadata subcommand group after worktree_app

```python
# Create metadata subcommand app
metadata_app = typer.Typer(name="metadata", help="Repository metadata management and research tools")
typer_app.add_typer(metadata_app, name="metadata")

@metadata_app.command("git")
def metadata_git(
    format: Annotated[str, typer.Option(
        "--format", help="Output format"
    )] = "yaml",
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Get git repository metadata."""
    from .core.metadata import get_git_metadata
    
    try:
        metadata = get_git_metadata()
        
        if format == "yaml":
            import yaml
            console.print(yaml.dump(metadata, default_flow_style=False))
        elif format == "json":
            import json
            console.print(json.dumps(metadata, indent=2))
        else:
            for key, value in metadata.items():
                console.print(f"{key}: {value}")
                
    except Exception as e:
        console.print(f"❌ [bold red]Error getting metadata: {e}[/bold red]")
        if verbose:
            console.print_exception()

@metadata_app.command("research")
def metadata_research(
    topic: Annotated[str, typer.Argument(help="Research topic/question")],
    output_file: Annotated[Optional[Path], typer.Option(
        "--output", "-o", help="Output to file"
    )] = None,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Generate complete metadata for research documents (replaces hack/spec_metadata.sh)."""
    from .core.metadata import generate_research_metadata
    
    try:
        metadata = generate_research_metadata(topic)
        
        if output_file:
            output_file.write_text(yaml.dump(metadata, default_flow_style=False))
            console.print(f"✅ [green]Metadata written to: {output_file}[/green]")
        else:
            console.print(yaml.dump(metadata, default_flow_style=False))
            
    except Exception as e:
        console.print(f"❌ [bold red]Error generating metadata: {e}[/bold red]")
        if verbose:
            console.print_exception()
```

#### 3. Core Worktree Module
**File**: `mem8/core/worktree.py`
**Changes**: Create new module for worktree management

```python
"""Git worktree management functionality."""

import subprocess
from pathlib import Path
from typing import Optional

def create_worktree(ticket_id: str, branch_name: str, base_dir: Path) -> Path:
    """Create a git worktree for ticket implementation."""
    import subprocess
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
```

#### 4. Core Metadata Module Enhancement
**File**: `mem8/core/metadata.py` 
**Changes**: Create new module for metadata generation

```python
"""Metadata generation for thoughts and research documents."""

import datetime
from pathlib import Path
from typing import Dict, Any
from .utils import get_git_info

def get_git_metadata() -> Dict[str, Any]:
    """Get current git repository metadata."""
    git_info = get_git_info()
    
    if not git_info['is_git_repo']:
        raise ValueError("Not in a git repository")
    
    import subprocess
    
    # Get current commit hash
    commit_result = subprocess.run(
        ["git", "rev-parse", "HEAD"], 
        capture_output=True, text=True
    )
    
    return {
        "git_commit": commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown",
        "branch": git_info['current_branch'],
        "repository": git_info['repo_root'].name,
        "repo_path": str(git_info['repo_root']),
        "is_clean": _check_git_status()
    }

def generate_research_metadata(topic: str) -> Dict[str, Any]:
    """Generate complete metadata for research documents."""
    git_metadata = get_git_metadata()
    current_time = datetime.datetime.now().astimezone()
    
    # Get researcher name from git config or default
    import subprocess
    name_result = subprocess.run(
        ["git", "config", "user.name"], 
        capture_output=True, text=True
    )
    researcher = name_result.stdout.strip() if name_result.returncode == 0 else "unknown"
    
    return {
        "date": current_time.isoformat(),
        "researcher": researcher,
        "git_commit": git_metadata["git_commit"],
        "branch": git_metadata["branch"],
        "repository": git_metadata["repository"],
        "topic": topic,
        "tags": ["research", "codebase"],
        "status": "draft",
        "last_updated": current_time.strftime("%Y-%m-%d"),
        "last_updated_by": researcher
    }

def _check_git_status() -> bool:
    """Check if git working directory is clean."""
    import subprocess
    
    status_result = subprocess.run(
        ["git", "status", "--porcelain"], 
        capture_output=True, text=True
    )
    
    return len(status_result.stdout.strip()) == 0
```

### Success Criteria:

#### Automated Verification:
- [x] CLI imports and loads without errors: `python -c "import mem8.cli_typer; print('OK')"`
- [x] New command groups are discoverable: `mem8 --help` shows worktree and metadata
- [x] Subcommands are properly registered: `mem8 worktree --help` and `mem8 metadata --help` work
- [x] Type checking passes: `mypy mem8/cli_typer.py mem8/core/worktree.py mem8/core/metadata.py`
- [x] Core modules import correctly: `python -c "from mem8.core import worktree, metadata; print('OK')"`

#### Manual Verification:
- [x] `mem8 worktree create TEST-123 test-branch` creates worktree successfully
- [x] `mem8 metadata git` returns current repository metadata
- [x] `mem8 metadata research "test topic"` generates properly formatted metadata
- [x] Commands follow established CLI patterns and error handling
- [x] Verbose mode provides useful debugging information

---

## Phase 3: Interactive Init Enhancement

### Overview
Enhance the existing init command with interactive mode that gathers user preferences and applies them to cookiecutter template generation.

### Changes Required:

#### 1. Init Command Enhancement
**File**: `mem8/cli_typer.py`
**Changes**: Add interactive flag and user choice gathering to existing init function (around line 794)

```python
@typer_app.command()
def init(
    template: Optional[str] = typer.Option(
        None,
        "--template", "-t",
        help="Force specific template: claude-config, thoughts-repo, or full (default: auto-detect)",
    ),
    repos: Annotated[Optional[str], typer.Option(
        "--repos", help="Comma-separated list of repository paths to discover"
    )] = None,
    shared_dir: Annotated[Optional[Path], typer.Option(
        "--shared-dir", help="Path to shared directory for thoughts"
    )] = None,
    web: Annotated[bool, typer.Option(
        "--web", help="Launch web UI after setup"
    )] = False,
    force: Annotated[bool, typer.Option(
        "--force", help="Skip confirmation prompts and use smart defaults"
    )] = False,
    interactive: Annotated[bool, typer.Option(
        "--interactive", "-i", help="Interactive mode with guided prompts for all configuration options"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Initialize mem8 workspace with intelligent defaults and guided setup."""
    from .core.smart_setup import (
        detect_project_context, generate_smart_config, setup_minimal_structure,
        launch_web_ui, show_setup_instructions
    )
    from .claude_integration import update_claude_md_integration
    
    set_app_state(verbose=verbose)
    
    # Add interactive mode handling after context detection
    console.print("🚀 [bold blue]Setting up mem8 with intelligent defaults...[/bold blue]")
    
    try:
        # 1. Auto-detect project context (existing logic)
        console.print("🔍 [dim]Analyzing project context...[/dim]")
        context = detect_project_context()
        
        # 2. Interactive mode: gather user preferences
        interactive_config = {}
        if interactive:
            interactive_config = _interactive_prompt_for_init(context)
            
            # Override parameters with interactive values where not explicitly set
            template = template or interactive_config.get('template')
            shared_dir = shared_dir or interactive_config.get('shared_dir') 
            web = web or interactive_config.get('web', False)
            repos = repos or interactive_config.get('repos')
        
        # 3. Generate smart configuration with interactive overrides
        config = generate_smart_config(context, repos)
        if interactive_config:
            config.update(interactive_config)
        
        # ... rest of existing init logic unchanged ...
        
    except Exception as e:
        console.print(f"❌ [bold red]Error during setup: {e}[/bold red]")
        if verbose:
            console.print_exception()
```

#### 2. Interactive Helper Function
**File**: `mem8/cli_typer.py`
**Changes**: Add interactive prompt function after line 195 (near other helper functions)

```python
def _interactive_prompt_for_init(context: Dict[str, Any]) -> Dict[str, Any]:
    """Interactive prompts for init command configuration."""
    import typer
    
    console.print("[bold blue]🎯 Interactive Setup Mode[/bold blue]")
    console.print(f"Detected: {context['project_type']} project with {len(context['git_repos'])} repositories")
    
    # Template selection with smart default
    if context['is_claude_code_project']:
        default_template = "claude-config"
        console.print("[dim]Claude Code project detected - defaulting to claude-config template[/dim]")
    else:
        default_template = "full"
    
    template = typer.prompt(
        "Template type", 
        default=default_template,
        type=typer.Choice(["full", "claude-config", "thoughts-repo", "none"])
    )
    
    interactive_config = {"template": template if template != "none" else None}
    
    # Only gather template configuration if we're installing templates
    if template and template != "none":
        console.print("\n📋 [bold blue]Template Configuration[/bold blue]")
        
        # Workflow provider selection
        workflow_provider = typer.prompt(
            "Workflow provider (GitHub is free and open source)",
            default="github",
            type=typer.Choice(["github", "linear", "none"])
        )
        interactive_config["workflow_provider"] = workflow_provider
        
        # Workflow automation level
        if workflow_provider != "none":
            workflow_automation = typer.prompt(
                "Workflow automation level",
                default="standard",  
                type=typer.Choice(["standard", "advanced", "none"])
            )
            interactive_config["workflow_automation"] = workflow_automation
        
        # GitHub-specific configuration
        if workflow_provider == "github":
            github_org = typer.prompt("GitHub organization/username", default="your-org")
            github_repo = typer.prompt("GitHub repository name", default="your-repo")
            interactive_config.update({
                "github_org": github_org,
                "github_repo": github_repo
            })
    
    # Repository selection
    if context['git_repos']:
        console.print(f"\n📁 [green]Found {len(context['git_repos'])} repositories:[/green]")
        for i, repo in enumerate(context['git_repos'][:5]):  # Show first 5
            console.print(f"  {i+1}. {repo['name']} ({repo['path']})")
        
        if len(context['git_repos']) > 5:
            console.print(f"  ... and {len(context['git_repos']) - 5} more")
        
        include_repos = typer.confirm("Include all found repositories?", default=True)
        if not include_repos:
            # For now, keep it simple - all or none
            interactive_config["repos"] = None
    
    # Shared directory with intelligent default
    default_shared = str(context.get('shared_location', Path.home() / "mem8-shared"))
    shared_dir = typer.prompt(
        "Shared directory path",
        default=default_shared
    )
    interactive_config["shared_dir"] = Path(shared_dir)
    
    # Web UI launch
    web = typer.confirm("Launch web UI after setup?", default=True)
    interactive_config["web"] = web
    
    return interactive_config
```

#### 3. Template Installation Enhancement
**File**: `mem8/cli_typer.py`
**Changes**: Modify `_install_templates()` function to support interactive configuration (around line 942)

```python
def _install_templates(template_type: str, force: bool, verbose: bool, interactive_config: Dict[str, Any] = None) -> None:
    """Install cookiecutter templates to the workspace."""
    from cookiecutter.main import cookiecutter
    from importlib import resources
    import mem8.templates
    
    # ... existing template path resolution ...
    
    # Run cookiecutter for each template
    for template_name in template_map[template_type]:
        template_path = template_base / template_name
        
        # ... existing target directory logic ...
        
        try:
            # Build extra_context from interactive configuration
            extra_context = {}
            if "claude" in template_name:
                extra_context = {"project_slug": ".claude"}
                
                # Apply interactive configuration to claude templates
                if interactive_config:
                    if "workflow_provider" in interactive_config:
                        extra_context["workflow_provider"] = interactive_config["workflow_provider"]
                    if "github_org" in interactive_config:
                        extra_context["github_org"] = interactive_config["github_org"]
                    if "github_repo" in interactive_config:
                        extra_context["github_repo"] = interactive_config["github_repo"]
                    if "workflow_automation" in interactive_config:
                        extra_context["include_workflow_automation"] = interactive_config["workflow_automation"]
            
            # Use interactive mode when interactive_config provided
            no_input = interactive_config is None
            
            cookiecutter(
                str(template_path),
                no_input=no_input,
                output_dir=str(workspace_dir),
                overwrite_if_exists=force,
                extra_context=extra_context
            )
            console.print(f"  ✓ Installed {template_name}")
        except Exception as e:
            if verbose:
                console.print(f"[yellow]Could not install {template_name}: {e}[/yellow]")
```

### Success Criteria:

#### Automated Verification:
- [ ] Non-interactive init still works: `mem8 init --template claude-config --force`
- [ ] Interactive mode can be invoked: `echo -e "claude-config\ngithub\nstandard\nyour-org\nyour-repo\ny\n/tmp/shared\ny" | mem8 init --interactive`
- [ ] CLI help shows new option: `mem8 init --help` includes `--interactive` flag
- [ ] Type checking passes: `mypy mem8/cli_typer.py`

#### Manual Verification:
- [ ] `mem8 init --interactive` prompts for all configuration options
- [ ] Different workflow provider choices generate appropriate templates
- [ ] Interactive mode respects existing CLI flags when provided
- [ ] Generated templates contain correct configuration based on user choices
- [ ] Backward compatibility maintained - existing scripts using init continue to work

---

## Phase 4: Template Content Updates

### Overview
Update template command references to use new CLI commands instead of hack scripts and ensure all naming follows established conventions.

### Changes Required:

#### 1. Command Reference Updates
**File**: `mem8/templates/claude-dot-md-template/{{cookiecutter.project_slug}}/commands/create_worktree.md`
**Changes**: Replace hack script reference with CLI command

```markdown
# Create Worktree

You are tasked with creating git worktrees for development work.

## Process:

1. **Determine worktree details:**
   - Ticket ID (e.g., ENG-1234, GH-123)
   - Branch name
   - Confirm with user

2. **Create worktree using CLI:**
   ```bash
   mem8 worktree create TICKET-ID BRANCH-NAME
   ```

3. **Launch implementation session:**
   The worktree command will automatically launch:
   ```bash
   mem8 dashboard -w ~/wt/repo/TICKET-ID "/implement_plan and when done, read ./claude/commands/commit.md and create commit, then read ./claude/commands/describe_pr.md and create PR"
   ```

Much simpler than the previous hack script approach!
```

#### 2. Research Command Updates
**File**: `mem8/templates/claude-dot-md-template/{{cookiecutter.project_slug}}/commands/research_codebase.md`  
**Changes**: Replace hack script reference with CLI command (around line 69)

```markdown
5. **Gather metadata for the research document:**
   - Generate metadata using CLI: `mem8 metadata research "Research Topic"`
   - Filename: `thoughts/shared/research/YYYY-MM-DD_HH-MM-SS_topic.md`
```

#### 3. Agent Naming Consistency
**File**: `mem8/templates/claude-dot-md-template/{{cookiecutter.project_slug}}/agents/github-workflow-agent.md`
**Changes**: Create GitHub workflow agent (following naming pattern)

```markdown
# GitHub Workflow Agent

Use this agent for GitHub Issues and repository workflow automation.

Focus on:
- GitHub Issues management via gh CLI
- Repository setup and configuration
- Simple workflow automation using GitHub labels
- Integration with GitHub Projects when needed

Tools: Bash (gh CLI), Read, Write, Edit
```

#### 4. Remove Ralph References
**File**: Template files throughout
**Changes**: Remove all references to ralph commands from existing templates

- Remove `ralph_impl.md`, `ralph_plan.md`, `ralph_research.md` 
- Update any command files that reference ralph workflows
- Replace with GitHub workflow equivalents

### Success Criteria:

#### Automated Verification:
- [ ] Template generation completes without errors
- [ ] No references to hack scripts remain: `grep -r "hack/" .claude/` returns empty
- [ ] No references to ralph commands: `grep -r "ralph" .claude/` returns empty  
- [ ] All CLI command references are valid: commands mentioned in templates exist
- [ ] Agent naming follows pattern: all agents use `domain-action.md` format

#### Manual Verification:
- [ ] Generated templates contain working command references
- [ ] All CLI commands referenced in templates actually work
- [ ] Agent names are consistent and follow established patterns
- [ ] GitHub workflow commands provide equivalent functionality to removed ralph commands
- [ ] Documentation is clear and actionable for users

---

## Testing Strategy

### Unit Tests:
- CLI command parsing and validation
- Cookiecutter template generation with different parameters
- Interactive prompt logic with mocked user input
- Git worktree and metadata generation functions

### Integration Tests:
- Full `mem8 init --interactive` workflow with real user choices
- Template generation with different workflow provider selections
- CLI command integration (`mem8 worktree create`, `mem8 metadata research`)
- GitHub workflow commands with real repositories

### Manual Testing Steps:
1. **Test non-interactive backward compatibility**: `mem8 init --template claude-config` still works
2. **Test interactive mode**: `mem8 init --interactive` with different choice combinations
3. **Test new CLI commands**: Create worktrees and generate metadata manually
4. **Test generated templates**: Verify GitHub workflow commands work with real repositories
5. **Test edge cases**: Interactive mode with existing directories, missing dependencies

## Performance Considerations

- Interactive prompts should have reasonable timeouts
- Template generation should remain fast (< 5 seconds)
- New CLI commands should follow lazy loading patterns from existing code
- Git operations should handle large repositories gracefully

## Migration Notes

### Backward Compatibility:
- All existing `mem8 init` usage continues to work unchanged
- Existing templates generated previously are not affected
- New CLI commands are additive - no existing functionality removed

### GitHub Migration:
- Linear integration remains available as option
- Ralph commands completely removed (they were workflow-specific automation)
- GitHub becomes the default due to free/open source nature

## References

- Original research: `thoughts/shared/research/2025-09-03_CLI-interactive-init-enhancement.md`
- CLI patterns: `mem8/cli_typer.py:568-1125` (command group structure)
- Template system: `mem8/templates/claude-dot-md-template/cookiecutter.json`
- Interactive patterns: `mem8/cli_typer.py:505,876` (typer.confirm usage)
- Agent naming: Template agents follow `domain-action.md` pattern
- Command naming: Template commands follow `action_object.md` pattern