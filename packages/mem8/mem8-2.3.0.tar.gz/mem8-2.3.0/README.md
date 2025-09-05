# mem8 - Claude Code Workspace Manager

A streamlined CLI tool for managing Claude Code customizations and documentation workflows. Create standardized project templates, manage thoughts/research documents, and enhance your Claude Code development experience.

## 🎯 Overview

mem8 is designed to work seamlessly with Claude Code, providing:
- **💻 Rich CLI Interface** - Manage Claude Code customizations and project templates  
- **📝 Thoughts Management** - Organize research, plans, and documentation in markdown
- **🎨 Dashboard** - Optional web interface to browse your workspace and thoughts
- **🏗️ Template System** - Cookiecutter templates for Claude Code configurations

## ✨ Core Features

### 💻 CLI Commands
```bash
mem8 init --template claude-config   # Initialize Claude Code workspace  
mem8 status                          # Check workspace health
mem8 search "query"                 # Search across all thoughts
mem8 serve                           # Start the API server (port 8000)
```

### 📁 Template System
- **claude-dot-md-template** - Generate `.claude/[agents,commands]` configurations
- **shared-thoughts-template** - Create structured thoughts repositories
- **Cookiecutter integration** - Flexible, customizable project generation

### 🔍 Thoughts Organization
```
thoughts/
├── shared/
│   ├── research/      # Research documents
│   ├── plans/         # Implementation plans  
│   ├── prs/          # PR descriptions
│   └── decisions/     # Technical decisions
└── {project}/         # Project-specific thoughts
```

## 🚀 Quick Start

### 1. Install mem8
```bash
# Install with uv (recommended)
uv tool install mem8

# Or install from source
git clone https://github.com/killerapp/mem8.git
cd mem8
uv tool install --editable .
```

### 2. Initialize Your Workspace
```bash
# Create Claude Code configuration
mem8 init --template claude-config

# Create thoughts repository
mem8 init --template thoughts-repo

# Check everything is working
mem8 status
```

### 3. Optional: View Your Workspace
```bash
# Option A: Quick start with npm (development mode)
cd frontend && npm install && npm run dev
# Access at http://localhost:22211

# Option B: Full stack with Docker Compose (includes backend)
docker-compose --env-file .env.dev up -d
# Frontend at http://localhost:22211
# Backend API at http://localhost:8000
```

## 🔄 Development Workflow

mem8 provides a structured inner loop for effective development:

### The Research → Plan → Implement → Commit Cycle

1. **Research** (`/research_codebase`) - Understand existing patterns and architecture
   - Uses parallel sub-agents for comprehensive codebase analysis
   - Creates timestamped research documents with metadata
   - Integrates findings from both code and thoughts repository

2. **Plan** (`/create_plan`) - Design your approach with concrete steps
   - Structured implementation plans with technical details
   - Clear requirements analysis and integration points  
   - Breaks down complex features into actionable tasks

3. **Implement** (`/implement_plan`) - Execute with progress tracking
   - Follows approved plans while adapting to reality
   - Updates progress with todo lists and checkboxes
   - Verification at natural stopping points

4. **Validate** (`/validate_plan`) - Verify implementation completeness
   - Systematic checking against original plan
   - Automated verification (build, tests, linting)
   - Recommendations for missing or incomplete work

5. **Commit** (`/commit`) - Create atomic, well-documented commits
   - Reviews session changes and creates logical groupings
   - Focuses on "why" rather than just "what" changed
   - Maintains clean git history

### Benefits
- **Thorough Understanding**: Research first reduces bugs and technical debt
- **Clear Direction**: Plans provide roadmap before coding begins  
- **Progress Tracking**: Todo lists and validation prevent incomplete work
- **Quality Commits**: Thoughtful commit messages improve team communication

### Getting Started
After running `mem8 init`, these commands are available in Claude Code as `/research_codebase`, `/create_plan`, etc. The workflow works best when following the sequence, but individual commands can be used as needed.

## 📋 Templates

### Claude Code Configuration (`claude-config`)
Generates `.claude/CLAUDE.md` with:
- Project-specific instructions
- Custom agents and commands
- Memory management settings
- Development workflows

**Example Usage:**
```bash
mem8 init --template claude-config
# Creates: .claude/CLAUDE.md, commands/, agents/
```

### Thoughts Repository (`thoughts-repo`)  
Creates structured documentation with:
- Research document templates
- Planning frameworks
- Decision logs
- Shared memory structure

**Example Usage:**
```bash
mem8 init --template thoughts-repo  
# Creates: thoughts/shared/, thoughts/research/, etc.
```

## 🎛️ Configuration

### Basic Setup
```bash
# Initialize in existing project
cd your-project
mem8 init --template claude-config

# Customize the generated .claude/CLAUDE.md
# Add project-specific instructions and workflows
```

### Advanced Configuration
```bash
# Use custom cookiecutter configs
mem8 init --template claude-config --config-file custom-config.yaml

# Link shared thoughts across projects
mem8 sync --link-shared ~/shared-thoughts
```

## 💻 Web Interface (Optional)

The mem8 web interface provides a browser-based viewer for your workspace:

### Features
- Browse research and planning documents
- Search across all markdown files  
- View file contents with syntax highlighting
- Navigate between different thought categories

### Setup Options

#### Quick Start (Development)
```bash
# Install dependencies and start the web interface
cd frontend && npm install && npm run dev
# Access at http://localhost:22211
```

#### Docker Compose (Full Stack)
```bash
# Start all services (frontend, backend, database)
docker-compose up -d

# Services available at:
# - Frontend: http://localhost:22211
# - Backend API: http://localhost:8000
# - PostgreSQL: localhost:5432
```

**Note:** The web interface is a simple file viewer - no authentication or database required.

## 🔧 Project Structure

```
your-project/
├── .claude/
│   ├── CLAUDE.md          # Main Claude Code configuration
│   ├── commands/          # Custom commands  
│   └── agents/           # Custom agent definitions
├── thoughts/
│   ├── shared/           # Shared documentation
│   ├── research/         # Research documents
│   └── plans/           # Implementation plans
└── mem8-config.yaml     # mem8 workspace settings
```

## 🛠️ Advanced Usage

### Search Functionality
```bash
# Full-text search
mem8 search "authentication"

# Search in specific directories
mem8 search "API" --path thoughts/shared/research

# Search with filters
mem8 search "bug" --tags "urgent" --type "plans"
```

### Sync and Sharing
```bash
# Sync with shared directory
mem8 sync

# Create symlinks to shared thoughts
mem8 sync --link ~/team-shared-thoughts

# Check sync status
mem8 status --verbose
```

### Custom Templates
```bash
# Create new template from existing project
mem8 template create my-template --from .

# Use custom template
mem8 init --template ./my-custom-template
```

## 📚 Integration with Claude Code

### Custom Agents
Place agent definitions in `.claude/agents/`:
```markdown
# .claude/agents/researcher.md
You are a research assistant focused on technical documentation...
```

### Custom Commands  
Add commands in `.claude/commands/`:
```bash
# .claude/commands/analyze.sh
#!/bin/bash
echo "Analyzing codebase structure..."
```

### Workspace Memory
Configure in `.claude/CLAUDE.md`:
```markdown
# Project Context
- Use `thoughts/research/` for background research
- Store implementation plans in `thoughts/plans/`
- Document decisions in `thoughts/decisions/`
```

## 🚀 Production Deployment

### Quick Start with Docker
```bash
# Build and start all services
docker-compose up -d

# Test the deployment (Windows PowerShell)
./test-docker.ps1

# Test the deployment (Linux/Mac)
./test-docker.sh

# Services will be available at:
# - Frontend: http://localhost:22211
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### API Server (Standalone)
The `mem8 serve` command provides a clean, production-ready API server:

```bash
# Development mode with auto-reload
mem8 serve --reload

# Production mode with multiple workers
mem8 serve --workers 4 --port 8000

# With custom host/port
mem8 serve --host 0.0.0.0 --port 8080 --workers 2
```

### Docker Deployment Options

#### Production Stack (docker-compose.prod.yml)
```bash
# Start full production stack
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend  # API logs
docker-compose -f docker-compose.prod.yml logs -f frontend # Frontend logs

# Stop services
docker-compose -f docker-compose.prod.yml down

# Clean up (removes volumes)
docker-compose -f docker-compose.prod.yml down -v
```

#### Development Stack (with Hot Reloading)
```bash
# Start development environment with hot-reload enabled
docker-compose --env-file .env.dev up -d --build

# Frontend and backend will auto-reload on code changes
# View logs: docker-compose --env-file .env.dev logs -f
```

### Architecture
The production deployment uses:
- **mem8 serve**: FastAPI backend with unified CLI entry point
- **PostgreSQL**: Primary database for storing thoughts and metadata
- **Redis**: Cache layer and websocket support
- **Next.js**: Frontend application on port 22211

## 🧰 Requirements

- **Python 3.8+** - For mem8 CLI
- **uv** - Package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Node.js 18+** - For optional web interface
- **Git** - For sync functionality

## 🔄 Workflow Examples

### Research & Planning
```bash
# Start new research
mem8 init --template thoughts-repo
cd thoughts/research
# Create research-topic.md

# Plan implementation  
cd ../plans
# Create implementation-plan.md

# Search for related work
mem8 search "similar feature" --type research
```

### Claude Code Customization
```bash
# Set up Claude Code for new project
cd my-new-project  
mem8 init --template claude-config

# Customize .claude/CLAUDE.md with:
# - Project-specific context
# - Custom agent definitions  
# - Development workflows

# Test configuration
claude-code --help
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Focus areas:
1. **New Templates** - Create templates for different project types
2. **CLI Enhancements** - Improve search and sync functionality
3. **Web Interface** - Enhance the thoughts file viewer
4. **Documentation** - Improve setup and usage guides

---
*Designed for developers using Claude Code to enhance AI-assisted development workflows.*