"""Version information for niti."""

import importlib.metadata

def get_version() -> str:
    """Get the version of niti from package metadata.
    
    Returns:
        Version string from pyproject.toml, or fallback version.
    """
    try:
        return importlib.metadata.version("niti")
    except importlib.metadata.PackageNotFoundError:
        # Fallback for development/editable installs
        return "0.1.5"

__version__ = get_version()