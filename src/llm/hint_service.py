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
