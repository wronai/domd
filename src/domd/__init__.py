"""DoMD Package"""

__version__ = "0.1.0"

from .detector import ProjectCommandDetector
from .cli import main

__all__ = ["ProjectCommandDetector", "main", "__version__"]
