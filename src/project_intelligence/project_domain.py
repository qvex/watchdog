from typing import Set, List
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DynamicProjectType:
    name: str
    category: str
    detection_method: str
    confidence: float


@dataclass(frozen=True, slots=True)
class ProjectConvention:
    pattern_name: str
    description: str
    hint_template: str
    examples: List[str]


@dataclass(frozen=True, slots=True)
class FrameworkSignature:
    imports: Set[str]
    config_files: Set[str]
    confidence_threshold: float


@dataclass(frozen=True, slots=True)
class ProjectDetectionResult:
    project_type: DynamicProjectType
    conventions: List[ProjectConvention]
    detected_imports: Set[str]
    detected_configs: Set[str]
    needs_confirmation: bool


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    project_type: DynamicProjectType
    conventions: List[ProjectConvention]
    framework_version: str
    root_path: str
    confirmed_by_user: bool
