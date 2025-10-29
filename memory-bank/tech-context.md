# Technical Context: Watchdog

## System Architecture Overview

### Complete System Architecture
- **VS Code Extension** (vscode-extension/src/): TypeScript-based inline completion provider
- **Python Backend** (src/llm/): LLM-powered hint generation service
- **Optional File Monitor** (watch_and_hint.py): Standalone terminal-based code monitoring

### Core Architecture Pattern
**Primary Pattern**: VS Code inline completion provider with HTTP backend
**Code Structure**: Extension (TypeScript) + Backend service (Python) architecture
**State Management**: Stateless completion requests with full-file context
**Event Flow**: User types → Extension requests hint → Backend analyzes → Ghost text displayed

## Current Development Status

### Implementation Phase
**Current Version**: v0.2.0 (VS Code Extension Complete)
**Status**: Inline completion provider operational with Python LLM backend
**Next Phase**: Enhanced LLM features and multi-language support

### Core Components Status

#### 1. VS Code Extension (COMPLETE)
**Location**: vscode-extension/src/
**Key Files**:
- `extension.ts`: Main extension lifecycle and activation
- `inlineCompletionProvider.ts`: Provides ghost text suggestions
- `backendManager.ts`: Manages Python backend process
- `httpClient.ts`: HTTP communication with backend

**Features Implemented**:
- Inline completion provider registration for Python files
- Full-file context analysis for suggestions
- Help comment detection (`# help ...`)
- Smart context filtering (only suggest when incomplete)
- Automatic backend startup and lifecycle management

**Performance Characteristics**:
- Completion suggestion latency: <500ms
- Backend communication: HTTP REST API
- Memory footprint: ~30-50MB for extension

#### 2. Python LLM Backend (COMPLETE)
**Location**: src/llm/hint_service.py
**Key Components**:
- `CodeContext`: Dataclass capturing code context for hint generation
- `generate_code_hint()`: Main function for LLM-powered hint generation

**Features Implemented**:
- Full-file code context analysis
- LLM-powered code completion and suggestions
- Support for help comments and learning hints
- Context-aware suggestion generation
- Pattern-based vs. solution-based hint modes

**Hint Generation Modes**:
- `help_comment`: Generates code from natural language request
- `learning_hint`: Provides next logical code step with patterns
- `context_completion`: Context-aware code suggestions

**Backend Characteristics**:
- Response time: <300ms for typical requests
- Uses Effects pattern for error handling (Success/Failure)
- Stateless request processing

#### 3. Optional File Monitor (COMPLETE)
**File**: watch_and_hint.py
**Key Components**:
- `CodeHintHandler`: FileSystemEventHandler for file change detection
- File watching with watchdog library for terminal-based hints

**Features Implemented**:
- Watches Python files in current directory
- Detects file modifications and extracts last 50 lines
- Sends context to hint service for analysis
- Displays hints in terminal output
- Code normalization to avoid duplicate processing

**Use Case**:
- Standalone terminal-based code monitoring
- Alternative to VS Code extension for non-IDE users
- Testing and development of hint generation
- Real-time terminal feedback during coding

## Technical Stack Specifications

### Core Technologies
**Extension Runtime**: TypeScript with VS Code Extension API
**Backend Runtime**: Python 3.8+ (type hints, dataclasses, Effects pattern)
**LLM Integration**: Configurable LLM providers for hint generation
**File Monitoring**: watchdog 3.0.0 (for optional terminal monitor)
**HTTP Communication**: Node.js fetch API for extension-backend communication

### Key Libraries
**VS Code Extension**: @types/vscode ^1.85.0, TypeScript ^5.3.0
**Python Backend**: dataclasses, typing, effects pattern implementation
**Optional Components**: rich 13.7.0 (terminal output), watchdog 3.0.0 (file monitoring)

## Development Environment

### Required Dependencies

**VS Code Extension**:
```json
{
  "@types/vscode": "^1.85.0",
  "@types/node": "^20.x",
  "typescript": "^5.3.0"
}
```

**Python Backend**:
```
dataclasses (built-in)
typing (built-in)
watchdog==3.0.0      # For optional file monitor
rich==13.7.0         # For terminal output (optional)
```

### Environment Setup

**Extension Development**:
```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VS Code to launch extension development host
```

**Backend Setup**:
```bash
python -m venv venv
# Activation (Windows)
venv\Scripts\activate
# Activation (Unix/macOS)
source venv/bin/activate

# Install dependencies for optional components
pip install watchdog rich
```

### Project Structure
```
watchdog/
├── vscode-extension/              # VS Code extension
│   ├── src/
│   │   ├── extension.ts           # Main extension entry
│   │   ├── inlineCompletionProvider.ts  # Completion provider
│   │   ├── backendManager.ts      # Backend process management
│   │   └── httpClient.ts          # Backend communication
│   ├── package.json               # Extension manifest
│   └── tsconfig.json              # TypeScript configuration
├── src/
│   ├── llm/
│   │   └── hint_service.py        # LLM-powered hint generation
│   └── effects.py                 # Effects pattern (Success/Failure)
├── watch_and_hint.py              # Optional terminal file monitor
├── project_configs/
│   ├── engineering-standards.md   # Development standards
│   ├── session-start-checklist.md # Quality gates
│   └── dev-log.md                 # Development history
├── memory-bank/
│   ├── projectbrief.md            # Project overview
│   ├── tech-context.md            # This file
│   ├── progress.md                # Milestone tracking
│   └── active-context.md          # Current development state
└── tests/                         # Unit tests (future)
```

## Data Architecture

### Request/Response Schema

**CodeContext Dataclass** (hint_service.py):
```python
@dataclass
class CodeContext:
    file_path: str                      # Current file name
    code_snippet: str                   # Full file content or context
    change_type: str                    # 'help_comment', 'learning_hint', 'context_completion'
    language: str = "python"            # Programming language
```

**HintRequest** (VS Code extension):
```typescript
interface HintRequest {
    file_path: string;                  // Document file name
    code_snippet: string;               // JSON with full_code, current_line, etc.
    change_type: string;                // Request type
    language: string;                   // Programming language
}
```

**HintResponse**:
```typescript
interface HintResponse {
    success: boolean;                   // Request success status
    hint: string;                       // Generated hint/suggestion
    error?: string;                     // Error message if failed
}
```

### State Management
**Approach**: Stateless request/response model
**Persistence**: None required - each request is independent
**Context**: Full file content sent with each request
**Caching**: Future enhancement for performance optimization

## Performance Specifications

### Latency Requirements
- **Inline Completion Trigger**: <100ms from typing to extension activation
- **Backend Request**: <300ms for LLM hint generation
- **Total User-Perceived Latency**: <500ms from typing to ghost text display
- **Extension Startup**: <3s for activation and backend initialization
- **Backend Startup**: <2s for Python service initialization

### Memory Footprint
- **VS Code Extension**: ~30-50MB (extension host + TypeScript runtime)
- **Python Backend**: ~50-100MB (Python interpreter + LLM client)
- **Per Request**: <1MB (code context + response)
- **Total System**: ~100-150MB for active usage

### Scalability Considerations
- **Concurrent Files**: Supports multiple open Python files simultaneously
- **Stateless Backend**: Each request is independent, no session state
- **Request Queuing**: Extension handles concurrent completion requests
- **Backend Scaling**: Single backend instance serves all open files

## Integration Architecture

### VS Code Extension Integration
**Method**: VS Code Extension API with inline completion provider
**Communication**: HTTP REST API between extension and Python backend
**Features**:
- Inline completion item provider registration
- Ghost text rendering at cursor position
- Automatic backend process management
- Configuration via VS Code settings

**Extension Configuration**:
```json
{
  "watchdog.backendPort": 5555,
  "watchdog.enableDiagnostics": true
}
```

### LLM Integration (Current)
**Architecture**: Configurable LLM provider in Python backend
**Features**:
- Context-aware code generation
- Natural language to code translation (help comments)
- Pattern-based learning hints
- Full-file context understanding

**Integration Patterns**:
- Stateless request/response model
- Full code context passed with each request
- Effects pattern for error handling (Success/Failure)
- Extensible for multiple LLM providers

## Development Constraints

### Technical Limitations
- **Python-only**: Currently supports Python files only (multi-language planned)
- **VS Code dependency**: Requires VS Code to use inline completion features
- **Backend requirement**: Needs Python backend running for hint generation
- **Network dependency**: Extension-backend communication via HTTP (localhost)

### Best Practices Enforcement
- **Extension**: TypeScript with strict type checking enabled
- **Backend**: Type hints, dataclasses, Effects pattern for error handling
- **Code Quality**: PEP 8 compliance (Python), ESLint (TypeScript)
- **Error Handling**: Effects pattern (Success/Failure) not exceptions
- **Testing**: Unit tests for core hint generation logic (planned)

### Performance Constraints
- **Completion Latency**: Must complete within 500ms for good UX
- **Context Size**: Full-file analysis limited by LLM context windows
- **Concurrent Requests**: Backend processes requests sequentially
- **Memory**: Stateless design prevents memory accumulation

This technical context provides comprehensive foundation for Watchdog as an inline code completion tool with clear specifications for all major architectural components.
