---
date: 2025-09-01T21:04:50
researcher: killerapp
git_commit: 2052e442b96f6931af0e368ce2716830dd80bd5a
branch: codex/mark-semantic-search-as-experimental
repository: mem8
topic: "Dependency footprint analysis - reviewing heavy ML dependencies for simple text tool"
tags: [research, codebase, dependencies, semantic-search, pytorch, performance]
status: complete
last_updated: 2025-09-01
last_updated_by: killerapp
---

# Research: Dependency Footprint Analysis - Heavy ML Dependencies for Simple Text Tool

**Date**: 2025-09-01T21:04:50
**Researcher**: killerapp  
**Git Commit**: 2052e442b96f6931af0e368ce2716830dd80bd5a
**Branch**: codex/mark-semantic-search-as-experimental
**Repository**: mem8

## Research Question
Review the dependencies it seems like we have torch and cuda and other stuff in there for a simple tool that does code text file stuff - I don't need the find to be so good semantically that it needs embeddings and other such tech, please review the footprint of this feature and other features that are adding to the large list of deps (see uv for listing commands) and sizing details

## Summary
The mem8 tool has accumulated extremely heavy machine learning dependencies (100+ packages including PyTorch, CUDA support, transformers) for what should be a simple text file management tool. **The culprit is `sentence-transformers>=2.2.0`** which pulls in the entire PyTorch ecosystem. However, the semantic search feature is already marked as **experimental** throughout the codebase and is completely optional - the tool functions perfectly without it using lightweight full-text search as the default.

## Key Findings

### 🚨 Heavy Dependency Impact
- **Total packages**: 100 packages (vs ~20-30 for basic text tools)
- **Primary culprit**: `sentence-transformers>=2.2.0` (pyproject.toml:36)
- **Heavy dependencies pulled in**:
  - `torch v2.8.0` - Full PyTorch framework (~800MB)
  - `transformers v4.56.0` - Hugging Face transformers library
  - `scikit-learn v1.7.1` with `numpy v2.3.2` and `scipy v1.16.1`
  - `huggingface-hub v0.34.4` - Model hub integration
  - `pillow v11.3.0` - Image processing (unnecessary for text)

### ✅ Semantic Search is Already Optional
Analysis shows the feature is properly implemented as optional:
- **Experimental status**: Marked as experimental throughout codebase
- **Default behavior**: All search operations default to lightweight fulltext search
- **Graceful fallback**: Built-in `ImportError` handling falls back to text search
- **Lazy loading**: ML dependencies only loaded when explicitly requested
- **User opt-in required**: Must use `--method semantic` or select in UI

## Detailed Findings

### Implementation Analysis

**CLI Implementation** (`mem8/cli_typer.py:347-445`):
- Default: `SearchMethod.FULLTEXT` (line 355)  
- Warning: "⚠️ Semantic search requires sentence-transformers library" (line 391)
- Explicit opt-in: `mem8 search "query" --method semantic`

**Core Memory Search** (`mem8/core/memory.py:415-575`):
- Default parameter: `search_method: str = 'fulltext'` (line 415)
- Conditional usage: Only calls semantic methods when `search_method == 'semantic'`
- Built-in fallback: ImportError handling (lines 543-545, 571-573)

**Backend API** (`backend/src/aimem_api/services/search.py:26-105`):
- Graceful fallback: Catches `ImportError` and falls back to text search (lines 42-54)
- Lazy loading: Model only initialized when semantic search requested (lines 56-57)
- Performance limits: Content truncated to 2000 characters (line 82)

### Timeline Analysis
Recent commits show when this was added:
- `1e3fa2b` - "feat: add experimental semantic search" 
- `420ff33` - "Implement Phase 1 CLI foundation with enhanced init command and semantic search"

The feature was recently added and consistently marked as experimental.

## Code References
- `pyproject.toml:36` - Heavy dependency: `"sentence-transformers>=2.2.0"`
- `mem8/core/memory.py:427` - Semantic search call in main search function
- `mem8/core/memory.py:504-546` - `_semantic_search_directory()` implementation
- `mem8/cli_typer.py:354` - Search method option with experimental note
- `backend/src/aimem_api/services/search.py:43` - Backend semantic search service
- `backend/src/aimem_api/schemas/search.py:12` - SearchType enum with experimental note

## Architecture Insights

### Current Dependency Strategy
- **Hard dependencies**: All dependencies in main `dependencies` list
- **No optional extras**: No use of `[project.optional-dependencies]` pattern
- **Graceful degradation**: Runtime detection with fallbacks

### Existing Fallback Patterns
The codebase already implements proper optional dependency patterns:
- **Lazy imports**: Dependencies imported inside methods, not at module level
- **Exception handling**: `try/except ImportError` with fallbacks
- **Default to lightweight**: All entry points default to fulltext search
- **User warnings**: Clear messaging about experimental features

## Recommendations

### 🎯 Immediate Fix: Move to Optional Dependencies
Move heavy ML dependencies to optional extras:

```toml
[project]
dependencies = [
    # Keep existing lightweight dependencies
    "click>=8.1.0",
    "rich>=13.0.0",
    "typer>=0.9.0",
    "pydantic>=2.0.0",
    "cookiecutter>=2.4.0",
    "gitpython>=3.1.0",
    "pathlib>=1.0.0",
    "platformdirs>=3.0.0",
    "pyyaml>=6.0",
    "watchdog>=3.0.0",
    "colorama>=0.4.6",
    "requests>=2.28.0",
    # Remove: "sentence-transformers>=2.2.0",
]

[project.optional-dependencies]
semantic = [
    "sentence-transformers>=2.2.0",
    "numpy>=1.21.0",  # Explicit for clarity
]
```

**Installation**:
- Default: `uv add mem8` (lightweight, ~20 packages)  
- With semantic: `uv add "mem8[semantic]"` (full ML stack)

### Alternative Approaches

1. **Feature flag approach**: Add configuration to disable semantic search entirely
2. **Lightweight alternatives**: Implement simpler scoring algorithms (TF-IDF, fuzzy matching)
3. **External service**: Move semantic search to optional external service
4. **Plugin architecture**: Make semantic search a separate plugin package

## Historical Context
The semantic search feature was added recently (commits `1e3fa2b` and `420ff33`) as an experimental enhancement. The implementation already follows good practices for optional dependencies but the packaging doesn't reflect this.

## Conclusion

**The problem is solved at the implementation level but not at the packaging level.** The semantic search feature is properly designed as optional and experimental, but `sentence-transformers` is incorrectly listed as a hard dependency.

**Impact of fixing this**:
- **Before**: 100+ packages including entire PyTorch ecosystem (~1-2GB)
- **After**: ~20-30 packages for core functionality (~50-100MB)  
- **With semantic**: Same as current for users who opt-in

**Zero breaking changes** - The feature already gracefully handles missing dependencies and defaults to fulltext search. Moving to optional dependencies just makes the packaging match the implementation reality.

## Open Questions
- Should we provide additional lightweight search improvements (fuzzy matching, TF-IDF) as middle ground?
- Would users prefer semantic search as a separate plugin package entirely?
- Should we consider external semantic search services instead of local models?