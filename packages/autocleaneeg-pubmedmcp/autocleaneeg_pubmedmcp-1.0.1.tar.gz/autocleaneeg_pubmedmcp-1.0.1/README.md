# AutoCleanEEG PubMed MCP Server

A Model Context Protocol (MCP) server that provides access to PubMed, the comprehensive biomedical literature database maintained by NCBI. This server enables AI assistants like Claude to search and retrieve detailed information from millions of biomedical research articles.

## Features

- **Search PubMed Database**: Search across 39+ million biomedical articles using flexible query syntax
- **Retrieve Article Details**: Get complete article metadata, abstracts, authors, and publication information  
- **Database Information**: Access current PubMed database statistics and status
- **API Key Support**: Optional NCBI API key integration for enhanced rate limits
- **MCP Protocol**: Full Model Context Protocol compliance for seamless AI assistant integration

## Installation

### From PyPI (Recommended)

```bash
pip install autocleaneeg-pubmedmcp
```

### From Source

```bash
git clone <repository-url>
cd claude_code_docker
pip install -e .
```

## Usage

### As MCP Server

The server can be run directly:

```bash
autocleaneeg-pubmedmcp
```

### Claude Desktop Integration

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "pubmed": {
      "command": "autocleaneeg-pubmedmcp",
      "args": [],
      "env": {
        "PUBMED_API_KEY": "your_api_key_here_optional"
      }
    }
  }
}
```

## API Key Setup (Optional)

For enhanced rate limits, obtain a free API key from NCBI:

1. Visit [NCBI API Key Settings](https://account.ncbi.nlm.nih.gov/settings/)
2. Create an account or log in
3. Generate an API key
4. Set environment variable: `export PUBMED_API_KEY="your_key_here"`

## Available Tools

### `search_pubmed`
Search the PubMed database with flexible query syntax.

**Parameters:**
- `term` (required): Search query using PubMed syntax
- `retmax` (optional): Maximum results to return (1-1000, default: 20)
- `email` (optional): Your email for NCBI tracking

**Example:**
```json
{
  "term": "BRCA1 mutations AND breast cancer",
  "retmax": 10
}
```

### `get_pubmed_details`
Retrieve detailed information for specific PubMed articles.

**Parameters:**
- `id` (required): PubMed ID(s) - single ID or array of IDs

**Example:**
```json
{
  "id": ["35123456", "35789012"]
}
```

### `get_pubmed_info`
Get current information about the PubMed database.

**Parameters:** None

## Query Syntax Examples

- Basic search: `"covid vaccine"`
- Multiple terms: `"BRCA1 AND breast cancer"`
- Author search: `"Smith J[Author]"`
- Date range: `"covid vaccine" AND 2020:2023[dp]`
- Journal: `"Nature[Journal]"`
- Title search: `"machine learning"[Title]`

## Error Handling

The server provides comprehensive error handling for:
- Invalid queries or parameters
- Network connectivity issues
- Rate limiting (automatically handled)
- Invalid PubMed IDs
- API key validation

## Development

### Testing

Run the test suite:

```bash
python test_focused.py
```

### Requirements

- Python 3.10+
- httpx>=0.25.0
- mcp>=1.0.0
- pydantic>=2.0.0
- email-validator>=2.0.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Support

For issues and questions:
- Check the troubleshooting section below
- Open an issue on the repository

## Troubleshooting

### Connection Issues
- Verify internet connectivity
- Check if NCBI servers are accessible
- Ensure firewall allows outbound HTTPS connections

### Rate Limiting
- Consider adding a PUBMED_API_KEY for higher limits
- Reduce query frequency
- Check NCBI rate limiting guidelines

### Invalid Results
- Verify PubMed ID format (numeric)
- Check query syntax against PubMed documentation
- Ensure search terms are properly formatted

---

**Made with ❤️ for biomedical research and AI assistance**