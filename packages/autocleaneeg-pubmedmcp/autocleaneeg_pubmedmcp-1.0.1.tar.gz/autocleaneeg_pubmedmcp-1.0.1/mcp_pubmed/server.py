#!/usr/bin/env python3
"""
AutoCleanEEG PubMed MCP Server

A standalone MCP server for Claude Desktop that provides access to PubMed research database.
Supports optional NCBI API key for enhanced rate limits.
"""

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field, EmailStr, field_validator

# Configuration
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
DEFAULT_EMAIL = "mcp-client@example.com"

# Get NCBI API key from environment (optional but recommended)
NCBI_API_KEY = os.getenv("PUBMED_API_KEY") or os.getenv("NCBI_API_KEY")

# Rate limiting info
if NCBI_API_KEY:
    print(
        "🔑 Using NCBI API key - enhanced rate limits (10 requests/sec)",
        file=sys.stderr,
    )
else:
    print(
        "⚠️  No API key found - using standard rate limits (3 requests/sec)",
        file=sys.stderr,
    )
    print(
        "💡 Set PUBMED_API_KEY environment variable for better performance",
        file=sys.stderr,
    )


# Pydantic models for validation
class ESearchRequest(BaseModel):
    email: Optional[EmailStr] = Field(
        DEFAULT_EMAIL, description="Contact email (required by NCBI)"
    )
    term: str = Field(..., description="PubMed search term or query")
    retmax: Optional[int] = Field(
        10, ge=1, le=1000, description="Maximum results to return (1-1000)"
    )
    retstart: Optional[int] = Field(0, ge=0, description="Starting position (0-based)")
    db: str = Field("pubmed", description="Database to search")

    @field_validator("retmax", "retstart", mode="before")
    @classmethod
    def parse_int(cls, v):
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError(f"Cannot convert '{v}' to integer")
        return v


class EFetchRequest(BaseModel):
    email: Optional[EmailStr] = Field(
        DEFAULT_EMAIL, description="Contact email (required by NCBI)"
    )
    id: List[str] = Field(..., description="List of PubMed IDs (PMIDs)")
    retmode: str = Field("xml", description="Return format (xml, json)")
    rettype: Optional[str] = Field(
        "abstract", description="Return type (abstract, full, etc)"
    )

    @field_validator("id", mode="before")
    @classmethod
    def ensure_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v


# Create MCP server
app = Server("autocleaneeg-pubmedmcp")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available PubMed research tools"""
    return [
        Tool(
            name="search_pubmed",
            description="Search PubMed for biomedical research articles and papers",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "Contact email (optional, uses default if not provided)",
                        "default": DEFAULT_EMAIL,
                    },
                    "term": {
                        "type": "string",
                        "description": "Search term, query, or keywords (e.g., 'covid vaccine', 'BRCA1 mutations')",
                    },
                    "retmax": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "default": 10,
                        "description": "Maximum number of results to return (1-1000)",
                    },
                    "retstart": {
                        "type": "integer",
                        "minimum": 0,
                        "default": 0,
                        "description": "Starting position for results (0-based, for pagination)",
                    },
                },
                "required": ["term"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get_pubmed_details",
            description="Retrieve detailed information about specific PubMed articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "Contact email (optional, uses default if not provided)",
                        "default": DEFAULT_EMAIL,
                    },
                    "id": {
                        "oneOf": [
                            {
                                "type": "string",
                                "description": "Single PubMed ID (PMID)",
                            },
                            {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of PubMed IDs (PMIDs)",
                            },
                        ],
                        "description": "PubMed ID(s) to retrieve details for",
                    },
                    "retmode": {
                        "type": "string",
                        "enum": ["xml", "json"],
                        "default": "xml",
                        "description": "Return format",
                    },
                    "rettype": {
                        "type": "string",
                        "enum": ["abstract", "full"],
                        "default": "abstract",
                        "description": "Level of detail to retrieve",
                    },
                },
                "required": ["id"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get_pubmed_info",
            description="Get general information about the PubMed database",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls with comprehensive error handling and API key support"""

    if name == "search_pubmed":
        try:
            req = ESearchRequest(**arguments)
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Input validation error: {e}")]

        # Search PubMed
        start = time.time()
        params = {
            "db": req.db,
            "term": req.term,
            "retmax": req.retmax,
            "retstart": req.retstart,
            "retmode": "json",
            "usehistory": "y",
            "tool": "autocleaneeg-pubmedmcp-server",
            "email": req.email,
        }

        # Add API key if available
        if NCBI_API_KEY:
            params["api_key"] = NCBI_API_KEY

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{EUTILS_BASE}esearch.fcgi", params=params)
                response.raise_for_status()
                data = response.json()

            result = data.get("esearchresult", {})
            elapsed = int((time.time() - start) * 1000)

            # Format response
            count = int(result.get("count", 0))
            ids = result.get("idlist", [])

            summary = {
                "query": req.term,
                "total_found": count,
                "returned": len(ids),
                "start_position": req.retstart,
                "article_ids": ids,
                "processing_time_ms": elapsed,
            }

            # Add helpful context
            if count > req.retmax:
                summary["note"] = (
                    f"Found {count:,} total articles. Use retstart parameter for pagination."
                )

            if count == 0:
                summary["suggestion"] = "Try broader search terms or check spelling."

            return [TextContent(type="text", text=json.dumps(summary, indent=2))]

        except httpx.HTTPError as e:
            return [TextContent(type="text", text=f"❌ NCBI API error: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Search error: {e}")]

    elif name == "get_pubmed_details":
        try:
            req = EFetchRequest(**arguments)
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Input validation error: {e}")]

        # Fetch article details
        start = time.time()
        params = {
            "db": "pubmed",
            "id": ",".join(req.id),
            "retmode": req.retmode,
            "rettype": req.rettype,
            "tool": "autocleaneeg-pubmedmcp-server",
            "email": req.email,
        }

        # Add API key if available
        if NCBI_API_KEY:
            params["api_key"] = NCBI_API_KEY

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{EUTILS_BASE}efetch.fcgi", params=params)
                response.raise_for_status()
                content = response.text

            elapsed = int((time.time() - start) * 1000)

            result = {
                "requested_ids": req.id,
                "count": len(req.id),
                "format": req.retmode,
                "type": req.rettype,
                "content": content,
                "processing_time_ms": elapsed,
                "note": f"Retrieved {req.rettype} data for {len(req.id)} article(s) in {req.retmode} format",
            }

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except httpx.HTTPError as e:
            return [TextContent(type="text", text=f"❌ NCBI API error: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Fetch error: {e}")]

    elif name == "get_pubmed_info":
        # Get PubMed database information
        start = time.time()
        params = {"db": "pubmed", "retmode": "json"}

        # Add API key if available
        if NCBI_API_KEY:
            params["api_key"] = NCBI_API_KEY

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{EUTILS_BASE}einfo.fcgi", params=params)
                response.raise_for_status()
                data = response.json()

            dbinfo_list = data.get("einforesult", {}).get("dbinfo", [])
            dbinfo = dbinfo_list[0] if dbinfo_list else {}
            elapsed = int((time.time() - start) * 1000)

            result = {
                "database": dbinfo.get("dbname", "pubmed"),
                "description": dbinfo.get(
                    "description", "PubMed bibliographic database"
                ),
                "total_records": (
                    int(dbinfo.get("count")) if dbinfo.get("count") else None
                ),
                "last_updated": dbinfo.get("lastupdate"),
                "version": dbinfo.get("dbbuild"),
                "processing_time_ms": elapsed,
                "api_key_status": (
                    "✅ Enhanced rate limits"
                    if NCBI_API_KEY
                    else "⚠️ Standard rate limits"
                ),
            }

            if result["total_records"]:
                result["formatted_count"] = f"{result['total_records']:,} articles"

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception:
            # Fallback static info if API fails
            elapsed = int((time.time() - start) * 1000)
            result = {
                "database": "PubMed",
                "description": "PubMed comprises citations for biomedical literature from MEDLINE, life science journals, and online books",
                "total_records": None,
                "last_updated": None,
                "processing_time_ms": elapsed,
                "status": "API unavailable - showing static information",
                "api_key_status": (
                    "✅ Enhanced rate limits"
                    if NCBI_API_KEY
                    else "⚠️ Standard rate limits"
                ),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]


async def main():
    """Run the MCP PubMed server"""
    print("🚀 Starting AutoCleanEEG PubMed MCP Server", file=sys.stderr)
    print(f"📚 Connecting to NCBI E-utilities at {EUTILS_BASE}", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def cli():
    """Command-line interface entry point"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 AutoCleanEEG PubMed MCP Server stopped", file=sys.stderr)
    except Exception as e:
        print(f"❌ Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
