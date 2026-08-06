"""Platform registry — maps platform name → handler class."""
from __future__ import annotations

from typing import Type

from src.automation.platforms.base import BasePlatform

_REGISTRY: dict[str, str] = {
    "linkedin":     "src.automation.platforms.linkedin:LinkedInPlatform",
    "indeed":       "src.automation.platforms.indeed:IndeedPlatform",
    "glassdoor":    "src.automation.platforms.glassdoor:GlassdoorPlatform",
    "ziprecruiter": "src.automation.platforms.ziprecruiter:ZipRecruiterPlatform",
    "dice":         "src.automation.platforms.dice:DicePlatform",
    "universal":    "src.automation.platforms.universal:UniversalPlatform",
}

AVAILABLE_PLATFORMS = list(_REGISTRY.keys())


def get_platform(name: str) -> Type[BasePlatform] | None:
    """Import and return the platform class for `name`, or None if not found."""
    spec = _REGISTRY.get(name.lower())
    if spec is None:
        return None
    module_path, class_name = spec.rsplit(":", 1)
    try:
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        from src.logging import logger
        logger.warning("Could not load platform '{}': {}", name, exc)
        return None
