"""Base MCP Server implementation using FastAPI."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import json
from typing import Dict, Any, Callable, List


class MCPServer:
    """Base class for MCP server implementation."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.app = FastAPI(title=f"MCP Server - {name}")
        self.tools: Dict[str, Callable] = {}
        self.logger = logging.getLogger(name)
        
        # Register MCP endpoints
        self.app.post("/mcp")(self.handle_mcp_request)
    
    def register_tool(self, name: str, handler: Callable, description: str = ""):
        """Register a tool handler."""
        self.tools[name] = handler
        self.logger.info(f"Registered tool: {name}")
    
    async def handle_mcp_request(self, request: Request) -> JSONResponse:
        """Handle incoming MCP JSON-RPC 2.0 requests."""
        try:
            payload = await request.json()
            method = payload.get("method")
            params = payload.get("params", {})
            request_id = payload.get("id")
            
            self.logger.debug(f"Received: {method}")
            
            # Handle different MCP methods
            if method == "initialize":
                result = self._handle_initialize()
            elif method == "tools/list":
                result = self._handle_tools_list()
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = await self._handle_tool_call(tool_name, arguments)
            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                })
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })
        
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": payload.get("id")
            })
    
    def _handle_initialize(self) -> Dict:
        """Handle MCP initialize."""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": self.name,
                "version": self.version
            },
            "capabilities": {}
        }
    
    def _handle_tools_list(self) -> Dict:
        """List available tools."""
        return {
            "tools": [{"name": name} for name in self.tools.keys()]
        }
    
    async def _handle_tool_call(self, tool_name: str, arguments: Dict) -> Any:
        """Execute a tool call."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        handler = self.tools[tool_name]
        result = await handler(arguments) if callable(handler) else handler
        
        # Wrap result in content array for MCP
        if isinstance(result, dict):
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
        elif isinstance(result, str):
            return {"content": [{"type": "text", "text": result}]}
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
