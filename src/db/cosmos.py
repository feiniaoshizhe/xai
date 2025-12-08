"""
Cosmos DB Connection Module

Uses Azure Identity for authentication (same as OpenAI client).
"""

import os
from functools import lru_cache
from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy
from azure.identity import (
    ChainedTokenCredential,
    ManagedIdentityCredential,
    AzureCliCredential,
)


def get_credential():
    """Get credential based on environment.

    Uses ChainedTokenCredential:
    - ManagedIdentityCredential for Azure cloud
    - AzureCliCredential for local development
    """
    return ChainedTokenCredential(
        ManagedIdentityCredential(),
        AzureCliCredential(),
    )


@lru_cache()
def get_cosmos_client() -> CosmosClient:
    """Get Cosmos DB client (singleton).

    Requires environment variable:
    - COSMOS_ENDPOINT: Cosmos DB account endpoint URL
    - Optionally COSMOS_KEY: if set, use key auth (recommended in containers without MSI/CLI)
    """
    endpoint = os.getenv("COSMOS_ENDPOINT")
    if not endpoint:
        raise ValueError("COSMOS_ENDPOINT environment variable is required")

    key = os.getenv("COSMOS_KEY")
    if key:
        # Prefer key auth when provided (works in containers without MSI/CLI)
        return CosmosClient(url=endpoint, credential=key)

    # Fallback to AAD credentials (MSI/CLI)
    return CosmosClient(url=endpoint, credential=get_credential())


def get_database(database_name: str = "maf_db") -> DatabaseProxy:
    """Get database proxy.

    Args:
        database_name: Name of the database (default: maf_db)
    """
    client = get_cosmos_client()
    return client.get_database_client(database_name)


def get_container(
    container_name: str = "conversations",
    database_name: str = "maf_db",
) -> ContainerProxy:
    """Get container proxy.

    Args:
        container_name: Name of the container (default: conversations)
        database_name: Name of the database (default: maf_db)
    """
    database = get_database(database_name)
    return database.get_container_client(container_name)
