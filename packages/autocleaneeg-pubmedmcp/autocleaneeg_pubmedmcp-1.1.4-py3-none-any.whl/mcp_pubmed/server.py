#!/usr/bin/env python3
"""
AutoCleanEEG PubMed MCP Server

A standalone MCP server for Claude Desktop that provides access to PubMed research database.
Supports optional NCBI API key for enhanced rate limits.
"""

import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal

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


# Structured response models for enhanced LLM integration
class SearchContext(BaseModel):
    """Context analysis for search optimization"""
    intent: Literal["research", "clinical", "review", "methodology", "general"] = Field(
        description="Inferred search intent"
    )
    domain: Optional[str] = Field(default=None, description="Medical domain (e.g., neurology, cardiology)")
    study_types: List[str] = Field(default=[], description="Preferred study types")
    date_preference: Optional[str] = Field(default=None, description="Date range preference")
    specificity_level: Literal["broad", "focused", "highly_specific"] = Field(
        description="Query specificity assessment"
    )


class ArticleMetadata(BaseModel):
    """Enhanced article metadata with LLM-friendly structure"""
    pmid: str = Field(description="PubMed ID")
    title: Optional[str] = Field(description="Article title")
    authors: List[str] = Field(default=[], description="Author list")
    journal: Optional[str] = Field(description="Journal name")
    pub_date: Optional[str] = Field(description="Publication date")
    study_type: Optional[str] = Field(default=None, description="Inferred study type")
    relevance_score: float = Field(description="Relevance score (0-1)")
    key_concepts: List[str] = Field(default=[], description="Extracted key concepts")
    abstract: Optional[str] = Field(default=None, description="Article abstract")


class SearchResult(BaseModel):
    """Structured search result with context and intelligence"""
    query_analysis: SearchContext = Field(description="Analysis of the search query")
    total_found: int = Field(description="Total articles found")
    returned_count: int = Field(description="Number of articles returned")
    articles: List[ArticleMetadata] = Field(description="Article metadata with intelligence")
    suggested_refinements: List[str] = Field(default=[], description="Query refinement suggestions")
    research_gaps: List[str] = Field(default=[], description="Identified research gaps")
    processing_time_ms: int = Field(description="Search processing time")
    confidence: float = Field(description="Overall result confidence (0-1)")


class QueryIntelligence:
    """Context-aware search intelligence engine"""
    
    # Medical domain patterns
    DOMAIN_PATTERNS = {
        "neurology": ["brain", "neural", "neuron", "neurological", "eeg", "epilepsy", "seizure"],
        "cardiology": ["heart", "cardiac", "cardiovascular", "coronary", "artery", "myocardial"],
        "oncology": ["cancer", "tumor", "malignant", "chemotherapy", "radiation", "glioblastoma"],
        "psychiatry": ["depression", "anxiety", "mental health", "psychiatric", "adhd", "behavioral"],
        "pediatrics": ["children", "pediatric", "infant", "child development"],
        "immunology": ["immune", "antibody", "vaccine", "autoimmune", "allergy"]
    }
    
    # Study type patterns
    STUDY_TYPE_PATTERNS = {
        "randomized controlled trial": ["rct", "randomized", "controlled trial", "double-blind"],
        "systematic review": ["systematic review", "meta-analysis", "cochrane"],
        "case study": ["case report", "case series", "case study"],
        "cohort study": ["cohort", "longitudinal", "prospective"],
        "cross-sectional": ["cross-sectional", "survey", "prevalence"]
    }
    
    @staticmethod
    def analyze_query(query: str) -> SearchContext:
        """Analyze query for context and intent"""
        query_lower = query.lower()
        
        # Detect domain with scoring for better accuracy
        domain = None
        best_score = 0
        for domain_name, keywords in QueryIntelligence.DOMAIN_PATTERNS.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > best_score:
                best_score = score
                domain = domain_name
        
        # Detect study types
        study_types = []
        for study_type, keywords in QueryIntelligence.STUDY_TYPE_PATTERNS.items():
            if any(keyword in query_lower for keyword in keywords):
                study_types.append(study_type)
        
        # Assess specificity
        word_count = len(query.split())
        if word_count <= 3:
            specificity = "broad"
        elif word_count <= 8:
            specificity = "focused"
        else:
            specificity = "highly_specific"
        
        # Infer intent
        intent = "general"
        if any(word in query_lower for word in ["treatment", "therapy", "intervention", "effectiveness"]):
            intent = "clinical"
        elif any(word in query_lower for word in ["review", "overview", "summary"]):
            intent = "review"
        elif any(word in query_lower for word in ["method", "protocol", "technique"]):
            intent = "methodology"
        elif len(study_types) > 0:
            intent = "clinical" if any("trial" in st for st in study_types) else "research"
        elif domain:
            intent = "research"
        
        return SearchContext(
            intent=intent,
            domain=domain,
            study_types=study_types,
            specificity_level=specificity
        )
    
    @staticmethod
    def enhance_query(original_query: str, context: SearchContext) -> str:
        """Enhance query based on context analysis"""
        enhanced = original_query
        
        # Add study type filters if beneficial
        if context.intent == "clinical" and "randomized" not in original_query.lower():
            enhanced += " AND (randomized controlled trial OR clinical trial)"
        
        # Add recency for clinical queries
        if context.intent == "clinical":
            enhanced += " AND (\"last 5 years\"[PDat] OR \"2019/01/01\"[PDat]:\"3000\"[PDat])"
        
        # Add domain-specific terms for broader searches
        if context.specificity_level == "broad" and context.domain:
            domain_terms = QueryIntelligence.DOMAIN_PATTERNS.get(context.domain, [])
            if domain_terms and len(domain_terms) > 2:
                enhanced += f" AND ({domain_terms[0]} OR {domain_terms[1]})"
        
        return enhanced
    
    @staticmethod
    def calculate_relevance(article_data: Dict, context: SearchContext) -> float:
        """Calculate relevance score for an article"""
        score = 0.5  # Base score
        
        # Boost for domain relevance
        if context.domain:
            domain_keywords = QueryIntelligence.DOMAIN_PATTERNS.get(context.domain, [])
            title = article_data.get("title", "").lower()
            matches = sum(1 for keyword in domain_keywords if keyword in title)
            score += min(0.3, matches * 0.1)
        
        # Boost for study type alignment
        if context.study_types:
            title = article_data.get("title", "").lower()
            for study_type in context.study_types:
                if study_type in title:
                    score += 0.2
                    break
        
        # Publication recency (for clinical queries)
        if context.intent == "clinical":
            pub_date = article_data.get("pubdate", "")
            if pub_date and "202" in pub_date:  # Recent publication
                score += 0.1
        
        return min(1.0, score)
    
    @staticmethod
    def suggest_refinements(query: str, context: SearchContext, result_count: int) -> List[str]:
        """Suggest query refinements based on results"""
        suggestions = []
        
        if result_count == 0:
            suggestions.extend([
                f"Try broader terms: remove specific technical terms",
                f"Check spelling and try synonyms",
                f"Remove date restrictions if present"
            ])
        elif result_count > 1000:
            suggestions.extend([
                f"Add specific study type filter (e.g., 'randomized controlled trial')",
                f"Narrow date range to recent years",
                f"Add specific population or condition terms"
            ])
        elif context.domain:
            domain_keywords = QueryIntelligence.DOMAIN_PATTERNS.get(context.domain, [])
            if len(domain_keywords) > 1:
                suggestions.append(f"Try related {context.domain} terms: {', '.join(domain_keywords[:3])}")
        
        return suggestions[:3]  # Limit to 3 suggestions


def parse_pubmed_xml(xml_content: str) -> List[Dict[str, Any]]:
    """Parse PubMed XML response and extract article metadata."""
    import xml.etree.ElementTree as ET
    
    articles = []
    try:
        root = ET.fromstring(xml_content)
        
        for article in root.findall('.//PubmedArticle'):
            article_data = {}
            
            # Extract PMID
            pmid_elem = article.find('.//PMID')
            article_data['pmid'] = pmid_elem.text if pmid_elem is not None else ''
            
            # Extract title
            title_elem = article.find('.//ArticleTitle')
            article_data['title'] = title_elem.text if title_elem is not None else ''
            
            # Extract authors
            authors = []
            for author in article.findall('.//Author'):
                last_name = author.find('LastName')
                first_name = author.find('ForeName')
                if last_name is not None and first_name is not None:
                    authors.append(f"{first_name.text} {last_name.text}")
                elif last_name is not None:
                    authors.append(last_name.text)
            article_data['authors'] = authors
            
            # Extract journal
            journal_elem = article.find('.//Journal/Title')
            if journal_elem is None:
                journal_elem = article.find('.//ISOAbbreviation')
            article_data['journal'] = journal_elem.text if journal_elem is not None else ''
            
            # Extract publication date
            pub_date_elem = article.find('.//PubDate/Year')
            if pub_date_elem is not None:
                article_data['pub_date'] = pub_date_elem.text
            else:
                article_data['pub_date'] = ''
            
            # Extract abstract
            abstract_elem = article.find('.//AbstractText')
            article_data['abstract'] = abstract_elem.text if abstract_elem is not None else ''
            
            articles.append(article_data)
            
    except ET.ParseError as e:
        print(f"XML parsing error: {e}", file=sys.stderr)
        return []
    
    return articles


def extract_key_concepts(text: str, query: str) -> List[str]:
    """Extract key concepts from text based on the query."""
    if not text:
        return []
    
    # Simple keyword extraction based on query terms
    query_terms = query.lower().split()
    text_lower = text.lower()
    
    concepts = []
    
    # Look for query terms in the text
    for term in query_terms:
        if term in text_lower and len(term) > 3:  # Skip short words
            concepts.append(term)
    
    # Add some common research concepts if found
    research_terms = [
        'statistical learning', 'alpha oscillations', 'neural networks',
        'cognitive function', 'brain activity', 'EEG', 'temporal windows',
        'learning mechanisms', 'neural plasticity', 'memory consolidation'
    ]
    
    for term in research_terms:
        if term.lower() in text_lower and term not in concepts:
            concepts.append(term)
    
    return concepts[:5]  # Limit to top 5 concepts


# Create MCP server
app = Server("autocleaneeg-pubmedmcp")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available PubMed research tools with enhanced LLM integration"""
    return [
        Tool(
            name="intelligent_search_pubmed",
            description="Context-aware PubMed search with automatic query enhancement and structured results optimized for LLM analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language research query (e.g., 'EEG biomarkers for ADHD diagnosis in children', 'recent COVID-19 vaccine effectiveness studies')"
                    },
                    "max_results": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 10,
                        "description": "Maximum articles to return with full analysis"
                    },
                    "focus_area": {
                        "type": "string",
                        "enum": ["clinical_trials", "systematic_reviews", "case_studies", "methodology", "recent_research", "comprehensive"],
                        "default": "comprehensive",
                        "description": "Research focus to optimize search strategy"
                    },
                    "include_context": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include query analysis and search context in response"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="search_pubmed",
            description="Traditional PubMed search for direct query control",
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
    """Handle tool calls with enhanced intelligence and structured responses"""

    if name == "intelligent_search_pubmed":
        try:
            # Extract parameters
            query = arguments.get("query", "")
            max_results = arguments.get("max_results", 10)
            focus_area = arguments.get("focus_area", "comprehensive")
            include_context = arguments.get("include_context", True)
            
            if not query:
                return [TextContent(type="text", text="❌ Query parameter is required")]
            
            start_time = time.time()
            
            # Step 1: Analyze query context
            context = QueryIntelligence.analyze_query(query)
            
            # Step 2: Enhance query based on context and focus area
            enhanced_query = QueryIntelligence.enhance_query(query, context)
            
            # Apply focus area modifications
            if focus_area == "clinical_trials":
                enhanced_query += " AND (clinical trial OR randomized controlled trial)"
            elif focus_area == "systematic_reviews":
                enhanced_query += " AND (systematic review OR meta-analysis)"
            elif focus_area == "recent_research":
                enhanced_query += " AND (\"last 3 years\"[PDat])"
            elif focus_area == "case_studies":
                enhanced_query += " AND (case report OR case series)"
            elif focus_area == "methodology":
                enhanced_query += " AND (method OR technique OR protocol)"
            
            # Step 3: Execute enhanced search
            search_params = {
                "db": "pubmed",
                "term": enhanced_query,
                "retmax": min(max_results * 2, 200),  # Get extra for filtering
                "retstart": 0,
                "retmode": "json",
                "usehistory": "y",
                "tool": "autocleaneeg-pubmedmcp-server",
                "email": DEFAULT_EMAIL,
            }
            
            if NCBI_API_KEY:
                search_params["api_key"] = NCBI_API_KEY
            
            async with httpx.AsyncClient(timeout=30) as client:
                # Step 3: Execute enhanced search
                response = await client.get(f"{EUTILS_BASE}esearch.fcgi", params=search_params)
                response.raise_for_status()
                search_data = response.json()
                
                search_result = search_data.get("esearchresult", {})
                total_found = int(search_result.get("count", 0))
                article_ids = search_result.get("idlist", [])[:max_results]
                
                # Step 4: Get detailed article information for relevance scoring
                articles = []
                if article_ids:
                    # Fetch article details in batches
                    detail_params = {
                        "db": "pubmed",
                        "id": ",".join(article_ids),
                        "retmode": "xml",
                        "rettype": "abstract",
                        "tool": "autocleaneeg-pubmedmcp-server",
                        "email": DEFAULT_EMAIL,
                    }
                    
                    if NCBI_API_KEY:
                        detail_params["api_key"] = NCBI_API_KEY
                    
                    detail_response = await client.get(f"{EUTILS_BASE}efetch.fcgi", params=detail_params)
                    detail_response.raise_for_status()
                
                    # Parse XML and extract real article metadata
                    xml_content = detail_response.text
                    parsed_articles = parse_pubmed_xml(xml_content)
                    
                    for article_data in parsed_articles:
                        relevance_score = QueryIntelligence.calculate_relevance(article_data, context)
                        
                        # Extract key concepts from abstract/title
                        key_concepts = extract_key_concepts(
                            article_data.get('title', '') + ' ' + article_data.get('abstract', ''),
                            query
                        )
                        
                        articles.append(ArticleMetadata(
                            pmid=article_data.get('pmid', ''),
                            title=article_data.get('title', 'Title not available'),
                            authors=article_data.get('authors', []),
                            journal=article_data.get('journal', 'Journal not available'),
                            pub_date=article_data.get('pub_date', 'Date not available'),
                            relevance_score=relevance_score,
                            key_concepts=key_concepts,
                            abstract=article_data.get('abstract', '')
                        ))
            
            # Sort by relevance score
            articles.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Step 5: Generate suggestions and assess confidence
            suggestions = QueryIntelligence.suggest_refinements(query, context, total_found)
            
            # Calculate overall confidence
            confidence = 0.7  # Base confidence
            if context.domain:
                confidence += 0.1
            if total_found > 0:
                confidence += 0.1
            if context.specificity_level != "broad":
                confidence += 0.1
            confidence = min(1.0, confidence)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Step 6: Build structured result
            result = SearchResult(
                query_analysis=context,
                total_found=total_found,
                returned_count=len(articles),
                articles=articles,
                suggested_refinements=suggestions,
                research_gaps=[],  # Could be enhanced to identify gaps
                processing_time_ms=processing_time,
                confidence=confidence
            )
            
            return [TextContent(type="text", text=result.model_dump_json(indent=2))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Intelligent search error: {e}")]

    elif name == "search_pubmed":
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
    import argparse
    from . import __version__
    
    parser = argparse.ArgumentParser(description="AutoCleanEEG PubMed MCP Server")
    parser.add_argument("--version", action="version", version=f"autocleaneeg-pubmedmcp {__version__}")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 AutoCleanEEG PubMed MCP Server stopped", file=sys.stderr)
    except Exception as e:
        print(f"❌ Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
