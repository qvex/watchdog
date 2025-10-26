from typing import Dict, Any
import json
import urllib.request
import urllib.error
from src.effects import Result, Success, Failure, ErrorType


OLLAMA_BASE_URL = "http://localhost:11434"


def check_model_available(model: str) -> Result[bool, ErrorType]:
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            models = [m["name"] for m in data.get("models", [])]
            return Success(model in models)
    except Exception as e:
        return Failure(ErrorType.VALIDATION_ERROR, f"Model check failed: {str(e)}")


def generate_hint(model: str, prompt: str, max_tokens: int, temperature: float) -> Result[str, ErrorType]:
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            hint_text = result.get("response", "")
            return Success(hint_text)

    except urllib.error.URLError as e:
        return Failure(ErrorType.VALIDATION_ERROR, f"Ollama connection failed: {str(e)}")
    except Exception as e:
        return Failure(ErrorType.VALIDATION_ERROR, f"Hint generation failed: {str(e)}")
