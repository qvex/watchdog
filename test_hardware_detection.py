from src.config.hardware_detector import (
    get_hardware_info,
    recommend_provider,
    detect_gpu
)
from src.effects import Success


def main():
    print("HARDWARE DETECTION TEST")

    gpu_result = detect_gpu()
    if isinstance(gpu_result, Success) and gpu_result.value:
        gpu = gpu_result.value
        print(f"\nGPU Detected:")
        print(f"  Vendor: {gpu.vendor}")
        print(f"  Model: {gpu.model}")
        print(f"  VRAM: {gpu.vram_gb} GB")
    else:
        print("\nGPU: Not detected")

    hw_info = get_hardware_info()
    print(f"\nOllama Installed: {hw_info.ollama_installed}")

    provider = recommend_provider(hw_info)
    print(f"\nRecommended Provider: {provider.upper()}")

    print("\nConfiguration Decision:")
    if provider == "ollama":
        print("  System has GPU + Ollama -> Using local Ollama")
        print("  Expected latency: 0.5-1s per hint")
        print("  Cost: FREE")
    else:
        print("  System lacks GPU or Ollama -> Using OpenAI API")
        print("  Expected latency: <1s per hint")
        print("  Estimated cost: ~$0.02-0.04/month")


if __name__ == "__main__":
    main()
