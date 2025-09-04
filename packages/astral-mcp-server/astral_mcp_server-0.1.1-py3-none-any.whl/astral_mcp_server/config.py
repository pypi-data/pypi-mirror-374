"""
Configuration module for Astral MCP Server

Contains configuration constants and settings for the MCP server.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Astral API base candidates
ASTRAL_API_BASE_URL = "https://api.astral.global"
ASTRAL_DEV_API_BASE_URL = "https://astral-dev.decentralizedgeo.org"


def _load_mcp_json() -> Dict[str, Any]:
    """Load .vscode/mcp.json if present and return its parsed content."""
    try:
        repo_root = Path(__file__).resolve().parents[1]
        mcp_path = repo_root / ".vscode" / "mcp.json"
        if mcp_path.exists():
            with mcp_path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
    except Exception:
        # Ignore any parse/load errors and fall back to defaults
        pass
    return {}


def _determine_base_url() -> str:
    """Determine which Astral API base URL to use.

    Priority order:
      1. Environment variable ASTRAL_USE_DEV_ENDPOINT ("1", "true", "True") -> uses dev endpoint
      2. .vscode/mcp.json -> `mcp_agent.use_dev_endpoint` boolean and optional `mcp_agent.dev_endpoint`
      3. Default production ASTRAL_API_BASE_URL
    """
    # Check environment flag first
    env_flag = os.getenv("ASTRAL_USE_DEV_ENDPOINT")
    if env_flag is not None and env_flag.lower() in {"1", "true", "yes"}:
        # Allow overriding dev endpoint URL via env var too
        return os.getenv("ASTRAL_DEV_ENDPOINT", ASTRAL_DEV_API_BASE_URL)

    # Next check workspace mcp.json
    mcp_conf = _load_mcp_json().get("mcp_agent", {})
    if isinstance(mcp_conf, dict):
        use_dev = mcp_conf.get("use_dev_endpoint", False)
        if use_dev:
            return mcp_conf.get("dev_endpoint", ASTRAL_DEV_API_BASE_URL)

    # Fallback to production
    return ASTRAL_API_BASE_URL


# Resolve base URL at import time
ASTRAL_BASE_URL = _determine_base_url()

# Endpoints built from resolved base URL
ASTRAL_HEALTH_ENDPOINT = f"{ASTRAL_BASE_URL}/health"
ASTRAL_LOCATION_PROOFS_ENDPOINT = f"{ASTRAL_BASE_URL}/api/v0/location-proofs"
ASTRAL_CONFIG_ENDPOINT = f"{ASTRAL_BASE_URL}/api/v0/config"

# HTTP Client Configuration
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3

# MCP Server Configuration
SERVER_NAME = "astral-mcp-server"
SERVER_VERSION = "0.1.0"


def get_api_key() -> Optional[str]:
    """
    Retrieve API key from environment variables.

    Returns:
        Optional[str]: API key if set, None otherwise
    """
    return os.getenv("ASTRAL_API_KEY")


def is_using_dev_endpoint() -> bool:
    """Return True if the resolved base URL is a dev endpoint (heuristic by comparing to prod)."""
    return ASTRAL_BASE_URL != ASTRAL_API_BASE_URL
