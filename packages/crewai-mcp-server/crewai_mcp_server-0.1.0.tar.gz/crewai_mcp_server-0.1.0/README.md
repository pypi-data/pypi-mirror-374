# CrewAI MCP Server

An MCP (Model Context Protocol) server that provides access to CrewAI documentation, enabling AI agents to help build CrewAI agents with up-to-date documentation.

## Features

- **Resources**: Structured access to CrewAI concepts, tools, and examples
- **Tools**: Interactive functionality for searching docs and generating templates
- **Real-time**: Fetches latest documentation from CrewAI docs

## Installation

```bash
pip install -e .
```

## Usage

```bash
crewai-mcp-server
```

## MCP Client Configuration

Add to your MCP client config:

```json
{
  "mcpServers": {
    "crewai-docs": {
      "command": "crewai-mcp-server"
    }
  }
}
```

## Available Resources

- `crewai://concepts/agents` - Agent configuration and examples
- `crewai://concepts/tasks` - Task definitions
- `crewai://concepts/crews` - Crew orchestration
- `crewai://tools/{category}` - Available tools
- `crewai://examples/{use_case}` - Example implementations

## Available Tools

- `search_crewai_docs` - Search documentation
- `get_agent_template` - Generate agent templates
- `get_crew_template` - Generate crew templates
- `list_tools` - List CrewAI tools
- `get_examples` - Retrieve examples