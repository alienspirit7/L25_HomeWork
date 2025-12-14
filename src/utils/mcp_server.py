"""Base MCP Server implementation using FastAPI."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import json
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime, timezone


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
            
            # Log incoming JSON request
            self.logger.info(f"[RECV Request] {json.dumps(payload, indent=2)}")
            
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
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                }
                self.logger.info(f"[SEND Response] {json.dumps(error_response, indent=2)}")
                return JSONResponse(error_response)
            
            success_response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
            
            # Log outgoing JSON response
            self.logger.info(f"[SEND Response] {json.dumps(success_response, indent=2)}")
            
            return JSONResponse(success_response)
        
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": payload.get("id")
            }
            self.logger.info(f"[SEND Response] {json.dumps(error_response, indent=2)}")
            return JSONResponse(error_response)
    
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
    
    # ========================================================================
    # Auth Token Validation
    # ========================================================================
    
    def validate_auth_token(self, params: Dict, expected_token: str) -> Optional[Dict]:
        """
        Validate auth_token in request.
        
        Args:
            params: Request parameters
            expected_token: Expected auth token value
        
        Returns:
            None if valid, error dict if invalid
        """
        provided_token = params.get("auth_token")
        if not provided_token:
            return self.create_league_error("E011", "AUTH_TOKEN_MISSING")
        if provided_token != expected_token:
            return self.create_league_error("E012", "AUTH_TOKEN_INVALID")
        return None
    
    def validate_utc_timestamp(self, timestamp: str) -> bool:
        """Ensure timestamp is UTC (ends with Z or +00:00)."""
        return timestamp.endswith('Z') or timestamp.endswith('+00:00')
    
    # ========================================================================
    # Error Response Helpers
    # ========================================================================
    
    def create_league_error(self, error_code: str, description: str,
                           original_message_type: Optional[str] = None,
                           context: Optional[Dict] = None) -> Dict:
        """
        Create LEAGUE_ERROR response.
        
        Args:
            error_code: Error code (E001, E011, etc.)
            description: Error description
            original_message_type: Message type that caused error
            context: Additional context
        
        Returns:
            LEAGUE_ERROR message dict
        """
        from .helpers import generate_conversation_id, utc_timestamp
        return {
            "protocol": "league.v2",
            "message_type": "LEAGUE_ERROR",
            "sender": "league_manager",
            "timestamp": utc_timestamp(),
            "conversation_id": generate_conversation_id(),
            "error_code": error_code,
            "error_description": description,
            "original_message_type": original_message_type,
            "context": context or {},
            "retryable": error_code in ["E001", "E009"]  # Timeout and connection errors
        }
    
    def create_game_error(self, error_code: str, description: str,
                         match_id: str, affected_player: str,
                         action_required: str, consequence: str,
                         sender: str, retry_info: Optional[Dict] = None) -> Dict:
        """
        Create GAME_ERROR response.
        
        Args:
            error_code: Error code (E001, E003, E004)
            description: Error description
            match_id: Match identifier
            affected_player: Player ID
            action_required: Required action that failed
            consequence: What happens if not resolved
            sender: Sender (e.g., "referee:REF01")
            retry_info: Retry information dict
        
        Returns:
            GAME_ERROR message dict
        """
        from .helpers import generate_conversation_id, utc_timestamp
        return {
            "protocol": "league.v2",
            "message_type": "GAME_ERROR",
            "sender": sender,
            "timestamp": utc_timestamp(),
            "conversation_id": generate_conversation_id(),
            "match_id": match_id,
            "error_code": error_code,
            "error_description": description,
            "affected_player": affected_player,
            "action_required": action_required,
            "retry_info": retry_info,
            "consequence": consequence
        }
