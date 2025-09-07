from .cli import main
from .__version__ import __version__
from .version_detection import (
    detect_package_version,
    get_package_version,
    VersionInfo,
    VersionDetectionResult,
)

__all__ = [
    "main",
    "__version__",
    "detect_package_version",
    "get_package_version",
    "VersionInfo",
    "VersionDetectionResult",
]
