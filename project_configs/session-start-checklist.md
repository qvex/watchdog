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
- AI-powered code completion tool similar to GitHub Copilot
- Inline ghost text suggestions as you type in VS Code
- Context-aware hints based on full-file analysis
- Help comment feature (`# help ...`) for targeted code generation
- Learning-focused hints that teach patterns rather than just providing solutions

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
- Phase 1: VS Code extension with inline completion provider - COMPLETE
- Phase 2: Python LLM backend for hint generation - COMPLETE
- Phase 3: Context-aware suggestions and smart filtering - COMPLETE
- Phase 4: Help comment system - COMPLETE
- Phase 5: Optional terminal file monitor - COMPLETE
- Phase 6: Enhanced LLM features and multi-language support - PLANNED

## Session Continuation Protocol

### For New Sessions
1. Reference engineering-standards.md for development standards
2. Review dev-log.md (last 200 lines) for recent changes and context
3. Understand VS Code extension + Python backend architecture
4. Check extension manifest (vscode-extension/package.json)
5. Review hint service implementation (src/llm/hint_service.py)

### For Continued Sessions
1. Maintain established code quality standards
2. TypeScript strict mode for extension code
3. Effects pattern (Success/Failure) for Python backend
4. Follow Python best practices (PEP 8) and TypeScript/ESLint standards
5. Update dev-log.md after significant progress
6. Test inline completions in VS Code with Python files

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
- [ ] TypeScript strict mode enabled for extension
- [ ] Type hints for all Python backend functions
- [ ] VS Code extension API used correctly
- [ ] HTTP communication handles timeouts and errors
- [ ] Backend startup/shutdown managed properly
- [ ] Inline completion filtering logic correct

### After Code Generation
- [ ] Extension compiles without TypeScript errors
- [ ] Backend processes requests without errors
- [ ] Type hints present and accurate
- [ ] Descriptive naming verified (no generic names)
- [ ] Effects pattern used for error handling (Success/Failure)
- [ ] Inline completions appear correctly in VS Code
- [ ] Help comments trigger code generation properly

## Red Flag Detection

**Auto-reject if ANY of these are present:**
- Missing type hints on public functions (TypeScript or Python)
- Try-catch error handling instead of Effects pattern in Python backend
- Bare except clauses without proper error handling
- Magic numbers without explanation
- Generic variable names (x, temp, data)
- Hardcoded ports or paths without configuration
- Blocking operations in VS Code extension main thread

This checklist ensures consistent code quality and adherence to critical priorities across all development sessions regardless of conversation state or Claude restarts.