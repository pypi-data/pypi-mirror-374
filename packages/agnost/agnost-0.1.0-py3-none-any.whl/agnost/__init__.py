from .client import AgnostAnalytics
from .types import AgnostConfig
from typing import Any

_client = AgnostAnalytics()

def track(server : Any, org_id: str, config: AgnostConfig = None):
    """ Track your MCP Server """
    if config is None:
        config = AgnostConfig()
    return _client.track_mcp(server, org_id, config)

config = AgnostConfig

__all__ = ["track", "config"]