from typing import Optional
from dataclasses import dataclass
from src.effects import Result, Success, Failure, ErrorType
from src.llm.provider_router import generate_hint as router_generate_hint


@dataclass(frozen=True, slots=True)
class CodeContext:
    file_path: str
    code_snippet: str
    change_type: str
    language: str = "python"


def build_prompt(context: CodeContext) -> str:
    if context.change_type == 'learning_hint':
        import json
        try:
            data = json.loads(context.code_snippet)
            full_code = data.get('full_code', '')
            current_line = data.get('current_line', '')
            line_number = data.get('line_number', 0)
        except:
            full_code = context.code_snippet
            current_line = ''
            line_number = 0

        prompt_template = f"""You are a learning assistant for Python programming. A student is coding and needs HINTS (not solutions).

FULL CODE CONTEXT:
{full_code}

CURRENT LINE (line {line_number}): {current_line}

CRITICAL ANALYSIS FIRST:
1. Is the current line or function ALREADY COMPLETE? If yes, return empty string (no hint needed)
2. Does the current line already have a return statement? If yes, return empty string
3. Is the student's cursor AFTER code that's already written? If yes, return empty string
4. Only provide hints if something is MISSING or INCOMPLETE

HINT RULES (only if hint is needed):
- If there's a syntax error: # Error: [brief explanation]
- If code is INCOMPLETE: Show syntax pattern options as a comment
- NEVER write the actual solution
- Show PATTERN/TEMPLATE, not the actual answer
- Format: # Pattern: [syntax template with placeholders]
- Keep under 60 characters

Examples:

Input: Line is empty after "def add(a, b):"
BAD: # Hint: What operation combines two numbers?
GOOD: # Pattern: return <result>

Input: Line already has "return a + b"
GOOD: [return empty - no hint needed, code is complete]

Input: "class Calculator:" and line below is empty
BAD: # Hint: What method initializes a class?
GOOD: # Pattern: def __init__(self):

Input: "def add(a b):"
GOOD: # Error: Missing comma between parameters

Input: After "for i in range(10):" on empty line
BAD: # Hint: How do you process each item?
GOOD: # Pattern: # process i here

Input: Empty line after "if x > 0:"
GOOD: # Pattern: # action when true

Input: Line after a complete return statement
GOOD: [return empty - function is complete]

REMEMBER:
- Show SYNTAX PATTERNS with <placeholders>, not questions
- If code is already complete, return NOTHING (empty string)
- Use "# Pattern:" or "# Error:" format only"""
        return prompt_template

    if context.change_type == 'help_comment':
        prompt_template = f"""You are a code suggestion assistant. The user wrote: "help {context.code_snippet}"

Generate ONLY the Python code that implements this request. No explanations, no markdown blocks, just clean executable Python code. Keep it concise (2-8 lines max)."""
        return prompt_template

    if context.change_type == 'context_completion':
        prompt_template = f"""You are a code completion assistant. The user is typing Python code. Based on the context below, suggest the next 1-3 lines of code that would logically follow.

Context:
{context.code_snippet}

Generate ONLY the Python code continuation. No explanations, no markdown blocks, just clean executable Python code. Be concise and context-aware."""
        return prompt_template

    if context.change_type == 'inline_completion':
        prompt_template = f"""You are a code suggestion assistant. The user wrote this comment describing what they want to code:

"{context.code_snippet}"

Generate ONLY the Python code that implements this request. No explanations, no markdown, just clean executable Python code. Keep it concise (2-5 lines max)."""
        return prompt_template

    prompt_template = f"""You are a coding learning assistant. A student is working on Python code.

File: {context.file_path}
Change: {context.change_type}

Current code:
```python
{context.code_snippet}
```

Provide a brief, helpful hint (1-2 sentences) about what they might do next or what pattern to consider. Be encouraging and educational."""

    return prompt_template


def generate_code_hint(context: CodeContext) -> Result[str, ErrorType]:
    prompt = build_prompt(context)
    return router_generate_hint(prompt)


def generate_simple_hint(question: str) -> Result[str, ErrorType]:
    prompt = f"You are a coding learning assistant. Answer this question briefly (1-2 sentences): {question}"
    return router_generate_hint(prompt)
