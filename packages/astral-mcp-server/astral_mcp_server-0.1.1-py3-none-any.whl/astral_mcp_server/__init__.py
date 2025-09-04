"""
Astral MCP Server

A Model Context Protocol server that enables AI models to query location attestations
using the Astral GraphQL endpoints and APIs.
"""

__version__ = "0.1.1"
__author__ = "Seth Docherty"

from .server import app

__all__ = ["app"]
