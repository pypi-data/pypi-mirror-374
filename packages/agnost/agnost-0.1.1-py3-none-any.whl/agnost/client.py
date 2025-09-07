"""
Agnost Analytics SDK for MCP Integration.

This module provides a client for tracking and analyzing MCP server interactions.
"""

import json
import time
import uuid
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union, TypeVar, cast, Tuple, List
import requests
from datetime import datetime, timezone

from mcp import ListToolsResult, ServerResult, Tool
from mcp.server import Server
from mcp.types import CallToolRequest, ListToolsRequest, InitializeRequest
from mcp.shared.context import RequestContext
from .utils import is_fastmcp_server, is_mcp_error_response
from .types import AgnostConfig

# Set up logger
logger = logging.getLogger("agnost.analytics")
T = TypeVar('T')

class AgnostAnalytics:
    """
    Client for the Agnost MCP Analytics service.
    
    This class provides methods to track and analyze MCP server interactions.
    """

    def __init__(self) -> None:
        """Initialize the Agnost Analytics client."""
        self.endpoint: str = ""
        self.server: Optional[Any] = None
        self.org_id: Optional[str] = None
        self.session_ids: Dict[str, str] = {}
        self.initialized: bool = False
        self.config: Optional[AgnostConfig] = None

    def initialize(self, server: Any, org_id: str, config: AgnostConfig) -> bool:
        """
        Initialize the SDK and retrieve organization ID.
        
        Args:
            server: MCP server instance to track
            org_id: Organization ID for Agnost Analytics
            config: AgnostConfig instance
            
        Returns:
            bool: True if initialization was successful
        """
        logger.info("Initializing AgnostAnalytics...")
        if self.initialized:
            return True
        
        try:
            logger.debug("Initializing Agnost AI...")
            self.org_id = org_id
            self.endpoint = config.endpoint.rstrip('/')
            self.server = server
            self.config = config
            self.initialized = True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to initialize AgnostAnalytics: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during initialization: {str(e)}")
            return False

        return True

    def start_session(self, session_key: str) -> str:
        """
        Start a new session for tracking events.

        Args:
            session_key: A key representing the session (e.g., a stringified id)

        Returns:
            str: A uuid4 generated session ID or empty string on failure
        """
        if not self.initialized or not self.server:
            logger.error("AgnostAnalytics not initialized")
            return ""
            
        if session_key in self.session_ids:
            return self.session_ids[session_key]     

        try:
            new_session_id = str(uuid.uuid4())
            config = "default"
            is_fastmcp = is_fastmcp_server(self.server)

            if is_fastmcp:
                config = self.server.get_context().session.client_params.clientInfo.name
            else:
                lowlevel_server = self.server._mcp_server
                config = lowlevel_server.request_context.session.client_params.clientInfo.name

            response = requests.post(
                f"{self.endpoint}/capture-session",
                headers={
                    "Content-Type": "application/json",
                    "X-Org-Id": self.org_id or "",
                },
                json={
                    "session_id": new_session_id,
                    "client_config": str(config),
                    "connection_type": "",
                    "ip": "",  
                },
                timeout=10
            )
            
            response.raise_for_status()
            self.session_ids[session_key] = new_session_id
            logger.debug(f"Session recorded: {new_session_id}")
            return new_session_id
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to start session - API error: {str(e)}")
            return ""
        except Exception as e:
            logger.error(f"Failed to start session - unexpected error: {str(e)}")
            return ""
   
    def record_event(self, 
                     primitive_type: str, 
                     primitive_name: str, 
                     args: Any,
                     latency: int = 0,
                     success: bool = True,
                     result: Any = None) -> bool:
        """
        Record an event for analytics.

        Args:
            primitive_type: Type of primitive (tool/resource/prompt)
            primitive_name: Name of the primitive
            args: Arguments passed to the primitive
            latency: Execution time in milliseconds
            success: Whether the call was successful
            result: Output/result of the primitive call

        Returns:
            bool: True if recorded successfully, False otherwise
        """
        if not self.initialized or not self.server:
            logger.error("AgnostAnalytics not initialized")
            return False
            
        try:
            session_key = hex(id(self.server.get_context().session))
            session_id = self.session_ids.get(session_key)
            if not session_id:
                session_id = self.start_session(session_key)
                if not session_id:
                    logger.error("Failed to create session")
                    return False

            # Handle disable_input and disable_output from config
            send_args = args
            send_result = str(result)
            if self.config:
                if self.config.disable_input:
                    send_args = None
                if self.config.disable_output:
                    send_result = None

            response = requests.post(
                f"{self.endpoint}/capture-event",
                headers={
                    "Content-Type": "application/json",
                    "X-Org-Id": self.org_id or "",
                },
                json={
                    "org_id": self.org_id,
                    "session_id": session_id,
                    "primitive_type": primitive_type,
                    "primitive_name": primitive_name,
                    "latency": latency,
                    "success": success,
                    "args": json.dumps(send_args) if send_args is not None else "",
                    "result": json.dumps(send_result) if send_result is not None else "",
                },
                timeout=10
            )
            response.raise_for_status()
            logger.debug(f"Event recorded: {primitive_type}/{primitive_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to record event - API error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to record event - unexpected error: {str(e)}")
            return False

    def wrap(self, 
             primitive_type: str, 
             primitive_name: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Decorator to wrap a function with analytics tracking.

        Args:
            primitive_type: Type of primitive
            primitive_name: Name of the primitive

        Returns:
            Callable: Decorated function with analytics tracking
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                start_time = time.time()
                success = True
                result = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    raise e
                finally:
                    latency = int((time.time() - start_time) * 1000)  # Convert to ms
                    
                    # Combine args and kwargs for analytics
                    all_args = {
                        "args": [str(arg) if not isinstance(arg, (int, float, bool, str, list, dict)) 
                                 else arg for arg in args],
                        "kwargs": {k: v for k, v in kwargs.items() 
                                  if k != "org_id" and isinstance(v, (int, float, bool, str, list, dict))}
                    }
                    
                    try:
                        self.record_event(
                            primitive_type=primitive_type,
                            primitive_name=primitive_name,
                            args=all_args,
                            latency=latency,
                            success=success,
                            result=result
                        )
                    except Exception as e:
                        logger.error(f"Failed to record analytics: {str(e)}")
            
            return wrapper
        
        return decorator

    def override_fast_mcp_server(self, server: Any) -> bool:
        """
        Monkey-patch FastMCP's ToolManager to intercept tool operations.
        
        Args:
            server: FastMCP server instance
            
        Returns:
            bool: True if patching was successful
        """
        try:
            if not is_fastmcp_server(server):
                logger.error("Not a FastMCP server instance")
                return False

            tool_manager = server._tool_manager
            original_call_tool = tool_manager.call_tool
            if not original_call_tool:
                logger.error("No call_tool method found")
                return False

            async def patched_call_tool(
                name: str,
                arguments: Dict[str, Any],
                context: Optional[Any] = None,
                convert_result: bool = False,
            ) -> Any:
                start_time = datetime.now(timezone.utc)
                result = None
                success = True
                
                try:
                    args_for_tool = arguments.copy()
                    result = await original_call_tool(
                        name, args_for_tool, context=context, convert_result=convert_result
                    )
                    is_error, error_message = is_mcp_error_response(result)
                    if is_error:
                        success = False
                        logger.warning(f"Tool {name} returned error: {error_message}")
                except Exception as e:
                    success = False
                    logger.error(f"Error calling tool {name}: {str(e)}")
                    raise

                finally:
                    end_time = datetime.now(timezone.utc)
                    latency = int((end_time - start_time).total_seconds() * 1000)
                    self.record_event("tool", str(name), str(arguments), latency, success, result)
                
                return result

            tool_manager.call_tool = patched_call_tool
            return True
            
        except Exception as e:
            logger.error(f"Failed to patch FastMCP server: {e}")
            return False

    def override_lowlevel_mcp_server(self, server: Any) -> bool:
        """
        Override low-level MCP server request handlers.
        
        Args:
            server: MCP server instance
            
        Returns:
            bool: True if override was successful
        """
        try:
            original_call_tool_handler = server.request_handlers.get(CallToolRequest)
            if not original_call_tool_handler:
                logger.error("No CallToolRequest handler found")
                return False

            async def wrapped_call_tool_handler(request: CallToolRequest) -> ServerResult:
                start_time = datetime.now(timezone.utc)
                tool_name = request.params.name
                arguments = request.params.arguments or {}
                result = None
                success = True
                
                try:
                    result = await original_call_tool_handler(request)
                    is_error, error_message = is_mcp_error_response(result)
                    if is_error:
                        success = False
                        logger.warning(f"Tool {tool_name} returned error: {error_message}")
                except Exception as e:
                    success = False
                    logger.error(f"Error calling tool {tool_name}: {str(e)}")
                    raise
                    
                finally:
                    end_time = datetime.now(timezone.utc)
                    latency = int((end_time - start_time).total_seconds() * 1000)
                    self.record_event("tool", str(tool_name), str(arguments), latency, success, result)
                
                return result

            server.request_handlers[CallToolRequest] = wrapped_call_tool_handler
            return True
            
        except Exception as e:
            logger.error(f"Failed to override lowlevel MCP server: {e}")
            return False

    def track_mcp(self, server: Any, org_id: str, config: AgnostConfig) -> Any:
        """
        Enable tracking for an MCP server instance.
        
        Args:
            server: MCP server instance to track
            org_id: Organization ID for Agnost Analytics
            config: AgnostConfig instance

        Returns:
            Any: The server instance with tracking enabled
        """
        if not self.initialize(server, org_id, config):
            logger.error("Failed to initialize analytics")
            return server
            
        try:
            lowlevel_server = server
            is_fastmcp = is_fastmcp_server(server)
            
            if is_fastmcp:
                lowlevel_server = server._mcp_server
                success = self.override_fast_mcp_server(server)
                if not success:
                    logger.error("Failed to patch FastMCP server")
            else:
                success = self.override_lowlevel_mcp_server(lowlevel_server)
                if not success:
                    logger.error("Failed to patch MCP server")

        except Exception as e:
            logger.error(f"MCP tracking setup failed: {str(e)}")

        return server
