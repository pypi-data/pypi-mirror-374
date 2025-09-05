"""Package metadata - works in both development and production."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _get_from_project_yml() -> Optional[dict]:
    """Try to read from .project.yml (development mode)."""
    try:
        import yaml

        project_root = Path(__file__).parent.parent
        project_file = project_root / ".project.yml"
        if project_file.exists():
            with open(project_file) as f:
                return yaml.safe_load(f)  # type: ignore[no-any-return]
    except Exception as e:
        logger.debug("Failed to read project.yml: %s", e)
    return None


def _get_from_package_metadata() -> Optional[dict]:
    """Try to read from package metadata (installed mode)."""
    try:
        from importlib.metadata import metadata, version

        meta = metadata("open-hostfactory-plugin")
        return {
            "project": {
                "name": meta["Name"],
                "short_name": "ohfp",  # Not in package metadata, hardcode this one
                "version": version("open-hostfactory-plugin"),
                "description": meta["Summary"],
                "author": meta["Author"],
                "email": meta["Author-email"],
                "license": meta["License"],
            },
            "repository": {
                "org": "awslabs",  # Not in package metadata
                "name": "open-hostfactory-plugin",  # Not in package metadata
                "registry": "ghcr.io",  # Not in package metadata
            },
        }
    except Exception as e:
        logger.debug("Failed to read package metadata: %s", e)
    return None


# Try development first, then production
config = _get_from_project_yml() or _get_from_package_metadata()

if not config:
    # Final fallback - used when both .project.yml and package metadata are unavailable
    # This occurs in scenarios like: missing .project.yml file, corrupted package installation,
    # missing dependencies (PyYAML), or constrained deployment environments
    config = {
        "project": {
            "name": "open-hostfactory-plugin",
            "short_name": "ohfp",
            # PEP 440 compliant development version - prevents PyPI normalization from "0.1.0-dev" to "0.1.0.dev0"
            # CI builds will override this with dynamic versions like "0.1.0.dev20250822145030+abc1234"
            "version": "0.1.0.dev0",
            "description": "Cloud provider integration plugin for IBM Spectrum Symphony Host Factory",
            "author": "AWS Professional Services",
            "email": "aws-proserve@amazon.com",
            "license": "Apache-2.0",
        },
        "repository": {
            "org": "awslabs",
            "name": "open-hostfactory-plugin",
            "registry": "ghcr.io",
        },
    }

# Export the same interface
PACKAGE_NAME = config["project"]["name"]
PACKAGE_NAME_SHORT = config["project"].get("short_name", "ohfp")
__version__ = config["project"]["version"]
VERSION = __version__
DESCRIPTION = config["project"]["description"]
AUTHOR = config["project"]["author"]
EMAIL = config["project"]["email"]

# Repository metadata
REPO_ORG = config["repository"]["org"]
REPO_NAME = config["repository"]["name"]
CONTAINER_REGISTRY = config["repository"].get("registry", "ghcr.io")

# Derived values
PACKAGE_NAME_PYTHON = PACKAGE_NAME.replace("-", "_")
REPO_URL = f"https://github.com/{REPO_ORG}/{REPO_NAME}"
REPO_ISSUES_URL = f"{REPO_URL}/issues"
DOCS_URL = f"https://{REPO_ORG}.github.io/{REPO_NAME}"
CONTAINER_IMAGE = PACKAGE_NAME
