"""MCP Client for making tool calls to other agents."""
import httpx
import logging
import json
from typing import Dict, Any, Optional


class MCPClient:
    """Client for calling MCP tools on remote servers."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.logger = logging.getLogger(__name__)
    
    async def call_tool(
        self,
        endpoint: str,
        tool_name: str,
        arguments: Dict[str, Any],
        request_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Call a tool on a remote MCP server.
        
        Args:
            endpoint: Full URL to MCP endpoint (e.g., http://localhost:8101/mcp)
            tool_name: Name of the tool to call
            arguments: Tool arguments
            request_id: Optional JSON-RPC request ID
        
        Returns:
            Tool result
        """
        if request_id is None:
            import random
            request_id = random.randint(1, 1000000)
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": request_id
        }
        
        try:
            self.logger.debug(f"Calling {tool_name} on {endpoint}")
            
            # Log outgoing JSON message
            self.logger.info(f"[SEND → {endpoint}] {json.dumps(payload, indent=2)}")
            
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Log incoming JSON response
            self.logger.info(f"[RECV ← {endpoint}] {json.dumps(result, indent=2)}")
            
            if "error" in result:
                self.logger.error(f"Tool call error: {result['error']}")
                raise Exception(f"Tool call failed: {result['error']}")
            
            return result.get("result", {})
        
        except httpx.TimeoutException:
            self.logger.error(f"Timeout calling {tool_name} on {endpoint}")
            raise
        except Exception as e:
            self.logger.error(f"Error calling {tool_name}: {e}")
            raise
    
    async def call_tool_with_retry(
        self,
        endpoint: str,
        tool_name: str,
        arguments: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> Optional[Dict[str, Any]]:
        """
        Call tool with retry on retryable errors.
        
        Per League Protocol V2 spec (section 2.9.4):
        - Maximum retries: 3
        - Delay between retries: 2 seconds
        - Retryable errors: E001 (timeout), E009 (connection)
        
        Args:
            endpoint: MCP endpoint URL
            tool_name: Name of tool to call
            arguments: Tool arguments
            max_retries: Maximum number of retries (default: 3)
            retry_delay: Delay in seconds between retries (default: 2.0)
        
        Returns:
            Tool result or None if all retries exhausted
        """
        import asyncio
        
        for attempt in range(max_retries + 1):
            try:
                return await self.call_tool(endpoint, tool_name, arguments)
            except httpx.TimeoutException as e:
                # E001: TIMEOUT_ERROR - retryable
                if attempt < max_retries:
                    self.logger.warning(
                        f"Timeout on {tool_name} (attempt {attempt + 1}/{max_retries + 1}). "
                        f"Retrying in {retry_delay}s..."
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                self.logger.error(f"Timeout: All {max_retries} retries exhausted for {tool_name}")
                return None
            except httpx.ConnectError as e:
                # E009: CONNECTION_ERROR - retryable
                if attempt < max_retries:
                    self.logger.warning(
                        f"Connection error on {tool_name} (attempt {attempt + 1}/{max_retries + 1}). "
                        f"Retrying in {retry_delay}s..."
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                self.logger.error(f"Connection error: All {max_retries} retries exhausted for {tool_name}")
                return None
            except Exception as e:
                # Non-retryable errors - fail immediately
                self.logger.error(f"Non-retryable error on {tool_name}: {e}")
                return None
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
