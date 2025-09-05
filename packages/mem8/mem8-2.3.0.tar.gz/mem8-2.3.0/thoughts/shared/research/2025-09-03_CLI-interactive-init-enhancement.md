---
date: 2025-09-02T19:12:49-05:00
researcher: vaski
git_commit: d50d670e464743f6833852bff3fbcad57a40fcf1
branch: main
repository: ai-mem
topic: "mem8 init --template claude-config interactive mode and missing CLI functionality"
tags: [research, codebase, cli, templates, cookiecutter, interactive, worktree, metadata]
status: complete
last_updated: 2025-09-02
last_updated_by: vaski
---

# Research: mem8 init --template claude-config Interactive Mode and Missing CLI Functionality

**Date**: 2025-09-02T19:12:49-05:00
**Researcher**: vaski
**Git Commit**: d50d670e464743f6833852bff3fbcad57a40fcf1
**Branch**: main
**Repository**: ai-mem

## Research Question
How to enhance the `mem8 init --template claude-config` command with interactive mode for user choice-based configuration (Linear vs GitHub issues) and integrate missing 'hack' command functionality into the mem8 CLI?

## Summary
The mem8 CLI has a solid foundation for interactive enhancement but needs significant additions. The current `init` command uses cookiecutter templates with `no_input=True`, preventing user interaction. Two critical "hack" scripts are missing from the CLI: `hack/create_worktree.sh` and `hack/spec_metadata.sh`. The template system is well-designed with conditional logic already in place, making interactive mode achievable through cookiecutter configuration expansion and CLI parameter gathering.

## Detailed Findings

### Current Template System Architecture

The cookiecutter integration is sophisticated but non-interactive:

- **Template Location**: `mem8/templates/` contains two templates
  - `claude-dot-md-template/` - Claude Code integration (`.claude` directory)
  - `shared-thoughts-template/` - Shared thoughts repository setup
- **Installation Function**: `mem8/cli_typer.py:942-995` handles template installation
- **Current Limitation**: `no_input=True` at line 986 prevents all user interaction

#### Claude Template Configuration (`claude-dot-md-template/cookiecutter.json`)
Available parameters for interactive enhancement:
```json
{
  "include_linear_integration": false,
  "include_ralph_commands": false,
  "include_web_search": true,
  "organization_name": "My Organization",
  "default_tools": "Read, Grep, Glob, LS"
}
```

#### Post-Generation Hooks
Smart conditional file removal system exists:
- `hooks/post_gen_project.py` removes unused files based on boolean parameters
- Linear integration files removed if `include_linear_integration=false`
- Ralph commands removed if `include_ralph_commands=false`

### Missing Hack Commands Analysis

#### 1. `hack/create_worktree.sh`
**Referenced in**: 
- `commands/create_worktree.md:3`
- `commands/ralph_impl.md:25`

**Expected Usage**: `./hack/create_worktree.sh ENG-XXXX BRANCH_NAME`

**Functionality Needed**: 
- Create git worktree in `~/wt/{repo-name}/{ticket-id}` pattern
- Switch to specified branch name
- Launch implementation session with mem8 dashboard

**Replacement CLI Command**: `mem8 worktree create`

#### 2. `hack/spec_metadata.sh`
**Referenced in**: `commands/research_codebase.md:69`

**Functionality Needed**:
- Generate git commit hash, branch info, timestamp
- Create researcher name from mem8 config
- Format metadata for research document frontmatter

**Replacement CLI Command**: `mem8 metadata research`

### CLI Architecture Analysis

Current CLI structure is well-organized but monolithic:

#### Existing Command Structure
- **Core Commands**: status, doctor, dashboard, search, init, sync
- **Subcommand Groups**: find, team, deploy
- **Pattern**: Uses Typer with Rich console formatting
- **State Management**: Global `AppState` with lazy initialization

#### Interactive Patterns Already Exist
- `typer.confirm()` used for destructive operations
- `--force` flags to skip confirmations consistently
- Rich console with consistent color scheme

### Historical Context from Thoughts Directory

#### CLI Architecture Issues
- **Monolithic Structure**: Current 1,166-line `cli_typer.py` violates single responsibility
- **Broken Template Installation**: Typer migration lost cookiecutter functionality that Click CLI had
- **Code Duplication**: Five nearly identical find commands with repeated parameters

#### Template System Problems
- **Templates Are Packaged Correctly**: Both templates exist in wheel at `mem8/templates/`
- **Smart Setup Override**: Current init uses "smart setup" instead of templates
- **Legacy Functionality**: Click CLI had working template installation

#### PostgreSQL Complexity
- **Over-Engineering**: 24+ database files for functionality that's primarily file-based
- **Simplification Opportunity**: Core Claude Code template management doesn't need database

## Code References

- `mem8/cli_typer.py:794-940` - Current init command implementation
- `mem8/cli_typer.py:942-995` - Template installation function
- `mem8/templates/claude-dot-md-template/cookiecutter.json` - Claude template configuration
- `mem8/templates/claude-dot-md-template/hooks/post_gen_project.py` - Conditional file removal
- `mem8/core/smart_setup.py:13-27` - Project context detection
- `mem8/core/utils.py:191-221` - Existing git utilities

## Architecture Insights

### Interactive Mode Implementation Strategy
1. **Parameter Gathering**: Add `--interactive` flag to init command
2. **User Prompts**: Use `typer.prompt()` with smart defaults from context detection
3. **Template Configuration**: Build `extra_context` from user choices instead of hardcoded values
4. **Cookiecutter Integration**: Remove `no_input=True` when interactive mode enabled

### Choice-Based Configuration Options
```python
# Recommended new cookiecutter.json parameters
{
  "issue_tracker": ["linear", "github", "none"],
  "workflow_commands": ["ralph", "standard", "minimal"],
  "research_tools": ["web-search", "local-only", "both"]
}
```

### New CLI Commands Needed
```bash
# Worktree management
mem8 worktree create ENG-1234 feature-branch-name
mem8 worktree list
mem8 worktree remove ENG-1234

# Metadata generation
mem8 metadata git        # Git hash, branch, repo info  
mem8 metadata research   # Complete research document metadata
```

## Historical Context (from thoughts/)

### CLI Refactoring Plans
- `thoughts/shared/plans/cli-architecture-refactoring.md` - Comprehensive modularization plan
- `thoughts/shared/plans/restore-typer-cli-functionality.md` - Fix broken template installation
- `thoughts/shared/plans/postgres-removal-simplification.md` - Simplify to focus on templates

### Previous Research
- `thoughts/shared/research/2025-09-02_CLI-architecture-redundancy-analysis.md` - PostgreSQL scope analysis
- `thoughts/shared/research/2025-09-01_wheel-packaging-templates.md` - Template packaging investigation
- `thoughts/shared/research/humanlayer-mem8-command-mapping.md` - Legacy command migration analysis

## Implementation Recommendations

### Phase 1: Interactive Init Enhancement
1. **Add Interactive Flag**: `mem8 init --interactive` with guided prompts
2. **Expand Template Configuration**: Add choice-based parameters to cookiecutter.json
3. **User Choice Gathering**: Interactive prompts for issue tracker, workflow commands, research tools
4. **Maintain Backward Compatibility**: All existing parameters work unchanged

### Phase 2: Missing Command Integration  
1. **Worktree Command Group**: New `mem8 worktree` subcommand following existing patterns
2. **Metadata Command Group**: New `mem8 metadata` for research document generation
3. **Template Updates**: Replace hack script references with proper CLI commands
4. **Git Utility Enhancement**: Extend existing git functions in `mem8/core/utils.py`

### Phase 3: CLI Architecture Cleanup
1. **Modularize CLI**: Break 1,166-line file into focused modules
2. **Eliminate Duplication**: Consolidate repeated find command patterns
3. **PostgreSQL Removal**: Simplify system to focus on template management

## Open Questions

1. **Interactive UX Flow**: Should interactive mode walk through all options or just key choices?
2. **Template Versioning**: How to handle template updates when users have customized configurations?
3. **GitHub Integration**: What specific GitHub Issues commands need to be created vs Linear equivalents?
4. **Worktree Naming**: Should worktree paths be configurable or follow strict `~/wt/{repo}/{ticket}` convention?

## Next Steps

1. **Implement Interactive Init**: Start with `--interactive` flag and basic prompts
2. **Create Metadata Commands**: Replace `hack/spec_metadata.sh` functionality first (simpler)
3. **Add Worktree Commands**: Implement git worktree management for development workflow
4. **Update Templates**: Modify command files to use new CLI commands instead of hack scripts
5. **Test Integration**: Ensure backward compatibility while adding new functionality