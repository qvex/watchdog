# Session Start Checklist - Watchdog

**ABSOLUTE CRITICAL: Execute at the beginning of EVERY development session**

## Immediate Actions Required

### 1. Code Standards Activation
State: "Following established coding standards from engineering-standards.md for Watchdog development. All implementations require 10/10 confidence and pre-implementation validation protocol completion."

### 2. Critical Priority Hierarchy Acknowledgment
Confirm understanding of absolute priorities:
- PRIORITY 1: Code stability - NEVER implement unless confidence is 10/10
- PRIORITY 2: Code clarity - Self-documenting code with clear naming
- PRIORITY 3: Error handling - Robust error handling with graceful degradation

### 3. Project Context Verification
- Interactive Python learning assistant with file monitoring
- Real-time hint generation based on code deletion detection
- Progressive hint system (4 levels: conceptual → structural → syntax → code)
- VS Code terminal integration for hint display
- Learning session tracking and progress monitoring

### 4. Current Configuration Status Check
```python
from pathlib import Path
import sys

# Verify project structure
required_dirs = ['src', 'hints', 'tests', 'examples']
for dir_name in required_dirs:
    if not Path(dir_name).exists():
        print(f"Missing directory: {dir_name}")
```

### 5. Development Phase Identification
Review current implementation phase:
- Phase 1: Core file watching system - COMPLETE
- Phase 2: Code analysis and AST parsing - COMPLETE
- Phase 3: Hint engine with progressive levels - COMPLETE
- Phase 4: State management and session tracking - COMPLETE
- Phase 5: VS Code terminal UI integration - COMPLETE
- Phase 6: LLM integration (OpenAI/Anthropic) - PLANNED

## Session Continuation Protocol

### For New Sessions
1. Reference engineering-standards.md
2. Review outline.md for complete system architecture
3. Check dev-log.md for recent changes and context
4. Verify virtual environment is activated
5. Test file watcher on example practice file

### For Continued Sessions
1. Maintain established code quality standards
2. Apply clear, descriptive naming conventions
3. Use docstrings for public APIs
4. Follow Python best practices (PEP 8)
5. Update dev-log.md after significant progress
6. Test changes with examples/practice.py

## Pre-Implementation Validation Protocol

**MANDATORY: Complete BEFORE writing any code**

### Step 1: Confidence Assessment
- [ ] Rate implementation confidence (1-10 scale)
- [ ] If confidence < 10: STOP and execute recovery protocol
- [ ] Recovery options: ask clarification, redesign approach, request context, defer implementation

### Step 2: Design Review
- [ ] Summarize implementation plan (3-5 sentences)
- [ ] Explain WHY this approach over alternatives
- [ ] Identify failure modes and mitigations
- [ ] Validate against CRITICAL PRIORITY items

### Step 3: Standards Compliance Check
- [ ] Proper error handling with try-except blocks
- [ ] Type hints for all function signatures
- [ ] Docstrings for all public classes and functions
- [ ] Code follows Python best practices (PEP 8)
- [ ] Self-documenting variable and function names

### Step 4: User Approval Gate
- [ ] Present plan summary, rationale, confidence rating to user
- [ ] Wait for explicit user approval
- [ ] If rejected: return to Step 1 with revised approach

**ONLY proceed to implementation after completing all 4 steps**

## Quality Assurance Checkpoints

### Before Any Code Generation
- [ ] engineering-standards.md referenced and CRITICAL PRIORITIES acknowledged
- [ ] Project terminology confirmed (hint levels, sessions, contexts)
- [ ] Documentation standards acknowledged (docstrings required)
- [ ] Performance requirements understood (file watching latency)
- [ ] Pre-implementation validation protocol completed
- [ ] Confidence level is 10/10

### During Development
- [ ] Type hints for all public functions
- [ ] Docstrings for all public classes and functions
- [ ] Watchdog event handlers implemented correctly
- [ ] AST parsing handles syntax errors gracefully
- [ ] Hint progression logic tested with edge cases
- [ ] Rich terminal output formatted properly

### After Code Generation
- [ ] Docstrings present for all public APIs
- [ ] Type hints present and accurate
- [ ] Descriptive naming verified (no generic names like 'data', 'temp')
- [ ] Python best practices followed
- [ ] Performance tested with file watch operations
- [ ] Error handling covers edge cases
- [ ] Examples/practice.py works as expected

## Red Flag Detection

**Auto-reject if ANY of these are present:**
- Missing docstrings on public classes/functions
- Bare except clauses without proper error handling
- Magic numbers without explanation
- Generic variable names (x, temp, data)
- Missing type hints on public functions
- Hardcoded file paths without Path objects
- Blocking operations in file event handlers

This checklist ensures consistent code quality and adherence to critical priorities across all development sessions regardless of conversation state or Claude restarts.