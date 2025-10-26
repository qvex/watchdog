from src.llm.ollama_client import check_model_available, generate_hint
from src.effects import Success, Failure

def main():
    print("OLLAMA CLIENT TEST")

    model = "deepseek-coder:6.7b"
    print(f"\nChecking if model '{model}' is available...")

    result = check_model_available(model)

    if isinstance(result, Success):
        if result.value:
            print(f"  Model found: YES")

            print(f"\nGenerating test hint...")
            prompt = "What is a Python list comprehension? Answer in one sentence."

            hint_result = generate_hint(model, prompt, max_tokens=100, temperature=0.3)

            if isinstance(hint_result, Success):
                print(f"\nGenerated hint:")
                print(f"  {hint_result.value}")
            else:
                print(f"\nHint generation failed:")
                print(f"  Error: {hint_result.context}")
        else:
            print(f"  Model found: NO")
            print(f"\nModel '{model}' is not installed.")
            print(f"To install, run: ollama pull {model}")
    else:
        print(f"  Model check failed:")
        print(f"  Error: {result.context}")
        print(f"\nIs Ollama running? Check with: ollama list")

if __name__ == "__main__":
    main()
