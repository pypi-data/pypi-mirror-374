# Research Report and Implementation Plan Structured Display

## Overview

Implement specialized frontend UI components to properly display research reports and implementation plans with their rich metadata and structured content. The backend already serves these documents with comprehensive YAML frontmatter and structured sections, but the frontend displays them as generic "thoughts" without surfacing their specialized nature.

## Current State Analysis

Based on research documented in `thoughts/shared/research/2025-09-04_21-33-44_frontend-backend-research-plan-display.md`:

### Key Discoveries:
- **Backend Infrastructure Complete**: FastAPI serves 21 structured documents (15 research reports + 6 implementation plans) via `/api/v1/thoughts/from-filesystem` with automatic tag detection
- **Rich Metadata Available**: YAML frontmatter includes researcher, status, git_commit, topic, tags, dates, and more
- **Structured Content Sections**: Research reports have Research Question, Summary, Detailed Findings, Code References; Plans have phased implementation with success criteria
- **WebSocket System Ready**: Real-time updates work but don't differentiate content types
- **Terminal Theme Established**: Consistent memory-cell styling with terminal glow effects and green primary colors
- **Content Type Tags**: Backend automatically adds 'research' and 'plans' tags based on directory structure (`backend/src/mem8_api/services/filesystem_thoughts.py:30-39`)

## Desired End State

Users can easily distinguish and interact with research reports and implementation plans through:
- Specialized display components that surface rich metadata (researcher, status, git_commit)
- Structured section rendering for research questions, findings, and plan phases
- Content-type filtering to show only research reports or implementation plans
- Visual differentiation using existing terminal theme patterns
- Progress tracking for implementation plans with interactive phase displays

### Verification Criteria:
- Research reports display YAML metadata in terminal-styled panels
- Implementation plans show phase-based progress visualization
- Content-type filters work using existing backend tag support
- All changes integrate with existing memory-cell and terminal styling patterns
- Real-time WebSocket updates continue to work for specialized displays

## What We're NOT Doing

- Not changing backend API endpoints (they already work correctly)
- Not modifying WebSocket infrastructure (it's functional)
- Not redesigning the terminal theme or memory-cell aesthetics
- Not adding collaborative editing features (future enhancement)
- Not creating new database models or migrations

## Implementation Approach

Build on existing component patterns (`memory-cell`, terminal theme, Badge/Button components) while adding content-type detection and specialized rendering. Use the automatic tag detection from the backend to determine when to show research vs plan vs regular thought displays.

## Phase 1: Content Type Detection and Enhanced Thought Display

### Overview
Add content type detection to existing thought cards and create enhanced metadata display components that integrate with the current terminal styling.

### Changes Required:

#### 1. Create Content Type Detection Utility
**File**: `frontend/lib/content-types.ts`
**Changes**: New utility file for content type detection and metadata parsing

```typescript
export type ContentType = 'research' | 'plan' | 'thought';

export interface ResearchMetadata {
  date: string;
  researcher: string;
  git_commit?: string;
  branch?: string;
  repository?: string;
  topic: string;
  status: 'complete' | 'in-progress' | 'draft';
  last_updated?: string;
  last_updated_by?: string;
}

export interface PlanMetadata {
  date: string;
  author: string;
  status: 'proposed' | 'in-progress' | 'complete' | 'on-hold';
  priority: 'high' | 'medium' | 'low';
  complexity?: 'low' | 'medium' | 'high';
  estimated_effort?: string;
}

export function detectContentType(tags: string[]): ContentType {
  if (tags.includes('research')) return 'research';
  if (tags.includes('plans')) return 'plan';
  return 'thought';
}

export function parseYamlMetadata(content: string): any {
  // Parse YAML frontmatter from content
  const yamlMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (!yamlMatch) return {};
  
  // Simple YAML parser for our specific metadata structure
  const yamlContent = yamlMatch[1];
  const metadata: any = {};
  
  yamlContent.split('\n').forEach(line => {
    const colonIndex = line.indexOf(':');
    if (colonIndex > 0) {
      const key = line.substring(0, colonIndex).trim();
      let value = line.substring(colonIndex + 1).trim();
      
      // Handle arrays
      if (value.startsWith('[') && value.endsWith(']')) {
        value = value.slice(1, -1).split(',').map(v => v.trim().replace(/['"]/g, ''));
      }
      
      metadata[key] = value;
    }
  });
  
  return metadata;
}
```

#### 2. Create Metadata Display Components
**File**: `frontend/components/MetadataPanel.tsx`
**Changes**: Terminal-styled metadata display component

```typescript
import { Badge } from '@/components/ui/badge';
import { CalendarDays, GitCommit, User, Tag as TagIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ResearchMetadata, PlanMetadata } from '@/lib/content-types';

interface MetadataPanelProps {
  metadata: ResearchMetadata | PlanMetadata;
  type: 'research' | 'plan';
  className?: string;
}

export function MetadataPanel({ metadata, type, className }: MetadataPanelProps) {
  return (
    <div className={cn(
      "border-t border-primary/20 pt-3 mt-3 space-y-2",
      "bg-primary/5 rounded-b-lg -mx-4 px-4 pb-3",
      className
    )}>
      <div className="flex flex-wrap items-center gap-3 text-xs">
        {/* Author/Researcher */}
        <div className="flex items-center gap-1 text-primary">
          <User className="w-3 h-3" />
          <span className="font-mono">
            {'researcher' in metadata ? metadata.researcher : metadata.author}
          </span>
        </div>
        
        {/* Status */}
        <Badge 
          variant={metadata.status === 'complete' ? 'active' : 'syncing'} 
          className="text-xs"
        >
          {metadata.status}
        </Badge>
        
        {/* Priority (plans only) */}
        {type === 'plan' && 'priority' in metadata && metadata.priority && (
          <Badge 
            variant={metadata.priority === 'high' ? 'error' : 'terminal'} 
            className="text-xs"
          >
            {metadata.priority}
          </Badge>
        )}
        
        {/* Date */}
        <div className="flex items-center gap-1 text-muted-foreground">
          <CalendarDays className="w-3 h-3" />
          <span className="font-mono">
            {new Date(metadata.date).toLocaleDateString()}
          </span>
        </div>
        
        {/* Git Commit (research only) */}
        {type === 'research' && 'git_commit' in metadata && metadata.git_commit && (
          <div className="flex items-center gap-1 text-accent">
            <GitCommit className="w-3 h-3" />
            <span className="font-mono text-xs">
              {metadata.git_commit.substring(0, 8)}
            </span>
          </div>
        )}
      </div>
      
      {/* Topic (research) or Effort (plans) */}
      {type === 'research' && 'topic' in metadata && (
        <div className="text-xs text-muted-foreground font-mono">
          <span className="text-primary">Topic:</span> {metadata.topic}
        </div>
      )}
      
      {type === 'plan' && 'estimated_effort' in metadata && metadata.estimated_effort && (
        <div className="text-xs text-muted-foreground font-mono">
          <span className="text-primary">Effort:</span> {metadata.estimated_effort}
        </div>
      )}
    </div>
  );
}
```

#### 3. Enhance Existing Thought Display
**File**: `frontend/app/page.tsx`
**Changes**: Add content type detection and metadata display to existing thought cards

```typescript
// Add imports at top
import { detectContentType, parseYamlMetadata } from '@/lib/content-types';
import { MetadataPanel } from '@/components/MetadataPanel';

// Modify the thought mapping function around line 168-176
return fsThoughts.thoughts.slice(0, 10).map((thought: any) => {
  const contentType = detectContentType(thought.tags || []);
  const metadata = parseYamlMetadata(thought.content);
  
  return {
    id: thought.id,
    title: thought.title,
    excerpt: thought.content.substring(0, 150) + '...',
    path: thought.path,
    team: thought.repository || 'Local',
    lastModified: new Date(thought.updated_at).toLocaleString(),
    tags: thought.tags || [],
    contentType,
    metadata,
    fullContent: thought.content
  };
});

// Modify the thought card rendering around line 490-522
<div key={thought.id} className="memory-cell p-4 rounded-lg hover:scale-[1.02] transition-all cursor-pointer">
  <div className="flex items-start justify-between mb-2">
    <div className="flex items-center gap-2">
      <h3 className="font-medium text-base">{thought.title}</h3>
      {thought.contentType !== 'thought' && (
        <Badge 
          variant={thought.contentType === 'research' ? 'active' : 'syncing'} 
          className="text-xs"
        >
          {thought.contentType === 'research' ? 'Research' : 'Plan'}
        </Badge>
      )}
    </div>
    <Badge variant="terminal" className="text-xs shrink-0">
      {thought.team}
    </Badge>
  </div>
  
  <p className="text-sm text-muted-foreground mb-3 leading-relaxed">
    {thought.excerpt}
  </p>
  
  <div className="flex items-center justify-between text-xs">
    <div className="flex items-center gap-2">
      <span className="text-muted-foreground font-mono">{thought.path}</span>
    </div>
    <div className="flex items-center gap-2">
      <span className="text-muted-foreground">{thought.lastModified}</span>
    </div>
  </div>
  
  {thought.tags && thought.tags.length > 0 && (
    <div className="flex flex-wrap gap-1 mt-2">
      {thought.tags.map((tag, index) => (
        <Badge key={`${tag}-${index}`} variant="outline" className="text-xs">
          {String(tag)}
        </Badge>
      ))}
    </div>
  )}
  
  {/* Add metadata panel for research/plans */}
  {thought.contentType !== 'thought' && thought.metadata && (
    <MetadataPanel 
      metadata={thought.metadata} 
      type={thought.contentType} 
    />
  )}
</div>
```

### Success Criteria:

#### Automated Verification:
- [x] Frontend builds without errors: `npm run build`
- [x] TypeScript compilation passes: `npm run type-check`
- [x] No linting errors: `npm run lint`
- [x] Components render without console errors in dev mode

#### Manual Verification:
- [x] Research reports show "Research" badge and display researcher, status, date metadata
- [x] Implementation plans show "Plan" badge and display author, priority, status metadata
- [x] Regular thoughts continue to display normally without metadata panels
- [x] Terminal styling and memory-cell effects are preserved
- [x] Metadata information is readable and properly formatted

---

## Phase 2: Research Report Structured Viewer

### Overview
Create a specialized component for displaying research report sections (Research Question, Summary, Detailed Findings, Code References) with proper terminal styling and code syntax highlighting.

### Changes Required:

#### 1. Create Research Report Viewer Component
**File**: `frontend/components/ResearchReportViewer.tsx`
**Changes**: New component for structured research report display

```typescript
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ResearchReportViewerProps {
  content: string;
  metadata: any;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

export function ResearchReportViewer({ 
  content, 
  metadata, 
  isExpanded = false,
  onToggleExpand 
}: ResearchReportViewerProps) {
  const sections = parseResearchSections(content);
  
  return (
    <div className="space-y-4">
      {/* Summary Section - Always Visible */}
      {sections.summary && (
        <div className="bg-primary/10 border border-primary/20 rounded-lg p-3">
          <h4 className="text-sm font-semibold text-primary mb-2 terminal-glow">
            Summary
          </h4>
          <div className="text-sm text-muted-foreground leading-relaxed">
            {sections.summary.substring(0, 300)}
            {sections.summary.length > 300 && !isExpanded && '...'}
          </div>
        </div>
      )}
      
      {/* Expand/Collapse Toggle */}
      <Button
        variant="ghost"
        size="sm"
        onClick={onToggleExpand}
        className="w-full justify-between font-mono terminal-glow"
      >
        <span>{isExpanded ? 'Show Less' : 'Show Full Report'}</span>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </Button>
      
      {/* Expanded Content */}
      {isExpanded && (
        <div className="space-y-4 animate-in slide-in-from-top-2">
          {/* Research Question */}
          {sections.researchQuestion && (
            <div className="border-l-2 border-accent pl-4">
              <h4 className="text-sm font-semibold text-accent mb-2">Research Question</h4>
              <div className="text-sm leading-relaxed">{sections.researchQuestion}</div>
            </div>
          )}
          
          {/* Detailed Findings */}
          {sections.detailedFindings && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-primary terminal-glow">
                Detailed Findings
              </h4>
              <div className="prose prose-sm prose-invert max-w-none">
                <ReactMarkdown 
                  components={{
                    code: ({ inline, className, children }) => (
                      <code className={cn(
                        "font-mono text-xs",
                        inline ? "bg-muted px-1 py-0.5 rounded" : "block bg-background border border-border rounded p-2 mt-2 terminal-glow"
                      )}>
                        {children}
                      </code>
                    ),
                    a: ({ href, children }) => (
                      <a 
                        href={href} 
                        className="text-accent hover:text-accent/80 inline-flex items-center gap-1"
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        {children}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )
                  }}
                >
                  {sections.detailedFindings}
                </ReactMarkdown>
              </div>
            </div>
          )}
          
          {/* Code References */}
          {sections.codeReferences && (
            <div className="bg-background/50 border border-border rounded-lg p-3">
              <h4 className="text-sm font-semibold text-secondary mb-2">Code References</h4>
              <div className="text-xs font-mono space-y-1">
                <ReactMarkdown>{sections.codeReferences}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Utility function to parse research report sections
function parseResearchSections(content: string) {
  const sections: any = {};
  
  // Remove YAML frontmatter
  const cleanContent = content.replace(/^---\n[\s\S]*?\n---\n/, '');
  
  // Extract sections using regex patterns
  const summaryMatch = cleanContent.match(/## Summary\s*\n([\s\S]*?)(?=\n## |\n# |$)/);
  if (summaryMatch) sections.summary = summaryMatch[1].trim();
  
  const questionMatch = cleanContent.match(/## Research Question\s*\n([\s\S]*?)(?=\n## |\n# |$)/);
  if (questionMatch) sections.researchQuestion = questionMatch[1].trim();
  
  const findingsMatch = cleanContent.match(/## Detailed Findings\s*\n([\s\S]*?)(?=\n## Code References|\n## Architecture|\n## |$)/);
  if (findingsMatch) sections.detailedFindings = findingsMatch[1].trim();
  
  const codeRefsMatch = cleanContent.match(/## Code References\s*\n([\s\S]*?)(?=\n## |\n# |$)/);
  if (codeRefsMatch) sections.codeReferences = codeRefsMatch[1].trim();
  
  return sections;
}
```

#### 2. Add React Markdown Dependency
**File**: `frontend/package.json`
**Changes**: Add markdown parsing dependency

```bash
npm install react-markdown remark-gfm rehype-highlight
```

#### 3. Integrate Research Viewer into Main Display
**File**: `frontend/app/page.tsx`
**Changes**: Add state for expanded research reports and integrate ResearchReportViewer

```typescript
// Add imports
import { ResearchReportViewer } from '@/components/ResearchReportViewer';

// Add state for expanded reports (around line 25)
const [expandedReports, setExpandedReports] = useState<Set<string>>(new Set());

const toggleReportExpansion = (thoughtId: string) => {
  const newExpanded = new Set(expandedReports);
  if (newExpanded.has(thoughtId)) {
    newExpanded.delete(thoughtId);
  } else {
    newExpanded.add(thoughtId);
  }
  setExpandedReports(newExpanded);
};

// Modify thought card rendering to include research viewer
{thought.contentType === 'research' && (
  <ResearchReportViewer
    content={thought.fullContent}
    metadata={thought.metadata}
    isExpanded={expandedReports.has(thought.id)}
    onToggleExpand={() => toggleReportExpansion(thought.id)}
  />
)}
```

### Success Criteria:

#### Automated Verification:
- [ ] Frontend builds successfully: `npm run build`
- [ ] TypeScript types are valid: `npm run type-check`
- [ ] New markdown dependencies install correctly: `npm install`
- [ ] No console errors when rendering research reports

#### Manual Verification:
- [ ] Research reports show structured sections (Summary, Research Question, Detailed Findings)
- [ ] Expand/collapse functionality works smoothly
- [ ] Code blocks display with proper syntax highlighting and terminal styling
- [ ] Code references are clickable and open in new tabs
- [ ] Research report styling integrates well with terminal theme
- [ ] Performance is acceptable with multiple expanded reports

---

## Phase 3: Implementation Plan Progress Tracker

### Overview
Create a specialized component for displaying implementation plans with phase visualization, progress tracking, and interactive success criteria checklists.

### Changes Required:

#### 1. Create Plan Progress Tracker Component
**File**: `frontend/components/PlanProgressTracker.tsx`
**Changes**: New component for interactive plan display with phase tracking

```typescript
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  ChevronDown, 
  ChevronUp,
  PlayCircle 
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface PlanProgressTrackerProps {
  content: string;
  metadata: any;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

export function PlanProgressTracker({ 
  content, 
  metadata, 
  isExpanded = false,
  onToggleExpand 
}: PlanProgressTrackerProps) {
  const planData = parsePlanStructure(content);
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());
  
  const toggleCheckItem = (itemId: string) => {
    const newChecked = new Set(checkedItems);
    if (newChecked.has(itemId)) {
      newChecked.delete(itemId);
    } else {
      newChecked.add(itemId);
    }
    setCheckedItems(newChecked);
  };
  
  const calculateProgress = () => {
    const totalItems = planData.phases.reduce((acc, phase) => acc + phase.tasks.length, 0);
    const completedItems = checkedItems.size;
    return totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;
  };
  
  return (
    <div className="space-y-4">
      {/* Overview Section */}
      <div className="bg-secondary/10 border border-secondary/20 rounded-lg p-3">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-semibold text-secondary terminal-glow">
            Implementation Plan
          </h4>
          <div className="flex items-center gap-2">
            <Badge variant={metadata.status === 'complete' ? 'active' : 'syncing'}>
              {metadata.status}
            </Badge>
            {metadata.priority && (
              <Badge variant={metadata.priority === 'high' ? 'error' : 'terminal'}>
                {metadata.priority}
              </Badge>
            )}
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Overall Progress</span>
            <span className="text-primary font-mono">{calculateProgress()}%</span>
          </div>
          <Progress 
            value={calculateProgress()} 
            className="h-2 bg-background"
            // Custom progress bar styling for terminal theme
          />
        </div>
        
        {planData.objective && (
          <div className="mt-3 text-sm text-muted-foreground leading-relaxed">
            {planData.objective.substring(0, 200)}
            {planData.objective.length > 200 && !isExpanded && '...'}
          </div>
        )}
      </div>
      
      {/* Expand/Collapse Toggle */}
      <Button
        variant="ghost"
        size="sm"
        onClick={onToggleExpand}
        className="w-full justify-between font-mono terminal-glow"
      >
        <span>{isExpanded ? 'Hide Implementation Details' : 'Show Implementation Plan'}</span>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </Button>
      
      {/* Expanded Plan Details */}
      {isExpanded && (
        <div className="space-y-4 animate-in slide-in-from-top-2">
          {/* Phases */}
          {planData.phases.map((phase, phaseIndex) => (
            <div key={phaseIndex} className="border border-border rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 border border-primary/30">
                  <span className="text-xs font-mono text-primary font-bold">
                    {phaseIndex + 1}
                  </span>
                </div>
                <div>
                  <h5 className="text-sm font-semibold text-primary">{phase.title}</h5>
                  {phase.duration && (
                    <p className="text-xs text-muted-foreground font-mono">
                      Estimated: {phase.duration}
                    </p>
                  )}
                </div>
              </div>
              
              {phase.overview && (
                <p className="text-sm text-muted-foreground leading-relaxed pl-11">
                  {phase.overview}
                </p>
              )}
              
              {/* Task Checklist */}
              {phase.tasks.length > 0 && (
                <div className="pl-11 space-y-2">
                  <h6 className="text-xs font-semibold text-accent uppercase tracking-wide">
                    Tasks
                  </h6>
                  {phase.tasks.map((task, taskIndex) => {
                    const taskId = `${phaseIndex}-${taskIndex}`;
                    const isChecked = checkedItems.has(taskId);
                    
                    return (
                      <div key={taskId} className="flex items-start gap-2">
                        <button
                          onClick={() => toggleCheckItem(taskId)}
                          className={cn(
                            "flex items-center justify-center w-4 h-4 border rounded mt-0.5 transition-colors",
                            isChecked 
                              ? "bg-primary border-primary text-background" 
                              : "border-muted-foreground hover:border-primary"
                          )}
                        >
                          {isChecked && <CheckCircle2 className="w-3 h-3" />}
                        </button>
                        <span className={cn(
                          "text-sm leading-relaxed",
                          isChecked ? "line-through text-muted-foreground" : ""
                        )}>
                          {task}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
          
          {/* Testing Strategy */}
          {planData.testing && (
            <div className="bg-accent/10 border border-accent/20 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-accent mb-2">Testing Strategy</h4>
              <div className="text-xs font-mono space-y-1">
                <ReactMarkdown>{planData.testing}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Utility function to parse implementation plan structure
function parsePlanStructure(content: string) {
  const planData: any = { phases: [] };
  
  // Remove YAML frontmatter
  const cleanContent = content.replace(/^---\n[\s\S]*?\n---\n/, '');
  
  // Extract objective
  const objectiveMatch = cleanContent.match(/## Objective\s*\n([\s\S]*?)(?=\n## |\n# |$)/);
  if (objectiveMatch) planData.objective = objectiveMatch[1].trim();
  
  // Extract phases
  const phaseMatches = cleanContent.match(/### Phase \d+:([^\n]*)\n([\s\S]*?)(?=\n### Phase|\n## |$)/g);
  if (phaseMatches) {
    planData.phases = phaseMatches.map((phaseText: string) => {
      const titleMatch = phaseText.match(/### Phase \d+:\s*([^\n]*)/);
      const title = titleMatch ? titleMatch[1].trim() : 'Untitled Phase';
      
      // Extract duration if mentioned
      const durationMatch = phaseText.match(/\(([^)]*(?:min|hour|day|week)[^)]*)\)/);
      const duration = durationMatch ? durationMatch[1] : null;
      
      // Extract overview
      const overviewMatch = phaseText.match(/#### Overview\s*\n([^\n]*)/);
      const overview = overviewMatch ? overviewMatch[1].trim() : null;
      
      // Extract tasks (numbered lists)
      const taskMatches = phaseText.match(/^\d+\.\s+(.+)$/gm);
      const tasks = taskMatches ? taskMatches.map(task => task.replace(/^\d+\.\s+/, '')) : [];
      
      return { title, duration, overview, tasks };
    });
  }
  
  // Extract testing strategy
  const testingMatch = cleanContent.match(/## Testing Strategy\s*\n([\s\S]*?)(?=\n## |\n# |$)/);
  if (testingMatch) planData.testing = testingMatch[1].trim();
  
  return planData;
}
```

#### 2. Add Progress Bar Component
**File**: `frontend/components/ui/progress.tsx`
**Changes**: Terminal-styled progress bar component

```typescript
import * as React from "react"
import * as ProgressPrimitive from "@radix-ui/react-progress"
import { cn } from "@/lib/utils"

const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>
>(({ className, value, ...props }, ref) => (
  <ProgressPrimitive.Root
    ref={ref}
    className={cn(
      "relative h-2 w-full overflow-hidden rounded-full bg-background border border-border",
      className
    )}
    {...props}
  >
    <ProgressPrimitive.Indicator
      className="h-full w-full flex-1 bg-gradient-to-r from-primary to-accent transition-all terminal-glow"
      style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
    />
  </ProgressPrimitive.Root>
))
Progress.displayName = ProgressPrimitive.Root.displayName

export { Progress }
```

#### 3. Integrate Plan Tracker into Main Display
**File**: `frontend/app/page.tsx`
**Changes**: Add plan tracker to thought display

```typescript
// Add import
import { PlanProgressTracker } from '@/components/PlanProgressTracker';

// Add state for expanded plans
const [expandedPlans, setExpandedPlans] = useState<Set<string>>(new Set());

const togglePlanExpansion = (thoughtId: string) => {
  const newExpanded = new Set(expandedPlans);
  if (newExpanded.has(thoughtId)) {
    newExpanded.delete(thoughtId);
  } else {
    newExpanded.add(thoughtId);
  }
  setExpandedPlans(newExpanded);
};

// Add plan tracker to thought card rendering
{thought.contentType === 'plan' && (
  <PlanProgressTracker
    content={thought.fullContent}
    metadata={thought.metadata}
    isExpanded={expandedPlans.has(thought.id)}
    onToggleExpand={() => togglePlanExpansion(thought.id)}
  />
)}
```

### Success Criteria:

#### Automated Verification:
- [ ] Progress component installs and builds: `npm install @radix-ui/react-progress`
- [ ] Frontend builds without TypeScript errors: `npm run build`
- [ ] No console warnings when rendering implementation plans
- [ ] React component state management works correctly

#### Manual Verification:
- [ ] Implementation plans show phase-based structure with progress visualization
- [ ] Task checkboxes can be toggled and affect overall progress percentage
- [ ] Plan metadata (status, priority, effort) displays correctly
- [ ] Expand/collapse animation works smoothly
- [ ] Progress bar updates in real-time as tasks are checked
- [ ] Terminal styling is consistent with existing memory-cell pattern

---

## Phase 4: Content-Type Filtering and Search Enhancement

### Overview
Add content-type filtering to the search interface and enhance the search experience with metadata-aware filters, leveraging the existing backend tag-based filtering capabilities.

### Changes Required:

#### 1. Create Content Filter Component
**File**: `frontend/components/ContentTypeFilter.tsx`
**Changes**: Filter buttons for research/plans/all content types

```typescript
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, FileText, ClipboardList, BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';

type FilterType = 'all' | 'research' | 'plans';

interface ContentTypeFilterProps {
  activeFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
  counts?: {
    total: number;
    research: number;
    plans: number;
  };
}

export function ContentTypeFilter({ 
  activeFilter, 
  onFilterChange, 
  counts 
}: ContentTypeFilterProps) {
  const filters = [
    {
      key: 'all' as FilterType,
      label: 'All Content',
      icon: FileText,
      count: counts?.total || 0,
      variant: 'terminal'
    },
    {
      key: 'research' as FilterType,
      label: 'Research Reports',
      icon: Search,
      count: counts?.research || 0,
      variant: 'active'
    },
    {
      key: 'plans' as FilterType,
      label: 'Implementation Plans',
      icon: ClipboardList,
      count: counts?.plans || 0,
      variant: 'syncing'
    }
  ];
  
  return (
    <div className="flex flex-wrap gap-2 p-4 bg-muted/30 border-b border-border">
      <div className="flex items-center gap-2 mr-4">
        <BookOpen className="w-4 h-4 text-primary terminal-glow" />
        <span className="text-sm font-mono text-primary">Filter:</span>
      </div>
      
      {filters.map(({ key, label, icon: Icon, count, variant }) => (
        <Button
          key={key}
          variant={activeFilter === key ? 'default' : 'ghost'}
          size="sm"
          onClick={() => onFilterChange(key)}
          className={cn(
            "flex items-center gap-2 font-mono transition-all",
            activeFilter === key 
              ? "bg-primary/20 border-primary/50 text-primary terminal-glow" 
              : "hover:bg-muted/50"
          )}
        >
          <Icon className="w-4 h-4" />
          <span>{label}</span>
          {count > 0 && (
            <Badge 
              variant={activeFilter === key ? variant as any : 'outline'} 
              className="text-xs min-w-[20px] h-4"
            >
              {count}
            </Badge>
          )}
        </Button>
      ))}
    </div>
  );
}
```

#### 2. Enhance API Hook for Filtered Searches
**File**: `frontend/hooks/useApi.ts`
**Changes**: Add content-type filtering to existing API hooks

```typescript
// Add new hook for filtered content
export function useFilteredThoughts(params?: {
  contentType?: 'research' | 'plans' | 'all';
  searchQuery?: string;
  repository?: string;
  limit?: number;
}) {
  const tags = params?.contentType === 'all' || !params?.contentType 
    ? [] 
    : [params.contentType];
    
  return useQuery({
    queryKey: ['filtered-thoughts', params],
    queryFn: () => {
      if (params?.searchQuery && params.searchQuery.length > 2) {
        return apiClient.searchThoughts({
          query: params.searchQuery,
          search_type: 'fulltext',
          limit: params?.limit || 50
        });
      } else {
        return apiClient.getFilesystemThoughts({
          tags: tags.length > 0 ? tags : undefined,
          repository: params?.repository,
          limit: params?.limit || 50
        });
      }
    },
    enabled: true,
    staleTime: 2 * 60 * 1000, // 2 minutes cache
  });
}
```

#### 3. Integrate Content Filtering into Main Page
**File**: `frontend/app/page.tsx`
**Changes**: Add content type filter state and integrate with existing search

```typescript
// Add imports
import { ContentTypeFilter } from '@/components/ContentTypeFilter';

// Add filter state (around existing state declarations)
const [contentTypeFilter, setContentTypeFilter] = useState<'all' | 'research' | 'plans'>('all');

// Replace existing data fetching with filtered version
const { data: filteredData, isLoading: filteredLoading } = useFilteredThoughts({
  contentType: contentTypeFilter,
  searchQuery: searchQuery.length > 2 ? searchQuery : undefined,
  limit: 50
});

// Update thought counts calculation
const thoughtCounts = useMemo(() => {
  if (!filteredData?.thoughts) return { total: 0, research: 0, plans: 0 };
  
  const thoughts = filteredData.thoughts;
  return {
    total: thoughts.length,
    research: thoughts.filter((t: any) => t.tags?.includes('research')).length,
    plans: thoughts.filter((t: any) => t.tags?.includes('plans')).length
  };
}, [filteredData]);

// Update the recentThoughts calculation to use filtered data
const recentThoughts = (() => {
  if (!filteredData?.thoughts) return [];
  
  return filteredData.thoughts.slice(0, 10).map((thought: any) => {
    const contentType = detectContentType(thought.tags || []);
    const metadata = parseYamlMetadata(thought.content);
    
    return {
      id: thought.id,
      title: thought.title,
      excerpt: thought.content.substring(0, 150) + '...',
      path: thought.path,
      team: thought.repository || 'Local',
      lastModified: new Date(thought.updated_at).toLocaleString(),
      tags: thought.tags || [],
      contentType,
      metadata,
      fullContent: thought.content
    };
  });
})();

// Add content filter to the UI (after search input, before thought list)
{/* Content Type Filter */}
<ContentTypeFilter
  activeFilter={contentTypeFilter}
  onFilterChange={setContentTypeFilter}
  counts={thoughtCounts}
/>
```

#### 4. Add Quick Filter Shortcuts
**File**: `frontend/app/page.tsx`
**Changes**: Add keyboard shortcuts for quick filtering

```typescript
// Add useEffect for keyboard shortcuts (around line 60)
useEffect(() => {
  const handleKeyPress = (event: KeyboardEvent) => {
    // Only trigger if not typing in an input field
    if (document.activeElement?.tagName === 'INPUT') return;
    
    if (event.ctrlKey || event.metaKey) {
      switch (event.key) {
        case '1':
          event.preventDefault();
          setContentTypeFilter('all');
          break;
        case '2':
          event.preventDefault();
          setContentTypeFilter('research');
          break;
        case '3':
          event.preventDefault();
          setContentTypeFilter('plans');
          break;
      }
    }
  };
  
  document.addEventListener('keydown', handleKeyPress);
  return () => document.removeEventListener('keydown', handleKeyPress);
}, []);
```

### Success Criteria:

#### Automated Verification:
- [ ] Frontend builds successfully with new filtering components: `npm run build`
- [ ] TypeScript compilation passes: `npm run type-check`
- [ ] No linting errors: `npm run lint`
- [ ] API hooks work correctly with tag-based filtering
- [ ] React Query caching works properly with filter changes

#### Manual Verification:
- [ ] Content type filter buttons work and show correct counts
- [ ] Filtering to "Research Reports" shows only research documents
- [ ] Filtering to "Implementation Plans" shows only plan documents
- [ ] "All Content" shows all thoughts including regular notes
- [ ] Search functionality works within filtered content types
- [ ] Keyboard shortcuts (Ctrl+1/2/3) change filters correctly
- [ ] Filter state persists during search but resets on page refresh
- [ ] Performance is acceptable when switching between filters

---

## Testing Strategy

### Unit Tests:
- Test content type detection utility with various tag combinations
- Test YAML metadata parsing with malformed and valid frontmatter
- Test component rendering with different metadata structures
- Test progress calculation in plan tracker component

### Integration Tests:
- Test complete workflow: load thoughts → detect content type → display specialized viewer
- Test search functionality with content type filters
- Test WebSocket updates maintain content type detection and specialized display
- Test responsive design on mobile/tablet devices

### Manual Testing Steps:
1. **Load Application**: `npm run dev` and verify terminal theme loads correctly
2. **Content Detection**: Navigate to application and verify research reports show "Research" badge
3. **Research Viewer**: Expand a research report and verify sections (Summary, Research Question, Detailed Findings) display properly
4. **Plan Tracker**: Expand an implementation plan and verify phase display and task checkboxes work
5. **Filtering**: Use content type filters and verify only relevant content shows
6. **Search**: Search within filtered content types and verify results are appropriately filtered
7. **Metadata Display**: Verify researcher, status, dates, and git commits display in metadata panels
8. **Real-time Updates**: Test WebSocket functionality with multiple browser tabs
9. **Performance**: Load with 20+ documents and verify smooth scrolling and interactions
10. **Keyboard Shortcuts**: Test Ctrl+1/2/3 shortcuts for quick filtering
11. **Mobile Responsive**: Test on mobile device for proper layout and interactions

## Performance Considerations

- **Lazy Loading**: Research and plan content is only parsed when expanded to avoid performance impact
- **React Query Caching**: Maintains 2-minute cache for filtered queries to reduce API calls
- **Virtualization**: Consider adding virtual scrolling if document count exceeds 100+ items
- **Bundle Size**: Markdown parsing adds ~50KB to bundle - consider code splitting for large deployments

## Migration Notes

- **No Backend Changes Required**: All functionality uses existing API endpoints
- **Progressive Enhancement**: Regular thoughts continue to display normally
- **Backward Compatibility**: Existing search and filtering functionality remains unchanged
- **Feature Flag**: Consider adding environment variable to enable/disable specialized viewers during rollout

## References

- Original research: `thoughts/shared/research/2025-09-04_21-33-44_frontend-backend-research-plan-display.md`
- Backend filesystem service: `backend/src/mem8_api/services/filesystem_thoughts.py:30-39`
- Frontend thought display: `frontend/app/page.tsx:489-522`
- Terminal theme implementation: `frontend/app/globals.css:97-174`
- Example research report: `thoughts/shared/research/2025-09-04_14-32-55_cli-project-root-detection.md`
- Example implementation plan: `thoughts/shared/plans/postgres-removal-simplification.md`