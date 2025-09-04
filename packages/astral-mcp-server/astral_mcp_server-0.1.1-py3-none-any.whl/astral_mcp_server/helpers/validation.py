"""Validation and query param helpers for Astral MCP server."""

from __future__ import annotations

import re
from typing import Dict, Optional, Union

# Shared constants
ERROR_TEXT_TRUNCATE_LENGTH = 500
MIN_QUERY_LIMIT = 1
MAX_QUERY_LIMIT = 100


def validate_query_args(
    limit: Optional[int],
    offset: Optional[int],
    prover: Optional[str],
    subject: Optional[str] = None,
    from_timestamp: Optional[str] = None,
    to_timestamp: Optional[str] = None,
    bbox: Optional[Union[str, list]] = None,
) -> None:
    if limit is not None and (
        not isinstance(limit, int) or limit < MIN_QUERY_LIMIT or limit > MAX_QUERY_LIMIT
    ):
        raise ValueError(
            f"limit must be an integer between {MIN_QUERY_LIMIT} and {MAX_QUERY_LIMIT}"
        )
    if offset is not None and (not isinstance(offset, int) or offset < 0):
        raise ValueError("offset must be a non-negative integer")
    if prover is not None and not re.match(r"^0x[a-fA-F0-9]{40}$", prover):
        raise ValueError(
            "prover must be a valid 40-character hexadecimal address starting with 0x"
        )
    if subject is not None and not re.match(r"^0x[a-fA-F0-9]{40}$", subject):
        raise ValueError(
            "subject must be a valid 40-character hexadecimal address starting with 0x"
        )
    if from_timestamp is not None and not isinstance(from_timestamp, str):
        raise ValueError("from_timestamp must be an ISO date string")
    if to_timestamp is not None and not isinstance(to_timestamp, str):
        raise ValueError("to_timestamp must be an ISO date string")

    # bbox may be provided as a comma-separated string or a list/tuple of 4 numbers
    if bbox is not None:
        coords = None
        if isinstance(bbox, str):
            parts = [p.strip() for p in bbox.split(",") if p.strip() != ""]
            try:
                coords = [float(p) for p in parts]
            except ValueError:
                raise ValueError("bbox string must contain four numeric values separated by commas")
        elif isinstance(bbox, (list, tuple)):
            try:
                coords = [float(p) for p in bbox]
            except (TypeError, ValueError):
                raise ValueError("bbox list must contain four numeric values")
        else:
            raise ValueError("bbox must be a comma-separated string or a list of four numbers")

        if coords is None or len(coords) != 4:
            raise ValueError("bbox must contain exactly four numeric values: [minLng,minLat,maxLng,maxLat]")

        min_lng, min_lat, max_lng, max_lat = coords
        if not (-180.0 <= min_lng <= 180.0 and -180.0 <= max_lng <= 180.0):
            raise ValueError("bbox longitude values must be between -180 and 180")
        if not (-90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0):
            raise ValueError("bbox latitude values must be between -90 and 90")
        if not (min_lng < max_lng and min_lat < max_lat):
            raise ValueError("bbox values must satisfy minLng < maxLng and minLat < maxLat")


def build_query_params(
    chain: Optional[str],
    prover: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
    subject: Optional[str] = None,
    from_timestamp: Optional[str] = None,
    to_timestamp: Optional[str] = None,
    bbox: Optional[Union[str, list]] = None,
) -> Dict[str, Union[str, int]]:
    params: Dict[str, Union[str, int]] = {}
    if chain is not None:
        params["chain"] = chain
    if prover is not None:
        params["prover"] = prover
    if subject is not None:
        params["subject"] = subject
    if from_timestamp is not None:
        params["fromTimestamp"] = from_timestamp
    if to_timestamp is not None:
        params["toTimestamp"] = to_timestamp
    if bbox is not None:
        # Normalize bbox to a comma-separated string: minLng,minLat,maxLng,maxLat
        if isinstance(bbox, (list, tuple)):
            bbox_str = ",".join(str(float(x)) for x in bbox)
        else:
            bbox_str = bbox
        params["bbox"] = bbox_str
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    return params
