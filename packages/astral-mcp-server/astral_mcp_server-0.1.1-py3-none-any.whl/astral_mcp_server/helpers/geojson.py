"""GeoJSON helper utilities for building mapping-friendly outputs."""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional


def find_point_geometry(obj: object) -> Optional[Dict[str, object]]:
    """Recursively find a GeoJSON Point geometry within an object."""
    if isinstance(obj, dict):
        t = obj.get("type")
        coords = obj.get("coordinates")
        if (
            isinstance(t, str)
            and t.lower() == "point"
            and isinstance(coords, (list, tuple))
            and len(coords) == 2
        ):
            try:
                lon = float(coords[0])
                lat = float(coords[1])
                return {"type": "Point", "coordinates": [lon, lat]}
            except Exception:
                return None
        for v in obj.values():
            g = find_point_geometry(v)
            if g is not None:
                return g
    elif isinstance(obj, list):
        for v in obj:
            g = find_point_geometry(v)
            if g is not None:
                return g
    return None


def point_from_latlon(lat_val: object, lon_val: object) -> Optional[Dict[str, object]]:
    """Return GeoJSON Point from latitude/longitude values if both are numeric.

    Ensures GeoJSON coordinate order [lon, lat].
    """
    try:
        if lat_val is None or lon_val is None:
            return None
        lat = float(lat_val)  # type: ignore[arg-type]
        lon = float(lon_val)  # type: ignore[arg-type]
        return {"type": "Point", "coordinates": [lon, lat]}
    except Exception:
        return None


def parse_location_field(loc: str) -> Optional[Dict[str, object]]:
    """Parse a `location` string into a GeoJSON Point if possible.

    Supports:
    - JSON string containing GeoJSON (e.g., '{"type":"Point",...}').
    - "lat, lon" or "lat lon" decimal strings.
    """
    s = loc.strip()
    if not s:
        return None

    # Case 1: JSON string with potential GeoJSON
    if s.startswith("{") and s.endswith("}"):
        try:
            obj = json.loads(s)
            return find_point_geometry(obj)
        except Exception:
            return None

    # Case 2: "lat, lon" or "lat lon" decimal strings
    m = re.match(r"^\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)\s*$", s)
    if not m:
        m = re.match(r"^\s*([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)\s*$", s)
    if m:
        try:
            lat = float(m.group(1))
            lon = float(m.group(2))
            return {"type": "Point", "coordinates": [lon, lat]}
        except Exception:
            return None

    return None


def attestation_to_feature(att: Dict[str, object]) -> Optional[Dict[str, object]]:
    """Map an attestation-like dict to a GeoJSON Feature if coords exist.

    Resolution order for geometry (prefer explicit numeric fields):
    1) Build from explicit `latitude` and `longitude` fields.
    2) Embedded GeoJSON anywhere in `att`.
    3) Parse `location` string (GeoJSON JSON or "lat, lon").
    """
    # 1) Prefer explicit latitude/longitude fields
    geom = point_from_latlon(att.get("latitude"), att.get("longitude"))

    # 2) Try embedded GeoJSON in the object
    if geom is None:
        geom = find_point_geometry(att)

    # 3) Optional: parse the `location` field if needed
    if geom is None:
        loc = att.get("location")
        if isinstance(loc, str):
            geom = parse_location_field(loc)

    if geom is None:
        return None

    props: Dict[str, object] = {}
    for key in ("uid", "timestamp", "chain", "prover", "subject", "srs", "revoked"):
        if key in att:
            props[key] = att[key]
    return {"type": "Feature", "geometry": geom, "properties": props}


def feature_collection_from_attestations(
    atts: List[Dict[str, object]]
) -> Dict[str, object]:
    """Build a FeatureCollection from a list of attestations."""
    features: List[Dict[str, object]] = []
    for att in atts:
        f = attestation_to_feature(att)
        if f is not None:
            features.append(f)
    return {"type": "FeatureCollection", "features": features}


def geojson_blocks_for_single(
    data: object, result: Dict[str, object]
) -> List[Dict[str, object]]:
    """Build JSON content blocks [result, FeatureCollection] for a single item.

    Args:
        data: The attestation data object (may be wrapped in location_proof key)
        result: The standard API result dictionary

    Returns:
        List of two JSON content blocks: [result, FeatureCollection]
    """
    att_obj = data.get("location_proof") if isinstance(data, dict) else None
    if att_obj is None and isinstance(data, dict):
        att_obj = data
    feature = attestation_to_feature(att_obj) if isinstance(att_obj, dict) else None
    features: List[Dict[str, object]] = []
    if feature is not None:
        features.append(feature)
    fc: Dict[str, object] = {"type": "FeatureCollection", "features": features}
    return [
        {"type": "json", "data": result},
        {"type": "json", "data": fc},
    ]
