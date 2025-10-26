from src.config.config_manager import get_config, save_machine_config

def main():
    print("CONFIGURATION MANAGER TEST")

    config = get_config()

    print(f"\nCurrent Configuration:")
    print(f"  Provider: {config.llm.provider}")
    print(f"  Model: {config.llm.model}")
    print(f"  Max Tokens: {config.llm.max_tokens}")
    print(f"  Temperature: {config.llm.temperature}")
    print(f"  Auto-detected: {config.auto_detected}")

    if config.auto_detected:
        print(f"\nConfiguration Source: Auto-detected from hardware")
        print(f"  (No machine config found at ~/.watchdog/machine-config.json)")
    else:
        print(f"\nConfiguration Source: Machine config (~/.watchdog/machine-config.json)")

    if config.llm.provider == "ollama":
        print(f"\nUsing Ollama (local, GPU-accelerated)")
    else:
        print(f"\nUsing OpenAI API")
        if not config.llm.api_key:
            print(f"  WARNING: OpenAI API key not set")
            print(f"  Set via .env file: OPENAI_API_KEY=your-key-here")

if __name__ == "__main__":
    main()
