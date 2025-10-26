from typing import Optional
import json
import urllib.request
import urllib.error
import os
from pathlib import Path
from dotenv import load_dotenv
from src.effects import Result, Success, Failure, ErrorType


OPENAI_BASE_URL = "https://api.openai.com/v1"


def load_api_key() -> Optional[str]:
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(env_path)
    return os.environ.get("OPENAI_API_KEY")


def generate_hint(api_key: str, model: str, prompt: str, max_tokens: int, temperature: float) -> Result[str, ErrorType]:
    try:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{OPENAI_BASE_URL}/chat/completions",
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            hint_text = result["choices"][0]["message"]["content"]
            return Success(hint_text)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return Failure(ErrorType.VALIDATION_ERROR, f"OpenAI API error {e.code}: {error_body}")
    except urllib.error.URLError as e:
        return Failure(ErrorType.VALIDATION_ERROR, f"OpenAI connection failed: {str(e)}")
    except Exception as e:
        return Failure(ErrorType.VALIDATION_ERROR, f"Hint generation failed: {str(e)}")
