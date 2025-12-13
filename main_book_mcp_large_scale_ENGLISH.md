# MCP Protocol for AI Agent League
## Large-Scale MCP Protocol for AI Agent League
### (Model Context Protocol – MCP)

**Dr. Yoram Segal**

© Dr. Yoram Segal - All Rights Reserved

December 2025

Version 1.0

---

# Table of Contents

1. [Introduction to MCP Protocol](#1-introduction-to-mcp-protocol)
   - 1.1 [Learning Objectives](#11-learning-objectives)
   - 1.2 [What is the MCP Protocol?](#12-what-is-the-mcp-protocol)
   - 1.3 [MCP Architecture](#13-mcp-architecture)
   - 1.4 [Tool Discovery](#14-tool-discovery)
   - 1.5 [Tool Call](#15-tool-call)
   - 1.6 [Chapter Summary](#16-chapter-summary)

2. [Client-Server Architecture Basics in Python](#2-client-server-architecture-basics-in-python)
   - 2.1 [Chapter Purpose](#21-chapter-purpose)
   - 2.2 [What is a Server and What is a Client?](#22-what-is-a-server-and-what-is-a-client)
   - 2.3 [Addresses and Ports: Localhost](#23-addresses-and-ports-localhost)
   - 2.4 [The Common Language: HTTP and JSON](#24-the-common-language-http-and-json)
   - 2.5 [Basic Server Implementation in FastAPI](#25-basic-server-implementation-in-fastapi)
   - 2.6 [Basic Client Implementation](#26-basic-client-implementation)
   - 2.7 [Running and Testing](#27-running-and-testing)
   - 2.8 [Connection to MCP Protocol](#28-connection-to-mcp-protocol)
   - 2.9 [Summary](#29-summary)

3. [MCP Protocol Fundamentals](#3-mcp-protocol-fundamentals)
   - 3.1 [JSON-RPC 2.0 Protocol](#31-json-rpc-20-protocol)
   - 3.2 [Standard Error Codes](#32-standard-error-codes)
   - 3.3 [Complete Initialization Process](#33-complete-initialization-process)
   - 3.4 [Capability Discovery](#34-capability-discovery)
   - 3.5 [Tool Schema (JSON Schema)](#35-tool-schema-json-schema)
   - 3.6 [Tool Call (tools/call)](#36-tool-call-toolscall)
   - 3.7 [Batch Requests](#37-batch-requests)
   - 3.8 [Protocol Handler Implementation](#38-protocol-handler-implementation)
   - 3.9 [Chapter Summary](#39-chapter-summary)

4. [League Architecture](#4-league-architecture)
   - 4.1 [Design Principles](#41-design-principles)
   - 4.2 [The Three Layers](#42-the-three-layers)
   - 4.3 [Agent Types](#43-agent-types)
   - 4.4 [The Role of the Orchestrator](#44-the-role-of-the-orchestrator)
   - 4.5 [Identifiers in the Protocol](#45-identifiers-in-the-protocol)
   - 4.6 [League Flow](#46-league-flow)
   - 4.7 [Important Principles](#47-important-principles)
   - 4.8 [Chapter Summary](#48-chapter-summary)

5. [Even/Odd Game Implementation](#5-evenodd-game-implementation)
   - 5.1 [Game Description](#51-game-description)
   - 5.2 [Protocol Messages](#52-protocol-messages)
   - 5.3 [Player Agent Implementation](#53-player-agent-implementation)
   - 5.4 [Possible Strategies](#54-possible-strategies)
   - 5.5 [MCP Server Implementation](#55-mcp-server-implementation)
   - 5.6 [Complete Game Flow](#56-complete-game-flow)
   - 5.7 [Chapter Summary](#57-chapter-summary)

6. [Scaling for Production Environment](#6-scaling-for-production-environment)
   - 6.1 [Motivation](#61-motivation)
   - 6.2 [Scalability Principles](#62-scalability-principles)
   - 6.3 [Distributed Architecture](#63-distributed-architecture)
   - 6.4 [Design Patterns](#64-design-patterns)
   - 6.5 [Failure Handling](#65-failure-handling)
   - 6.6 [Monitoring](#66-monitoring)
   - 6.7 [Future Extensions](#67-future-extensions)
   - 6.8 [Chapter Summary](#68-chapter-summary)

7. [Home Exercise](#7-home-exercise)
   - 7.1 [Task Overview](#71-task-overview)
   - 7.2 [Technical Requirements](#72-technical-requirements)
   - 7.3 [Required Agent Structure](#73-required-agent-structure)
   - 7.4 [Development Environment](#74-development-environment)
   - 7.5 [Common Errors](#75-common-errors)
   - 7.6 [Code Skeleton](#76-code-skeleton)
   - 7.7 [Frequently Asked Questions](#77-frequently-asked-questions)
   - 7.8 [Schedule](#78-schedule)
   - 7.9 [Summary](#79-summary)
   - 7.10 [English References](#710-english-references)

---

# 1. Introduction to MCP Protocol

## 1.1 Learning Objectives

In this course, we will learn three central topics, in order of priority:

1. **MCP Protocol** – Deep understanding of the Model Context Protocol at the highest level.
2. **Game League** – Using an agent league as an interesting and enjoyable pedagogical tool.
3. **Scalable Architecture** – Designing modular code that can scale from 4 players to millions.

## 1.2 What is the MCP Protocol?

MCP (Model Context Protocol) is a standard communication protocol developed by Anthropic [1]. The protocol enables AI agents to communicate with external services in a uniform manner.

### 1.2.1 The Problem the Protocol Solves

Before MCP, every integration between an AI agent and an external service required unique development. This created a fragmentation problem – for each agent and each service, separate integration code was required.

MCP solves this by creating a universal interface:

- **Uniform format** – All messages in JSON-RPC 2.0 format.
- **Three primitives** – Tools, Resources, Prompts.
- **Capability discovery** – Agents automatically discover what each other can do.

### 1.2.2 The Three Primitives of MCP

**Table 1: The Three Primitives of MCP**

| Primitive | Role | Example |
|-----------|------|---------|
| Tools | Execute actions | `send_email`, `read_file` |
| Resources | Access to data | `file://config.json` |
| Prompts | Pre-defined instructions | `review_code` |

In this exercise, we mainly focus on **Tools** – functions that agents expose for other uses.

## 1.3 MCP Architecture

### 1.3.1 Client and Server

In an MCP system, there are two main component types:

- **MCP Server** – A component that exposes capabilities (tools, resources, prompts). The server receives requests and executes actions.
- **MCP Client** – A component that sends requests to servers. The client discovers capabilities and calls tools.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MCP Client                                  │
│                     (Host Application)                              │
└──────────┬─────────────────┬─────────────────┬──────────────────────┘
           │                 │                 │
     JSON-RPC 2.0      JSON-RPC 2.0      JSON-RPC 2.0
           │                 │                 │
           ▼                 ▼                 ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   MCP Server 1   │ │   MCP Server 2   │ │   MCP Server 3   │
│ Tools: read_file │ │ Tools: query_db  │ │ Tools: send_email│
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### 1.3.2 Initialization Process (Handshake)

Before any communication, client and server must perform a handshake:

1. Client sends `initialize` – with protocol version and capabilities.
2. Server returns `initializeResult` – with its capabilities.
3. Client sends `initialized` – notification that initialization is complete.

**Initialization Request – initialize**

```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "clientInfo": {
      "name": "LeagueOrchestrator",
      "version": "1.0.0"
    }
  },
  "id": 1
}
```

**Initialization Response – initializeResult**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {"listChanged": true}
    },
    "serverInfo": {
      "name": "PlayerAgent",
      "version": "1.0.0"
    }
  },
  "id": 1
}
```

> **Important:** Without the initialization process, communication is not valid according to the MCP protocol. Every implementation must include the Handshake stage.

## 1.4 Tool Discovery

After initialization, the client can discover which tools the server exposes:

**Tool List Request – tools/list**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 2
}
```

**Tool List Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "choose_parity",
        "description": "Choose even or odd for the game",
        "inputSchema": {
          "type": "object",
          "properties": {
            "parity_choice": {
              "type": "string",
              "enum": ["even", "odd"],
              "description": "The player's choice"
            }
          },
          "required": ["parity_choice"]
        }
      }
    ]
  },
  "id": 2
}
```

### 1.4.1 Tool Schema (inputSchema)

Each tool must define `inputSchema` – parameter description in JSON Schema:

- **type** – Data type (object, string, number, etc.)
- **properties** – Description of each parameter
- **required** – List of required parameters
- **enum** – Possible values (optional)

## 1.5 Tool Call

After tool discovery, the client can call a tool:

**Tool Call – tools/call**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "choose_parity",
    "arguments": {
      "parity_choice": "even"
    }
  },
  "id": 3
}
```

**Tool Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Choice recorded: even"
      }
    ]
  },
  "id": 3
}
```

## 1.6 Chapter Summary

In this chapter we learned:

1. MCP is a standard protocol for communication between AI agents.
2. The protocol is based on JSON-RPC 2.0.
3. There are three primitives: Tools, Resources, Prompts.
4. All communication begins with an initialization process (Handshake).
5. Tools are defined with `inputSchema` in JSON Schema.

In the next chapter, we will learn in depth the protocol structure and standard error codes.

---

# 2. Client-Server Architecture Basics in Python

## 2.1 Chapter Purpose

This chapter is intended for those who have no experience implementing client-server architecture. This knowledge is a foundation for implementing the MCP protocol. Those familiar with the topic can skip to the next chapter.

By the end of this chapter, you will know:

- What is a server and what is a client
- How to set up a basic FastAPI server
- How to send JSON requests from a client
- How these principles are applied in an MCP game league

## 2.2 What is a Server and What is a Client?

Client-server architecture is similar to a restaurant visit.

- **The Client** – You. You request items from the menu. This is a **Request**.
- **The Server** – The kitchen. It receives the order, processes it, and returns the dish. This is a **Response**.

In our MCP league:

- **The Client** – The Referee or Orchestrator.
- **The Server** – Your agent (PlayerAgent).

The referee sends a request to choose a move. The agent returns the choice.

## 2.3 Addresses and Ports: Localhost

When developing on a personal computer, the client and server are on the same machine.

- **Localhost (127.0.0.1)** – The local machine address. This is like talking to yourself.
- **Port** – Like an apartment number in a building. Each service listens on a different port.

**Table 2: Ports in the MCP League**

| Component | Port | Full Address |
|-----------|------|--------------|
| League Manager | 8000 | http://127.0.0.1:8000 |
| Player 1 | 8101 | http://127.0.0.1:8101 |
| Player 2 | 8102 | http://127.0.0.1:8102 |

## 2.4 The Common Language: HTTP and JSON

For a server and client to understand each other, they need a common language.

- **HTTP** – The transport protocol. Defines how information is sent over the network. We use the POST method for sending data.
- **JSON** – The data format. Structured text of keys and values.

**Simple JSON Example**

```json
{
  "name": "PlayerAgent",
  "version": "1.0.0",
  "score": 100
}
```

## 2.5 Basic Server Implementation in FastAPI

### 2.5.1 Installation

We will use FastAPI – the same library that will serve us in agent implementation.

**Installing Libraries**

```bash
pip install fastapi uvicorn httpx
```

### 2.5.2 Server Code

A simple server that receives two numbers and returns their sum:

**my_server.py – Basic Server**

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/calculate")
async def calculate_sum(data: dict):
    """Receive two numbers, return their sum."""
    num1 = data.get("x")
    num2 = data.get("y")
    result = num1 + num2
    return {"result": result}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

**Explanation:**

- `@app.post("/calculate")` – Defines a route that receives POST requests
- `data: dict` – The parameter contains the JSON that was sent
- `return` – Returns JSON as a response

## 2.6 Basic Client Implementation

A client that sends a request to the server:

**my_client.py – Basic Client**

```python
import httpx

def send_request():
    url = "http://127.0.0.1:8000/calculate"
    payload = {"x": 5, "y": 10}

    response = httpx.post(url, json=payload)

    if response.status_code == 200:
        print("Result:", response.json())
    else:
        print("Error")

if __name__ == "__main__":
    send_request()
```

## 2.7 Running and Testing

1. Open a terminal and run the server: `python my_server.py`
2. Open another terminal and run the client: `python my_client.py`
3. The client will send `{x: 5, y: 10}`, the server will return `{result: 15}`

## 2.8 Connection to MCP Protocol

The principles are identical. The difference is in the JSON structure.

Instead of sending simple `x` and `y`, in the MCP protocol we send messages in JSON-RPC 2.0 format:

**MCP Request for Move Selection**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "choose_parity",
    "arguments": {"match_id": "M001"}
  },
  "id": 1
}
```

**Table 3: Comparison: Basic Server vs. MCP Server**

| Attribute | Basic Server | MCP Server |
|-----------|-------------|------------|
| Route | /calculate | /mcp |
| Request Format | {x, y} | JSON-RPC 2.0 |
| Required Fields | Per function | jsonrpc, method, id |
| Initialization | Not required | Required |

## 2.9 Summary

In this chapter we learned:

1. **Server** receives requests and returns responses.
2. **Client** sends requests and processes responses.
3. **FastAPI** allows quickly setting up a server.
4. **httpx** allows sending HTTP requests.
5. In the MCP protocol we use the same principles with JSON-RPC 2.0 format.

In the next chapter we will learn the complete protocol structure.

---

# 3. MCP Protocol Fundamentals

## 3.1 JSON-RPC 2.0 Protocol

MCP protocol is based on JSON-RPC 2.0 [2] – a lightweight Remote Procedure Call protocol. It uses JSON for message encoding.

### 3.1.1 Request Structure

**Table 4: Request Fields in JSON-RPC 2.0**

Every request in JSON-RPC 2.0 must contain the following fields:

| Field | Required? | Description |
|-------|----------|-------------|
| jsonrpc | Yes | Must be "2.0" |
| method | Yes | The method name to call |
| params | No | Parameters (object or array) |
| id | Yes* | Request identifier (*missing in notifications) |

**JSON-RPC Request Example**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "choose_parity",
    "arguments": {"parity_choice": "even"}
  },
  "id": "req-001"
}
```

### 3.1.2 Response Structure

A response can be either a success response or an error response:

**Success Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {"type": "text", "text": "Choice recorded: even"}
    ]
  },
  "id": "req-001"
}
```

**Error Response**

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": {"method": "unknown_method"}
  },
  "id": "req-001"
}
```

> **Important:** The `result` field and `error` field are mutually exclusive. A response will contain **only one of them** – never both together.

### 3.1.3 Notifications

A notification is a request without an `id` field. The server does not return a response to a notification.

**Notification Example**

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

## 3.2 Standard Error Codes

The JSON-RPC 2.0 protocol defines standard error codes. Correct use of these codes is essential for proper MCP implementation.

**Table 5: Standard Error Codes of JSON-RPC 2.0**

| Code | Name | Description |
|------|------|-------------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid Request | The JSON is not a valid request |
| -32601 | Method not found | The method does not exist |
| -32602 | Invalid params | Invalid parameters |
| -32603 | Internal error | Internal server error |
| -32000 to -32099 | Server error | Implementation-defined errors |

### 3.2.1 Error Code Implementation in Python

**Error Code Definition**

```python
class JsonRpcError:
    """Standard JSON-RPC 2.0 error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

def create_error_response(code: int, message: str,
                          request_id=None, data=None) -> dict:
    """Create a JSON-RPC error response."""
    error_obj = {"code": code, "message": message}
    if data is not None:
        error_obj["data"] = data
    return {
        "jsonrpc": "2.0",
        "error": error_obj,
        "id": request_id
    }
```

## 3.3 Complete Initialization Process

The initialization process (Handshake) is a critical step in the MCP protocol. Without proper initialization, the communication is not valid.

### 3.3.1 The Three Steps

1. **initialize** – Client sends initialization request with version and capabilities.
2. **initializeResult** – Server returns its capabilities.
3. **initialized** – Client sends notification that initialization is complete.

```
┌────────────┐                          ┌────────────┐
│ MCP Client │                          │ MCP Server │
└─────┬──────┘                          └──────┬─────┘
      │                                        │
      │  1. initialize                         │
      │───────────────────────────────────────>│
      │                                        │
      │  2. initialize Result                  │
      │<───────────────────────────────────────│
      │                                        │
      │  3. initialized (notification)         │
      │───────────────────────────────────────>│
      │                                        │
```

### 3.3.2 Complete initialize Request

**initialize Request**

```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": {"listChanged": true},
      "sampling": {}
    },
    "clientInfo": {
      "name": "LeagueOrchestrator",
      "version": "1.0.0"
    }
  },
  "id": 1
}
```

### 3.3.3 Complete initializeResult Response

**initializeResult Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {"listChanged": true},
      "resources": {"subscribe": true},
      "prompts": {"listChanged": true}
    },
    "serverInfo": {
      "name": "PlayerAgent",
      "version": "1.0.0"
    }
  },
  "id": 1
}
```

### 3.3.4 initialized Notification

**initialized Notification**

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

> **Required:** Without completing the initialization process, any additional communication is not valid according to the protocol. A standard MCP server can reject requests sent before initialization is complete.

## 3.4 Capability Discovery

After initialization, the client can discover which capabilities the server exposes.

### 3.4.1 Tool Discovery – tools/list

**Tool List Request**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 2
}
```

**Tool List Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "choose_parity",
        "description": "Choose even or odd",
        "inputSchema": {
          "type": "object",
          "properties": {
            "parity_choice": {
              "type": "string",
              "enum": ["even", "odd"]
            }
          },
          "required": ["parity_choice"]
        }
      }
    ]
  },
  "id": 2
}
```

### 3.4.2 Resource Discovery – resources/list

**Resource List Request**

```json
{
  "jsonrpc": "2.0",
  "method": "resources/list",
  "id": 3
}
```

**Resource List Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "resources": [
      {
        "uri": "file:///league/standings.json",
        "name": "League Standings",
        "description": "Current league standings",
        "mimeType": "application/json"
      }
    ]
  },
  "id": 3
}
```

### 3.4.3 Prompt Discovery – prompts/list

**Prompt List Request**

```json
{
  "jsonrpc": "2.0",
  "method": "prompts/list",
  "id": 4
}
```

**Prompt List Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "prompts": [
      {
        "name": "game_strategy",
        "description": "Strategy prompt for game decisions",
        "arguments": [
          {"name": "opponent", "required": true},
          {"name": "history", "required": false}
        ]
      }
    ]
  },
  "id": 4
}
```

## 3.5 Tool Schema (JSON Schema)

Each tool in MCP is defined with `inputSchema` in JSON Schema format. This allows agents to know exactly which parameters each tool requires.

### 3.5.1 inputSchema Structure

**Table 6: inputSchema Fields**

| Field | Possible Values | Description |
|-------|-----------------|-------------|
| type | object, string, number | Data type |
| properties | Object | Description of each parameter |
| required | Array of strings | Required parameters |
| enum | Array | Possible values (optional) |
| description | String | Parameter description |

### 3.5.2 Complete Tool Example

**Tool Definition with inputSchema**

```json
{
  "name": "register_player",
  "description": "Register a new player to the league",
  "inputSchema": {
    "type": "object",
    "properties": {
      "player_name": {
        "type": "string",
        "description": "Display name of the player"
      },
      "endpoint": {
        "type": "string",
        "description": "MCP server endpoint URL"
      },
      "strategy_type": {
        "type": "string",
        "enum": ["random", "deterministic", "llm", "adaptive"],
        "description": "Type of strategy the player uses"
      }
    },
    "required": ["player_name", "endpoint"]
  }
}
```

## 3.6 Tool Call (tools/call)

After tool discovery, the client can call a tool:

**Tool Call Request**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "choose_parity",
    "arguments": {
      "parity_choice": "even"
    }
  },
  "id": 5
}
```

**Tool Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Choice recorded: even"
      }
    ]
  },
  "id": 5
}
```

### 3.6.1 Content Types in Response

A tool response can contain several content types:

- **text** – Plain text
- **image** – Image encoded in base64
- **resource** – Reference to a resource

## 3.7 Batch Requests

JSON-RPC 2.0 supports batch requests – multiple requests in a single message:

**Batch Request**

```json
[
  {"jsonrpc": "2.0", "method": "tools/list", "id": 1},
  {"jsonrpc": "2.0", "method": "resources/list", "id": 2},
  {"jsonrpc": "2.0", "method": "prompts/list", "id": 3}
]
```

**Batch Response**

```json
[
  {"jsonrpc": "2.0", "result": {"tools": [...]}, "id": 1},
  {"jsonrpc": "2.0", "result": {"resources": [...]}, "id": 2},
  {"jsonrpc": "2.0", "result": {"prompts": [...]}, "id": 3}
]
```

## 3.8 Protocol Handler Implementation

**Basic MCP Protocol Handler**

```python
import json
from dataclasses import dataclass
from typing import Any, Callable, Optional

@dataclass
class JsonRpcRequest:
    jsonrpc: str
    method: str
    params: dict
    id: Optional[str | int]

@dataclass
class JsonRpcResponse:
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[dict] = None
    id: Optional[str | int] = None

    def to_dict(self) -> dict:
        response = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error is not None:
            response["error"] = self.error
        else:
            response["result"] = self.result
        return response

class McpProtocolHandler:
    def __init__(self, name: str):
        self.name = name
        self._handlers: dict[str, Callable] = {}

    def register_handler(self, method: str,
                         handler: Callable) -> None:
        self._handlers[method] = handler

    def handle_request(self, request: JsonRpcRequest):
        if request.method not in self._handlers:
            return JsonRpcResponse(
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {request.method}"
                }
            )
        try:
            handler = self._handlers[request.method]
            result = handler(request.params)
            return JsonRpcResponse(id=request.id, result=result)
        except Exception as e:
            return JsonRpcResponse(
                id=request.id,
                error={"code": -32603, "message": str(e)}
            )
```

## 3.9 Chapter Summary

In this chapter we learned:

1. JSON-RPC 2.0 request and response structure.
2. Standard error codes (-32700 to -32603).
3. Complete initialization process (Handshake).
4. Capability discovery: tools/list, resources/list, prompts/list.
5. Tool schema with JSON Schema.
6. Tool call with tools/call.
7. Batch Requests.

In the next chapter we will learn the league architecture and how it integrates with the MCP protocol.

---

# 4. League Architecture

## 4.1 Design Principles

The league is designed according to three guiding principles:

1. **Modularity** – Each component is independent and replaceable.
2. **Scalability** – The system can scale from 4 players to millions.
3. **Separation of Responsibility** – Each component is responsible for a single role only.

## 4.2 The Three Layers

The system is composed of three separate layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Layer 1: League                                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   League Manager                            │    │
│  │  • Tournament  • Standings  • Registration                  │    │
│  └─────────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────────┤
│                    Layer 2: Referee                                 │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      Referee                                │    │
│  │  • Match Flow  • Move Validation  • Result Reporting        │    │
│  └─────────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────────┤
│                    Layer 3: Game Rules                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   Even/Odd Rules                             │   │
│  │  • Game Logic  • Win Conditions  • Move Types                │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2.1 Layer 1: League Management

The league layer is responsible for:

- Player registration to the league
- Game schedule creation (Round-Robin)
- Receiving results from referees
- Standings calculation and publication

### 4.2.2 Layer 2: Refereeing

The refereeing layer is responsible for:

- Inviting players to a game
- Managing turns and moves
- Validating move legality
- Announcing results

### 4.2.3 Layer 3: Game Rules

The game rules layer contains:

- The specific game logic
- Win conditions
- Types of possible moves

**Separation Advantage:** Replacing the game (for example, from Even/Odd to Tic-Tac-Toe) requires changes only in Layer 3. Layers 1 and 2 remain unchanged.

## 4.3 Agent Types

### 4.3.1 League Manager

The League Manager is an MCP server that operates on port 8000.

**League Manager Endpoint**

```
League Manager: http://localhost:8000/mcp
```

**Tools it exposes:**

- `register_player` – Register a new player
- `create_schedule` – Create game schedule
- `report_match_result` – Report game result
- `get_standings` – Get standings table

### 4.3.2 Referee

The Referee is an MCP server that operates on port 8001.

**Referee Endpoint**

```
Referee: http://localhost:8001/mcp
```

**Tools it exposes:**

- `start_match` – Start a game
- `collect_choices` – Collect choices from players
- `draw_number` – Draw number and determine winner
- `finalize_match` – End and report to league

### 4.3.3 Player Agent

Each player is a separate MCP server on a unique port.

**Port Allocation for Players**

```
Player 1: http://localhost:8101/mcp
Player 2: http://localhost:8102/mcp
Player 3: http://localhost:8103/mcp
Player 4: http://localhost:8104/mcp
```

**Tools it exposes:**

- `handle_game_invitation` – Handle game invitation
- `choose_parity` – Choose even/odd
- `notify_match_result` – Receive result notification

## 4.4 The Role of the Orchestrator

The Orchestrator (or Host) is the component that coordinates between all agents.

```
                              ┌───────────────────┐
                              │    Orchestrator   │
                              │      (Host)       │
                              └─────────┬─────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            │                           │                           │
           MCP                         MCP                          │
            │                           │                           │
            ↕                           ↕                           ↕
     ┌──────────────┐           ┌──────────────┐           ┌──────────────┐
     │    League    │           │              │           │   Players    │
     │    Manager   │           │    Referee   │           ├──────────────┤
     │              │           │              │           │  Player 1    │
     └──────────────┘           └──────────────┘           │  Player 2    │
                                                           │  Player 3    │
                                                           │  Player 4    │
                                                           └──────────────┘

               All communication goes through the Orchestrator
```

### 4.4.1 Orchestrator Roles

1. **Routing** – Sending requests to the correct agent
2. **Coordination** – Synchronization between agents
3. **Logging** – Recording all communication
4. **Error Handling** – Dealing with failures

> **Important Principle:** Players do not communicate directly with each other. All communication goes through the Orchestrator. This ensures that the protocol is maintained and allows tracking of all messages.

## 4.5 Identifiers in the Protocol

Each component in the system is uniquely identified:

**Table 7: Identifiers in the League Protocol**

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| league_id | String | league_2025_eo | League identifier |
| round_id | Integer | 1, 2, 3 | Round number |
| match_id | String | R1M1 | Match identifier |
| player_id | String | P01 | Player identifier |
| game_type | String | even_odd | Game type |

## 4.6 League Flow

### 4.6.1 Step 1: Player Registration

**Player Registration Request**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "register_player",
    "arguments": {
      "player_name": "AlphaBot",
      "endpoint": "http://localhost:8101/mcp",
      "strategy_type": "adaptive"
    }
  },
  "id": 1
}
```

**Registration Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"player_id\": \"P01\", \"status\": \"registered\"}"
      }
    ]
  },
  "id": 1
}
```

### 4.6.2 Step 2: Game Schedule Creation

After all players are registered, a game schedule is created using the Round-Robin method:

**Table 8: Game Schedule for 4 Players**

| Round | Match | Player A | Player B |
|-------|-------|----------|----------|
| 1 | R1M1 | P01 | P02 |
| 1 | R1M2 | P03 | P04 |
| 2 | R2M1 | P01 | P03 |
| 2 | R2M2 | P02 | P04 |
| 3 | R3M1 | P01 | P04 |
| 3 | R3M2 | P02 | P03 |

### 4.6.3 Step 3: Round Announcement

Before each round, the League Manager publishes a message:

**Round Announcement Message**

```json
{
  "protocol": "league.v1",
  "message_type": "ROUND_ANNOUNCEMENT",
  "league_id": "league_2025_eo",
  "round_id": 1,
  "matches": [
    {
      "match_id": "R1M1",
      "player_A": {"id": "P01", "name": "AlphaBot"},
      "player_B": {"id": "P02", "name": "BetaBot"}
    },
    {
      "match_id": "R1M2",
      "player_A": {"id": "P03", "name": "GammaBot"},
      "player_B": {"id": "P04", "name": "DeltaBot"}
    }
  ],
  "timestamp": "2025-12-10T10:00:00Z"
}
```

### 4.6.4 Step 4: Game Management

**Single Game Flow:**

```
    ┌─────────────┐
    │ Start Match │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐
    │Send Invitations │
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │Collect Choices  │
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │  Draw Number    │
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │    Winner?      │
    └──────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
    Yes         Tie
     │           │
     ▼           ▼
┌─────────────┐ ┌────────────┐
│Report Winner│ │Report Tie  │
└─────┬───────┘ └─────┬──────┘
      │               │
      └──────┬────────┘
             │
             ▼
      ┌───────────┐
      │ End Match │
      └───────────┘
```

### 4.6.5 Step 5: Standings Update

After each game, the standings are updated:

**Standings Table**

```json
{
  "standings": [
    {"rank": 1, "player_id": "P01", "wins": 2, "ties": 0, "losses": 0, "points": 6},
    {"rank": 2, "player_id": "P03", "wins": 1, "ties": 1, "losses": 0, "points": 4},
    {"rank": 3, "player_id": "P02", "wins": 0, "ties": 1, "losses": 1, "points": 1},
    {"rank": 4, "player_id": "P04", "wins": 0, "ties": 0, "losses": 2, "points": 0}
  ]
}
```

## 4.7 Important Principles

### 4.7.1 Single Source of Truth

The referee is the source of truth for the game state. Players do not maintain internal game state. They rely on the information the referee sends.

### 4.7.2 Response Times

Each request has a maximum response time:

**Table 9: Maximum Response Times**

| Action | Maximum Time |
|--------|--------------|
| Game invitation | 5 seconds |
| Move selection | 30 seconds |
| Notifications | 5 seconds |

### 4.7.3 Error Handling

If a player doesn't respond in time or sends an invalid move:

1. The referee sends a `MOVE_REJECTED` message
2. The player receives another opportunity
3. After 3 attempts – technical loss

## 4.8 Chapter Summary

In this chapter we learned:

1. Three architecture layers: League, Refereeing, Game Rules
2. Three agent types: League Manager, Referee, Player
3. Port allocation: 8000 for league, 8001 for referee, 8101-8104 for players
4. The Orchestrator's role in communication coordination
5. Unique identifiers for each component in the system
6. Complete league flow from registration to standings

In the next chapter we will focus on the specific Even/Odd game implementation.

---

# 5. Even/Odd Game Implementation

## 5.1 Game Description

The "Even/Odd" game is a simple game that allows learning important principles in agent programming. The simplicity allows focusing on the architecture and protocol.

### 5.1.1 Game Rules

1. Two players participate in a game
2. Each player chooses "even" or "odd" – in parallel
3. The referee draws a natural number between 1 and 10
4. If the number is even – the player who chose "even" wins
5. If the number is odd – the player who chose "odd" wins
6. If both choose the same option – tie

> **Important Clarification:** Both players choose **in parallel**, without knowing the opponent's choice. If both choose the same option – the result is a **tie**, whether they were right or wrong.

### 5.1.2 Results Table

**Table 10: Even/Odd Game Results Table**

| A's Choice | B's Choice | Even Number | Odd Number |
|------------|------------|-------------|------------|
| even | odd | A wins | B wins |
| odd | even | B wins | A wins |
| even | even | Tie | Tie |
| odd | odd | Tie | Tie |

### 5.1.3 Points Calculation

- **Win:** 3 points
- **Tie:** 1 point for each player
- **Loss:** 0 points

## 5.2 Protocol Messages

### 5.2.1 Game Invitation

The referee sends an invitation to each player:

**GAME_INVITATION – Game Invitation**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "handle_game_invitation",
    "arguments": {
      "protocol": "league.v1",
      "message_type": "GAME_INVITATION",
      "match_id": "R1M1",
      "game_type": "even_odd",
      "opponent_id": "P02",
      "timeout_seconds": 5
    }
  },
  "id": 10
}
```

**GAME_JOIN_ACK – Invitation Confirmation**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"message_type\": \"GAME_JOIN_ACK\",
               \"match_id\": \"R1M1\",
               \"player_id\": \"P01\",
               \"accept\": true}"
    }]
  },
  "id": 10
}
```

### 5.2.2 Choice Request

The referee requests each player to choose:

**CHOOSE_PARITY_CALL – Choice Request**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "choose_parity",
    "arguments": {
      "protocol": "league.v1",
      "message_type": "CHOOSE_PARITY_CALL",
      "match_id": "R1M1",
      "opponent_id": "P02",
      "standings": [...],
      "timeout_seconds": 30
    }
  },
  "id": 11
}
```

**Choice Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"message_type\": \"PARITY_CHOICE\",
               \"match_id\": \"R1M1\",
               \"player_id\": \"P01\",
               \"choice\": \"even\"}"
    }]
  },
  "id": 11
}
```

### 5.2.3 Result Notification

The referee notifies the players of the result:

**GAME_OVER – Result Notification**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "notify_match_result",
    "arguments": {
      "protocol": "league.v1",
      "message_type": "GAME_OVER",
      "match_id": "R1M1",
      "drawn_number": 6,
      "number_parity": "even",
      "choices": {
        "P01": "even",
        "P02": "odd"
      },
      "winner_id": "P01",
      "result_type": "win"
    }
  },
  "id": 12
}
```

## 5.3 Player Agent Implementation

### 5.3.1 Basic Structure

**Player Agent Structure**

```python
from dataclasses import dataclass
from typing import Optional
import random

@dataclass
class PlayerState:
    player_id: str
    history: list = None

    def __post_init__(self):
        self.history = self.history or []

class EvenOddPlayer:
    def __init__(self, player_id: str):
        self.state = PlayerState(player_id=player_id)

    def get_tools(self) -> list:
        """Return list of MCP tools this player exposes."""
        return [
            {
                "name": "handle_game_invitation",
                "description": "Handle invitation to a game",
                "inputSchema": {...}
            },
            {
                "name": "choose_parity",
                "description": "Choose even or odd",
                "inputSchema": {...}
            },
            {
                "name": "notify_match_result",
                "description": "Receive match result",
                "inputSchema": {...}
            }
        ]
```

### 5.3.2 Handling Invitation

**handle_game_invitation Implementation**

```python
def handle_game_invitation(self, params: dict) -> dict:
    """
    Handle game invitation from referee.
    Must respond within 5 seconds!
    """
    match_id = params.get("match_id")
    game_type = params.get("game_type")
    opponent_id = params.get("opponent_id")

    # Log the invitation
    print(f"Received invitation for {match_id}")
    print(f"Opponent: {opponent_id}, Game: {game_type}")

    # Always accept (could add logic to reject)
    return {
        "message_type": "GAME_JOIN_ACK",
        "match_id": match_id,
        "player_id": self.state.player_id,
        "accept": True,
        "timestamp": datetime.now().isoformat() + "Z"
    }
```

### 5.3.3 Move Selection – The Agent's Heart

**choose_parity Implementation**

```python
def choose_parity(self, params: dict) -> dict:
    """
    Choose even or odd.
    This is YOUR main implementation!
    Must respond within 30 seconds!
    """
    match_id = params.get("match_id")
    opponent_id = params.get("opponent_id")
    standings = params.get("standings", [])

    # === YOUR STRATEGY HERE ===
    choice = self._make_choice(opponent_id, standings)
    # ==========================

    return {
        "message_type": "PARITY_CHOICE",
        "match_id": match_id,
        "player_id": self.state.player_id,
        "choice": choice,
        "timestamp": datetime.now().isoformat() + "Z"
    }

def _make_choice(self, opponent_id: str,
                 standings: list) -> str:
    """Override this method with your strategy."""
    return random.choice(["even", "odd"])
```

### 5.3.4 Receiving Result

**notify_match_result Implementation**

```python
def notify_match_result(self, params: dict) -> dict:
    """
    Receive match result notification.
    Use this to update internal state.
    """
    match_id = params.get("match_id")
    winner_id = params.get("winner_id")
    drawn_number = params.get("drawn_number")
    choices = params.get("choices", {})

    # Update history
    self.state.history.append({
        "match_id": match_id,
        "opponent": params.get("opponent_id"),
        "my_choice": choices.get(self.state.player_id),
        "drawn_number": drawn_number,
        "won": winner_id == self.state.player_id
    })

    return {
        "message_type": "RESULT_ACK",
        "match_id": match_id,
        "player_id": self.state.player_id,
        "received": True
    }
```

## 5.4 Possible Strategies

### 5.4.1 Strategy 1: Random

**Random Strategy**

```python
import random

def _make_choice(self, opponent_id, standings):
    return random.choice(["even", "odd"])
```

**Advantage:** Simple, unpredictable.

**Disadvantage:** 50% average chance.

### 5.4.2 Strategy 2: Deterministic

**Deterministic Strategy**

```python
def _make_choice(self, opponent_id, standings):
    return "even"  # Always choose even
```

**Advantage:** Simplest possible.

**Disadvantage:** Completely predictable.

### 5.4.3 Strategy 3: History-Based

**History-Based Strategy**

```python
def _make_choice(self, opponent_id, standings):
    if not self.state.history:
        return random.choice(["even", "odd"])

    # Analyze last 5 games
    recent = self.state.history[-5:]

    # Count parity of drawn numbers
    even_count = sum(
        1 for h in recent
        if h['drawn_number'] % 2 == 0
    )
    odd_count = len(recent) - even_count

    # Choose based on observed bias
    if even_count > odd_count:
        return "even"
    elif odd_count > even_count:
        return "odd"
    else:
        return random.choice(["even", "odd"])
```

### 5.4.4 Strategy 4: LLM-Guided

**LLM-Guided Strategy**

```python
import anthropic  # or openai

def _make_choice(self, opponent_id, standings):
    client = anthropic.Anthropic()

    prompt = f"""You are playing an Even/Odd game.
    Your ID: {self.state.player_id}
    Opponent: {opponent_id}
    Current standings:
    {standings}
    Previous games:
    {self.state.history[-5:]}

    Choose "even" or "odd" to maximize winning.
    Reply with only the word "even" or "odd".
    """

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )

    choice = response.content[0].text.strip().lower()
    return choice if choice in ["even", "odd"] else "even"
```

> **Note on Strategies:** Since the drawing is truly random, there is no "better" strategy from a mathematical perspective. Any strategy will enter to learn the architecture, not to win. The goal is 50% success over time.

## 5.5 MCP Server Implementation

**MCP Server for Player**

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()
player = EvenOddPlayer("P01")

@app.post("/mcp")
async def handle_mcp_request(request: dict):
    """Handle incoming MCP requests."""
    jsonrpc = request.get("jsonrpc")
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "result": {"tools": player.get_tools()},
            "id": request_id
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "handle_game_invitation":
            result = player.handle_game_invitation(arguments)
        elif tool_name == "choose_parity":
            result = player.choose_parity(arguments)
        elif tool_name == "notify_match_result":
            result = player.notify_match_result(arguments)
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Unknown tool"},
                "id": request_id
            }

        return {
            "jsonrpc": "2.0",
            "result": {
                "content": [{"type": "text", "text": str(result)}]
            },
            "id": request_id
        }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8101)
```

## 5.6 Complete Game Flow

```
┌─────────┐                 ┌──────────┐                 ┌──────────┐
│ Referee │                 │ Player 1 │                 │ Player 2 │
└────┬────┘                 └────┬─────┘                 └────┬─────┘
     │                           │                            │
     │  GAME_INVITATION          │                            │
     │──────────────────────────>│                            │
     │                           │                            │
     │  GAME_INVITATION          │                            │
     │───────────────────────────┼───────────────────────────>│
     │                           │                            │
     │  GAME_JOIN_ACK            │                            │
     │<──────────────────────────│                            │
     │                           │                            │
     │  GAME_JOIN_ACK            │                            │
     │<──────────────────────────┼────────────────────────────│
     │                           │                            │
     │  CHOOSE_PARITY_CALL       │                            │
     │──────────────────────────>│                            │
     │                           │                            │
     │  CHOOSE_PARITY_CALL       │                            │
     │───────────────────────────┼───────────────────────────>│
     │                           │                            │
     │  PARITY_CHOICE: even      │                            │
     │<──────────────────────────│                            │
     │                           │                            │
     │  PARITY_CHOICE: odd       │                            │
     │<──────────────────────────┼────────────────────────────│
     │                           │                            │
     │     Draw: 6 (even)        │                            │
     │                           │                            │
     │  GAME_OVER (winner: P1)   │                            │
     │──────────────────────────>│                            │
     │                           │                            │
     │  GAME_OVER (winner: P1)   │                            │
     │───────────────────────────┼───────────────────────────>│
     │                           │                            │
     │  RESULT_ACK               │                            │
     │<──────────────────────────│                            │
     │                           │                            │
     │  RESULT_ACK               │                            │
     │<──────────────────────────┼────────────────────────────│
     │                           │                            │
```

## 5.7 Chapter Summary

In this chapter we learned:

1. Even/Odd game rules
2. Protocol messages: GAME_INVITATION, CHOOSE_PARITY_CALL, GAME_OVER
3. Player agent implementation with three tools
4. Four possible strategies
5. Complete MCP server in FastAPI
6. Complete game flow

In the next chapter we will learn how to design the system to support large scale.

---

# 6. Scaling for Production Environment

## 6.1 Motivation

What if we want to run:
- Thousands of leagues in parallel?
- Tens of thousands of referees?
- Millions of players?

The architecture we learned fits 4 players. Modular design enables scaling without protocol changes.

## 6.2 Scalability Principles

### 6.2.1 Principle 1: State Separation

Each component maintains only its own state. There is no dependency on other components' state.

**State Separation**

```python
# BAD - shared state
class BadLeague:
    players = []  # Class variable - shared!

# GOOD - isolated state
class GoodLeague:
    def __init__(self, league_id: str):
        self.league_id = league_id
        self.players = []  # Instance variable - isolated
```

### 6.2.2 Principle 2: Asynchronous Communication

All calls should be asynchronous. This enables handling a large number of requests in parallel.

**Asynchronous Communication**

```python
import asyncio
import httpx

async def call_player(endpoint: str, request: dict):
    """Async call to player MCP server."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{endpoint}/mcp",
            json=request,
            timeout=30.0
        )
        return response.json()

async def collect_choices(players: list):
    """Collect choices from all players in parallel."""
    tasks = [
        call_player(p["endpoint"], create_choose_request(p))
        for p in players
    ]
    return await asyncio.gather(*tasks)
```

### 6.2.3 Principle 3: Stateless

Components should be as stateless as possible. State is stored in an external data store.

**Stateless Component**

```python
class StatelessReferee:
    def __init__(self, db_connection):
        self.db = db_connection

    async def start_match(self, match_info: dict):
        # Load state from DB
        match_state = await self.db.get_match(match_info["match_id"])

        # Process
        match_state["status"] = "in_progress"

        # Save state to DB
        await self.db.save_match(match_state)

        return match_state
```

## 6.3 Distributed Architecture

### 6.3.1 Routing Layer

Instead of a single Orchestrator, we use a routing layer:

```
                    ┌─────────────────────┐
                    │    Load Balancer    │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Orchestrator 1  │  │ Orchestrator 2  │  │ Orchestrator 3  │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ Message Queue (Redis/RabbitMQ)│
              └───────────────┬───────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ Worker 1 │        │ Worker 2 │        │ Worker 3 │
    └──────────┘        └──────────┘        └──────────┘
```

### 6.3.2 Storage Layer

Data is stored in a distributed store:

**Table 11: Data Store Types**

| Store Type | Use | Examples |
|------------|-----|----------|
| Cache | Current game state | Redis, Memcached |
| Document DB | Game history | MongoDB, DynamoDB |
| Relational DB | Standings tables | PostgreSQL, MySQL |
| Message Queue | Coordination between components | RabbitMQ, Kafka |

## 6.4 Design Patterns

### 6.4.1 Factory Pattern for Games

**Factory Pattern**

```python
from abc import ABC, abstractmethod

class Game(ABC):
    @abstractmethod
    def get_valid_moves(self, state: dict) -> list:
        pass

    @abstractmethod
    def make_move(self, state: dict, move: dict) -> dict:
        pass

    @abstractmethod
    def check_winner(self, state: dict) -> str | None:
        pass

class EvenOddGame(Game):
    def get_valid_moves(self, state: dict) -> list:
        return ["even", "odd"]

    def make_move(self, state: dict, move: dict) -> dict:
        state["choices"][move["player_id"]] = move["choice"]
        return state

    def check_winner(self, state: dict) -> str | None:
        # Implementation...
        pass

class GameFactory:
    _games = {
        "even_odd": EvenOddGame,
        # "tic_tac_toe": TicTacToeGame,
        # "rock_paper_scissors": RPSGame,
    }

    @classmethod
    def create(cls, game_type: str) -> Game:
        if game_type not in cls._games:
            raise ValueError(f"Unknown game: {game_type}")
        return cls._games[game_type]()
```

### 6.4.2 Strategy Pattern for Agents

**Strategy Pattern**

```python
from abc import ABC, abstractmethod

class PlayerStrategy(ABC):
    @abstractmethod
    def choose(self, context: dict) -> str:
        pass

class RandomStrategy(PlayerStrategy):
    def choose(self, context: dict) -> str:
        return random.choice(["even", "odd"])

class LLMStrategy(PlayerStrategy):
    def __init__(self, llm_client):
        self.llm = llm_client

    def choose(self, context: dict) -> str:
        prompt = self._build_prompt(context)
        response = self.llm.complete(prompt)
        return self._parse_response(response)

class AdaptiveStrategy(PlayerStrategy):
    def __init__(self):
        self.history = []

    def choose(self, context: dict) -> str:
        # Analyze history and choose
        pass

# Usage
class Player:
    def __init__(self, strategy: PlayerStrategy):
        self.strategy = strategy

    def choose_parity(self, context: dict) -> str:
        return self.strategy.choose(context)
```

### 6.4.3 Observer Pattern for Notifications

**Observer Pattern**

```python
from abc import ABC, abstractmethod

class LeagueObserver(ABC):
    @abstractmethod
    async def on_match_complete(self, result: dict):
        pass

    @abstractmethod
    async def on_standings_update(self, standings: list):
        pass

class StandingsUpdater(LeagueObserver):
    async def on_match_complete(self, result: dict):
        # Update standings in database
        pass

    async def on_standings_update(self, standings: list):
        # Notify subscribers
        pass

class WebhookNotifier(LeagueObserver):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def on_match_complete(self, result: dict):
        async with httpx.AsyncClient() as client:
            await client.post(self.webhook_url, json=result)

class League:
    def __init__(self):
        self._observers: list[LeagueObserver] = []

    def add_observer(self, observer: LeagueObserver):
        self._observers.append(observer)

    async def notify_match_complete(self, result: dict):
        for observer in self._observers:
            await observer.on_match_complete(result)
```

## 6.5 Failure Handling

### 6.5.1 Retry Strategies

**Retry Strategy**

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def call_player_with_retry(endpoint: str, request: dict):
    """Call player with automatic retry on failure."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{endpoint}/mcp",
            json=request,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
```

### 6.5.2 Default Fallback on Failure

**Default Fallback**

```python
async def get_player_choice(player: dict, context: dict) -> str:
    """Get choice with fallback."""
    try:
        result = await call_player_with_retry(
            player["endpoint"],
            create_choose_request(context)
        )
        return parse_choice(result)
    except Exception as e:
        logger.error(f"Player {player['id']} failed: {e}")
        # Default choice on failure
        return "even"
```

### 6.5.3 Circuit Breaker

**Circuit Breaker**

```python
from pybreaker import CircuitBreaker

player_breaker = CircuitBreaker(
    fail_max=5,        # Open after 5 failures
    reset_timeout=60   # Try again after 60 seconds
)

@player_breaker
async def call_player_safe(endpoint: str, request: dict):
    """Call player with circuit breaker protection."""
    return await call_player_with_retry(endpoint, request)

# Usage
try:
    result = await call_player_safe(endpoint, request)
except CircuitBreakerError:
    logger.warning(f"Circuit open for {endpoint}")
    result = default_response()
```

## 6.6 Monitoring

### 6.6.1 Important Metrics

**Table 12: Monitoring Metrics**

| Metric | Unit | Alert Threshold |
|--------|------|-----------------|
| Average response time | Milliseconds | > 500 ms |
| Error percentage | Percent | > 1% |
| Active games | Number | > 10000 |
| Connection failures | Per minute | > 10 |

### 6.6.2 Log Recording

**Structured Log Recording**

```python
import logging
import json

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_mcp_request(self, request: dict, response: dict,
                        duration_ms: float):
        self.logger.info(json.dumps({
            "event": "mcp_request",
            "method": request.get("method"),
            "request_id": request.get("id"),
            "duration_ms": duration_ms,
            "success": "error" not in response,
            "timestamp": datetime.now().isoformat()
        }))

    def log_match_result(self, match_id: str, winner: str,
                         duration_ms: float):
        self.logger.info(json.dumps({
            "event": "match_complete",
            "match_id": match_id,
            "winner": winner,
            "duration_ms": duration_ms
        }))
```

## 6.7 Future Extensions

### 6.7.1 Support for Additional Games

The architecture supports adding new games:

- Tic-Tac-Toe
- Rock-Paper-Scissors
- Connect Four

### 6.7.2 Tiered Leagues

- Division into tiers (Bronze, Silver, Gold)
- Promotion and relegation between tiers
- Seasonal tournaments

### 6.7.3 Advanced LLM Integration

- Agents that learn from experience
- Opponent strategy analysis
- New strategy creation

## 6.8 Chapter Summary

In this chapter we learned:

1. Scalability principles: State separation, asynchronous, statelessness
2. Distributed architecture with routing layer
3. Design patterns: Factory, Strategy, Observer
4. Failure handling: Retry, Circuit Breaker
5. Monitoring and logging
6. Possible future extensions

In the next chapter we will detail the exercise requirements.

---

# 7. Home Exercise

## 7.1 Task Overview

In this exercise you will develop an AI agent that participates in an "Even/Odd" game league. Your agent must communicate using the MCP protocol that we learned.

### 7.1.1 What to Submit

1. **Source code file:** `player_agent.py` – your agent
2. **Documentation file:** `README.md` – explanation of strategy
3. **Configuration file:** `config.json` (if relevant) – connection details

## 7.2 Technical Requirements

### 7.2.1 MCP Protocol Requirements

**Critical requirements – without compliance the agent will be disqualified:**

1. The agent must implement complete MCP initialization process
2. Every message must be in JSON-RPC 2.0 format
3. The agent must expose tools through tools/list
4. Every tool must include valid inputSchema

### 7.2.2 Initialization Requirements

The agent must support the complete initialization process:

**Required initializeResult Response**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {"listChanged": true}
    },
    "serverInfo": {
      "name": "StudentAgent",
      "version": "1.0.0"
    }
  },
  "id": 1
}
```

### 7.2.3 Response Time Requirements

**Table 13: Maximum Response Times**

| Action | Maximum Time | Required Response |
|--------|--------------|-------------------|
| initialize | 5 seconds | initializeResult |
| tools/list | 5 seconds | Tool list |
| Game invitation | 5 seconds | GAME_JOIN_ACK |
| Move selection | 30 seconds | PARITY_CHOICE |

**Penalty for timeout:** If the agent doesn't respond in time, it loses the game with a **technical loss**.

## 7.3 Required Agent Structure

### 7.3.1 Required Tools

The agent must expose the following tools:

**Required Tools in tools/list**

```json
{
  "tools": [
    {
      "name": "handle_game_invitation",
      "description": "Handle invitation to join a game",
      "inputSchema": {
        "type": "object",
        "properties": {
          "match_id": {"type": "string"},
          "game_type": {"type": "string"},
          "opponent_id": {"type": "string"}
        },
        "required": ["match_id", "game_type", "opponent_id"]
      }
    },
    {
      "name": "choose_parity",
      "description": "Choose even or odd for the game",
      "inputSchema": {
        "type": "object",
        "properties": {
          "match_id": {"type": "string"},
          "opponent_id": {"type": "string"},
          "standings": {"type": "array"}
        },
        "required": ["match_id"]
      }
    },
    {
      "name": "notify_match_result",
      "description": "Receive match result notification",
      "inputSchema": {
        "type": "object",
        "properties": {
          "match_id": {"type": "string"},
          "winner_id": {"type": "string"},
          "drawn_number": {"type": "integer"}
        },
        "required": ["match_id"]
      }
    }
  ]
}
```

### 7.3.2 Agent Class

**Required Agent Interface**

```python
class PlayerAgent:
    """Required interface for your agent."""

    def __init__(self, player_id: str, config: dict = None):
        """Initialize the agent with player ID."""
        self.player_id = player_id
        self.config = config or {}
        self.history = []

    def get_server_info(self) -> dict:
        """Return MCP server info for initialization."""
        return {
            "name": f"Agent_{self.player_id}",
            "version": "1.0.0"
        }

    def get_capabilities(self) -> dict:
        """Return MCP capabilities."""
        return {"tools": {"listChanged": True}}

    def get_tools(self) -> list:
        """Return list of tools with inputSchema."""
        # Must return all three required tools
        pass

    def handle_tool_call(self, name: str, arguments: dict) -> dict:
        """Handle incoming tool calls."""
        pass

    def choose_parity(self, context: dict) -> str:
        """Your strategy implementation."""
        pass
```

## 7.4 Development Environment

### 7.4.1 Installation

**Development Environment Installation**

```bash
# 1. Clone the league framework
git clone https://github.com/course/mcp-league.git

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run local test
python test_agent.py your_agent.py
```

### 7.4.2 Running Local League

**Running Local League**

```bash
# Run local league with 4 agents
python run_local_league.py \
  --agents your_agent.py dummy1.py dummy2.py dummy3.py \
  --rounds 3

# Run with verbose MCP logging
python run_local_league.py \
  --agents your_agent.py dummy1.py \
  --verbose
```

### 7.4.3 Test Checklist

Before submission, make sure your agent passes all tests:

- [ ] Agent completes MCP initialization process
- [ ] Agent returns valid tools/list
- [ ] Every tool includes complete inputSchema
- [ ] Agent responds to invitation within 5 seconds
- [ ] Agent responds to choice request within 30 seconds
- [ ] Choice is "even" or "odd" only
- [ ] Agent receives result notification without crashing
- [ ] Agent completes a league of 6 games

## 7.5 Common Errors

Errors that will cause grade reduction:

1. Lack of support for MCP initialization process
2. Missing or invalid inputSchema
3. Use of non-standard error codes
4. Exceeding response times
5. Crashing mid-game

## 7.6 Code Skeleton

**MCP Agent Code Skeleton**

```python
"""
Even/Odd League Player Agent
Student: [YOUR NAME]
"""

import json
import random
from datetime import datetime
from fastapi import FastAPI
import uvicorn

app = FastAPI()

class PlayerAgent:
    def __init__(self, player_id: str):
        self.player_id = player_id
        self.history = []

    def get_server_info(self) -> dict:
        return {"name": f"Agent_{self.player_id}", "version": "1.0.0"}

    def get_capabilities(self) -> dict:
        return {"tools": {"listChanged": True}}

    def get_tools(self) -> list:
        return [
            {
                "name": "handle_game_invitation",
                "description": "Handle game invitation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "match_id": {"type": "string"},
                        "opponent_id": {"type": "string"}
                    },
                    "required": ["match_id"]
                }
            },
            {
                "name": "choose_parity",
                "description": "Choose even or odd",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "match_id": {"type": "string"}
                    },
                    "required": ["match_id"]
                }
            },
            # ... (continue with notify_match_result)
        ]

    def handle_game_invitation(self, params: dict) -> dict:
        # YOUR IMPLEMENTATION
        pass

    def choose_parity(self, params: dict) -> dict:
        # YOUR STRATEGY
        pass

    def notify_match_result(self, params: dict) -> dict:
        # YOUR IMPLEMENTATION
        pass


# Initialize agent
player = PlayerAgent("P01")

@app.post("/mcp")
async def handle_mcp(request: dict):
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": player.get_capabilities(),
                "serverInfo": player.get_server_info()
            },
            "id": request_id
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "result": {"tools": player.get_tools()},
            "id": request_id
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        # Route to appropriate handler
        # ...

    return {"jsonrpc": "2.0", "error": {"code": -32601}, "id": request_id}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8101)
```

## 7.7 Frequently Asked Questions

### 7.7.1 Is it allowed to use an LLM?

**Yes.** Allowed and recommended. However:

- You are responsible for API costs
- Must meet response times
- Must handle API failures

### 7.7.2 What if the course server fails?

Every game that was not completed is considered a technical loss. Check thoroughly before submission!

## 7.8 Schedule

**Table 14: Schedule**

| Week | Activity | Notes |
|------|----------|-------|
| Week 1 | Exercise opening | Publication of this document |
| Week 2 | Last date for questions | Questions in forum |
| Week 3 | Submission deadline | 23:59 |
| Week 4 | League run | At the announced time |

## 7.9 Summary

In this chapter we detailed:

1. Complete MCP protocol requirements
2. Tool structure and required schemas
3. Development and testing environment
4. Evaluation criteria
5. Skeleton code to start

**Good luck!**

## 7.10 English References

1. Anthropic, *Model context protocol specification*, Official MCP documentation, 2024. [Online]. Available: https://modelcontextprotocol.io/

2. JSON-RPC Working Group, *JSON-RPC 2.0 specification*, 2010. [Online]. Available: https://www.jsonrpc.org/specification

---

© Dr. Yoram Segal - All Rights Reserved
