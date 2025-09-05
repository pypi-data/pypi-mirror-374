"""
OHFP (Open Host Factory Plugin) - Main package namespace.

This package provides the ohfp namespace for importing package components.
Users can import as: from ohfp.domain import ... or import ohfp.cli
"""

__version__ = "0.1.0"

import api
import application

# Import submodules using absolute imports
import cli
import config
import domain
import infrastructure
import providers

__all__: list[str] = [
    "api",
    "application",
    "cli",
    "config",
    "domain",
    "infrastructure",
    "providers",
]
