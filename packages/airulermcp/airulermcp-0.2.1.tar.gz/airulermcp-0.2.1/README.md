# AIMCP

[![PyPI version](https://badge.fury.io/py/aimcp.svg)](https://badge.fury.io/py/aimcp)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AIMCP is an MCP (Model Context Protocol) server that enables teams to distribute MCP tool specifications from GitLab repositories to IDEs like Cursor and VS Code. The server discovers `tools.json` files in repositories, dynamically generates MCP tools from their specifications, and serves referenced files as resources through a secure URI scheme.

## Features

- **GitLab Integration**: Automatically discovers and fetches `tools.json` files from configured repositories
- **Dynamic Tool Generation**: Creates MCP tools from specifications at runtime
- **Secure Resource Access**: Serves repository files via `aimcp://` URI scheme with access control
- **Dual Caching**: Caches both tool specifications and file content for optimal performance
- **Conflict Resolution**: Handles duplicate tool names across repositories with configurable strategies
- **Async Architecture**: Built on `fastmcp` for high-performance async operations

## Installation

```bash
pip install aimcp
```

## Quick Start

1. Create a configuration file `config.yaml`:

```yaml
gitlab:
  base_url: "https://gitlab.example.com"
  token: "your-gitlab-token"
  repositories:
    - path: "team/tools-repo"
      branch: "main"

cache:
  type: "memory"
  ttl: 3600

conflict_resolution: "prefix"
```

2. Run the server:

```bash
aimcp
```

3. Connect your IDE to the MCP server at the configured endpoint.

## Tool Specifications

Each repository must contain a `tools.json` file following the [MCP specification](https://spec.modelcontextprotocol.io/). Example:

```json
{
  "tools": [
    {
      "name": "analyze_code",
      "description": "Analyze code quality and suggest improvements",
      "resourceRefs": ["analyzer_script", "analyzer_rules"]
      }
    }
  ],
  "resources": [
    {
      "name": "analyzer_script",
      "uri": "scripts/analyze.py",
    },
    {
      "name": "analyzer_rules",
      "uri": "configs/rules.yaml"
    }
  ]
}
```

## Configuration

### Conflict Resolution Strategies

- `prefix`: Add repository prefix to tool names (`repo1_toolname`, `repo2_toolname`)
- `priority`: First repository in configuration order wins
- `error`: Fail startup with detailed conflict report
- `merge`: Combine tool descriptions and resource lists

### Cache Options

- `memory`: In-memory caching (default)
- `redis`: Redis-backed caching for distributed setups (not implemented)

## Development

### Prerequisites

- Python 3.13+
- uv (recommended package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/aimcp.git
cd aimcp

# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Vibe coding product

Generated with Claude
