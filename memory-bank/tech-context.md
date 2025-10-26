# Technical Context: Watchdog

## System Architecture Overview

### Complete System Architecture
- **outline.md**: The primary reference document containing complete implementation code for all system components. This file serves as the single source of truth for the system's architecture and implementation details.

### Core Architecture Pattern
**Primary Pattern**: Observer pattern with file system event handlers
**Code Structure**: Modular component design with clear separation of concerns
**State Management**: In-memory session state with dataclass-based structures
**Event Flow**: File change → Analysis → Hint generation → Terminal display

## Current Development Status

### Implementation Phase
**Current Version**: v0.1.0 (Template Complete)
**Status**: All core components implemented from outline.md specification
**Next Phase**: Testing and validation with real practice files

### Core Components Status

#### 1. File Watching System (COMPLETE)
**File**: src/file_watcher.py
**Key Classes**:
- `CodeChangeEvent`: Dataclass capturing before/after states with deleted content detection
- `PythonFileWatcher`: FileSystemEventHandler with debounce and change callbacks

**Features Implemented**:
- Observer pattern for file monitoring
- Debounce mechanism (0.5s) prevents rapid-fire events
- Deleted line extraction using difflib.unified_diff
- Deleted function detection using AST comparison
- Callback-based event notification

**Performance Characteristics**:
- File change detection: <500ms from save to event trigger
- AST parsing overhead: ~50-100ms for typical files
- Memory per watcher: ~5-10MB

#### 2. Code Analysis Engine (COMPLETE)
**File**: src/code_analyzer.py
**Key Classes**:
- `CodeContext`: Dataclass with surrounding_code, missing_element, expected_pattern, difficulty_level
- `CodeAnalyzer`: Pattern detection and difficulty estimation

**Features Implemented**:
- AST-based code structure analysis
- Pattern detection for: loops, conditionals, functions, classes, comprehensions, context managers, error handling
- Difficulty estimation (1-5 scale) based on deleted pattern type
- Graceful SyntaxError handling for incomplete code
- Function signature extraction

**Supported Patterns**:
```python
{
    'loops': ['for', 'while'],
    'conditionals': ['if', 'elif', 'else'],
    'functions': ['def'],
    'classes': ['class'],
    'comprehensions': ['[', 'for', 'in'],
    'context_managers': ['with'],
    'error_handling': ['try', 'except', 'finally']
}
```

**Difficulty Mapping**:
- loops: 2/5
- conditionals: 2/5
- functions: 3/5
- comprehensions: 4/5
- classes: 4/5
- error_handling: 3/5
- unknown: 1/5

#### 3. Progressive Hint Engine (COMPLETE)
**File**: src/hint_engine.py
**Key Classes**:
- `Hint`: Dataclass with level (1-4), content, best_practice
- `HintEngine`: Template-based hint generation with progression logic

**4-Level Hint System**:
1. **Level 1 - Conceptual**: General thinking prompts ("Think about repeating an action...")
2. **Level 2 - Structural**: Component identification ("You'll need: function definition, parameters...")
3. **Level 3 - Syntax**: Syntax templates ("Syntax: `for item in collection:`")
4. **Level 4 - Code**: Complete code examples with comments

**Best Practice Integration**:
- Loops: enumerate() for index+value, list comprehensions, avoid modifying while iterating
- Functions: Descriptive names, single responsibility, docstrings, type hints
- Conditionals: elif vs multiple if, ternary operators, early returns

**Hint Progression**:
- Time threshold: 30 seconds per level
- Maximum level: 4 (complete solution)
- Random selection from template pool for variety

#### 4. State Management (COMPLETE)
**File**: src/state_manager.py
**Key Classes**:
- `LearningSession`: Dataclass tracking file_path, started_at, current_hint_level, hints_shown, time_on_current_task, task_completed
- `StateManager`: Session lifecycle and progress tracking

**Features Implemented**:
- Session initialization with timestamp
- Hint recording with history tracking
- Time tracking for hint progression decisions
- Session completion marking
- Session history for analytics
- Timer reset on code updates

#### 5. VS Code Terminal Integration (COMPLETE)
**File**: src/vscode_integration.py
**Key Classes**:
- `VSCodeIntegration`: Rich console output with styled panels

**Features Implemented**:
- Hint display with level-based emoji indicators:
  - Level 1: 🤔 (thinking)
  - Level 2: 💡 (light bulb)
  - Level 3: ✏️ (pencil)
  - Level 4: 📝 (notebook)
- Markdown rendering for code examples
- Styled panels with borders
- Progress tracking display
- Encouragement message rotation

#### 6. Main Application Coordinator (COMPLETE)
**File**: main.py
**Key Classes**:
- `PythonLearningBot`: Main coordinator orchestrating all components

**Features Implemented**:
- Component initialization and wiring
- Code change event handling
- Hint level progression logic (30s per level)
- Session lifecycle management
- CLI argument parsing (file path)
- Graceful shutdown on Ctrl+C

## Technical Stack Specifications

### Core Technologies
**Runtime**: Python 3.8+ (type hints, dataclasses, AST features)
**File Monitoring**: watchdog 3.0.0 (Observer pattern)
**Terminal UI**: rich 13.7.0 (styled console output)
**Code Analysis**: Built-in ast module (Abstract Syntax Trees)
**Diff Analysis**: Built-in difflib module (unified diff)

### Future Integrations (Planned)
**LLM Services**: OpenAI 1.3.0, Anthropic 0.7.0
**Environment Management**: python-dotenv 1.0.0
**Version Control Integration**: GitPython 3.1.40

## Development Environment

### Required Dependencies
```
watchdog==3.0.0      # File system event monitoring
rich==13.7.0         # Terminal formatting and panels
gitpython==3.1.40    # Version control integration (future)
openai==1.3.0        # LLM integration (future)
anthropic==0.7.0     # LLM integration (future)
python-dotenv==1.0.0 # Environment variable management (future)
```

### Environment Setup
```bash
# Virtual environment creation
python -m venv venv

# Activation (Unix/macOS)
source venv/bin/activate

# Activation (Windows)
venv\Scripts\activate

# Dependency installation
pip install -r requirements.txt
```

### Project Structure
```
watchdog/
├── src/
│   ├── __init__.py                 # Package marker
│   ├── file_watcher.py            # 145 lines: Event detection
│   ├── code_analyzer.py           # 250 lines: AST analysis
│   ├── hint_engine.py             # 393 lines: Hint generation
│   ├── state_manager.py           # 152 lines: Session tracking
│   └── vscode_integration.py      # 114 lines: Terminal UI
├── hints/
│   └── patterns.json              # Custom hint templates (future)
├── tests/
│   └── test_hint_engine.py        # Unit tests (future)
├── examples/
│   └── practice.py                # Example practice file
├── project_configs/
│   ├── engineering-standards.md   # Development standards
│   ├── session-start-checklist.md # Quality gates
│   └── dev-log.md                 # Development history
├── memory-bank/
│   ├── projectbrief.md            # Project overview
│   ├── tech-context.md            # This file
│   ├── progress.md                # Milestone tracking
│   └── active-context.md          # Current development state
├── main.py                        # 90 lines: Application entry
├── outline.md                     # Complete implementation spec
├── requirements.txt               # Dependencies
├── setup.py                       # Package configuration
└── README.md                      # User documentation
```

## Data Architecture

### State Management Schema

**LearningSession Dataclass**:
```python
@dataclass
class LearningSession:
    file_path: str                      # Monitored file path
    started_at: datetime                # Session start timestamp
    current_hint_level: int = 1         # Current hint progression (1-4)
    hints_shown: List[str] = []         # History of displayed hints
    time_on_current_task: float = 0     # Seconds since last code update
    task_completed: bool = False        # Task completion flag
```

**CodeContext Dataclass**:
```python
@dataclass
class CodeContext:
    surrounding_code: str               # Remaining code after deletion
    missing_element: str                # Detected pattern type
    expected_pattern: Optional[str]     # Specific keyword/pattern
    difficulty_level: int               # 1-5 difficulty rating
```

**Hint Dataclass**:
```python
@dataclass
class Hint:
    level: int                          # 1-4 hint progression
    content: str                        # Hint text/code
    best_practice: Optional[str] = None # Related best practice tip
```

### Session Storage
**Storage**: In-memory (Python object)
**Persistence**: None (session-scoped, resets on restart)
**History**: Maintained in StateManager.sessions_history list
**Retention**: Duration of application lifetime

## Performance Specifications

### Latency Requirements
- **File Change Detection**: <500ms from save to event handler
- **AST Parsing**: <100ms for files up to 1000 lines
- **Hint Generation**: <50ms for template lookup and formatting
- **Terminal Display**: <100ms for rich panel rendering
- **Total Responsiveness**: <1s from code save to hint display

### Memory Footprint
- **Base Application**: ~10-15MB (Python interpreter + imports)
- **Per Watcher Instance**: ~5-10MB (observer thread + callbacks)
- **Session State**: <1MB (session data + hint history)
- **AST Parse Tree**: ~2-5MB for typical practice files
- **Total Expected**: <50MB for normal usage

### Scalability Considerations
- **Single File Focus**: One file per application instance
- **Multiple Instances**: Separate process per monitored file (if needed)
- **Session History**: Grows with number of hints (acceptable for learning sessions)
- **Pattern Templates**: Fixed size, loaded once at startup

## Integration Architecture

### VS Code Terminal Integration
**Method**: Standard output (stdout) with ANSI escape codes
**Library**: rich Console for styled output
**Features**:
- Markdown rendering for code examples
- Styled panels with borders and titles
- Progress indicators and emoji icons
- Color-coded hint levels

**Terminal Requirements**:
- ANSI color support
- UTF-8 encoding for emoji
- Minimum width: 80 characters for panel display

### Future LLM Integration (Planned)
**OpenAI Integration**:
- Dynamic hint generation based on actual code context
- Personalized explanations adapted to user skill level
- Natural language understanding of deleted code intent

**Anthropic Integration**:
- Alternative LLM provider for hint generation
- Claude-specific prompt engineering for educational content

**Integration Pattern**:
- Fallback chain: LLM → Templates → Generic hints
- API key management via python-dotenv
- Rate limiting and cost controls
- Caching of LLM-generated hints

## Development Constraints

### Technical Limitations
- Python AST limitations: Only valid Python syntax parsable
- File system access: Requires read/write permissions on monitored file
- Terminal dependency: Requires terminal access for rich output
- Single file scope: Cannot monitor multiple files simultaneously per instance

### Best Practices Enforcement
- Type hints for all function signatures
- Docstrings for all public classes and methods
- PEP 8 compliance for code style
- Graceful error handling with try-except blocks
- Meaningful variable names (no single-letter variables)

### Performance Constraints
- Debounce delay: Minimum 0.5s between file change events
- AST parsing: Limited to files <10,000 lines (practical limit)
- Hint progression: Fixed 30s per level threshold
- Memory: Session history unbounded (acceptable for learning sessions)

This technical context provides comprehensive foundation for Watchdog development with clear specifications for all major architectural components.
