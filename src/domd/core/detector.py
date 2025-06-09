"""Project command detector for finding and executing commands in project files.

This module is a backward compatibility layer that imports and re-exports the
ProjectCommandDetector class from the new modular structure.
"""

import logging

from domd.core.project_detection import ProjectCommandDetector

logger = logging.getLogger(__name__)

# Re-export the ProjectCommandDetector class
__all__ = ["ProjectCommandDetector"]
