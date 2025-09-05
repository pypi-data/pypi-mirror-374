---
date: 2025-09-04T21:33:44+0000
researcher: claude-code
git_commit: fb7c1a4f434129d39770392dea24a674a785216a
branch: main
repository: mem8
topic: "Frontend and backend not showing research and plan elements that are core to the knowledge base"
tags: [research, frontend, backend, fastapi, websockets, thoughts, ui, integration]
status: complete
last_updated: 2025-09-04
last_updated_by: claude-code
---

# Research: Frontend and Backend Display of Research Reports and Implementation Plans

**Date**: 2025-09-04T21:33:44+0000
**Researcher**: claude-code
**Git Commit**: fb7c1a4f434129d39770392dea24a674a785216a
**Branch**: main
**Repository**: mem8

## Research Question
Why are the frontend and backend not showing research and plan elements that are the core of the knowledge base? These should be served by the Docker backend/FastAPI and displayed in the frontend UI with the existing websockets system.

## Summary
The mem8 system has comprehensive backend infrastructure for serving thoughts data and a functional frontend, but significant gaps exist in properly displaying research reports and implementation plans as structured content. The system successfully identifies and serves research/plan documents but lacks specialized UI components to render their rich metadata and structured formats.

**Key Finding**: The infrastructure is complete, but the presentation layer needs enhancement to surface the structured nature of research reports and implementation plans.

## Detailed Findings

### Backend Architecture - Fully Functional

**FastAPI Docker Setup**
- Production-ready Docker configuration at `docker-compose.yml` and `docker-compose.prod.yml`
- Integrated CLI entry point with `mem8 serve` command
- PostgreSQL + Redis + FastAPI + Frontend services properly orchestrated
- Health checks and volume mounting for development workflows

**API Endpoints for Research/Plans**
- `GET /api/v1/thoughts/from-filesystem` - **Successfully serves filesystem-based research data**
- `GET /api/v1/public/thoughts/local` - Public access to thoughts including research reports
- `POST /api/v1/search/` - Full-text and semantic search across all document types
- Complete CRUD operations for thoughts with team-based access control

**Data Processing Pipeline**
- `backend/src/mem8_api/services/filesystem_thoughts.py:57-108` - Automatically scans `.md` files
- `backend/src/mem8_api/services/filesystem_thoughts.py:24-54` - Extracts YAML frontmatter metadata
- **Path-based tag detection** - Automatically identifies 'research' and 'plans' tags from directory structure
- Multi-repository support for scanning across worktrees

### Frontend Architecture - Missing Specialized Components

**Current UI System**
- Next.js 15.5.2 with terminal theme and WebSocket integration
- TanStack React Query for state management
- Basic thought display with tags and search functionality
- Real-time updates via WebSocket system

**Critical Gap: No Structured Content Display**
- Research documents appear as generic thoughts despite rich YAML metadata
- Implementation plans show as plain text instead of phased task lists
- No visual differentiation between research reports and regular notes
- Missing components: Research viewer, plan tracker, metadata display panels

### Thoughts Structure - Rich But Underutilized

**Research Reports** (`thoughts/shared/research/` - 15 documents)
- **Structured YAML frontmatter** with researcher, git_commit, status, topic
- **Standardized sections**: Research Question, Summary, Detailed Findings, Code References
- **Cross-references** to implementation files with line numbers
- **Status tracking**: complete, in-progress, draft

**Implementation Plans** (`thoughts/shared/plans/` - 6 documents)
- **Phased implementation structure** with success criteria
- **Explicit scope management** ("What We're NOT Doing" sections)
- **Testing strategies** with automated and manual verification
- **Migration notes** and deployment considerations

### WebSocket System - Ready for Real-time Updates

**Backend WebSocket Manager**
- `backend/src/mem8_api/routers/sync.py` - Team-based connection management
- Message types: `thought_created`, `thought_updated`, `thought_deleted`
- Broadcasting to team members with automatic cleanup

**Frontend WebSocket Integration**
- `frontend/hooks/useWebSocket.ts` - React hook with reconnection logic
- React Query cache invalidation on WebSocket events
- Connection status display in UI (`frontend/app/page.tsx:50-54`)

**Integration Pattern Working**
- Real-time updates trigger across team members
- Proper error handling and exponential backoff
- Authentication-aware connections

## Code References

**Backend Serving Infrastructure**:
- `backend/src/mem8_api/routers/thoughts.py:26` - Main thoughts API endpoint
- `backend/src/mem8_api/services/filesystem_thoughts.py:143` - Filesystem scanning service
- `backend/src/mem8_api/routers/sync.py` - WebSocket sync endpoint

**Frontend Data Flow**:
- `frontend/hooks/useApi.ts:14-28` - API hooks for thoughts data
- `frontend/app/page.tsx:159-189` - Main display logic prioritizing filesystem data
- `frontend/hooks/useWebSocket.ts` - Real-time update integration

**Thoughts Organization**:
- `thoughts/shared/research/` - 15 research report documents
- `thoughts/shared/plans/` - 6 implementation plan documents

## Architecture Insights

**Successful Patterns**:
1. **Hybrid Data Sources**: System correctly prioritizes filesystem over database for research content
2. **Automatic Discovery**: Path-based tag detection properly identifies research/plan content types  
3. **Real-time Sync**: WebSocket system provides live collaboration capabilities
4. **Team Organization**: Multi-tenant architecture supports collaborative knowledge management
5. **Rich Metadata**: YAML frontmatter provides comprehensive document metadata

**Missing Patterns**:
1. **Content Type UI Specialization**: No differentiated display for research vs plans vs regular thoughts
2. **Metadata Presentation**: Rich YAML frontmatter not surfaced in user interface
3. **Structured Content Rendering**: Research sections and plan phases not highlighted
4. **Progress Tracking**: Implementation plan status and phases not visualized
5. **Related Content Discovery**: Backend `/thoughts/{id}/related` endpoint unused

## Open Questions

1. **Should research reports have a dedicated viewer component?** The current generic thought display doesn't showcase the structured research format.

2. **How should implementation plan progress be tracked?** Plans have phases and success criteria that could be interactive.

3. **Should the search UI have content-type filters?** Backend supports tag-based filtering but frontend doesn't expose "research only" or "plans only" views.

4. **Are there plans for collaborative editing?** The WebSocket system could support real-time collaborative editing of research documents.

## Recommendations

### High Priority - UI Enhancement
1. **Create Research Report Viewer Component**
   - Display YAML metadata (researcher, status, git_commit)
   - Structured sections (Research Question, Summary, Findings)
   - Code reference links with line numbers

2. **Implement Plan Progress Tracker**
   - Phase-based progress visualization
   - Task list with completion status
   - Success criteria checklists

3. **Add Content Type Filtering**
   - Quick filters for "Research Reports" and "Implementation Plans"  
   - Utilize existing backend tag-based filtering

### Medium Priority - Enhanced Integration
4. **Surface Related Content**
   - Use existing `/thoughts/{id}/related` endpoint
   - Show related research and plans in sidebars

5. **Enhance Search Experience**
   - Content-type specific search results
   - Metadata-aware search filters

### Low Priority - Advanced Features
6. **Real-time Collaborative Editing**
   - Leverage existing WebSocket infrastructure
   - Live editing with conflict resolution

The core infrastructure is solid - this is primarily a frontend enhancement project to surface the rich structured content that already exists in the backend systems.