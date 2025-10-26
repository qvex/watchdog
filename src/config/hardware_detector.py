from typing import Optional
from dataclasses import dataclass
from pathlib import Path
import subprocess
import platform
from src.effects import Result, Success, Failure, ErrorType


@dataclass(frozen=True, slots=True)
class GPUInfo:
    vendor: str
    model: str
    vram_gb: int


@dataclass(frozen=True, slots=True)
class HardwareInfo:
    has_gpu: bool
    gpu_info: Optional[GPUInfo]
    ollama_installed: bool


def detect_gpu() -> Result[Optional[GPUInfo], ErrorType]:
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(',')
            model = parts[0].strip()
            vram = int(float(parts[1].strip()) / 1024)
            return Success(GPUInfo(vendor="NVIDIA", model=model, vram_gb=vram))
        return Success(None)
    except Exception:
        return Success(None)


def check_ollama_installed() -> bool:
    if platform.system() == "Windows":
        paths = [
            Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe",
            Path("C:/Program Files/Ollama/ollama.exe"),
            Path("C:/Program Files (x86)/Ollama/ollama.exe"),
        ]
        for path in paths:
            if path.exists():
                try:
                    result = subprocess.run([str(path), 'list'], capture_output=True, timeout=5)
                    return result.returncode == 0
                except Exception:
                    return False
        return False
    else:
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False


def get_hardware_info() -> HardwareInfo:
    gpu_result = detect_gpu()
    gpu_info = gpu_result.value if isinstance(gpu_result, Success) else None
    has_gpu = gpu_info is not None
    ollama_installed = check_ollama_installed()
    return HardwareInfo(has_gpu=has_gpu, gpu_info=gpu_info, ollama_installed=ollama_installed)


def recommend_provider(hw_info: HardwareInfo) -> str:
    if hw_info.has_gpu and hw_info.ollama_installed:
        return "ollama"
    return "openai"
