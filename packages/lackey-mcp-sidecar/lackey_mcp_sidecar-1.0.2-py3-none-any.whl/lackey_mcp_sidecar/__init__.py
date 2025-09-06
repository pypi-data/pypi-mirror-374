"""Lackey MCP Sidecar - FastAPI web interface for task management."""

from importlib.metadata import PackageNotFoundError, version

try:  # pragma: no cover - version is provided by packaging
    __version__ = version("lackey-mcp-sidecar")
except PackageNotFoundError:  # pragma: no cover - fallback for local usage
    __version__ = "0.0.0"

__all__ = ["__version__"]
