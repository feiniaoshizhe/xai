"""
Database module - Cosmos DB connection and utilities
"""

from .cosmos import get_cosmos_client, get_database, get_container
from .cosmos_chat_store import CosmosChatMessageStore

__all__ = [
    "get_cosmos_client",
    "get_database",
    "get_container",
    "CosmosChatMessageStore",
]
