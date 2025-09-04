"""
AutoCleanEEG PubMed MCP Server - A Model Context Protocol server for PubMed research.

This package provides a standalone MCP server that allows AI assistants like Claude
to search and retrieve information from the PubMed biomedical literature database.
"""

__version__ = "1.0.2"
__author__ = "Ernest Pedapati"
__email__ = "ernest.pedapati@cchmc.org"

from .server import main, cli

__all__ = ["main", "cli"]
