# astral-api-mcp

A MCP (Model Context Protocol) server that enables AI models to query location attestations using the available Astral GraphQL endpoints and APIs.

**Table of Contents**
- [astral-api-mcp](#astral-api-mcp)
  - [Project Overview](#project-overview)
  - [Integration with the Recall Platform](#integration-with-the-recall-platform)
  - [Quick Start](#quick-start)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Available Agent Tools](#available-agent-tools)
    - [Testing the MCP Server](#testing-the-mcp-server)
    - [Testing](#testing)
    - [Development](#development)
    - [Troubleshooting](#troubleshooting)

## Project Overview

We are exploring the development of a Model Context Protocol (MCP) agent that integrates with the [Astral API](https://docs.astral.global/getting-started) to enable intelligent querying and analysis of attestations submitted to blockchain ecosystems such as the Ethereum Attestation Service (EAS). This agent would support complex queries across spatial and temporal dimensions, such as filtering attestations by schema ID, location, or date range, while maintaining persistent context across sessions. By leveraging Astral’s structured API and EAS’s open schema model, the agent could automate common analytical workflows—like generating attestation heatmaps or tracking schema usage over time—making it a valuable tool for both research and production use cases. This early scoping phase would help assess feasibility and determine if this direction merits further investment.

To learn more, please refer to the following [document](docs/ai/README.md) for additional details on the purpose, use cases, architecture, and development plans.

## Integration with the Recall Platform

[Recall](https://docs.recall.network/advanced/overview) is a blockchain-based platform to support persistent, intelligent agents for onchain storage primitives and agent collaboration tools, enabling AI agents to maintain persistent memory, share data across sessions, and participate in a broader ecosystem of interconnected agents. By integrating the Astral MCP agent with Recall, we can transform it from a standalone location attestation query tool into a collaborative participant in an agent network with long-term memory—enabling it to store spatial analysis insights onchain, build knowledge graphs of location patterns over time, and share geospatial intelligence with other agents in the ecosystem. This integration unlocks powerful capabilities like persistent session context, cross-agent location verification services, and the ability to contribute to community-driven location intelligence, positioning your agent as both a consumer and provider of valuable spatial data within a growing network of AI agents that can learn from and build upon each other's discoveries.

Once the Astral MCP agent is functional, we plan to integrate it with the Recall platform to enable persistent memory by storing insights onchain. You can find out more details on this next stage of development [in the following section](./docs/integration-with-recall.md).

## Quick Start

### Prerequisites

- Python 3.12+ (tested with Python 3.13)
- Poetry for dependency management

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd astral-api-mcp
```

2. Install dependencies using Poetry:

```bash
poetry install
```

3. Verify the installation:

```bash
poetry run python -c "import astral_mcp_server; print('Installation successful!')"
```

4. Test API connectivity:

```bash
poetry run python -c "import asyncio; from astral_mcp_server.server import check_astral_api_health; print('Health check:', asyncio.run(check_astral_api_health())['status'])"
```

### Configuration

**Selecting API Endpoint**:

The MCP server can be configured to use either the production or development Astral API endpoint:

1. **Via Environment Variable** (highest priority):

   ```bash
   export ASTRAL_USE_DEV_ENDPOINT=true
   poetry run start-server
   ```

2. **Via MCP Configuration** (`.vscode/mcp.json`):

   ```json
   {
     "servers": {
       "astral-api": {
         "command": "poetry",
         "args": ["run", "start-server"],
         "cwd": "${workspaceFolder}",
         "type": "stdio"
       }
     },
     "mcp_agent": {
       "use_dev_endpoint": true,
       "dev_endpoint": "https://custom-dev-api.example.com"
     }
   }
   ```

**Configuration Options**:

- `use_dev_endpoint`: Set to `true` to use the development API endpoint
- `dev_endpoint` (optional): Override the default dev endpoint URL with a custom one

The server will automatically select the appropriate endpoint on startup and log which endpoint is being used.

### Available Agent Tools

- `check_astral_api_health`: Verify connectivity to the Astral API
- `get_server_info`: Get information about the MCP server instance
- `query_location_proofs`: Query location proofs by various filters (chain, prover, schema ID, etc.)
- `get_location_proof_by_uid`: Retrieve a specific location proof attestation by its unique identifier
- `get_astral_config`: Fetch the Astral API configuration and supported chains

Learn more about the available tools and how to use them in the [MCP Tools Guide](docs/mcp-tools-guide.md).

### Testing the MCP Server

> **Important**: MCP servers don't run as web servers - they communicate via the MCP protocol.

**Test with MCP Inspector (interactive debugging)**:

```bash
poetry run mcp dev astral_mcp_server/server.py
```

Alternatively, you can start the MCP Inspector from [mcp.json](.vscode/mcp.json) via the UI in VSCode.

This will open the [MCP Inspector tool](https://github.com/modelcontextprotocol/inspector) in your browser where you can:

- See available tools (`check_astral_api_health`, `get_server_info`)
- Execute tools interactively
- View tool outputs and debug

> The [.env-mcp-inspector](.env-mcp-inspector) file sets environment variables that the MCP Inspector uses to connect to the MCP server. You can modify it if needed.

**Use with Claude Desktop or other MCP clients**:

The following configurations allow you to connect the MCP server with clients like Claude Desktop or VSCode MCP extension.

**Claude Desktop's config:**

```json
{
  "mcpServers": {
    "astral-api": {
      "command": "poetry",
      "args": ["run", "start-server"],
      "cwd": "/path/to/astral-api-mcp" // the local path to cloned astral-api-mcp repo
    }
  }
}
```

**VSCode MCP extension's config:**

```json
{
  "servers": {
    "astral-api": {
      "command": "poetry",
      "args": ["run", "start-server"],
      "cwd": "${workspaceFolder}" // or the local path to cloned astral-api-mcp repo
    }
  }
}
```

Once configured, you can connect to the MCP server from your client (i.e. GitHub Copilot Chat in `agent` mode) and start using the available tools.

### Testing

Run the test suite:

```bash
poetry run pytest tests/ -v
```

### Development

This project uses:

- **Poetry** for dependency management
- **FastMCP** framework for MCP server implementation
- **httpx** for HTTP requests to Astral API
- **pytest** for testing


### Troubleshooting

If you encounter any `PORT IS IN USE` errors while running the MCP Inspector such as this:

> [warning] [server stderr] ❌  MCP Inspector PORT IS IN USE at http://localhost:8881 ❌

The MCP Inspector may already be running in another terminal or process or the port is occupied by another service that will need to be stopped. If the MCP Inspector is not running, it may have not exited cleanly, leaving an orphaned process i.e. `node.exe` still holding the port.  If that's the case, you can try running the **free-mcp-ports** scripts found [here](/scripts/).
