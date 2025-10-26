from typing import Optional
from dataclasses import dataclass
from pathlib import Path
import json
from src.config.hardware_detector import get_hardware_info, recommend_provider


@dataclass(frozen=True, slots=True)
class LLMConfig:
    provider: str
    model: str
    api_key: Optional[str]
    max_tokens: int
    temperature: float


@dataclass(frozen=True, slots=True)
class WatchdogConfig:
    llm: LLMConfig
    auto_detected: bool


def get_default_config() -> WatchdogConfig:
    llm = LLMConfig(
        provider="openai",
        model="gpt-4o-mini",
        api_key=None,
        max_tokens=1000,
        temperature=0.3
    )
    return WatchdogConfig(llm=llm, auto_detected=True)


def load_machine_config() -> Optional[WatchdogConfig]:
    config_path = Path.home() / ".watchdog" / "machine-config.json"
    if not config_path.exists():
        return None

    try:
        data = json.loads(config_path.read_text())
        llm = LLMConfig(**data["llm"])
        return WatchdogConfig(llm=llm, auto_detected=False)
    except Exception:
        return None


def save_machine_config(config: WatchdogConfig) -> bool:
    config_path = Path.home() / ".watchdog" / "machine-config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        data = {
            "llm": {
                "provider": config.llm.provider,
                "model": config.llm.model,
                "api_key": config.llm.api_key,
                "max_tokens": config.llm.max_tokens,
                "temperature": config.llm.temperature
            }
        }
        config_path.write_text(json.dumps(data, indent=2))
        return True
    except Exception:
        return False


def get_config() -> WatchdogConfig:
    machine_config = load_machine_config()
    if machine_config:
        return machine_config
    return get_default_config()
