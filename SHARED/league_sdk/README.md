# League SDK

Python library for AI Agent League system implementing the League Protocol V2.

## Overview

This SDK provides a clean abstraction layer between JSON configuration files and agent code, implementing:

- **Dataclasses** for type-safe configuration models
- **Repository Pattern** for runtime data access
- **Lazy Loading** with caching for efficient configuration access
- **Structured Logging** using JSONL format
- **MCP Protocol** schemas and client/server implementations

## Installation

```bash
cd SHARED
pip install -e .
```

## Quick Start

### Loading Configuration

```python
from league_sdk import ConfigLoader

loader = ConfigLoader()

# Load system configuration
system_config = loader.load_system()
print(system_config.protocol_version)  # "league.v2"

# Load agents
agents = loader.load_agents()
active_players = loader.get_active_players()

# Load league configuration
league = loader.load_league("league_2025_even_odd")
```

### Structured Logging

```python
from league_sdk import JsonLogger

logger = JsonLogger("my_agent", league_id="league_2025_even_odd")

logger.info("AGENT_STARTED", agent_id="P01", version="1.0.0")
logger.error("CONNECTION_FAILED", endpoint="http://localhost:8000")
```

### Data Repositories

```python
from league_sdk import StandingsRepository

repo = StandingsRepository("league_2025_even_odd")

# Update player standings
repo.update_player("P01", result="WIN", points=3)

# Load current standings
standings = repo.load()
```

## Modules

- **config_models**: Dataclass definitions for all configuration types
- **config_loader**: ConfigLoader class for loading configurations
- **repositories**: Repository classes for runtime data
- **logger**: JsonLogger for structured logging
- **schemas**: Pydantic models for MCP protocol messages
- **helpers**: Utility functions (timestamps, IDs, validation)
- **mcp_client**: MCP client implementation
- **mcp_server**: MCP server base
- **game_rules**: Game rules implementations

## Directory Structure

```
league_sdk/
├── __init__.py
├── config_models.py
├── config_loader.py
├── repositories.py
├── logger.py
├── schemas.py
├── helpers.py
├── mcp_client.py
├── mcp_server.py
└── game_rules/
```

## Requirements

- Python 3.10+
- pydantic (for schema validation)
