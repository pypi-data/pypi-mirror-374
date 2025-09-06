# Python-A2A Implementation Strategy
## Critical Issues & Enterprise Improvements

**Version**: 1.0  
**Date**: January 2025  
**Status**: Implementation Ready  

---

## Executive Summary

This document outlines the comprehensive implementation strategy for addressing critical gaps in the python-a2a library, focusing on MCP protocol compatibility, memory/checkpointing, and Google A2A v0.3 compliance. The strategy is divided into 4 phases with clear priorities and implementation details.

### Key Objectives
- ✅ Fix MCP protocol compatibility issues (GitHub #74, #65)
- ✅ Implement enterprise-grade memory and checkpointing (#67, #68)
- ✅ Add Google A2A v0.3 compliance features
- ✅ Enhance developer experience and production readiness

---

## Phase 1: MCP Protocol Compliance Fix (CRITICAL - Week 1)

### Overview
The current MCP implementation has critical protocol compatibility issues that break interoperability with standard MCP servers.

### Issues Identified
1. **HTTP Method Inconsistency**: Using GET/POST instead of JSON-RPC 2.0
2. **Missing Protocol Negotiation**: No `initialize` handshake
3. **Incorrect Message Format**: Not following MCP specification

### 1.1 Implement Spec-Compliant MCP Client

**File**: `python_a2a/mcp/spec_compliant_client.py`

```python
"""
Specification-compliant MCP client following 2025-03-26 standard.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List
import httpx
from dataclasses import dataclass
from enum import Enum

class MCPErrorCode(Enum):
    """Standard MCP error codes"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

@dataclass
class MCPCapabilities:
    """MCP client capabilities"""
    tools: Dict[str, bool] = None
    resources: Dict[str, bool] = None
    prompts: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = {"listChanged": True}
        if self.resources is None:
            self.resources = {"listChanged": True, "subscribe": True}
        if self.prompts is None:
            self.prompts = {"listChanged": True}

@dataclass
class MCPClientInfo:
    """MCP client information"""
    name: str = "python-a2a"
    version: str = "0.5.9"

class SpecCompliantMCPClient:
    """
    MCP client that follows the official MCP 2025-03-26 specification.
    
    This implementation properly handles:
    - JSON-RPC 2.0 protocol
    - Initialize handshake
    - Proper error handling
    - Capability negotiation
    """
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = None
        self.request_id_counter = 0
        self.server_capabilities: Optional[Dict[str, Any]] = None
        self.initialized = False
        
    def _get_request_id(self) -> int:
        """Generate unique request ID"""
        self.request_id_counter += 1
        return self.request_id_counter
    
    async def _call_jsonrpc(
        self, 
        server_url: str, 
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make JSON-RPC 2.0 call to MCP server"""
        if not self.session:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        
        try:
            response = await self.session.post(
                server_url,
                json=request,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Handle JSON-RPC errors
            if "error" in result:
                error = result["error"]
                raise MCPProtocolError(
                    f"MCP Error {error['code']}: {error['message']}"
                )
            
            return result
            
        except httpx.HTTPError as e:
            raise MCPConnectionError(f"HTTP error: {str(e)}")
        except json.JSONDecodeError as e:
            raise MCPProtocolError(f"Invalid JSON response: {str(e)}")
    
    async def _send_notification(
        self, 
        server_url: str, 
        notification: Dict[str, Any]
    ) -> None:
        """Send JSON-RPC notification (no response expected)"""
        if not self.session:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        
        try:
            await self.session.post(
                server_url,
                json=notification,
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            # Notifications don't require responses, so we log but don't raise
            print(f"Warning: Failed to send notification: {e}")
    
    async def initialize(self, server_url: str) -> Dict[str, Any]:
        """
        Perform MCP initialization handshake.
        
        This is required before any other operations and establishes:
        - Protocol version compatibility
        - Client/server capabilities
        - Implementation information
        
        Args:
            server_url: URL of the MCP server
            
        Returns:
            Server information and capabilities
        """
        capabilities = MCPCapabilities()
        client_info = MCPClientInfo()
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": capabilities.tools,
                    "resources": capabilities.resources,
                    "prompts": capabilities.prompts
                },
                "clientInfo": {
                    "name": client_info.name,
                    "version": client_info.version
                }
            }
        }
        
        response = await self._call_jsonrpc(server_url, request)
        
        # Store server capabilities
        result = response["result"]
        self.server_capabilities = result.get("capabilities", {})
        
        # Send initialized notification
        await self._send_notification(server_url, {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        })
        
        self.initialized = True
        return result
    
    async def list_tools(self, server_url: str) -> List[Dict[str, Any]]:
        """
        List available tools from MCP server.
        
        Args:
            server_url: URL of the MCP server
            
        Returns:
            List of tool definitions
        """
        if not self.initialized:
            await self.initialize(server_url)
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": "tools/list",
            "params": {}
        }
        
        response = await self._call_jsonrpc(server_url, request)
        return response["result"]["tools"]
    
    async def call_tool(
        self, 
        server_url: str, 
        name: str, 
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            server_url: URL of the MCP server
            name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if not self.initialized:
            await self.initialize(server_url)
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        
        response = await self._call_jsonrpc(server_url, request)
        return response["result"]
    
    async def list_resources(self, server_url: str) -> List[Dict[str, Any]]:
        """List available resources from MCP server"""
        if not self.initialized:
            await self.initialize(server_url)
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": "resources/list",
            "params": {}
        }
        
        response = await self._call_jsonrpc(server_url, request)
        return response["result"]["resources"]
    
    async def read_resource(
        self, 
        server_url: str, 
        uri: str
    ) -> Dict[str, Any]:
        """Read a resource from MCP server"""
        if not self.initialized:
            await self.initialize(server_url)
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": "resources/read",
            "params": {"uri": uri}
        }
        
        response = await self._call_jsonrpc(server_url, request)
        return response["result"]
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.aclose()

# Custom exceptions
class MCPProtocolError(Exception):
    """MCP protocol-related errors"""
    pass

class MCPConnectionError(Exception):
    """MCP connection-related errors"""
    pass
```

### 1.2 Fix LangChain Integration

**File**: `python_a2a/langchain/mcp_fixed.py`

```python
"""
Fixed MCP-LangChain integration using spec-compliant client.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from ..mcp.spec_compliant_client import SpecCompliantMCPClient, MCPProtocolError, MCPConnectionError
from .exceptions import MCPToolConversionError, LangChainNotInstalledError

logger = logging.getLogger(__name__)

# Check for LangChain availability
try:
    from langchain.tools import Tool
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    class Tool:
        pass

def to_langchain_tool_fixed(mcp_url: str, tool_name: Optional[str] = None):
    """
    Convert MCP server tool(s) to LangChain tool(s) using spec-compliant client.
    
    This is the FIXED version that properly implements MCP 2025-03-26 specification.
    
    Args:
        mcp_url: URL of the MCP server
        tool_name: Optional specific tool to convert
        
    Returns:
        LangChain tool or list of tools
        
    Raises:
        LangChainNotInstalledError: If LangChain is not installed
        MCPToolConversionError: If tool conversion fails
    """
    if not HAS_LANGCHAIN:
        raise LangChainNotInstalledError()
    
    try:
        # Create spec-compliant MCP client
        mcp_client = SpecCompliantMCPClient()
        
        # Get available tools using proper protocol
        available_tools = asyncio.run(mcp_client.list_tools(mcp_url))
        logger.info(f"Found {len(available_tools)} tools on MCP server using spec-compliant protocol")
        
        # Filter tools if specific tool requested
        if tool_name is not None:
            available_tools = [t for t in available_tools if t.get("name") == tool_name]
            if not available_tools:
                raise MCPToolConversionError(f"Tool '{tool_name}' not found on MCP server")
        
        # Create LangChain tools
        langchain_tools = []
        
        for tool_info in available_tools:
            name = tool_info.get("name", "unnamed_tool")
            description = tool_info.get("description", f"MCP Tool: {name}")
            
            logger.info(f"Creating LangChain tool for MCP tool: {name}")
            
            def create_tool_func(tool_name, client_url):
                def tool_func(*args, **kwargs):
                    """Call MCP tool using spec-compliant client"""
                    try:
                        # Handle different input patterns
                        if len(args) == 1 and not kwargs:
                            # Single argument case
                            arguments = {"input": args[0]}
                        else:
                            # Use kwargs as arguments
                            arguments = kwargs
                        
                        # Create new client for each call (or implement connection pooling)
                        client = SpecCompliantMCPClient()
                        
                        # Call tool using proper MCP protocol
                        result = asyncio.run(client.call_tool(
                            client_url, tool_name, arguments
                        ))
                        
                        # Clean up
                        asyncio.run(client.close())
                        
                        # Extract result content
                        content = result.get("content", [])
                        if content and isinstance(content, list):
                            # Return first text content
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "text":
                                    return item.get("text", "")
                        
                        # Fallback to string representation
                        return str(result)
                        
                    except Exception as e:
                        logger.exception(f"Error calling MCP tool {tool_name}")
                        return f"Error calling MCP tool: {str(e)}"
                
                return tool_func
            
            # Create LangChain tool with proper function
            tool_func = create_tool_func(name, mcp_url)
            
            lc_tool = Tool(
                name=name,
                description=description,
                func=tool_func
            )
            
            # Add metadata
            if hasattr(lc_tool, "metadata"):
                lc_tool.metadata = {
                    "source": "mcp_spec_compliant",
                    "url": mcp_url,
                    "tool_info": tool_info
                }
            
            langchain_tools.append(lc_tool)
            logger.info(f"Successfully created LangChain tool: {name}")
        
        # Return single tool if requested, otherwise return list
        if tool_name is not None and len(langchain_tools) == 1:
            return langchain_tools[0]
        
        return langchain_tools
        
    except (MCPProtocolError, MCPConnectionError) as e:
        logger.error(f"MCP protocol error: {e}")
        raise MCPToolConversionError(f"MCP protocol error: {str(e)}")
    except Exception as e:
        logger.exception("Failed to convert MCP tool to LangChain format")
        raise MCPToolConversionError(f"Failed to convert MCP tool: {str(e)}")

# Async version for better performance
async def to_langchain_tool_async(mcp_url: str, tool_name: Optional[str] = None):
    """Async version of MCP to LangChain tool conversion"""
    if not HAS_LANGCHAIN:
        raise LangChainNotInstalledError()
    
    mcp_client = SpecCompliantMCPClient()
    
    try:
        # Get tools asynchronously
        available_tools = await mcp_client.list_tools(mcp_url)
        
        # Filter and create tools (same logic as sync version)
        # ... implementation details ...
        
    finally:
        await mcp_client.close()
```

### 1.3 Update Module Imports

**File**: `python_a2a/langchain/__init__.py`

```python
"""
Updated LangChain integration module with fixed MCP support.
"""

# Import fixed implementations
from .mcp_fixed import to_langchain_tool_fixed as to_langchain_tool
from .mcp_fixed import to_langchain_tool_async

# Keep backward compatibility
from .mcp import to_mcp_server
from .a2a import to_a2a_server, to_langchain_agent

__all__ = [
    "to_langchain_tool",  # Now uses fixed implementation
    "to_langchain_tool_async",  # New async version
    "to_mcp_server",
    "to_a2a_server", 
    "to_langchain_agent"
]
```

---

## Phase 2: Enterprise Memory & Checkpointing (Weeks 2-3)

### Overview
Implement enterprise-grade state management with distributed checkpointing, workflow pause/resume, and persistent memory.

### 2.1 Checkpoint Storage Architecture

**File**: `python_a2a/checkpoint/__init__.py`

```python
"""
Enterprise checkpoint and state management system.
"""

from .store import CheckpointStore, RedisCheckpointStore, DatabaseCheckpointStore, FileCheckpointStore
from .context import PersistentWorkflowContext, CheckpointableContext
from .manager import CheckpointManager, DistributedCheckpointManager

__all__ = [
    "CheckpointStore",
    "RedisCheckpointStore", 
    "DatabaseCheckpointStore",
    "FileCheckpointStore",
    "PersistentWorkflowContext",
    "CheckpointableContext",
    "CheckpointManager",
    "DistributedCheckpointManager"
]
```

**File**: `python_a2a/checkpoint/store.py`

```python
"""
Checkpoint storage implementations for different backends.
"""

import json
import pickle
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class CheckpointStore(ABC):
    """Abstract base class for checkpoint storage backends"""
    
    @abstractmethod
    async def save_checkpoint(
        self, 
        workflow_id: str, 
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save workflow checkpoint.
        
        Args:
            workflow_id: Unique workflow identifier
            state: Workflow state to checkpoint
            metadata: Optional metadata about the checkpoint
            
        Returns:
            Checkpoint ID
        """
        pass
    
    @abstractmethod
    async def load_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Load workflow checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Checkpoint data including state and metadata
        """
        pass
    
    @abstractmethod
    async def list_checkpoints(
        self, 
        workflow_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List checkpoints for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            limit: Maximum number of checkpoints to return
            
        Returns:
            List of checkpoint metadata
        """
        pass
    
    @abstractmethod
    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def cleanup_old_checkpoints(
        self, 
        workflow_id: str,
        keep_count: int = 10
    ) -> int:
        """
        Clean up old checkpoints keeping only the most recent.
        
        Args:
            workflow_id: Workflow identifier
            keep_count: Number of recent checkpoints to keep
            
        Returns:
            Number of checkpoints deleted
        """
        pass

class RedisCheckpointStore(CheckpointStore):
    """Redis-based checkpoint storage for distributed systems"""
    
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        key_prefix: str = "a2a:checkpoint",
        default_ttl: int = 86400 * 7  # 7 days
    ):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self._redis = None
    
    async def _get_redis(self):
        """Get Redis connection (lazy initialization)"""
        if not self._redis:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self.redis_url, decode_responses=True)
            except ImportError:
                raise ImportError("redis package required for RedisCheckpointStore")
        return self._redis
    
    async def save_checkpoint(
        self, 
        workflow_id: str, 
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save checkpoint to Redis"""
        redis = await self._get_redis()
        
        checkpoint_id = f"{workflow_id}:{int(time.time() * 1000)}:{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "workflow_id": workflow_id,
            "state": state,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "created_at": timestamp
        }
        
        # Serialize checkpoint data
        serialized_data = json.dumps(checkpoint_data, default=str)
        
        # Save checkpoint
        checkpoint_key = f"{self.key_prefix}:data:{checkpoint_id}"
        await redis.set(checkpoint_key, serialized_data, ex=self.default_ttl)
        
        # Add to workflow's checkpoint index
        index_key = f"{self.key_prefix}:index:{workflow_id}"
        await redis.zadd(index_key, {checkpoint_id: time.time()})
        
        # Set TTL on index
        await redis.expire(index_key, self.default_ttl)
        
        logger.info(f"Saved checkpoint {checkpoint_id} for workflow {workflow_id}")
        return checkpoint_id
    
    async def load_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Load checkpoint from Redis"""
        redis = await self._get_redis()
        
        checkpoint_key = f"{self.key_prefix}:data:{checkpoint_id}"
        serialized_data = await redis.get(checkpoint_key)
        
        if not serialized_data:
            raise KeyError(f"Checkpoint {checkpoint_id} not found")
        
        return json.loads(serialized_data)
    
    async def list_checkpoints(
        self, 
        workflow_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List checkpoints for workflow from Redis"""
        redis = await self._get_redis()
        
        index_key = f"{self.key_prefix}:index:{workflow_id}"
        
        # Get checkpoint IDs ordered by timestamp (newest first)
        checkpoint_ids = await redis.zrevrange(index_key, 0, limit - 1)
        
        checkpoints = []
        for checkpoint_id in checkpoint_ids:
            try:
                checkpoint_data = await self.load_checkpoint(checkpoint_id)
                checkpoints.append({
                    "checkpoint_id": checkpoint_id,
                    "workflow_id": workflow_id,
                    "timestamp": checkpoint_data.get("timestamp"),
                    "metadata": checkpoint_data.get("metadata", {})
                })
            except KeyError:
                # Checkpoint was deleted, remove from index
                await redis.zrem(index_key, checkpoint_id)
        
        return checkpoints
    
    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete checkpoint from Redis"""
        redis = await self._get_redis()
        
        # Extract workflow_id from checkpoint_id
        workflow_id = checkpoint_id.split(':')[0]
        
        # Delete checkpoint data
        checkpoint_key = f"{self.key_prefix}:data:{checkpoint_id}"
        deleted_count = await redis.delete(checkpoint_key)
        
        # Remove from index
        index_key = f"{self.key_prefix}:index:{workflow_id}"
        await redis.zrem(index_key, checkpoint_id)
        
        return deleted_count > 0
    
    async def cleanup_old_checkpoints(
        self, 
        workflow_id: str,
        keep_count: int = 10
    ) -> int:
        """Clean up old checkpoints in Redis"""
        redis = await self._get_redis()
        
        index_key = f"{self.key_prefix}:index:{workflow_id}"
        
        # Get all checkpoint IDs
        all_checkpoints = await redis.zrevrange(index_key, 0, -1)
        
        if len(all_checkpoints) <= keep_count:
            return 0
        
        # Delete old checkpoints
        old_checkpoints = all_checkpoints[keep_count:]
        deleted_count = 0
        
        for checkpoint_id in old_checkpoints:
            if await self.delete_checkpoint(checkpoint_id):
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old checkpoints for workflow {workflow_id}")
        return deleted_count

class DatabaseCheckpointStore(CheckpointStore):
    """Database-based checkpoint storage using SQLAlchemy"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._engine = None
        self._session_maker = None
    
    async def _get_session(self):
        """Get database session (lazy initialization)"""
        if not self._engine:
            try:
                from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
                from sqlalchemy.orm import sessionmaker
                
                self._engine = create_async_engine(self.database_url)
                self._session_maker = sessionmaker(
                    self._engine, class_=AsyncSession, expire_on_commit=False
                )
            except ImportError:
                raise ImportError("sqlalchemy package required for DatabaseCheckpointStore")
        
        return self._session_maker()
    
    # Implementation details for database operations...
    # (Similar structure to Redis but using SQLAlchemy ORM)

class FileCheckpointStore(CheckpointStore):
    """File-based checkpoint storage for development and testing"""
    
    def __init__(self, base_directory: str = "./checkpoints"):
        import os
        self.base_directory = base_directory
        os.makedirs(base_directory, exist_ok=True)
    
    async def save_checkpoint(
        self, 
        workflow_id: str, 
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save checkpoint to file"""
        import os
        
        checkpoint_id = f"{workflow_id}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "workflow_id": workflow_id,
            "state": state,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Create workflow directory
        workflow_dir = os.path.join(self.base_directory, workflow_id)
        os.makedirs(workflow_dir, exist_ok=True)
        
        # Save checkpoint
        checkpoint_file = os.path.join(workflow_dir, f"{checkpoint_id}.json")
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, default=str, indent=2)
        
        return checkpoint_id
    
    # Implementation details for other file operations...
```

### 2.2 Persistent Workflow Context

**File**: `python_a2a/checkpoint/context.py`

```python
"""
Persistent workflow context with checkpointing capabilities.
"""

import time
import uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import logging

from ..workflow.flow import WorkflowContext
from .store import CheckpointStore

logger = logging.getLogger(__name__)

@dataclass
class CheckpointMetadata:
    """Metadata for checkpoints"""
    step_id: Optional[str] = None
    step_name: Optional[str] = None
    step_index: Optional[int] = None
    total_steps: Optional[int] = None
    trigger: str = "manual"  # manual, auto, error, pause
    tags: List[str] = field(default_factory=list)
    
class PersistentWorkflowContext(WorkflowContext):
    """
    Enhanced workflow context with automatic checkpointing and persistence.
    
    Features:
    - Automatic checkpointing at configurable intervals
    - Persistent state across workflow executions
    - Error recovery with checkpoint restoration
    - Distributed workflow coordination
    """
    
    def __init__(
        self,
        initial_data: Optional[Dict[str, Any]] = None,
        checkpoint_store: Optional[CheckpointStore] = None,
        workflow_id: Optional[str] = None,
        checkpoint_interval: int = 5,  # Checkpoint every 5 steps
        auto_cleanup: bool = True,
        max_checkpoints: int = 20
    ):
        super().__init__(initial_data)
        
        self.checkpoint_store = checkpoint_store
        self.workflow_id = workflow_id or f"workflow_{uuid.uuid4().hex[:12]}"
        self.checkpoint_interval = checkpoint_interval
        self.auto_cleanup = auto_cleanup
        self.max_checkpoints = max_checkpoints
        
        # Checkpoint tracking
        self.step_count = 0
        self.last_checkpoint_id: Optional[str] = None
        self.checkpoint_history: List[str] = []
        
        # State tracking
        self.is_restored = False
        self.restore_checkpoint_id: Optional[str] = None
    
    async def checkpoint(
        self, 
        metadata: Optional[CheckpointMetadata] = None,
        force: bool = False
    ) -> Optional[str]:
        """
        Create a checkpoint of current workflow state.
        
        Args:
            metadata: Optional metadata about the checkpoint
            force: Force checkpoint even if store is not configured
            
        Returns:
            Checkpoint ID if successful, None otherwise
        """
        if not self.checkpoint_store and not force:
            return None
        
        try:
            # Prepare state for checkpointing
            state = {
                "workflow_id": self.workflow_id,
                "data": self.data,
                "results": self.results,
                "history": self.history,
                "errors": self.errors,
                "step_count": self.step_count,
                "start_time": self.start_time,
                "checkpoint_history": self.checkpoint_history
            }
            
            # Prepare metadata
            checkpoint_metadata = {
                "workflow_name": self.data.get("workflow_name", "Unknown"),
                "total_execution_time": time.time() - self.start_time,
                "step_count": self.step_count,
                "error_count": len(self.errors),
                "result_count": len(self.results)
            }
            
            if metadata:
                checkpoint_metadata.update({
                    "step_id": metadata.step_id,
                    "step_name": metadata.step_name,
                    "step_index": metadata.step_index,
                    "total_steps": metadata.total_steps,
                    "trigger": metadata.trigger,
                    "tags": metadata.tags
                })
            
            # Save checkpoint
            checkpoint_id = await self.checkpoint_store.save_checkpoint(
                self.workflow_id,
                state,
                checkpoint_metadata
            )
            
            # Update tracking
            self.last_checkpoint_id = checkpoint_id
            self.checkpoint_history.append(checkpoint_id)
            
            # Cleanup old checkpoints if enabled
            if self.auto_cleanup and len(self.checkpoint_history) > self.max_checkpoints:
                await self._cleanup_old_checkpoints()
            
            logger.info(f"Created checkpoint {checkpoint_id} for workflow {self.workflow_id}")
            return checkpoint_id
            
        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return None
    
    async def add_result(self, step_id: str, result: Any) -> None:
        """Add result and auto-checkpoint if configured"""
        super().add_result(step_id, result)
        self.step_count += 1
        
        # Auto-checkpoint at intervals
        if (self.checkpoint_store and 
            self.checkpoint_interval > 0 and 
            self.step_count % self.checkpoint_interval == 0):
            
            metadata = CheckpointMetadata(
                step_id=step_id,
                step_index=self.step_count,
                trigger="auto"
            )
            await self.checkpoint(metadata)
    
    async def add_error(self, step_id: str, error: Exception) -> None:
        """Add error and create error checkpoint"""
        super().add_error(step_id, error)
        
        # Create checkpoint on error for recovery
        if self.checkpoint_store:
            metadata = CheckpointMetadata(
                step_id=step_id,
                trigger="error",
                tags=["error", "recovery"]
            )
            await self.checkpoint(metadata)
    
    @classmethod
    async def from_checkpoint(
        cls,
        checkpoint_id: str,
        checkpoint_store: CheckpointStore,
        **kwargs
    ) -> 'PersistentWorkflowContext':
        """
        Restore workflow context from checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to restore from
            checkpoint_store: Checkpoint storage backend
            **kwargs: Additional arguments for context creation
            
        Returns:
            Restored workflow context
        """
        # Load checkpoint data
        checkpoint_data = await checkpoint_store.load_checkpoint(checkpoint_id)
        state = checkpoint_data["state"]
        
        # Create context with restored data
        context = cls(
            initial_data=state["data"],
            checkpoint_store=checkpoint_store,
            workflow_id=state["workflow_id"],
            **kwargs
        )
        
        # Restore state
        context.results = state["results"]
        context.history = state["history"]
        context.errors = state["errors"]
        context.step_count = state["step_count"]
        context.start_time = state["start_time"]
        context.checkpoint_history = state.get("checkpoint_history", [])
        
        # Mark as restored
        context.is_restored = True
        context.restore_checkpoint_id = checkpoint_id
        
        logger.info(f"Restored workflow context from checkpoint {checkpoint_id}")
        return context
    
    async def list_available_checkpoints(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List available checkpoints for this workflow"""
        if not self.checkpoint_store:
            return []
        
        return await self.checkpoint_store.list_checkpoints(self.workflow_id, limit)
    
    async def _cleanup_old_checkpoints(self) -> None:
        """Clean up old checkpoints beyond the maximum count"""
        if not self.checkpoint_store:
            return
        
        try:
            deleted_count = await self.checkpoint_store.cleanup_old_checkpoints(
                self.workflow_id,
                self.max_checkpoints
            )
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old checkpoints")
        except Exception as e:
            logger.error(f"Failed to cleanup old checkpoints: {e}")
```

### 2.3 Pausable Flow Engine

**File**: `python_a2a/workflow/pausable_flow.py`

```python
"""
Enhanced Flow with pause/resume capabilities and checkpointing.
"""

import asyncio
import uuid
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

from .flow import Flow
from ..checkpoint.store import CheckpointStore
from ..checkpoint.context import PersistentWorkflowContext, CheckpointMetadata

logger = logging.getLogger(__name__)

class FlowState(Enum):
    """Flow execution states"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

@dataclass
class FlowExecutionInfo:
    """Information about flow execution"""
    flow_id: str
    state: FlowState
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None
    checkpoint_id: Optional[str] = None

class PausableFlow(Flow):
    """
    Enhanced Flow with pause/resume capabilities and enterprise checkpointing.
    
    Features:
    - Pause execution at any point
    - Resume from checkpoints
    - Distributed execution coordination
    - Step-by-step debugging
    - Error recovery
    """
    
    def __init__(
        self,
        agent_network: 'AgentNetwork',
        checkpoint_store: Optional[CheckpointStore] = None,
        flow_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(agent_network, **kwargs)
        
        self.checkpoint_store = checkpoint_store
        self.flow_id = flow_id or f"flow_{uuid.uuid4().hex[:12]}"
        
        # Execution state
        self.state = FlowState.CREATED
        self.current_step_index = 0
        self.execution_info = FlowExecutionInfo(
            flow_id=self.flow_id,
            state=self.state
        )
        
        # Pause/resume control
        self.is_paused = False
        self.pause_after_step: Optional[str] = None
        self.pause_conditions: List[Callable] = []
        self.resume_event = asyncio.Event()
        
        # Step execution hooks
        self.before_step_hooks: List[Callable] = []
        self.after_step_hooks: List[Callable] = []
        self.error_hooks: List[Callable] = []
    
    def add_pause_condition(self, condition: Callable[[Dict[str, Any]], bool]) -> None:
        """
        Add a condition that will pause execution when met.
        
        Args:
            condition: Function that takes context and returns True to pause
        """
        self.pause_conditions.append(condition)
    
    def add_before_step_hook(self, hook: Callable) -> None:
        """Add hook to run before each step"""
        self.before_step_hooks.append(hook)
    
    def add_after_step_hook(self, hook: Callable) -> None:
        """Add hook to run after each step"""
        self.after_step_hooks.append(hook)
    
    def add_error_hook(self, hook: Callable) -> None:
        """Add hook to run when errors occur"""
        self.error_hooks.append(hook)
    
    async def pause_after(self, step_id: Optional[str] = None) -> None:
        """
        Schedule pause after specified step or immediately.
        
        Args:
            step_id: Step ID to pause after, or None to pause immediately
        """
        if step_id is None:
            # Pause immediately
            self.is_paused = True
            self.state = FlowState.PAUSED
            self.resume_event.clear()
            logger.info(f"Flow {self.flow_id} paused immediately")
        else:
            # Schedule pause after step
            self.pause_after_step = step_id
            logger.info(f"Flow {self.flow_id} scheduled to pause after step {step_id}")
    
    async def resume(self, checkpoint_id: Optional[str] = None) -> None:
        """
        Resume flow execution.
        
        Args:
            checkpoint_id: Optional checkpoint to resume from
        """
        if checkpoint_id:
            # Resume from specific checkpoint
            logger.info(f"Resuming flow {self.flow_id} from checkpoint {checkpoint_id}")
            # This would be implemented with checkpoint restoration logic
        else:
            # Just unpause current execution
            self.is_paused = False
            self.state = FlowState.RUNNING
            self.resume_event.set()
            logger.info(f"Flow {self.flow_id} resumed")
    
    async def cancel(self) -> None:
        """Cancel flow execution"""
        self.state = FlowState.CANCELED
        self.is_paused = False
        self.resume_event.set()
        logger.info(f"Flow {self.flow_id} canceled")
    
    async def run(
        self, 
        initial_context: Optional[Dict[str, Any]] = None,
        start_from_step: int = 0
    ) -> Any:
        """
        Execute the flow with pause/resume support.
        
        Args:
            initial_context: Initial context data
            start_from_step: Step index to start from (for resume)
            
        Returns:
            Flow execution result
        """
        import time
        
        # Initialize execution
        self.state = FlowState.RUNNING
        self.execution_info.start_time = time.time()
        self.execution_info.total_steps = len(self.steps)
        self.current_step_index = start_from_step
        
        # Create persistent context
        context = PersistentWorkflowContext(
            initial_context,
            checkpoint_store=self.checkpoint_store,
            workflow_id=self.flow_id
        )
        
        # Add workflow name to context
        context.data["workflow_name"] = self.name
        
        result = None
        
        try:
            # Execute steps starting from specified index
            for i in range(start_from_step, len(self.steps)):
                step = self.steps[i]
                self.current_step_index = i
                self.execution_info.current_step = i
                
                # Check pause conditions
                await self._check_pause_conditions(context)
                
                # Wait if paused
                if self.is_paused:
                    await self._handle_pause(context, step)
                    if self.state == FlowState.CANCELED:
                        return {"status": "canceled"}
                
                # Run before-step hooks
                await self._run_hooks(self.before_step_hooks, context, step)
                
                try:
                    logger.info(f"Executing step {i+1}/{len(self.steps)}: {step.id}")
                    
                    # Execute the step
                    step_result = await step.execute(context)
                    await context.add_result(step.id, step_result)
                    result = step_result
                    
                    # Run after-step hooks
                    await self._run_hooks(self.after_step_hooks, context, step, step_result)
                    
                    # Check if we should pause after this step
                    if self.pause_after_step == step.id:
                        await self.pause_after()
                        self.pause_after_step = None
                    
                except Exception as e:
                    logger.error(f"Error executing step {step.id}: {e}")
                    await context.add_error(step.id, e)
                    
                    # Run error hooks
                    await self._run_hooks(self.error_hooks, context, step, e)
                    
                    # Check if we should continue or fail
                    if not getattr(step, 'continue_on_error', False):
                        self.state = FlowState.FAILED
                        self.execution_info.error = str(e)
                        raise
            
            # Flow completed successfully
            self.state = FlowState.COMPLETED
            self.execution_info.end_time = time.time()
            
            # Create final checkpoint
            if self.checkpoint_store:
                final_metadata = CheckpointMetadata(
                    trigger="completion",
                    tags=["final", "completed"]
                )
                final_checkpoint = await context.checkpoint(final_metadata)
                self.execution_info.checkpoint_id = final_checkpoint
            
            logger.info(f"Flow {self.flow_id} completed successfully")
            return result
            
        except Exception as e:
            self.state = FlowState.FAILED
            self.execution_info.end_time = time.time()
            self.execution_info.error = str(e)
            
            logger.error(f"Flow {self.flow_id} failed: {e}")
            raise
    
    async def _check_pause_conditions(self, context: PersistentWorkflowContext) -> None:
        """Check if any pause conditions are met"""
        for condition in self.pause_conditions:
            try:
                if await self._call_hook(condition, context):
                    await self.pause_after()
                    break
            except Exception as e:
                logger.error(f"Error in pause condition: {e}")
    
    async def _handle_pause(
        self, 
        context: PersistentWorkflowContext, 
        current_step
    ) -> None:
        """Handle pause state - create checkpoint and wait for resume"""
        # Create pause checkpoint
        if self.checkpoint_store:
            pause_metadata = CheckpointMetadata(
                step_id=current_step.id,
                step_index=self.current_step_index,
                total_steps=len(self.steps),
                trigger="pause",
                tags=["pause", "resumable"]
            )
            checkpoint_id = await context.checkpoint(pause_metadata)
            self.execution_info.checkpoint_id = checkpoint_id
            
            logger.info(f"Created pause checkpoint {checkpoint_id} at step {current_step.id}")
        
        # Wait for resume signal
        logger.info(f"Flow {self.flow_id} waiting for resume signal...")
        await self.resume_event.wait()
    
    async def _run_hooks(self, hooks: List[Callable], *args, **kwargs) -> None:
        """Run a list of hooks with error handling"""
        for hook in hooks:
            try:
                await self._call_hook(hook, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in hook {hook.__name__}: {e}")
    
    async def _call_hook(self, hook: Callable, *args, **kwargs) -> Any:
        """Call a hook function, handling both sync and async"""
        if asyncio.iscoroutinefunction(hook):
            return await hook(*args, **kwargs)
        else:
            return hook(*args, **kwargs)
    
    def get_execution_info(self) -> FlowExecutionInfo:
        """Get current execution information"""
        return self.execution_info
    
    async def list_checkpoints(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List available checkpoints for this flow"""
        if not self.checkpoint_store:
            return []
        
        return await self.checkpoint_store.list_checkpoints(self.flow_id, limit)
    
    @classmethod
    async def from_checkpoint(
        cls,
        checkpoint_id: str,
        checkpoint_store: CheckpointStore,
        agent_network: 'AgentNetwork',
        **kwargs
    ) -> 'PausableFlow':
        """
        Create a flow instance from a checkpoint.
        
        This allows resuming a paused flow from any checkpoint.
        """
        # Load checkpoint to get flow configuration
        checkpoint_data = await checkpoint_store.load_checkpoint(checkpoint_id)
        
        # Create flow instance
        flow = cls(
            agent_network=agent_network,
            checkpoint_store=checkpoint_store,
            flow_id=checkpoint_data["state"]["workflow_id"],
            **kwargs
        )
        
        # TODO: Restore flow steps and configuration from checkpoint
        # This would require serializing the flow definition in checkpoints
        
        return flow

# Enhanced workflow step with pause support
class PausableStep:
    """Base class for steps that support pausing"""
    
    def __init__(self, step_id: str, **kwargs):
        self.id = step_id
        self.continue_on_error = kwargs.get('continue_on_error', False)
        self.pause_before = kwargs.get('pause_before', False)
        self.pause_after = kwargs.get('pause_after', False)
    
    async def execute(self, context: PersistentWorkflowContext) -> Any:
        """Execute step with pause support"""
        if self.pause_before:
            # Pause before execution
            context.flow.pause_after()
        
        result = await self.do_execute(context)
        
        if self.pause_after:
            # Pause after execution
            context.flow.pause_after()
        
        return result
    
    async def do_execute(self, context: PersistentWorkflowContext) -> Any:
        """Override this method in subclasses"""
        raise NotImplementedError
```

---

## Phase 3: Google A2A v0.3 Protocol Compliance (Week 4)

### Overview
Implement the latest Google A2A v0.3 features including gRPC support, dynamic UX negotiation, QuerySkill method, and enhanced agent cards.

### 3.1 gRPC Transport Implementation

**File**: `python_a2a/transport/grpc_transport.py`

```python
"""
gRPC transport implementation for Google A2A v0.3 protocol.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, AsyncIterator
import grpc
from google.protobuf.json_format import MessageToDict, ParseDict

logger = logging.getLogger(__name__)

# Protocol Buffer definitions would go here
# For now, we'll define the interface and use JSON over gRPC

class A2AGRPCTransport:
    """
    High-performance gRPC transport for A2A protocol v0.3.
    
    Provides:
    - Bidirectional streaming
    - Connection pooling
    - Automatic retry with exponential backoff
    - Load balancing support
    """
    
    def __init__(
        self,
        server_address: str,
        credentials: Optional[grpc.ChannelCredentials] = None,
        options: Optional[List] = None
    ):
        self.server_address = server_address
        self.credentials = credentials
        self.options = options or [
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
        ]
        
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub = None
    
    async def connect(self) -> None:
        """Establish gRPC connection"""
        try:
            if self.credentials:
                self.channel = grpc.aio.secure_channel(
                    self.server_address,
                    self.credentials,
                    options=self.options
                )
            else:
                self.channel = grpc.aio.insecure_channel(
                    self.server_address,
                    options=self.options
                )
            
            # Wait for channel to be ready
            await self.channel.channel_ready()
            
            # Create service stub (would be generated from .proto files)
            # self.stub = A2AServiceStub(self.channel)
            
            logger.info(f"Connected to A2A gRPC server at {self.server_address}")
            
        except Exception as e:
            logger.error(f"Failed to connect to gRPC server: {e}")
            raise
    
    async def send_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send task via gRPC.
        
        Args:
            task: Task dictionary
            
        Returns:
            Task response
        """
        if not self.channel:
            await self.connect()
        
        try:
            # Convert dict to protobuf message
            # request = ParseDict(task, TaskRequest())
            # response = await self.stub.ProcessTask(request)
            # return MessageToDict(response)
            
            # Placeholder implementation using JSON over gRPC
            # In real implementation, would use proper protobuf messages
            pass
            
        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC error: {e.code()}: {e.details()}")
            raise
        except Exception as e:
            logger.error(f"Error sending task via gRPC: {e}")
            raise
    
    async def stream_tasks(
        self, 
        tasks: AsyncIterator[Dict[str, Any]]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream tasks bidirectionally.
        
        Args:
            tasks: Async iterator of tasks to send
            
        Yields:
            Task responses
        """
        if not self.channel:
            await self.connect()
        
        try:
            # Bidirectional streaming implementation
            # async with self.stub.StreamTasks() as stream:
            #     async for task in tasks:
            #         request = ParseDict(task, TaskRequest())
            #         await stream.write(request)
            #         
            #         response = await stream.read()
            #         if response:
            #             yield MessageToDict(response)
            
            # Placeholder implementation
            async for task in tasks:
                # Process task and yield response
                response = await self.send_task(task)
                yield response
                
        except Exception as e:
            logger.error(f"Error in streaming tasks: {e}")
            raise
    
    async def close(self) -> None:
        """Close gRPC connection"""
        if self.channel:
            await self.channel.close()
            self.channel = None
            logger.info("Closed gRPC connection")

class A2AGRPCServer:
    """
    gRPC server implementation for A2A protocol.
    """
    
    def __init__(self, port: int = 50051):
        self.port = port
        self.server: Optional[grpc.aio.Server] = None
        self.agent_handler = None
    
    def set_agent_handler(self, handler) -> None:
        """Set the agent handler for processing requests"""
        self.agent_handler = handler
    
    async def start(self) -> None:
        """Start the gRPC server"""
        self.server = grpc.aio.server()
        
        # Add service to server
        # a2a_pb2_grpc.add_A2AServiceServicer_to_server(
        #     A2AServiceServicer(self.agent_handler), self.server
        # )
        
        listen_addr = f'[::]:{self.port}'
        self.server.add_insecure_port(listen_addr)
        
        await self.server.start()
        logger.info(f"A2A gRPC server started on {listen_addr}")
    
    async def stop(self) -> None:
        """Stop the gRPC server"""
        if self.server:
            await self.server.stop(grace=5)
            self.server = None
            logger.info("A2A gRPC server stopped")
    
    async def wait_for_termination(self) -> None:
        """Wait for server termination"""
        if self.server:
            await self.server.wait_for_termination()

# gRPC service implementation
class A2AServiceServicer:
    """gRPC service implementation"""
    
    def __init__(self, agent_handler):
        self.agent_handler = agent_handler
    
    # async def ProcessTask(self, request, context):
    #     """Process a single task"""
    #     try:
    #         task_dict = MessageToDict(request)
    #         result = await self.agent_handler.handle_task(task_dict)
    #         return ParseDict(result, TaskResponse())
    #     except Exception as e:
    #         context.set_details(str(e))
    #         context.set_code(grpc.StatusCode.INTERNAL)
    #         raise
    # 
    # async def StreamTasks(self, request_iterator, context):
    #     """Handle bidirectional task streaming"""
    #     async for request in request_iterator:
    #         try:
    #             task_dict = MessageToDict(request)
    #             result = await self.agent_handler.handle_task(task_dict)
    #             yield ParseDict(result, TaskResponse())
    #         except Exception as e:
    #             logger.error(f"Error processing streamed task: {e}")
    #             # Could send error response or handle gracefully
```

### 3.2 Dynamic UX Negotiation

**File**: `python_a2a/protocol/ux_negotiation.py`

```python
"""
Dynamic UX negotiation for A2A v0.3 protocol.

Supports dynamic switching between modalities during conversation:
- Text to audio
- Text to video  
- Audio to text
- Mixed media conversations
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

class MediaModality(Enum):
    """Supported media modalities"""
    TEXT = "text"
    AUDIO = "audio" 
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    STRUCTURED_DATA = "structured_data"

@dataclass
class UXCapabilities:
    """UX capabilities of an agent"""
    supported_modalities: List[MediaModality] = field(default_factory=list)
    input_formats: Dict[MediaModality, List[str]] = field(default_factory=dict)
    output_formats: Dict[MediaModality, List[str]] = field(default_factory=dict)
    max_content_size: Dict[MediaModality, int] = field(default_factory=dict)
    streaming_support: Dict[MediaModality, bool] = field(default_factory=dict)
    
    def supports_modality(self, modality: MediaModality) -> bool:
        """Check if modality is supported"""
        return modality in self.supported_modalities
    
    def can_switch_to(self, modality: MediaModality, format: str = None) -> bool:
        """Check if can switch to specific modality and format"""
        if not self.supports_modality(modality):
            return False
        
        if format:
            supported_formats = self.input_formats.get(modality, [])
            return format in supported_formats
        
        return True

@dataclass 
class UXNegotiationRequest:
    """Request for UX modality negotiation"""
    requested_modality: MediaModality
    requested_format: Optional[str] = None
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class UXNegotiationResponse:
    """Response to UX negotiation request"""
    accepted: bool
    final_modality: MediaModality
    final_format: Optional[str] = None
    reason: Optional[str] = None
    alternative_options: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DynamicUXNegotiator:
    """
    Handles dynamic UX modality negotiation during conversations.
    
    Features:
    - Real-time modality switching
    - Capability matching
    - Fallback options
    - Custom negotiation logic
    """
    
    def __init__(self, agent_capabilities: UXCapabilities):
        self.capabilities = agent_capabilities
        self.current_modality = MediaModality.TEXT
        self.current_format: Optional[str] = None
        
        # Negotiation handlers
        self.negotiation_handlers: Dict[MediaModality, Callable] = {}
        self.fallback_handlers: Dict[MediaModality, Callable] = {}
        
        # History
        self.negotiation_history: List[Dict[str, Any]] = []
        
        # Default negotiation policies
        self.auto_accept_compatible = True
        self.allow_degraded_quality = True
        self.prefer_native_formats = True
    
    def register_negotiation_handler(
        self, 
        modality: MediaModality, 
        handler: Callable[[UXNegotiationRequest], UXNegotiationResponse]
    ) -> None:
        """Register custom negotiation handler for a modality"""
        self.negotiation_handlers[modality] = handler
    
    def register_fallback_handler(
        self,
        modality: MediaModality,
        handler: Callable[[UXNegotiationRequest], List[Dict[str, Any]]]
    ) -> None:
        """Register fallback handler for unsupported modalities"""
        self.fallback_handlers[modality] = handler
    
    async def negotiate_modality_switch(
        self,
        request: UXNegotiationRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> UXNegotiationResponse:
        """
        Negotiate switching to a different UX modality.
        
        Args:
            request: Negotiation request
            context: Optional conversation context
            
        Returns:
            Negotiation response with decision
        """
        logger.info(f"Negotiating modality switch to {request.requested_modality.value}")
        
        # Check if we have a custom handler
        if request.requested_modality in self.negotiation_handlers:
            handler = self.negotiation_handlers[request.requested_modality]
            response = await self._call_handler(handler, request, context)
        else:
            # Use default negotiation logic
            response = await self._default_negotiation_logic(request, context)
        
        # Record negotiation
        self.negotiation_history.append({
            "request": request,
            "response": response,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update current modality if accepted
        if response.accepted:
            self.current_modality = response.final_modality
            self.current_format = response.final_format
            logger.info(f"Switched to modality {self.current_modality.value}")
        
        return response
    
    async def _default_negotiation_logic(
        self,
        request: UXNegotiationRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> UXNegotiationResponse:
        """Default negotiation logic"""
        
        # Check if modality is supported
        if not self.capabilities.supports_modality(request.requested_modality):
            # Try to find fallbacks
            alternatives = await self._find_alternatives(request)
            
            return UXNegotiationResponse(
                accepted=False,
                final_modality=self.current_modality,
                reason=f"Modality {request.requested_modality.value} not supported",
                alternative_options=alternatives
            )
        
        # Check format compatibility
        requested_format = request.requested_format
        if requested_format:
            supported_formats = self.capabilities.input_formats.get(
                request.requested_modality, []
            )
            
            if requested_format not in supported_formats:
                # Try to find compatible format
                compatible_format = self._find_compatible_format(
                    request.requested_modality, requested_format
                )
                
                if not compatible_format:
                    return UXNegotiationResponse(
                        accepted=False,
                        final_modality=self.current_modality,
                        reason=f"Format {requested_format} not supported for {request.requested_modality.value}"
                    )
                
                requested_format = compatible_format
        
        # Accept the switch
        return UXNegotiationResponse(
            accepted=True,
            final_modality=request.requested_modality,
            final_format=requested_format,
            reason="Modality switch accepted"
        )
    
    async def _find_alternatives(
        self,
        request: UXNegotiationRequest
    ) -> List[Dict[str, Any]]:
        """Find alternative modalities for unsupported requests"""
        alternatives = []
        
        # Check if we have a fallback handler
        if request.requested_modality in self.fallback_handlers:
            handler = self.fallback_handlers[request.requested_modality]
            alternatives.extend(await self._call_handler(handler, request))
        
        # Add general alternatives based on supported modalities
        for modality in self.capabilities.supported_modalities:
            if modality != request.requested_modality:
                formats = self.capabilities.input_formats.get(modality, [])
                
                alternatives.append({
                    "modality": modality.value,
                    "formats": formats,
                    "reason": f"Alternative to {request.requested_modality.value}"
                })
        
        return alternatives
    
    def _find_compatible_format(
        self,
        modality: MediaModality,
        requested_format: str
    ) -> Optional[str]:
        """Find compatible format for a modality"""
        supported_formats = self.capabilities.input_formats.get(modality, [])
        
        # Direct match
        if requested_format in supported_formats:
            return requested_format
        
        # Try format conversion mappings
        format_mappings = {
            # Audio format mappings
            "mp3": ["audio/mpeg", "audio/mp3"],
            "wav": ["audio/wav", "audio/wave"],
            "m4a": ["audio/m4a", "audio/mp4"],
            
            # Video format mappings  
            "mp4": ["video/mp4", "video/mpeg"],
            "webm": ["video/webm"],
            "avi": ["video/avi", "video/x-msvideo"],
            
            # Image format mappings
            "jpg": ["image/jpeg", "image/jpg"],
            "png": ["image/png"],
            "gif": ["image/gif"],
            "webp": ["image/webp"]
        }
        
        # Check if any supported format can handle the requested format
        for supported_format in supported_formats:
            equivalent_formats = format_mappings.get(supported_format, [])
            if requested_format in equivalent_formats:
                return supported_format
        
        # No compatible format found
        return None
    
    async def _call_handler(self, handler: Callable, *args, **kwargs) -> Any:
        """Call handler function, handling both sync and async"""
        if asyncio.iscoroutinefunction(handler):
            return await handler(*args, **kwargs)
        else:
            return handler(*args, **kwargs)
    
    def get_current_modality(self) -> MediaModality:
        """Get current active modality"""
        return self.current_modality
    
    def get_negotiation_history(self) -> List[Dict[str, Any]]:
        """Get negotiation history"""
        return self.negotiation_history.copy()
    
    def set_negotiation_policy(self, **policies) -> None:
        """Update negotiation policies"""
        if "auto_accept_compatible" in policies:
            self.auto_accept_compatible = policies["auto_accept_compatible"]
        if "allow_degraded_quality" in policies:
            self.allow_degraded_quality = policies["allow_degraded_quality"]
        if "prefer_native_formats" in policies:
            self.prefer_native_formats = policies["prefer_native_formats"]

# Integration with A2A server
class UXNegotiationMixin:
    """Mixin to add UX negotiation to A2A servers"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ux_negotiator: Optional[DynamicUXNegotiator] = None
    
    def setup_ux_negotiation(self, capabilities: UXCapabilities) -> None:
        """Setup UX negotiation with specified capabilities"""
        self.ux_negotiator = DynamicUXNegotiator(capabilities)
        
        # Add UX capabilities to agent card
        if hasattr(self, 'agent_card'):
            if not hasattr(self.agent_card, 'ux_capabilities'):
                self.agent_card.ux_capabilities = {}
            
            self.agent_card.ux_capabilities.update({
                "dynamic_ux_negotiation": True,
                "supported_modalities": [m.value for m in capabilities.supported_modalities],
                "modality_switching": True
            })
    
    async def handle_ux_negotiation(
        self,
        request: UXNegotiationRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> UXNegotiationResponse:
        """Handle UX negotiation request"""
        if not self.ux_negotiator:
            return UXNegotiationResponse(
                accepted=False,
                final_modality=MediaModality.TEXT,
                reason="UX negotiation not supported"
            )
        
        return await self.ux_negotiator.negotiate_modality_switch(request, context)
```

### 3.3 QuerySkill Dynamic Discovery

**File**: `python_a2a/protocol/skill_discovery.py`

```python
"""
Dynamic skill discovery and querying for A2A v0.3.

Implements the QuerySkill() method for runtime skill discovery.
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class SkillType(Enum):
    """Types of skills"""
    COMPUTATIONAL = "computational"
    CREATIVE = "creative" 
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"
    TOOL_USAGE = "tool_usage"
    DOMAIN_SPECIFIC = "domain_specific"

@dataclass
class SkillParameter:
    """Skill parameter definition"""
    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = True
    default: Optional[Any] = None
    constraints: Optional[Dict[str, Any]] = None

@dataclass  
class AgentSkill:
    """Definition of an agent skill"""
    name: str
    description: str
    skill_type: SkillType
    agent_id: str
    confidence: float = 1.0
    parameters: List[SkillParameter] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)

@dataclass
class SkillQuery:
    """Query for finding skills"""
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    skill_type: Optional[SkillType] = None
    required_parameters: List[str] = field(default_factory=list)
    min_confidence: float = 0.5
    max_results: int = 10
    tags: List[str] = field(default_factory=list)

@dataclass
class SkillQueryResult:
    """Result of skill query"""
    skills: List[AgentSkill] = field(default_factory=list)
    total_found: int = 0
    query_time: float = 0.0
    agents_queried: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

class DynamicSkillDiscovery:
    """
    Dynamic skill discovery system for A2A agent networks.
    
    Features:
    - Runtime skill querying
    - Intelligent skill matching
    - Skill capability caching
    - Distributed skill registry
    """
    
    def __init__(self, agent_network: 'AgentNetwork'):
        self.agent_network = agent_network
        self.skill_cache: Dict[str, Dict] = {}
        self.cache_ttl = 300  # 5 minutes
        self.skill_matchers: List[Callable] = []
        
        # Add default skill matcher
        self.skill_matchers.append(self._semantic_skill_matcher)
    
    def add_skill_matcher(self, matcher: Callable[[SkillQuery, AgentSkill], float]) -> None:
        """
        Add custom skill matcher function.
        
        Args:
            matcher: Function that takes (query, skill) and returns confidence score
        """
        self.skill_matchers.append(matcher)
    
    async def query_skill(
        self,
        query: SkillQuery,
        use_cache: bool = True
    ) -> SkillQueryResult:
        """
        Query for agents that have specific skills.
        
        Args:
            query: Skill query parameters
            use_cache: Whether to use cached skill information
            
        Returns:
            Query results with matching skills
        """
        start_time = time.time()
        
        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(query)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.debug(f"Returning cached skill query result for: {query.description}")
                return cached_result
        
        discovered_skills = []
        agents_queried = 0
        
        # Query all agents in network
        query_tasks = []
        for agent_name, agent_client in self.agent_network.agents.items():
            task = self._query_agent_skills(agent_name, agent_client, query)
            query_tasks.append(task)
        
        # Execute queries concurrently
        results = await asyncio.gather(*query_tasks, return_exceptions=True)
        
        # Process results
        for agent_name, result in zip(self.agent_network.agents.keys(), results):
            if isinstance(result, Exception):
                logger.debug(f"Error querying skills from {agent_name}: {result}")
                continue
            
            agents_queried += 1
            if result:
                discovered_skills.extend(result)
        
        # Sort by confidence and apply limits
        discovered_skills.sort(key=lambda s: s.confidence, reverse=True)
        if query.max_results > 0:
            discovered_skills = discovered_skills[:query.max_results]
        
        # Create result
        query_time = time.time() - start_time
        result = SkillQueryResult(
            skills=discovered_skills,
            total_found=len(discovered_skills),
            query_time=query_time,
            agents_queried=agents_queried,
            metadata={
                "cache_used": False,
                "query_hash": self._generate_cache_key(query)
            }
        )
        
        # Cache result if enabled
        if use_cache:
            self._cache_result(self._generate_cache_key(query), result)
        
        logger.info(f"Found {len(discovered_skills)} skills from {agents_queried} agents in {query_time:.2f}s")
        return result
    
    async def _query_agent_skills(
        self,
        agent_name: str,
        agent_client,
        query: SkillQuery
    ) -> List[AgentSkill]:
        """Query skills from a specific agent"""
        try:
            # Check if agent supports QuerySkill method
            if hasattr(agent_client, 'query_skill'):
                # Call the new QuerySkill method
                response = await agent_client.query_skill(
                    query.description, 
                    query.context
                )
                
                # Parse response
                if isinstance(response, dict):
                    skills = response.get("skills", [])
                    return [self._parse_skill_response(s, agent_name) for s in skills]
                else:
                    return []
            else:
                # Fallback: try to get agent capabilities and match against query
                return await self._fallback_skill_query(agent_name, agent_client, query)
                
        except Exception as e:
            logger.debug(f"Error querying skills from {agent_name}: {e}")
            return []
    
    async def _fallback_skill_query(
        self,
        agent_name: str,
        agent_client,
        query: SkillQuery  
    ) -> List[AgentSkill]:
        """Fallback skill querying for agents without QuerySkill support"""
        try:
            # Try to get agent card or capabilities
            agent_info = None
            
            if hasattr(agent_client, 'get_agent_card'):
                agent_info = await agent_client.get_agent_card()
            elif hasattr(agent_client, 'get_capabilities'):
                agent_info = await agent_client.get_capabilities()
            
            if not agent_info:
                return []
            
            # Extract skills from agent info
            skills = []
            
            # Check agent description for skill keywords
            description = agent_info.get("description", "")
            if self._matches_description(query.description, description):
                skill = AgentSkill(
                    name=f"{agent_name}_general",
                    description=description,
                    skill_type=SkillType.CONVERSATIONAL,
                    agent_id=agent_name,
                    confidence=0.6,  # Lower confidence for fallback
                    metadata={"discovered_via": "fallback"}
                )
                skills.append(skill)
            
            # Check explicit skills if available
            explicit_skills = agent_info.get("skills", [])
            for skill_info in explicit_skills:
                if isinstance(skill_info, dict):
                    skill = AgentSkill(
                        name=skill_info.get("name", "unknown"),
                        description=skill_info.get("description", ""),
                        skill_type=SkillType(skill_info.get("type", "conversational")),
                        agent_id=agent_name,
                        confidence=skill_info.get("confidence", 0.8),
                        metadata={"discovered_via": "fallback"}
                    )
                    
                    # Apply skill matching
                    match_score = self._calculate_skill_match(query, skill)
                    if match_score >= query.min_confidence:
                        skill.confidence = match_score
                        skills.append(skill)
            
            return skills
            
        except Exception as e:
            logger.debug(f"Error in fallback skill query for {agent_name}: {e}")
            return []
    
    def _parse_skill_response(self, skill_data: Dict[str, Any], agent_name: str) -> AgentSkill:
        """Parse skill response from agent"""
        return AgentSkill(
            name=skill_data.get("name", "unknown"),
            description=skill_data.get("description", ""),
            skill_type=SkillType(skill_data.get("type", "conversational")),
            agent_id=agent_name,
            confidence=skill_data.get("confidence", 1.0),
            parameters=[
                SkillParameter(**param) if isinstance(param, dict) else param
                for param in skill_data.get("parameters", [])
            ],
            examples=skill_data.get("examples", []),
            metadata=skill_data.get("metadata", {}),
            version=skill_data.get("version", "1.0.0"),
            tags=skill_data.get("tags", [])
        )
    
    def _calculate_skill_match(self, query: SkillQuery, skill: AgentSkill) -> float:
        """Calculate match score between query and skill"""
        scores = []
        
        # Apply all skill matchers
        for matcher in self.skill_matchers:
            try:
                score = matcher(query, skill)
                if score is not None:
                    scores.append(score)
            except Exception as e:
                logger.debug(f"Error in skill matcher: {e}")
        
        # Return weighted average (can be customized)
        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.0
    
    def _semantic_skill_matcher(self, query: SkillQuery, skill: AgentSkill) -> float:
        """Default semantic skill matcher"""
        # Simple keyword-based matching (can be enhanced with embeddings)
        query_words = set(query.description.lower().split())
        skill_words = set((skill.name + " " + skill.description).lower().split())
        
        # Calculate word overlap
        overlap = len(query_words & skill_words)
        total_unique = len(query_words | skill_words)
        
        if total_unique == 0:
            return 0.0
        
        base_score = overlap / total_unique
        
        # Boost score based on skill type match
        if query.skill_type and query.skill_type == skill.skill_type:
            base_score *= 1.5
        
        # Boost score based on tag matches
        if query.tags and skill.tags:
            tag_overlap = len(set(query.tags) & set(skill.tags))
            if tag_overlap > 0:
                base_score *= (1 + tag_overlap * 0.2)
        
        return min(base_score, 1.0)
    
    def _matches_description(self, query_desc: str, agent_desc: str) -> bool:
        """Simple description matching"""
        query_words = set(query_desc.lower().split())
        agent_words = set(agent_desc.lower().split())
        
        # Check for meaningful overlap
        overlap = len(query_words & agent_words)
        return overlap >= min(2, len(query_words) * 0.3)
    
    def _generate_cache_key(self, query: SkillQuery) -> str:
        """Generate cache key for query"""
        import hashlib
        
        key_data = f"{query.description}_{query.skill_type}_{query.min_confidence}_{sorted(query.tags)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[SkillQueryResult]:
        """Get cached result if valid"""
        if cache_key in self.skill_cache:
            cached_entry = self.skill_cache[cache_key]
            if time.time() - cached_entry["timestamp"] < self.cache_ttl:
                cached_entry["result"].metadata["cache_used"] = True
                return cached_entry["result"]
        return None
    
    def _cache_result(self, cache_key: str, result: SkillQueryResult) -> None:
        """Cache query result"""
        self.skill_cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
    
    def clear_cache(self) -> None:
        """Clear skill cache"""
        self.skill_cache.clear()
        logger.info("Skill discovery cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cached_queries": len(self.skill_cache),
            "cache_ttl": self.cache_ttl,
            "oldest_entry": min(
                (entry["timestamp"] for entry in self.skill_cache.values()),
                default=time.time()
            ),
            "newest_entry": max(
                (entry["timestamp"] for entry in self.skill_cache.values()),
                default=time.time()
            )
        }

# Integration with A2A servers
class SkillDiscoveryMixin:
    """Mixin to add skill discovery to A2A servers"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registered_skills: List[AgentSkill] = []
        self.skill_handlers: Dict[str, Callable] = {}
    
    def register_skill(
        self,
        skill: AgentSkill,
        handler: Optional[Callable] = None
    ) -> None:
        """Register a skill with this agent"""
        skill.agent_id = getattr(self, 'agent_name', 'unknown')
        self.registered_skills.append(skill)
        
        if handler:
            self.skill_handlers[skill.name] = handler
        
        logger.info(f"Registered skill: {skill.name}")
    
    async def query_skill(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Implementation of QuerySkill method for A2A v0.3.
        
        This method allows other agents to query this agent's skills.
        """
        context = context or {}
        
        # Create skill query
        query = SkillQuery(
            description=description,
            context=context,
            min_confidence=context.get("min_confidence", 0.5),
            max_results=context.get("max_results", 10)
        )
        
        # Match against registered skills
        matching_skills = []
        
        for skill in self.registered_skills:
            # Calculate match score
            match_score = self._calculate_local_skill_match(query, skill)
            
            if match_score >= query.min_confidence:
                skill_copy = skill
                skill_copy.confidence = match_score
                matching_skills.append(skill_copy)
        
        # Sort by confidence
        matching_skills.sort(key=lambda s: s.confidence, reverse=True)
        
        # Apply result limit
        if query.max_results > 0:
            matching_skills = matching_skills[:query.max_results]
        
        # Format response
        return {
            "skills": [
                {
                    "name": skill.name,
                    "description": skill.description,
                    "type": skill.skill_type.value,
                    "confidence": skill.confidence,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.type,
                            "description": p.description,
                            "required": p.required,
                            "default": p.default
                        } for p in skill.parameters
                    ],
                    "examples": skill.examples,
                    "metadata": skill.metadata,
                    "version": skill.version,
                    "tags": skill.tags
                }
                for skill in matching_skills
            ],
            "total_found": len(matching_skills),
            "agent_id": getattr(self, 'agent_name', 'unknown')
        }
    
    def _calculate_local_skill_match(self, query: SkillQuery, skill: AgentSkill) -> float:
        """Calculate match score for local skill"""
        # Simple keyword matching (can be enhanced)
        query_words = set(query.description.lower().split())
        skill_words = set((skill.name + " " + skill.description).lower().split())
        
        overlap = len(query_words & skill_words)
        total_unique = len(query_words | skill_words)
        
        if total_unique == 0:
            return 0.0
        
        return overlap / total_unique
```

---

## Phase 4: Testing & Integration (Week 5)

### 4.1 Comprehensive Test Suite

**File**: `tests/test_mcp_compliance.py`

```python
"""
Test suite for MCP protocol compliance.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch

from python_a2a.mcp.spec_compliant_client import SpecCompliantMCPClient
from python_a2a.langchain.mcp_fixed import to_langchain_tool_fixed

class TestMCPCompliance:
    """Test MCP protocol compliance"""
    
    @pytest.fixture
    async def mock_mcp_server(self):
        """Mock MCP server for testing"""
        mock_server = AsyncMock()
        
        # Mock initialize response
        mock_server.initialize.return_value = {
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"listChanged": True}
                },
                "serverInfo": {
                    "name": "test-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
        
        # Mock tools list
        mock_server.list_tools.return_value = [
            {
                "name": "calculator",
                "description": "Perform calculations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression"
                        }
                    }
                }
            }
        ]
        
        return mock_server
    
    @pytest.mark.asyncio
    async def test_initialization_handshake(self):
        """Test proper MCP initialization"""
        client = SpecCompliantMCPClient()
        
        with patch('httpx.AsyncClient') as mock_http:
            # Mock initialize response
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {"listChanged": True}
                    },
                    "serverInfo": {
                        "name": "test-server",
                        "version": "1.0.0"
                    }
                }
            }
            
            mock_http_client = AsyncMock()
            mock_http_client.post.return_value = mock_response
            mock_http.return_value = mock_http_client
            
            # Test initialization
            result = await client.initialize("http://test-server")
            
            # Verify initialization request
            assert mock_http_client.post.called
            call_args = mock_http_client.post.call_args
            request_data = call_args[1]["json"]
            
            assert request_data["jsonrpc"] == "2.0"
            assert request_data["method"] == "initialize"
            assert "protocolVersion" in request_data["params"]
            assert "capabilities" in request_data["params"]
            assert "clientInfo" in request_data["params"]
            
            # Verify initialized notification was sent
            assert mock_http_client.post.call_count == 2  # initialize + notification
    
    @pytest.mark.asyncio
    async def test_tool_listing(self):
        """Test proper tool listing via JSON-RPC"""
        client = SpecCompliantMCPClient()
        client.initialized = True
        
        with patch('httpx.AsyncClient') as mock_http:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "jsonrpc": "2.0",
                "id": 2,
                "result": {
                    "tools": [
                        {
                            "name": "calculator",
                            "description": "Mathematical calculator"
                        }
                    ]
                }
            }
            
            mock_http_client = AsyncMock()
            mock_http_client.post.return_value = mock_response
            mock_http.return_value = mock_http_client
            
            # Test tool listing
            tools = await client.list_tools("http://test-server")
            
            # Verify request
            call_args = mock_http_client.post.call_args
            request_data = call_args[1]["json"]
            
            assert request_data["method"] == "tools/list"
            assert len(tools) == 1
            assert tools[0]["name"] == "calculator"
    
    @pytest.mark.asyncio
    async def test_langchain_integration_fixed(self):
        """Test fixed LangChain integration"""
        
        with patch('python_a2a.mcp.spec_compliant_client.SpecCompliantMCPClient') as mock_client_class:
            # Setup mock client
            mock_client = AsyncMock()
            mock_client.list_tools.return_value = [
                {
                    "name": "test_tool",
                    "description": "Test tool",
                    "inputSchema": {"type": "object"}
                }
            ]
            mock_client.call_tool.return_value = {
                "content": [{"type": "text", "text": "Tool result"}]
            }
            mock_client_class.return_value = mock_client
            
            # Test conversion
            tools = to_langchain_tool_fixed("http://test-server")
            
            assert len(tools) == 1
            assert tools[0].name == "test_tool"
            
            # Test tool execution
            result = tools[0].func(input="test")
            assert result == "Tool result"

class TestCheckpointing:
    """Test checkpointing functionality"""
    
    @pytest.fixture
    async def checkpoint_store(self):
        """Mock checkpoint store"""
        from python_a2a.checkpoint.store import CheckpointStore
        
        store = AsyncMock(spec=CheckpointStore)
        store.save_checkpoint.return_value = "checkpoint_123"
        store.load_checkpoint.return_value = {
            "state": {
                "workflow_id": "test_workflow",
                "data": {"key": "value"},
                "results": {},
                "history": [],
                "errors": [],
                "step_count": 0,
                "start_time": 1234567890
            },
            "metadata": {}
        }
        return store
    
    @pytest.mark.asyncio
    async def test_persistent_context_checkpointing(self, checkpoint_store):
        """Test persistent workflow context checkpointing"""
        from python_a2a.checkpoint.context import PersistentWorkflowContext
        
        context = PersistentWorkflowContext(
            initial_data={"test": "data"},
            checkpoint_store=checkpoint_store
        )
        
        # Add some results
        await context.add_result("step1", "result1")
        await context.add_result("step2", "result2")
        
        # Create checkpoint
        checkpoint_id = await context.checkpoint()
        
        assert checkpoint_id == "checkpoint_123"
        assert checkpoint_store.save_checkpoint.called
    
    @pytest.mark.asyncio  
    async def test_context_restoration(self, checkpoint_store):
        """Test workflow context restoration from checkpoint"""
        from python_a2a.checkpoint.context import PersistentWorkflowContext
        
        # Restore from checkpoint
        context = await PersistentWorkflowContext.from_checkpoint(
            "checkpoint_123",
            checkpoint_store
        )
        
        assert context.is_restored
        assert context.restore_checkpoint_id == "checkpoint_123"
        assert context.data["key"] == "value"
    
    @pytest.mark.asyncio
    async def test_pausable_flow(self, checkpoint_store):
        """Test pausable flow execution"""
        from python_a2a.workflow.pausable_flow import PausableFlow
        from python_a2a.client.network import AgentNetwork
        
        # Create mock agent network
        network = AsyncMock(spec=AgentNetwork)
        
        # Create pausable flow
        flow = PausableFlow(
            agent_network=network,
            checkpoint_store=checkpoint_store,
            name="Test Flow"
        )
        
        # Test pause scheduling
        await flow.pause_after("step1")
        assert flow.pause_after_step == "step1"
        
        # Test state management
        assert flow.state.value == "created"
        await flow.resume()
        assert flow.state.value == "running"

class TestSkillDiscovery:
    """Test dynamic skill discovery"""
    
    @pytest.fixture
    def mock_agent_network(self):
        """Mock agent network"""
        network = AsyncMock()
        
        # Mock agents
        agent1 = AsyncMock()
        agent1.query_skill.return_value = {
            "skills": [{
                "name": "math_calculation",
                "description": "Mathematical calculations",
                "type": "computational",
                "confidence": 0.9
            }]
        }
        
        agent2 = AsyncMock()
        agent2.query_skill.return_value = {
            "skills": [{
                "name": "text_analysis",
                "description": "Text analysis and processing",
                "type": "analytical", 
                "confidence": 0.8
            }]
        }
        
        network.agents = {
            "math_agent": agent1,
            "text_agent": agent2
        }
        
        return network
    
    @pytest.mark.asyncio
    async def test_skill_query(self, mock_agent_network):
        """Test skill querying functionality"""
        from python_a2a.protocol.skill_discovery import DynamicSkillDiscovery, SkillQuery
        
        discovery = DynamicSkillDiscovery(mock_agent_network)
        
        query = SkillQuery(
            description="mathematical calculation",
            min_confidence=0.7
        )
        
        result = await discovery.query_skill(query, use_cache=False)
        
        assert result.total_found == 1
        assert result.skills[0].name == "math_calculation"
        assert result.skills[0].confidence >= 0.7

if __name__ == "__main__":
    pytest.main([__file__])
```

### 4.2 Integration Tests

**File**: `tests/integration/test_end_to_end.py`

```python
"""
End-to-end integration tests for the enhanced python-a2a system.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import AsyncMock, patch

from python_a2a import A2AServer
from python_a2a.checkpoint.store import FileCheckpointStore
from python_a2a.workflow.pausable_flow import PausableFlow
from python_a2a.client.network import AgentNetwork

class TestEndToEndIntegration:
    """Complete end-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_workflow_with_checkpointing(self):
        """Test complete workflow with checkpointing"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup checkpoint store
            checkpoint_store = FileCheckpointStore(temp_dir)
            
            # Create mock agent network
            network = AsyncMock(spec=AgentNetwork)
            
            # Create pausable flow
            flow = PausableFlow(
                agent_network=network,
                checkpoint_store=checkpoint_store,
                name="Integration Test Flow"
            )
            
            # Add mock steps
            from python_a2a.workflow.steps import WorkflowStep
            
            class MockStep(WorkflowStep):
                def __init__(self, step_id):
                    super().__init__(step_id)
                
                async def execute(self, context):
                    return f"Result from {self.id}"
            
            flow.steps = [
                MockStep("step1"),
                MockStep("step2"),
                MockStep("step3")
            ]
            
            # Run workflow
            result = await flow.run({"initial": "data"})
            
            # Verify checkpoints were created
            checkpoint_files = os.listdir(os.path.join(temp_dir, flow.flow_id))
            assert len(checkpoint_files) > 0
            
            # Verify flow completed
            assert flow.state.value == "completed"
    
    @pytest.mark.asyncio
    async def test_mcp_integration_workflow(self):
        """Test MCP integration in a workflow"""
        
        # This would test the complete MCP integration
        # including spec-compliant client, LangChain conversion,
        # and usage in workflows
        
        with patch('python_a2a.mcp.spec_compliant_client.SpecCompliantMCPClient') as mock_client_class:
            # Setup mock MCP client
            mock_client = AsyncMock()
            mock_client.list_tools.return_value = [
                {
                    "name": "data_processor",
                    "description": "Process data using MCP tool"
                }
            ]
            mock_client.call_tool.return_value = {
                "content": [{"type": "text", "text": "Processed data"}]
            }
            mock_client_class.return_value = mock_client
            
            # Create workflow that uses MCP tools
            from python_a2a.langchain.mcp_fixed import to_langchain_tool_fixed
            
            # Convert MCP tool to LangChain
            tools = to_langchain_tool_fixed("http://mcp-server")
            
            assert len(tools) == 1
            assert tools[0].name == "data_processor"
            
            # Use tool in workflow
            result = tools[0].func(data="test input")
            assert result == "Processed data"
    
    @pytest.mark.asyncio
    async def test_skill_discovery_integration(self):
        """Test skill discovery in agent network"""
        
        # Create real agent instances with skill discovery
        from python_a2a.protocol.skill_discovery import SkillDiscoveryMixin, AgentSkill, SkillType
        
        class TestAgent(A2AServer, SkillDiscoveryMixin):
            def __init__(self, name):
                super().__init__(name=name)
                
                # Register some skills
                self.register_skill(AgentSkill(
                    name="text_processing",
                    description="Process and analyze text",
                    skill_type=SkillType.ANALYTICAL,
                    agent_id=name
                ))
        
        # Create agents
        agent1 = TestAgent("text_processor")
        agent2 = TestAgent("data_analyzer")
        
        # Test skill querying
        result = await agent1.query_skill("text analysis")
        
        assert "skills" in result
        assert len(result["skills"]) > 0
        assert result["skills"][0]["name"] == "text_processing"
```

---

## Implementation Timeline & Milestones

### Week 1: MCP Protocol Compliance (CRITICAL)
- **Day 1-2**: Implement `SpecCompliantMCPClient`
- **Day 3-4**: Fix LangChain integration with `to_langchain_tool_fixed`
- **Day 5**: Update module imports and backward compatibility
- **Day 6-7**: Testing and bug fixes

**Success Criteria**: All GitHub issues #74, #65 resolved

### Week 2: Checkpoint Storage Architecture  
- **Day 1-2**: Implement `CheckpointStore` interfaces
- **Day 3-4**: Build `RedisCheckpointStore` and `DatabaseCheckpointStore`
- **Day 5**: Create `PersistentWorkflowContext`
- **Day 6-7**: Integration testing

**Success Criteria**: Workflows can be checkpointed and restored

### Week 3: Pausable Flow Engine
- **Day 1-3**: Implement `PausableFlow` class
- **Day 4-5**: Add pause/resume functionality
- **Day 6-7**: Error recovery and distributed coordination

**Success Criteria**: Workflows can pause/resume across restarts

### Week 4: A2A v0.3 Features
- **Day 1-2**: gRPC transport implementation
- **Day 3-4**: Dynamic UX negotiation
- **Day 5**: QuerySkill method and skill discovery
- **Day 6-7**: Integration and testing

**Success Criteria**: Full A2A v0.3 protocol support

### Week 5: Testing & Documentation
- **Day 1-3**: Comprehensive test suite
- **Day 4-5**: Integration testing
- **Day 6-7**: Documentation and examples

**Success Criteria**: 90%+ test coverage, complete documentation

---

## Deployment Strategy

### 1. Backward Compatibility
All changes maintain full backward compatibility:
- Existing imports continue to work
- New features are opt-in
- Migration path is seamless

### 2. Feature Flags
Implementation uses feature flags for gradual rollout:
```python
# Enable new features gradually
ENABLE_SPEC_COMPLIANT_MCP = os.getenv("A2A_ENABLE_SPEC_MCP", "false").lower() == "true"
ENABLE_CHECKPOINTING = os.getenv("A2A_ENABLE_CHECKPOINTING", "false").lower() == "true"
ENABLE_GRPC_TRANSPORT = os.getenv("A2A_ENABLE_GRPC", "false").lower() == "true"
```

### 3. Performance Monitoring
- Checkpoint creation/restoration times
- MCP protocol compatibility metrics
- Workflow execution performance
- Memory usage optimization

### 4. Documentation Updates
- Update README.md with new features
- Add migration guide
- Create performance tuning guide
- Update API documentation

---

## Risk Mitigation

### Technical Risks
1. **MCP Compatibility**: Extensive testing with real MCP servers
2. **Performance Impact**: Benchmarking and optimization
3. **Memory Usage**: Efficient checkpoint serialization
4. **Distributed Coordination**: Robust error handling

### Mitigation Strategies
1. **Incremental Rollout**: Feature flags and gradual deployment
2. **Comprehensive Testing**: Unit, integration, and end-to-end tests
3. **Monitoring**: Real-time performance and error tracking
4. **Rollback Plan**: Quick rollback capability for each phase

---

## Success Metrics

### Technical Metrics
- **Protocol Compliance**: 100% MCP 2025-03-26 compliance
- **Issue Resolution**: Close all critical GitHub issues
- **Performance**: <10% overhead for new features
- **Reliability**: 99.9% workflow completion rate

### Business Metrics  
- **Developer Adoption**: 50% increase in active users
- **Enterprise Features**: Meets all enterprise requirements
- **Community Growth**: 100+ GitHub stars, 20+ contributors
- **Documentation**: Complete API coverage

This implementation strategy provides a comprehensive roadmap for transforming python-a2a into the definitive enterprise-grade A2A protocol implementation with cutting-edge MCP compatibility and advanced state management capabilities.