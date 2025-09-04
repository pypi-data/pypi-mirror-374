"""
Memory Layer Client - Simple Python client for the Memory Layer API.
"""

import requests
from typing import List, Dict, Optional, Any


class MemoryLayerClient:
    """
    A simple client for the Memory Layer API.
    
    This client provides methods to save memories, search for relevant memories,
    and get contextual information from stored memories.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://brain-ai-backend.onrender.com/v1"):
        """
        Initialize the Memory Layer client.
        
        Args:
            api_key: Your Memory Layer API key
            base_url: Base URL for the Memory Layer API (defaults to production)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def save(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Save a memory to the Memory Layer.
        
        Args:
            text: The text content to save as a memory
            metadata: Optional metadata to associate with the memory
            
        Returns:
            Dictionary containing the response from the API
            
        Raises:
            requests.RequestException: If the API request fails
        """
        payload = {
            "content": text,
            "metadata": metadata or {}
        }
        
        response = requests.post(
            f"{self.base_url}/memory",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories similar to the given query.
        
        Args:
            query: The search query
            top_k: Maximum number of results to return (default: 5)
            
        Returns:
            List of dictionaries containing matching memories
            
        Raises:
            requests.RequestException: If the API request fails
        """
        payload = {
            "query": query,
            "limit": top_k
        }
        
        response = requests.post(
            f"{self.base_url}/memory/search",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        
        # Return the results array, or empty list if not found
        return result.get("results", [])
    
    def context(self, query: str, max_memories: int = 5) -> str:
        """
        Get contextual information based on the query.
        
        This method searches for relevant memories and formats them
        as a context string that can be used in prompts or conversations.
        
        Args:
            query: The query to find relevant context for
            max_memories: Maximum number of memories to include in context
            
        Returns:
            Formatted context string
            
        Raises:
            requests.RequestException: If the API request fails
        """
        memories = self.search(query, top_k=max_memories)
        
        if not memories:
            return ""
        
        # Format memories into a context string
        context_parts = []
        for i, memory in enumerate(memories, 1):
            content = memory.get("content", "")
            if content:
                context_parts.append(f"{i}. {content}")
        
        return "\n".join(context_parts)
    
    def list_memories(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all memories for the authenticated user.
        
        Args:
            limit: Maximum number of memories to return (default: 50)
            offset: Number of memories to skip (default: 0)
            
        Returns:
            List of dictionaries containing memories
            
        Raises:
            requests.RequestException: If the API request fails
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        response = requests.get(
            f"{self.base_url}/memory",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a specific memory.
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            requests.RequestException: If the API request fails
        """
        response = requests.delete(
            f"{self.base_url}/memory/{memory_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the Memory Layer API.
        
        Returns:
            Dictionary containing health status information
            
        Raises:
            requests.RequestException: If the API request fails
        """
        # Remove /v1 from base_url for health check
        health_url = self.base_url.replace('/v1', '') + '/health'
        
        response = requests.get(health_url)
        response.raise_for_status()
        return response.json()
