#!/usr/bin/env python3
"""
Typer-based CLI implementation for mem8.
Modern CLI framework with enhanced type safety and developer experience.
"""

import typer
from typing import Annotated, Optional, Dict, Any
from enum import Enum
from pathlib import Path

from rich.console import Console

from . import __version__
from .core.config import Config
from .core.memory import MemoryManager
from .core.sync import SyncManager
from .core.utils import setup_logging
from .core.intelligent_query import IntelligentQueryEngine
from .core.thought_actions import ThoughtActionEngine

# Create Rich console with UTF-8 support
console = Console(
    force_terminal=True,
    legacy_windows=None  # Auto-detect Windows compatibility
)

# Create Typer app
typer_app = typer.Typer(
    name="mem8",
    help="Memory management CLI for team collaboration",
    add_completion=False,  # We'll manage this ourselves
    rich_markup_mode="rich"
)


# Enums for type safety
class ShellType(str, Enum):
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    POWERSHELL = "powershell"


# Legacy template types - kept for backwards compatibility but not used in new init
class TemplateType(str, Enum):
    CLAUDE_CONFIG = "claude-config"
    THOUGHTS_REPO = "thoughts-repo"
    FULL = "full"


class SearchMethod(str, Enum):
    FULLTEXT = "fulltext"
    SEMANTIC = "semantic"  # Experimental


class SearchScope(str, Enum):
    PERSONAL = "personal"
    SHARED = "shared"
    TEAM = "team"
    ALL = "all"


class ThoughtType(str, Enum):
    PLAN = "plan"
    RESEARCH = "research"
    TICKET = "ticket"
    PR = "pr"
    DECISION = "decision"
    ALL = "all"


class ContentType(str, Enum):
    THOUGHTS = "thoughts"
    MEMORIES = "memories"
    ALL = "all"


class ActionType(str, Enum):
    SHOW = "show"
    DELETE = "delete"
    ARCHIVE = "archive"
    PROMOTE = "promote"


class SyncDirection(str, Enum):
    PULL = "pull"
    PUSH = "push"
    BOTH = "both"


class DeployEnvironment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


# Enhanced state management with lazy initialization (Phase 2)
class AppState:
    def __init__(self):
        self._config = None
        self._memory_manager = None
        self._sync_manager = None
        self._query_engine = None
        self._action_engine = None
        self._initialized = False
        self._verbose = False
        self._config_dir = None
        
    def initialize(self, verbose: bool = False, config_dir: Optional[Path] = None):
        """Initialize state with parameters."""
        if self._initialized and self._verbose == verbose and self._config_dir == config_dir:
            return  # Already initialized with same parameters
            
        self._verbose = verbose
        self._config_dir = config_dir
        
        if verbose:
            setup_logging(True)
            
        # Initialize components
        self._config = Config(config_dir)
        self._memory_manager = MemoryManager(self._config)
        self._sync_manager = SyncManager(self._config)
        self._query_engine = IntelligentQueryEngine(self._memory_manager.thought_discovery)
        self._action_engine = ThoughtActionEngine(self._config)
        self._initialized = True
    
    @property
    def config(self) -> Config:
        if not self._config:
            self.initialize()
        return self._config
        
    @property
    def memory_manager(self) -> MemoryManager:
        if not self._memory_manager:
            self.initialize()
        return self._memory_manager
        
    @property
    def sync_manager(self) -> SyncManager:
        if not self._sync_manager:
            self.initialize()
        return self._sync_manager
        
    @property
    def query_engine(self) -> IntelligentQueryEngine:
        if not self._query_engine:
            self.initialize()
        return self._query_engine
        
    @property
    def action_engine(self) -> ThoughtActionEngine:
        if not self._action_engine:
            self.initialize()
        return self._action_engine


# Global app state instance
app_state = AppState()


def get_state() -> AppState:
    """Dependency injection helper for accessing app state."""
    return app_state


# Dependency injection helpers
def get_memory_manager() -> MemoryManager:
    """Get memory manager instance."""
    return app_state.memory_manager


def get_query_engine() -> IntelligentQueryEngine:
    """Get query engine instance."""
    return app_state.query_engine


def get_action_engine() -> ThoughtActionEngine:
    """Get action engine instance."""
    return app_state.action_engine


def get_sync_manager() -> SyncManager:
    """Get sync manager instance."""
    return app_state.sync_manager


def get_config() -> Config:
    """Get configuration instance."""
    return app_state.config


def set_app_state(verbose: bool = False, config_dir: Optional[Path] = None):
    """Initialize app state with parameters."""
    app_state.initialize(verbose=verbose, config_dir=config_dir)


# ============================================================================
# Simple Commands (Phase 1)
# ============================================================================

def version_callback(value: bool):
    if value:
        console.print(f"mem8 version {__version__}")
        raise typer.Exit()


@typer_app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-V", 
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    )
):
    """Memory management CLI for team collaboration."""
    pass


@typer_app.command()
def status(
    detailed: Annotated[bool, typer.Option("--detailed", help="Show detailed status information")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Show mem8 workspace status."""
    set_app_state(verbose=verbose)
    state = get_state()
    memory_manager = state.memory_manager
    
    console.print("[bold blue]mem8 Workspace Status[/bold blue]")
    
    try:
        status_info = memory_manager.get_status(detailed=detailed)
        
        # Check Claude Code integration
        claude_analysis = _analyze_claude_template(Path.cwd())
        has_claude = Path('.claude').exists()
        
        # Basic status table
        from rich.table import Table
        table = Table()
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")
        
        # Add Claude Code status first if it exists
        if has_claude:
            claude_status = f"✅ Active ({len(claude_analysis['existing_commands'])} cmds, {len(claude_analysis['existing_agents'])} agents)"
            table.add_row(
                "🤖 Claude Code",
                claude_status,
                ".claude/"
            )
        
        for component, info in status_info['components'].items():
            status_icon = "✅" if info['exists'] else "❌"
            table.add_row(
                component.title().replace('_', ' '),
                f"{status_icon} {'Ready' if info['exists'] else 'Missing'}",
                str(info['path'])
            )
        
        console.print(table)
        
        # Show thought counts if detailed
        if detailed:
            if 'thought_counts' in status_info:
                counts = status_info['thought_counts']
                console.print("\n[bold blue]Thought Statistics:[/bold blue]")
                
                count_table = Table()
                count_table.add_column("Type", style="cyan")
                count_table.add_column("Count", style="yellow")
                
                for thought_type, count in counts.items():
                    count_table.add_row(thought_type.title(), str(count))
                
                console.print(count_table)
            
            # Show Claude Code details if present
            if has_claude and (claude_analysis['existing_commands'] or claude_analysis['existing_agents']):
                console.print("\n[bold blue]Claude Code Components:[/bold blue]")
                if claude_analysis['existing_commands']:
                    cmd_preview = ', '.join(claude_analysis['existing_commands'][:6])
                    if len(claude_analysis['existing_commands']) > 6:
                        cmd_preview += f" (+{len(claude_analysis['existing_commands']) - 6} more)"
                    console.print(f"  📝 Commands: {cmd_preview}")
                if claude_analysis['existing_agents']:
                    agent_preview = ', '.join(claude_analysis['existing_agents'][:4])
                    if len(claude_analysis['existing_agents']) > 4:
                        agent_preview += f" (+{len(claude_analysis['existing_agents']) - 4} more)"
                    console.print(f"  🤖 Agents: {agent_preview}")
        
        # Show any issues
        if 'issues' in status_info and status_info['issues']:
            console.print("\n⚠️  [bold yellow]Issues:[/bold yellow]")
            for issue in status_info['issues']:
                console.print(f"  • {issue}")
                
    except Exception as e:
        console.print(f"❌ [bold red]Error checking status: {e}[/bold red]")
        if verbose:
            console.print_exception()


@typer_app.command()
def doctor(
    auto_fix: Annotated[bool, typer.Option("--auto-fix", help="Attempt to automatically fix issues")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Diagnose and fix mem8 workspace issues."""
    set_app_state(verbose=verbose)
    state = get_state()
    memory_manager = state.memory_manager
    
    console.print("[bold blue]Running mem8 diagnostics...[/bold blue]")
    
    try:
        diagnosis = memory_manager.diagnose_workspace(auto_fix=auto_fix)
        
        # Show issues
        if diagnosis['issues']:
            console.print("\n⚠️  [bold yellow]Issues found:[/bold yellow]")
            for issue in diagnosis['issues']:
                severity_icon = "❌" if issue['severity'] == 'error' else "⚠️"
                console.print(f"  {severity_icon} {issue['description']}")
                if auto_fix and issue.get('fixed'):
                    console.print(f"    ✅ [green]Fixed automatically[/green]")
        
        # Show fixes applied
        if auto_fix and diagnosis['fixes_applied']:
            console.print("\n✅ [bold green]Fixes applied:[/bold green]")
            for fix in diagnosis['fixes_applied']:
                console.print(f"  • {fix}")
        
        # Show recommendations
        if diagnosis.get('recommendations'):
            console.print("\n💡 [bold blue]Recommendations:[/bold blue]")
            for rec in diagnosis['recommendations']:
                console.print(f"  • {rec}")
        
        # Overall health
        if not diagnosis['issues']:
            console.print("\n✅ [bold green]All checks passed! Your mem8 workspace is healthy.[/bold green]")
        elif auto_fix:
            console.print(f"\n🔧 [blue]Fixed {len(diagnosis['fixes_applied'])} of {len(diagnosis['issues'])} issues.[/blue]")
        else:
            console.print(f"\n⚠️  [yellow]Found {len(diagnosis['issues'])} issues. Run with --auto-fix to attempt repairs.[/yellow]")
            
    except Exception as e:
        console.print(f"❌ [bold red]Error running diagnostics: {e}[/bold red]")
        if verbose:
            console.print_exception()




@typer_app.command()
def serve(
    host: Annotated[str, typer.Option("--host", help="Host to bind to")] = "0.0.0.0",
    port: Annotated[int, typer.Option("--port", help="Port to bind to")] = 8000,
    reload: Annotated[bool, typer.Option("--reload", help="Enable auto-reload for development")] = False,
    workers: Annotated[int, typer.Option("--workers", help="Number of worker processes")] = 1,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Start the mem8 API server (FastAPI backend)."""
    console.print(f"🚀 [bold blue]Starting mem8 API server on {host}:{port}[/bold blue]")
    
    # Check for backend in multiple locations
    import os
    backend_locations = [
        Path(__file__).parent.parent / "backend",  # Development: repo root
        Path("/app/backend"),  # Docker container
        Path.cwd() / "backend"  # Current directory
    ]
    
    backend_path = None
    for loc in backend_locations:
        if loc.exists():
            backend_path = loc
            break
    
    if not backend_path:
        console.print("❌ [red]Backend not found. Please ensure backend directory exists.[/red]")
        console.print("💡 [dim]Run from mem8 repository root or install with backend support.[/dim]")
        return
    
    try:
        import subprocess
        import sys
        
        # Build uvicorn command
        cmd = [
            sys.executable, "-m", "uvicorn",
            "mem8_api.main:app",
            "--host", host,
            "--port", str(port)
        ]
        
        if reload:
            cmd.append("--reload")
        
        if workers > 1 and not reload:
            cmd.extend(["--workers", str(workers)])
        
        if verbose:
            cmd.append("--log-level=debug")
        else:
            cmd.append("--log-level=info")
        
        # Change to backend/src directory for proper module resolution
        backend_src = backend_path / "src"
        
        # Set PYTHONPATH to include src directory
        env = os.environ.copy()
        if "PYTHONPATH" in env:
            # Use os.pathsep for cross-platform compatibility (: on Unix, ; on Windows)
            env["PYTHONPATH"] = f"{backend_src}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = str(backend_src)
        
        console.print(f"📁 [dim]Working directory: {backend_src}[/dim]")
        if verbose:
            console.print(f"⚙️  [dim]Command: {' '.join(cmd)}[/dim]")
            console.print(f"📚 [dim]PYTHONPATH: {env.get('PYTHONPATH')}[/dim]")
        
        # Run the server
        result = subprocess.run(cmd, cwd=str(backend_src), env=env)
        
        if result.returncode != 0:
            console.print("❌ [red]Server exited with error[/red]")
            sys.exit(result.returncode)
            
    except ImportError:
        console.print("❌ [red]FastAPI dependencies not installed.[/red]")
        console.print("💡 Install with: [cyan]pip install 'mem8[api]'[/cyan]")
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Server shutdown requested[/yellow]")
    except Exception as e:
        console.print(f"❌ [bold red]Error starting server: {e}[/bold red]")
        if verbose:
            console.print_exception()


@typer_app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", help="Maximum number of results to return")] = 10,
    content_type: Annotated[ContentType, typer.Option("--type", help="Type of content to search")] = ContentType.ALL,
    method: Annotated[
        SearchMethod,
        typer.Option("--method", help="Search method (semantic is experimental)")
    ] = SearchMethod.FULLTEXT,
    path: Annotated[Optional[str], typer.Option("--path", help="Restrict search to specific path")] = None,
    web: Annotated[bool, typer.Option("--web", help="Open results in web UI")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Search through AI memory and thoughts. Semantic search is experimental."""
    import urllib.parse
    import webbrowser
    from rich.table import Table
    
    set_app_state(verbose=verbose)
    
    # Handle web UI search
    if web and query:
        console.print(f"🌐 [bold blue]Opening search for '{query}' in web UI...[/bold blue]")
        # Open web UI with pre-populated search
        search_url = f'http://localhost:20040?search={urllib.parse.quote(query)}'
        
        from .core.smart_setup import launch_web_ui, show_setup_instructions
        if launch_web_ui():
            webbrowser.open(search_url)
            console.print("✅ [green]Search opened in web browser![/green]")
        else:
            console.print("ℹ️  [yellow]Backend not running. Here's how to start it:[/yellow]")
            instructions = show_setup_instructions()
            console.print(instructions)
        return
    
    # Traditional CLI search
    state = get_state()
    memory_manager = state.memory_manager
    
    search_method = f"[cyan]{method.value}[/cyan]"
    console.print(f"[bold blue]Searching for: '{query}' ({search_method})[/bold blue]")
    
    if method == SearchMethod.SEMANTIC:
        try:
            import sentence_transformers
        except ImportError:
            console.print("[yellow]⚠️  Semantic search requires sentence-transformers library[/yellow]")
            console.print("Install with: [dim]pip install 'mem8[semantic]'[/dim]")
    
    try:
        results = memory_manager.search_content(
            query=query,
            limit=limit,
            content_type=content_type.value,
            search_method=method.value,
            path_filter=path
        )
        
        if results['matches']:
            table = Table(title=f"Search Results ({len(results['matches'])} found)")
            table.add_column("Type", style="cyan", width=10)
            table.add_column("Title", style="green")
            table.add_column("Path", style="dim")
            table.add_column("Score", justify="right", style="yellow", width=8)
            
            for match in results['matches']:
                # Format score
                score_str = f"{match.get('score', 0.0):.2f}" if 'score' in match else "N/A"
                
                # Get title from match
                title = match.get('title', match.get('name', 'Untitled'))
                path_display = str(match.get('path', ''))
                
                # Truncate long paths
                if len(path_display) > 50:
                    path_display = "..." + path_display[-47:]
                
                table.add_row(
                    match.get('type', 'Unknown'),
                    title,
                    path_display,
                    score_str
                )
            
            console.print(table)
            
            # Show summary
            console.print(f"\\n💡 [dim]Found {len(results['matches'])} matches. Use --limit to see more results.[/dim]")
            if web:
                console.print("💡 [dim]Add --web to open results in web UI for better browsing.[/dim]")
                
        else:
            console.print(f"🔍 [yellow]No results found for '{query}' in {content_type.value}[/yellow]")
            console.print("💡 [dim]Try:")
            console.print("   • Different search terms")
            console.print("   • --method semantic for meaning-based search")
            console.print("   • --type all to search all content types")
            
    except Exception as e:
        console.print(f"❌ [bold red]Error during search: {e}[/bold red]")
        if verbose:
            console.print_exception()


# ============================================================================
# Intelligent Completion Functions
# ============================================================================

def complete_thought_queries(incomplete: str):
    """Provide intelligent completion for thought queries."""
    try:
        # Initialize app state for completion
        state = get_state()
        memory_manager = state.memory_manager
        entities = memory_manager.get_thought_entities()
        
        suggestions = set()
        
        # Add common query patterns
        common_patterns = [
            "completed plans", "active research", "draft plans", 
            "personal notes", "shared decisions", "recent thoughts"
        ]
        suggestions.update([p for p in common_patterns if p.startswith(incomplete.lower())])
        
        # Add thought titles and topics
        for entity in entities[:50]:  # Limit for performance
            title = entity.metadata.get('topic', entity.path.stem)
            if incomplete.lower() in title.lower():
                suggestions.add(title)
                
            # Add individual words from titles for partial matching
            words = title.lower().split()
            for word in words:
                if len(word) > 3 and word.startswith(incomplete.lower()):
                    suggestions.add(word)
        
        # Add type-based suggestions
        type_patterns = ["plans", "research", "tickets", "decisions", "prs"]
        suggestions.update([t for t in type_patterns if t.startswith(incomplete.lower())])
        
        return sorted(list(suggestions))[:10]  # Limit to 10 suggestions
    except Exception:
        # Fallback to basic suggestions if anything fails
        return ["plans", "research", "completed", "active", "shared", "personal"]


# ============================================================================
# Complex Commands (Phase 2)
# ============================================================================


def _interactive_prompt_for_init(context: Dict[str, Any]) -> Dict[str, Any]:
    """Interactive prompts for init command configuration."""
    import typer
    from .core.config import Config
    
    # Load saved preferences
    config = Config()
    defaults = config.get_workflow_defaults()
    
    # Show project detection info more clearly
    if context['is_claude_code_project']:
        console.print("\n🤖 [cyan]Claude Code project detected[/cyan]")
    
    console.print(f"\nDetected: {context['project_type']} project")
    
    # Explain the mem8 workflow philosophy
    console.print("\n[cyan]📚 About mem8 Development Workflow[/cyan]")
    console.print("mem8 helps you follow a structured development loop:")
    console.print("  • [bold green]Research[/bold green]: Understand existing code patterns (/research_codebase)")
    console.print("  • [bold blue]Plan[/bold blue]: Design your implementation approach (/create_plan)")  
    console.print("  • [bold yellow]Implement[/bold yellow]: Execute with progress tracking (/implement_plan)")
    console.print("  • [bold magenta]Commit[/bold magenta]: Create atomic, well-documented changes (/commit)")
    console.print("")
    
    # Template selection with enhanced context
    default_template = defaults.get('template', 'full')
    if defaults.get('template') != 'full':
        console.print(f"[dim]💾 Using saved preference: {default_template}[/dim]")
    template_choices = ["full", "claude-config", "thoughts-repo", "none"]
    
    console.print("[cyan]📋 Template Selection[/cyan]")
    console.print("[bold yellow]Template Options:[/bold yellow]")
    console.print("  • [green]full[/green]: Complete workflow commands + shared knowledge repository")
    console.print("  • [blue]claude-config[/blue]: Just workflow commands for Claude Code integration")
    console.print("  • [magenta]thoughts-repo[/magenta]: Just shared knowledge repository structure")
    console.print("  • [red]none[/red]: Skip template installation")
    console.print("")
    
    template = typer.prompt(
        "[bold]Choose template type[/bold]", 
        default=default_template
    )
    while template not in template_choices:
        console.print(f"[red]Invalid choice. Please select from: {', '.join(template_choices)}[/red]")
        template = typer.prompt("Template type", default=default_template)
    
    interactive_config = {"template": template if template != "none" else None}
    
    # Only gather template configuration if we're installing templates
    if template and template != "none":
        console.print("\n[cyan]🔧 Workflow Provider Configuration[/cyan]")
        console.print("Choose how you track and manage development tasks:")
        console.print("")
        console.print("[bold yellow]Provider Options:[/bold yellow]")
        console.print("  • [green]github[/green]: Use GitHub Issues with labels (free, open source)")
        console.print("    - Creates commands for issue management via 'gh' CLI")
        console.print("    - Simple workflow: needs-triage → ready-for-plan → ready-for-dev")
        console.print("  • [blue]linear[/blue]: Use Linear for project management (requires account)")
        console.print("  • [red]none[/red]: No issue tracking integration")
        console.print("")
        
        # Workflow provider selection
        workflow_choices = ["github", "linear", "none"]
        default_workflow = defaults.get('workflow_provider', 'github')
        if defaults.get('workflow_provider') and defaults.get('workflow_provider') != 'github':
            console.print(f"[dim]💾 Using saved preference: {default_workflow}[/dim]")
        workflow_provider = typer.prompt(
            "[bold]Choose workflow provider[/bold]",
            default=default_workflow
        )
        while workflow_provider not in workflow_choices:
            console.print(f"[red]Invalid choice. Please select from: {', '.join(workflow_choices)}[/red]")
            workflow_provider = typer.prompt("Workflow provider (GitHub is free and open source)", default="github")
        interactive_config["workflow_provider"] = workflow_provider
        
        # Workflow automation level
        if workflow_provider != "none":
            console.print("[cyan]⚙️  Workflow Automation Level[/cyan]")
            console.print("Configure workflow helper commands:")
            console.print("")
            console.print("[bold yellow]Automation Options:[/bold yellow]")
            console.print("  • [green]standard[/green]: Include workflow automation commands")
            console.print("    - Commands for issue management and workflow progression")
            console.print("    - Integration with mem8 worktree and GitHub workflows")
            console.print("  • [red]none[/red]: No workflow automation commands")
            console.print("    - Just core research/plan/implement/commit commands")
            console.print("")
            console.print("[dim]Note: 'advanced' level planned for future features[/dim]")
            console.print("")
            
            automation_choices = ["standard", "none"]  # Remove 'advanced' until implemented
            default_automation = defaults.get('automation_level', 'standard')
            if defaults.get('automation_level') and defaults.get('automation_level') != 'standard':
                console.print(f"[dim]💾 Using saved preference: {default_automation}[/dim]")
            workflow_automation = typer.prompt(
                "[bold]Choose automation level[/bold]",
                default=default_automation
            )
            while workflow_automation not in automation_choices:
                console.print(f"[red]Invalid choice. Please select from: {', '.join(automation_choices)}[/red]")
                workflow_automation = typer.prompt("[bold]Choose automation level[/bold]", default="standard")
            interactive_config["workflow_automation"] = workflow_automation
        
        # GitHub-specific configuration
        if workflow_provider == "github":
            console.print("[cyan]🐙 GitHub Repository Configuration[/cyan]")
            console.print("Configure GitHub integration for issue management and workflows.")
            console.print("")
            
            # Try to auto-detect GitHub repo info using gh CLI, or use saved defaults
            github_org = defaults.get('github_org') or "your-org"
            github_repo = defaults.get('github_repo') or "your-repo" 
            
            import shutil
            import subprocess
            import json
            
            if shutil.which("gh"):
                try:
                    result = subprocess.run(
                        ["gh", "repo", "view", "--json", "owner,name"], 
                        capture_output=True, 
                        text=True, 
                        timeout=5
                    )
                    if result.returncode == 0:
                        repo_data = json.loads(result.stdout)
                        github_org = repo_data["owner"]["login"]
                        github_repo = repo_data["name"]
                        console.print(f"[green]✓ Auto-detected from gh CLI: {github_org}/{github_repo}[/green]")
                        console.print("")
                    else:
                        console.print("[yellow]⚠️  gh CLI available but no repository detected in current directory[/yellow]")
                        console.print("")
                except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, FileNotFoundError):
                    console.print("[yellow]⚠️  Could not auto-detect repository info from gh CLI[/yellow]")
                    console.print("")
            else:
                console.print("[yellow]💡 Tip: Install 'gh' CLI for auto-detection of GitHub repositories[/yellow]")
                console.print("")
            
            github_org = typer.prompt("GitHub username (for personal repos, use your username; for org repos, use organization name)", default=github_org)
            github_repo = typer.prompt("GitHub repository name", default=github_repo)
            interactive_config.update({
                "github_org": github_org,
                "github_repo": github_repo
            })
    
    # Repository selection - simplified
    if context.get('repos_from_parent'):
        console.print(f"\n📁 [green]Found {context['repos_from_parent']} repositories in parent directory[/green]")
        include_repos = typer.confirm("Include discovered repositories?", default=False)
        interactive_config["include_repos"] = include_repos
    else:
        interactive_config["include_repos"] = False
    
    # Shared directory with intelligent default
    default_shared = str(context.get('shared_location', Path.home() / "mem8-shared"))
    shared_dir = typer.prompt(
        "Shared directory path",
        default=default_shared
    )
    interactive_config["shared_dir"] = Path(shared_dir)
    
    # Remove web UI launch question - per feedback
    interactive_config["web"] = False
    
    # Save workflow preferences for future use
    if template and template != "none":
        config.save_workflow_preferences(
            template=template,
            workflow_provider=interactive_config.get('workflow_provider', 'github'),
            automation_level=interactive_config.get('workflow_automation', 'standard'),
            github_org=interactive_config.get('github_org'),
            github_repo=interactive_config.get('github_repo')
        )
        console.print("\n[dim]💾 Saved preferences for future init commands[/dim]")
    
    return interactive_config


def _execute_action(action: str, results: list, force: bool, verbose: bool):
    """Execute action on found thoughts."""
    if not force and action in ['delete', 'archive']:
        import typer
        confirm = typer.confirm(f"Are you sure you want to {action} {len(results)} thoughts?")
        if not confirm:
            console.print("❌ [yellow]Action cancelled[/yellow]")
            return
    
    # Get action engine for execution  
    state = get_state()
    action_engine = state.action_engine
    
    try:
        if action == 'show':
            for entity in results:
                console.print(f"📄 [bold]{entity.path}[/bold]")
                content = entity.path.read_text(encoding='utf-8')
                console.print(content[:500] + "..." if len(content) > 500 else content)
                console.print()
        elif action == 'delete':
            # Use the bulk delete method
            result = action_engine.delete_thoughts(results, dry_run=False)
            for success_path in result['success']:
                console.print(f"🗑️  [red]Deleted: {Path(success_path).name}[/red]")
            for error in result['errors']:
                console.print(f"❌ [red]Error deleting: {error}[/red]")
        elif action == 'archive':
            # For now, just show that archive isn't fully implemented
            console.print(f"❌ [yellow]Archive action not yet fully implemented[/yellow]")
        elif action == 'promote':
            # For now, just show that promote isn't fully implemented  
            console.print(f"❌ [yellow]Promote action not yet fully implemented[/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Error executing {action}: {e}[/red]")
        if verbose:
            console.print_exception()


def _preview_action(action: str, results: list):
    """Preview what action would do without executing."""
    from rich.table import Table
    
    table = Table(title=f"Would {action} {len(results)} thoughts (dry run)")
    table.add_column("Action", style="cyan", width=10)
    table.add_column("Type", style="blue", width=10)
    table.add_column("Path", style="dim")
    
    for entity in results:
        # Format relative path for display
        try:
            # If path is not relative to current directory, use absolute path or just filename
            rel_path = entity.path.relative_to(Path.cwd())
        except ValueError:
            # If path is not relative to current directory, use absolute path or just filename
            rel_path = entity.path.name
        table.add_row(action.title(), entity.type, str(rel_path))
        
    console.print(table)
    console.print(f"[dim]Run without --dry-run to execute[/dim]")


# ============================================================================
# Find Subcommands - New Structure
# ============================================================================

# Create find subcommand app
find_app = typer.Typer(name="find", help="Find thoughts by category and keywords")
typer_app.add_typer(find_app, name="find")

def _find_thoughts_new(
    filter_type: str = "all",
    filter_value: str = None,
    keywords: Optional[str] = None,
    limit: int = 20,
    action: Optional[ActionType] = None,
    dry_run: bool = False,
    force: bool = False,
    verbose: bool = False
):
    """Core find logic used by all subcommands."""
    from rich.table import Table
    from pathlib import Path
    import re
    
    set_app_state(verbose=verbose)
    state = get_state()
    discovery = state.memory_manager.thought_discovery
    
    # Get filtered thoughts using existing methods
    if filter_type == "type":
        results = discovery.find_by_type(filter_value)
    elif filter_type == "scope":
        results = discovery.find_by_scope(filter_value)
    elif filter_type == "status":
        results = discovery.find_by_status(filter_value)
    else:
        results = discovery.discover_all_thoughts()
    
    # Apply keyword filter if provided
    if keywords and keywords.strip():
        keyword_results = []
        # Split keywords by spaces, treat each as regex pattern
        patterns = [re.compile(k.strip(), re.IGNORECASE) for k in keywords.split() if k.strip()]
        
        for entity in results:
            # Search in content, title, tags
            searchable_text = (
                entity.content + ' ' + 
                str(entity.metadata.get('topic', '')) + ' ' +
                ' '.join(entity.metadata.get('tags', []))
            )
            
            # Match if ANY pattern matches (OR logic)
            if any(pattern.search(searchable_text) for pattern in patterns):
                keyword_results.append(entity)
        
        results = keyword_results
    
    # Limit results
    results = results[:limit]
    
    if not results:
        console.print("[yellow]❌ No thoughts found[/yellow]")
        return
    
    # Show what we're finding
    search_desc = filter_value or filter_type
    if keywords:
        search_desc += f" matching '{keywords}'"
    console.print(f"[bold blue]🔍 Finding: {search_desc}[/bold blue]")
    
    if action:
        action_color = "yellow" if dry_run else "red" if action == ActionType.DELETE else "cyan"
        dry_run_text = " (dry run)" if dry_run else ""
        console.print(f"[bold {action_color}]Action: {action.value}{dry_run_text}[/bold {action_color}]")
    
    # Display results table
    table = Table(title=f"Found {len(results)} thoughts")
    table.add_column("Type", style="cyan", width=10)
    table.add_column("Title", style="green")
    table.add_column("Status", style="yellow", width=12)
    table.add_column("Scope", style="blue", width=10)
    table.add_column("Path", style="dim")
    
    for entity in results:
        # Extract title from metadata or content
        title = entity.metadata.get('topic', entity.path.stem)
        if len(title) > 40:
            title = title[:37] + "..."
        
        # Format path relative to workspace
        try:
            rel_path = entity.path.relative_to(Path.cwd())
        except ValueError:
            rel_path = entity.path
        
        table.add_row(
            entity.type.title(),
            title,
            entity.lifecycle_state or "Unknown",
            entity.scope or "Unknown",
            str(rel_path)
        )
    
    console.print(table)
    
    # Execute action if specified
    if action and not dry_run:
        _execute_action(action.value, results, force, verbose)
    elif action and dry_run:
        _preview_action(action.value, results)

@find_app.command("all")
def find_all_new(
    keywords: Annotated[Optional[str], typer.Argument(
        help="Keywords to search for (space-separated, supports regex)"
    )] = None,
    limit: Annotated[int, typer.Option(
        "--limit", help="Maximum results to return"
    )] = 20,
    action: Annotated[Optional[ActionType], typer.Option(
        "--action", help="Action to perform on found thoughts"
    )] = None,
    dry_run: Annotated[bool, typer.Option(
        "--dry-run", help="Show what would be done without executing"
    )] = False,
    force: Annotated[bool, typer.Option(
        "--force", help="Skip confirmation prompts for destructive actions"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Find all thoughts, optionally filtered by keywords."""
    _find_thoughts_new("all", None, keywords, limit, action, dry_run, force, verbose)

@find_app.command("plans")
def find_plans_new(
    keywords: Annotated[Optional[str], typer.Argument(
        help="Keywords to search for (space-separated, supports regex)"
    )] = None,
    limit: Annotated[int, typer.Option(
        "--limit", help="Maximum results to return"
    )] = 20,
    action: Annotated[Optional[ActionType], typer.Option(
        "--action", help="Action to perform on found thoughts"
    )] = None,
    dry_run: Annotated[bool, typer.Option(
        "--dry-run", help="Show what would be done without executing"
    )] = False,
    force: Annotated[bool, typer.Option(
        "--force", help="Skip confirmation prompts for destructive actions"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Find plan documents, optionally filtered by keywords."""
    _find_thoughts_new("type", "plan", keywords, limit, action, dry_run, force, verbose)

@find_app.command("research")
def find_research_new(
    keywords: Annotated[Optional[str], typer.Argument(
        help="Keywords to search for (space-separated, supports regex)"
    )] = None,
    limit: Annotated[int, typer.Option(
        "--limit", help="Maximum results to return"
    )] = 20,
    action: Annotated[Optional[ActionType], typer.Option(
        "--action", help="Action to perform on found thoughts"
    )] = None,
    dry_run: Annotated[bool, typer.Option(
        "--dry-run", help="Show what would be done without executing"
    )] = False,
    force: Annotated[bool, typer.Option(
        "--force", help="Skip confirmation prompts for destructive actions"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Find research documents, optionally filtered by keywords."""
    _find_thoughts_new("type", "research", keywords, limit, action, dry_run, force, verbose)

@find_app.command("shared")
def find_shared_new(
    keywords: Annotated[Optional[str], typer.Argument(
        help="Keywords to search for (space-separated, supports regex)"
    )] = None,
    limit: Annotated[int, typer.Option(
        "--limit", help="Maximum results to return"
    )] = 20,
    action: Annotated[Optional[ActionType], typer.Option(
        "--action", help="Action to perform on found thoughts"
    )] = None,
    dry_run: Annotated[bool, typer.Option(
        "--dry-run", help="Show what would be done without executing"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Find shared thoughts, optionally filtered by keywords."""
    _find_thoughts_new("scope", "shared", keywords, limit, action, dry_run, verbose)

@find_app.command("completed")
def find_completed_new(
    keywords: Annotated[Optional[str], typer.Argument(
        help="Keywords to search for (space-separated, supports regex)"
    )] = None,
    limit: Annotated[int, typer.Option(
        "--limit", help="Maximum results to return"
    )] = 20,
    action: Annotated[Optional[ActionType], typer.Option(
        "--action", help="Action to perform on found thoughts"
    )] = None,
    dry_run: Annotated[bool, typer.Option(
        "--dry-run", help="Show what would be done without executing"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Find completed thoughts, optionally filtered by keywords."""
    _find_thoughts_new("status", "completed", keywords, limit, action, dry_run, verbose)


# ============================================================================
# Remaining Commands (Phase 3)
# ============================================================================

def _validate_init_workspace_location(force: bool) -> Path:
    """Validate workspace location for init command only."""
    from .core.utils import get_git_info
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
    
    # If not in a git repository, warn user about non-standard location
    if force:
        typer.secho(f"🔧 Force mode: Using current directory {current_dir}", fg=typer.colors.CYAN)
        return current_dir
    
    typer.secho("⚠️  Warning: Creating .claude directory outside git repository", fg=typer.colors.YELLOW)
    typer.secho(f"Current directory: {current_dir}", fg=typer.colors.WHITE)
    typer.secho("This directory is not part of a git repository.", fg=typer.colors.YELLOW)
    typer.echo()
    typer.secho("Consider running this command from a git repository root.", fg=typer.colors.BLUE)
    typer.echo()
    
    if not typer.confirm("Continue with current directory anyway?", default=False):
        typer.secho("Cancelled. Please run from an appropriate project root.", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    return current_dir

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
        "--force", help="Skip all confirmations, overwrite existing directories, use defaults"
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
    
    console.print("🚀 [bold blue]Welcome to mem8 setup![/bold blue]")
    
    # INIT-SPECIFIC workspace validation - check git repository before setup
    validated_workspace_dir = _validate_init_workspace_location(force)
    
    try:
        # 1. Auto-detect project context
        if verbose:
            console.print("🔍 [dim]Detecting project configuration...[/dim]")
        context = detect_project_context()
        
        if verbose:
            console.print(f"[dim]Detected: {context['project_type']} project, "
                        f"{len(context['git_repos'])} repositories found[/dim]")
        
        # 2. Interactive mode: gather user preferences
        interactive_config = {}
        if interactive and not force:  # Skip interactive prompts if force flag is used
            interactive_config = _interactive_prompt_for_init(context)
            
            # Override parameters with interactive values where not explicitly set
            template = template or interactive_config.get('template')
            shared_dir = shared_dir or interactive_config.get('shared_dir') 
            web = web or interactive_config.get('web', False)
            repos = repos or interactive_config.get('repos')
        elif force:
            # With force flag, use sensible defaults
            template = template or "full"
            console.print("[dim]Using --force mode with default settings[/dim]")
        
        # 3. Generate smart configuration with interactive overrides
        context['interactive_config'] = interactive_config
        config = generate_smart_config(context, repos)
        if interactive_config:
            config.update(interactive_config)
        
        # 3. Auto-detect if templates should be installed
        should_install_templates = False
        template_type = template  # Use explicit template if provided
        
        if template and template != "none":
            # User explicitly requested templates
            should_install_templates = True
        elif template == "none":
            # User explicitly doesn't want templates
            should_install_templates = False
        elif context['is_claude_code_project'] and not template:
            # Auto-detect Claude Code projects need templates
            should_install_templates = True
            template_type = "claude-config"  # Default for Claude projects
        
        # 3. Check for existing setup and conflicts
        existing_thoughts = Path('thoughts').exists()
        existing_claude = Path('.claude').exists()
        needs_confirmation = False
        issues = []
        
        if existing_thoughts and not force:
            issues.append("thoughts/ directory already exists")
            needs_confirmation = True
        
        if existing_claude and should_install_templates and "claude" in (template_type or "") and not force:
            issues.append(".claude/ directory already exists")
            needs_confirmation = True
        
        # Only show repository info in verbose mode or if explicitly requested
        if verbose and config.get('repositories'):
            console.print(f"📁 [dim]Including {len(config['repositories'])} repositories[/dim]")
        
        if shared_dir:
            config['shared_location'] = shared_dir
        
        # 4. Handle confirmations if needed
        if needs_confirmation and not force:
            console.print("\n⚠️  [yellow]Issues detected:[/yellow]")
            for issue in issues:
                console.print(f"  • {issue}")
            
            import typer
            proceed = typer.confirm("Continue with setup?")
            if not proceed:
                console.print("❌ [yellow]Setup cancelled[/yellow]")
                return
        
        # 5. Create directory structure
        console.print("📂 [dim]Creating directory structure...[/dim]")
        setup_result = setup_minimal_structure(config)
        
        # 6. Install templates if needed
        if should_install_templates and template_type != "none":
            template_name = template_type or "full"
            console.print(f"\n📦 [cyan]Installing '{template_name}' template...[/cyan]")
            _install_templates(template_name, force, verbose, interactive_config)
        
        if setup_result['errors']:
            console.print("❌ [red]Errors during setup:[/red]")
            for error in setup_result['errors']:
                console.print(f"  • {error}")
            return
        
        # Show what was created
        if setup_result['created']:
            console.print("\n✅ [green]Created:[/green]")
            for created in setup_result['created']:
                console.print(f"  • {created}")
        
        if setup_result['linked']:
            console.print("🔗 [blue]Linked:[/blue]")
            for linked in setup_result['linked']:
                console.print(f"  • {linked}")
        
        # Claude.md update removed per feedback - can be handled by frontend if needed
        # Web UI launch removed per feedback - separate command
        
        # 8. Create ~/.mem8 shortcut for easy config access
        from .core.config import Config
        config_manager = Config()
        if config_manager.create_home_shortcut():
            console.print("🔗 [dim]Created ~/.mem8 shortcut for config access[/dim]")
        
        # 9. Show next steps
        console.print("\n💡 [bold blue]Next steps:[/bold blue]")
        console.print("  • Run [cyan]mem8 status[/cyan] to verify your setup")
        console.print("  • Use [cyan]mem8 search \"query\"[/cyan] to find thoughts")
        
    except Exception as e:
        console.print(f"❌ [bold red]Error during setup: {e}[/bold red]")
        if verbose:
            console.print_exception()


def _analyze_claude_template(workspace_dir: Path) -> Dict[str, Any]:
    """Analyze existing Claude integration and what will be installed."""
    analysis = {
        'existing_commands': [],
        'existing_agents': [],
        'new_commands': [],
        'new_agents': [],
        'conflicts': [],
        'total_existing': 0,
        'total_new': 0
    }
    
    # Check existing Claude setup
    claude_dir = workspace_dir / '.claude'
    if claude_dir.exists():
        # Count existing commands
        commands_dir = claude_dir / 'commands'
        if commands_dir.exists():
            analysis['existing_commands'] = [f.stem for f in commands_dir.glob('*.md')]
            
        # Count existing agents
        agents_dir = claude_dir / 'agents'
        if agents_dir.exists():
            analysis['existing_agents'] = [f.stem for f in agents_dir.glob('*.md')]
            
        analysis['total_existing'] = len(analysis['existing_commands']) + len(analysis['existing_agents'])
    
    # List of commands/agents that mem8 templates will install
    # These are based on the claude-dot-md-template
    analysis['template_commands'] = [
        'browse-memories', 'commit', 'create_plan', 'create_worktree', 
        'debug', 'describe_pr', 'founder_mode', 'github_issues',
        'implement_plan', 'local_review', 'repo_setup', 'research_codebase',
        'setup-memory', 'validate_plan', 'workflow_automation'
    ]
    
    analysis['template_agents'] = [
        'codebase-analyzer', 'codebase-locator', 'codebase-pattern-finder',
        'github-workflow-agent', 'thoughts-analyzer', 'thoughts-locator', 
        'web-search-researcher'
    ]
    
    # Determine what's new vs conflicts
    for cmd in analysis['template_commands']:
        if cmd in analysis['existing_commands']:
            analysis['conflicts'].append(f"command: {cmd}")
        else:
            analysis['new_commands'].append(cmd)
            
    for agent in analysis['template_agents']:
        if agent in analysis['existing_agents']:
            analysis['conflicts'].append(f"agent: {agent}")
        else:
            analysis['new_agents'].append(agent)
            
    analysis['total_new'] = len(analysis['new_commands']) + len(analysis['new_agents'])
    
    return analysis

def _install_templates(template_type: str, force: bool, verbose: bool, interactive_config: Dict[str, Any] = None) -> None:
    """Install cookiecutter templates to the workspace."""
    from cookiecutter.main import cookiecutter
    from importlib import resources
    import mem8.templates
    from .core.config import Config
    
    # Resolve template paths
    try:
        template_base = resources.files(mem8.templates)
    except (ImportError, AttributeError):
        # Development fallback
        template_base = Path(__file__).parent.parent
    
    # Map template types to directories
    template_map = {
        "full": ["claude-dot-md-template", "shared-thoughts-template"],
        "claude-config": ["claude-dot-md-template"],
        "thoughts-repo": ["shared-thoughts-template"],
    }
    
    if template_type not in template_map:
        console.print(f"[red]Invalid template: {template_type}[/red]")
        return
    
    # Use current working directory (validation already done at init start)
    workspace_dir = Path.cwd()
    
    # Run cookiecutter for each template
    for template_name in template_map[template_type]:
        template_path = template_base / template_name
        
        # Check if target already exists
        target_dir = ".claude" if "claude" in template_name else "thoughts"
        
        # Special handling for Claude templates - analyze what will be installed
        if "claude" in template_name:
            analysis = _analyze_claude_template(workspace_dir)
            
            if (workspace_dir / target_dir).exists() and not force:
                console.print(f"\n⚠️  [yellow]Existing Claude Code integration detected:[/yellow]")
                console.print(f"  • {len(analysis['existing_commands'])} existing commands")
                console.print(f"  • {len(analysis['existing_agents'])} existing agents")
                
                if analysis['conflicts']:
                    console.print(f"\n🔄 [red]These will be overwritten by mem8:[/red]")
                    for conflict in analysis['conflicts'][:5]:  # Show first 5
                        console.print(f"    • {conflict}")
                    if len(analysis['conflicts']) > 5:
                        console.print(f"    • ... and {len(analysis['conflicts']) - 5} more")
                
                console.print(f"\n🎯 [cyan]mem8 will install:[/cyan]")
                console.print(f"  • {len(analysis['template_commands'])} commands")
                console.print(f"  • {len(analysis['template_agents'])} agents")
                
                import typer
                if not typer.confirm("\nProceed? (mem8 will manage Claude Code components from now on)"):
                    console.print("  ⏭️  Skipping .claude/ installation")
                    continue
        elif (workspace_dir / target_dir).exists() and not force:
            # For non-Claude directories, simple skip
            console.print(f"  ⏭️  Skipping {target_dir}/ - already exists")
            continue
        
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
            
            # Use no_input mode when NOT in interactive mode
            # When interactive_config is None, we're in regular mode, so no_input=True
            # When interactive_config is provided, we already have all values, so no_input=True
            no_input = True
            
            cookiecutter(
                str(template_path),
                no_input=no_input,
                output_dir=str(workspace_dir),
                overwrite_if_exists=force,
                extra_context=extra_context
            )
            
            # Show detailed installation report for Claude templates
            if "claude" in template_name:
                analysis = _analyze_claude_template(workspace_dir)
                console.print(f"\n🤖 [bold cyan]Claude Code Integration Complete![/bold cyan]")
                console.print(f"\n  📝 **{len(analysis['template_commands'])} commands** installed:")
                cmd_list = ', '.join(analysis['template_commands'][:5])
                if len(analysis['template_commands']) > 5:
                    cmd_list += f" (+{len(analysis['template_commands']) - 5} more)"
                console.print(f"     {cmd_list}")
                
                console.print(f"\n  🤖 **{len(analysis['template_agents'])} agents** installed:")
                agent_list = ', '.join(analysis['template_agents'][:4])
                if len(analysis['template_agents']) > 4:
                    agent_list += f" (+{len(analysis['template_agents']) - 4} more)"
                console.print(f"     {agent_list}")
                
                console.print(f"\n  🌐 [dim]mem8 now manages these Claude Code components for:[/dim]")
                console.print(f"     [dim]• Dynamic agentic workflows & knowledge base[/dim]")
                console.print(f"     [dim]• Version-controlled outer-loop automation[/dim]")
                console.print(f"     [dim]• Human-driven subagent orchestration[/dim]")
            elif "thoughts" in template_name:
                console.print(f"  ✅ Installed thoughts/ structure")
        except Exception as e:
            if verbose:
                console.print(f"[yellow]Could not install {template_name}: {e}[/yellow]")


def _check_conflicts(workspace_dir: Path, templates: list[str]) -> list[str]:
    """Check for existing files that would be overwritten."""
    conflicts = []
    
    for template in templates:
        if "claude" in template and (workspace_dir / ".claude").exists():
            conflicts.append(".claude directory")
        if "thoughts" in template and (workspace_dir / "thoughts").exists():
            conflicts.append("thoughts directory")
    
    return conflicts


def _backup_shared_thoughts(workspace_dir: Path) -> Optional[Path]:
    """Backup existing thoughts/shared directory."""
    shared_dir = workspace_dir / "thoughts" / "shared"
    if shared_dir.exists() and any(shared_dir.iterdir()):
        backup_dir = workspace_dir / ".mem8_backup" / "thoughts_shared"
        backup_dir.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copytree(shared_dir, backup_dir, dirs_exist_ok=True)
        console.print(f"[yellow]Backed up thoughts/shared to {backup_dir}[/yellow]")
        return backup_dir
    
    return None


def _restore_shared_thoughts(workspace_dir: Path, backup_dir: Path) -> None:
    """Restore backed up thoughts/shared directory."""
    if backup_dir.exists():
        import shutil
        shared_dir = workspace_dir / "thoughts" / "shared"
        shutil.copytree(backup_dir, shared_dir, dirs_exist_ok=True)
        console.print("[green]Restored thoughts/shared from backup[/green]")
        shutil.rmtree(backup_dir.parent)


@typer_app.command()
def sync(
    direction: Annotated[SyncDirection, typer.Option(
        "--direction", help="Sync direction"
    )] = SyncDirection.BOTH,
    dry_run: Annotated[bool, typer.Option(
        "--dry-run", help="Show what would be synced without making changes"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Synchronize local and shared memory."""
    set_app_state(verbose=verbose)
    state = get_state()
    sync_manager = state.sync_manager
    
    action = "Dry run:" if dry_run else "Syncing"
    console.print(f"[bold blue]{action} memory ({direction.value})...[/bold blue]")
    
    try:
        result = sync_manager.sync_memory(direction=direction.value, dry_run=dry_run)
        
        if result['success']:
            console.print("✅ [green]Sync completed successfully[/green]")
            if 'stats' in result:
                stats = result['stats']
                console.print(f"📊 [dim]Files synced: {stats.get('files_synced', 0)}, "
                            f"Conflicts: {stats.get('conflicts', 0)}[/dim]")
        else:
            console.print("❌ [red]Sync failed[/red]")
            if 'error' in result:
                console.print(f"Error: {result['error']}")
                
    except Exception as e:
        console.print(f"❌ [red]Error during sync: {e}[/red]")
        if verbose:
            console.print_exception()


# ============================================================================
# Command Groups (Team and Deploy)
# ============================================================================

# Create team subapp
team_app = typer.Typer(name="team", help="Experimental team collaboration commands")
typer_app.add_typer(team_app, name="team")

@team_app.command()
def create(
    name: Annotated[str, typer.Option("--name", help="Team name")],
    description: Annotated[Optional[str], typer.Option("--description", help="Team description")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Create a new team (experimental)."""
    set_app_state(verbose=verbose)
    
    console.print(f"[bold blue]Creating team: {name}[/bold blue]")
    if description:
        console.print(f"Description: {description}")
    
    console.print("[yellow]⚠️  Team features require backend API (Phase 2)[/yellow]")
    console.print("For now, teams are managed locally through shared directories.")


@team_app.command()
def list(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """List available teams (experimental)."""
    set_app_state(verbose=verbose)
    
    console.print("[bold blue]Available teams:[/bold blue]")
    console.print("[yellow]⚠️  Team features require backend API (Phase 2)[/yellow]")


@team_app.command()
def join(
    team_name: Annotated[str, typer.Argument(help="Team name to join")],
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Join an existing team (experimental)."""
    set_app_state(verbose=verbose)
    
    console.print(f"[bold blue]Joining team: {team_name}[/bold blue]")
    console.print("[yellow]⚠️  Team features require backend API (Phase 2)[/yellow]")


# Create deploy subapp
deploy_app = typer.Typer(name="deploy", help="Experimental deployment commands")
typer_app.add_typer(deploy_app, name="deploy")

@deploy_app.command()
def kubernetes(
    env: Annotated[DeployEnvironment, typer.Option(
        "--env", help="Deployment environment"
    )] = DeployEnvironment.LOCAL,
    domain: Annotated[Optional[str], typer.Option("--domain", help="Custom domain for deployment")] = None,
    replicas: Annotated[int, typer.Option("--replicas", help="Number of replicas")] = 2,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Deploy to Kubernetes cluster (experimental)."""
    set_app_state(verbose=verbose)
    
    console.print(f"[bold blue]Deploying to Kubernetes ({env.value})...[/bold blue]")
    if domain:
        console.print(f"Domain: {domain}")
    console.print(f"Replicas: {replicas}")
    
    console.print("[yellow]⚠️  Kubernetes deployment requires backend API (Phase 2)[/yellow]")
    console.print("Available after backend API and frontend are implemented.")


@deploy_app.command()
def local(
    port: Annotated[int, typer.Option("--port", help="Port to run on")] = 8000,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False
):
    """Start local development server (experimental)."""
    set_app_state(verbose=verbose)
    
    console.print(f"[bold blue]Starting local server on port {port}...[/bold blue]")
    console.print("[yellow]⚠️  Local server requires backend API (Phase 2)[/yellow]")


# ============================================================================
# Worktree Management Commands
# ============================================================================

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
        "--launch", help="Auto-launch VS Code in worktree"
    )] = False,
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
            # Try to open in VS Code
            import subprocess
            import shutil
            
            if shutil.which("code"):
                console.print(f"🚀 [cyan]Opening worktree in VS Code[/cyan]")
                subprocess.run(["code", str(worktree_path)], shell=False)
            else:
                console.print(f"💡 [dim]Install VS Code to auto-open worktrees[/dim]")
            
    except Exception as e:
        console.print(f"❌ [bold red]Error creating worktree: {e}[/bold red]")
        if verbose:
            console.print_exception()

@worktree_app.command("list")
def worktree_list(
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """List existing worktrees."""
    from .core.worktree import list_worktrees
    from rich.table import Table
    
    set_app_state(verbose=verbose)
    
    try:
        worktrees = list_worktrees()
        
        if not worktrees:
            console.print("[yellow]No worktrees found[/yellow]")
            return
        
        table = Table(title=f"Git Worktrees ({len(worktrees)} found)")
        table.add_column("Path", style="cyan")
        table.add_column("Branch", style="green")
        table.add_column("Commit", style="dim", width=12)
        table.add_column("Status", style="yellow")
        
        for wt in worktrees:
            path = wt.get('path', 'Unknown')
            branch = wt.get('branch', wt.get('commit', 'Detached'))[:20] if wt.get('branch') else 'detached'
            commit = wt.get('commit', 'Unknown')[:12]
            
            if wt.get('bare'):
                status = "bare"
            elif wt.get('detached'):
                status = "detached"
            else:
                status = "active"
            
            table.add_row(path, branch, commit, status)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [bold red]Error listing worktrees: {e}[/bold red]")
        if verbose:
            console.print_exception()

@worktree_app.command("remove")  
def worktree_remove(
    worktree_path: Annotated[Path, typer.Argument(help="Path to worktree to remove")],
    force: Annotated[bool, typer.Option(
        "--force", help="Force removal even with uncommitted changes"
    )] = False,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Remove a worktree."""
    from .core.worktree import remove_worktree
    
    set_app_state(verbose=verbose)
    
    if not force:
        import typer
        confirm = typer.confirm(f"Remove worktree at {worktree_path}?")
        if not confirm:
            console.print("❌ [yellow]Removal cancelled[/yellow]")
            return
    
    try:
        remove_worktree(worktree_path, force)
        console.print(f"✅ [green]Removed worktree: {worktree_path}[/green]")
        
    except Exception as e:
        console.print(f"❌ [bold red]Error removing worktree: {e}[/bold red]")
        if verbose:
            console.print_exception()


# ============================================================================
# Metadata Management Commands  
# ============================================================================

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
    
    set_app_state(verbose=verbose)
    
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
    format: Annotated[str, typer.Option(
        "--format", help="Output format: yaml, json, or frontmatter"
    )] = "frontmatter",
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Generate complete metadata for research documents (replaces hack/spec_metadata.sh)."""
    from .core.metadata import generate_research_metadata, format_frontmatter
    
    set_app_state(verbose=verbose)
    
    try:
        metadata = generate_research_metadata(topic)
        
        if format == "frontmatter":
            output = format_frontmatter(metadata)
        elif format == "yaml":
            import yaml
            output = yaml.dump(metadata, default_flow_style=False)
        elif format == "json":
            import json
            output = json.dumps(metadata, indent=2)
        else:
            output = "\n".join(f"{key}: {value}" for key, value in metadata.items())
        
        if output_file:
            output_file.write_text(output, encoding='utf-8')
            console.print(f"✅ [green]Metadata written to: {output_file}[/green]")
        else:
            console.print(output)
            
    except Exception as e:
        console.print(f"❌ [bold red]Error generating metadata: {e}[/bold red]")
        if verbose:
            console.print_exception()

@metadata_app.command("project")
def metadata_project(
    format: Annotated[str, typer.Option(
        "--format", help="Output format"
    )] = "yaml",
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v", help="Enable verbose output"
    )] = False
):
    """Get project metadata and statistics."""
    from .core.metadata import generate_project_metadata
    
    set_app_state(verbose=verbose)
    
    try:
        metadata = generate_project_metadata()
        
        if format == "yaml":
            import yaml
            console.print(yaml.dump(metadata, default_flow_style=False))
        elif format == "json":
            import json
            console.print(json.dumps(metadata, indent=2))
        else:
            console.print(f"Project Type: {metadata.get('project_type', 'Unknown')}")
            console.print(f"Repository: {metadata['git_metadata']['repository']}")
            console.print(f"Branch: {metadata['git_metadata']['branch']}")
            console.print(f"Commits: {metadata['repository_stats']['total_commits']}")
            console.print(f"Contributors: {metadata['repository_stats']['contributors']}")
                
    except Exception as e:
        console.print(f"❌ [bold red]Error getting project metadata: {e}[/bold red]")
        if verbose:
            console.print_exception()


# ============================================================================
# Shell Completion (Using Typer's built-in system)
# ============================================================================

# Enable Typer's built-in completion
typer_app.add_completion = True
