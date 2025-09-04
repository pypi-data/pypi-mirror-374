"""
Zeeker - Database customization tool with project management capabilities.

A tool for creating, validating, and deploying database customizations
for Zeeker's Datasette-based system using sqlite-utils and following
the three-pass asset system.
"""

from .core import (
    DatabaseCustomization,
    DeploymentChanges,
    ValidationResult,
    ZeekerDeployer,
    ZeekerGenerator,
    ZeekerProject,
    ZeekerProjectManager,
    ZeekerValidator,
)

__version__ = "0.5.1"
__all__ = [
    "ValidationResult",
    "DatabaseCustomization",
    "DeploymentChanges",
    "ZeekerProject",
    "ZeekerProjectManager",
    "ZeekerValidator",
    "ZeekerGenerator",
    "ZeekerDeployer",
]
