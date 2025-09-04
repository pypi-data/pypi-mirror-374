"""
Response extraction utilities for Astral MCP API responses.
Handles various response shapes and extracts relevant data.
"""

from __future__ import annotations

from typing import Dict, List, Optional


def extract_location_proofs_list(data: object) -> List[Dict[str, object]]:
    """Extract the attestations array from varying API response shapes.

    Supports shapes like:
    - { "location_proofs": [ ... ] }
    - { "data": [ ... ], "pagination": { ... } }
    - { "data": { "data": [ ... ], ... } }
    - Fallback to other common keys ("results", "items") if present.
    """
    atts: List[Dict[str, object]] = []
    if not isinstance(data, dict):
        return atts

    # 1) Preferred top-level keys
    for key in ("location_proofs", "data", "results", "items"):
        v = data.get(key)
        if isinstance(v, list):
            return [a for a in v if isinstance(a, dict)]

    # 2) Nested under data: {...}
    v = data.get("data")
    if isinstance(v, dict):
        for key in ("location_proofs", "data", "results", "items"):
            inner = v.get(key)
            if isinstance(inner, list):
                return [a for a in inner if isinstance(a, dict)]

    return atts


def extract_pagination(data: object) -> Optional[Dict[str, object]]:
    """Extract pagination object from common response shapes if present."""
    if not isinstance(data, dict):
        return None
    pag = data.get("pagination")
    if isinstance(pag, dict):
        return pag
    inner = data.get("data")
    if isinstance(inner, dict):
        pag2 = inner.get("pagination")
        if isinstance(pag2, dict):
            return pag2
    return None
