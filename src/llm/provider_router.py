from src.effects import Result, Success, Failure, ErrorType
from src.config.config_manager import get_config
from src.config.hardware_detector import check_ollama_installed
from src.llm import ollama_client, openai_service


def generate_hint(prompt: str) -> Result[str, ErrorType]:
    config = get_config()
    api_key = config.llm.api_key or openai_service.load_api_key()

    if api_key:
        result = openai_service.generate_hint(
            api_key=api_key,
            model=config.llm.model,
            prompt=prompt,
            max_tokens=config.llm.max_tokens,
            temperature=config.llm.temperature
        )

        if isinstance(result, Success):
            return result

    if check_ollama_installed():
        return ollama_client.generate_hint(
            model="deepseek-coder:6.7b",
            prompt=prompt,
            max_tokens=config.llm.max_tokens,
            temperature=config.llm.temperature
        )

    if api_key:
        return Failure(ErrorType.VALIDATION_ERROR, "OpenAI API failed and Ollama not available")
    else:
        return Failure(ErrorType.VALIDATION_ERROR, "No LLM provider available (OpenAI key missing, Ollama not installed)")
