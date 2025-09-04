#!/usr/bin/env python3
"""
Tests for the Memory Layer Client.

These tests verify the functionality of the MemoryLayerClient class.
"""

import unittest
import os
from unittest.mock import Mock, patch
from memory_layer import MemoryLayerClient


class TestMemoryLayerClient(unittest.TestCase):
    """Test cases for MemoryLayerClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "mlive_test_key_12345"
        self.base_url = "https://test-api.memory-layer.com/v1"
        self.client = MemoryLayerClient(api_key=self.api_key, base_url=self.base_url)
    
    def test_client_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.base_url, self.base_url)
        self.assertIn("Authorization", self.client.headers)
        self.assertEqual(self.client.headers["Authorization"], f"Bearer {self.api_key}")
    
    def test_default_base_url(self):
        """Test client with default base URL."""
        client = MemoryLayerClient(api_key=self.api_key)
        self.assertEqual(client.base_url, "https://brain-ai-backend.onrender.com/v1")
    
    @patch('requests.post')
    def test_save_memory(self, mock_post):
        """Test saving a memory."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "memory": {"id": "mem_123", "content": "Test memory"}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test save
        result = self.client.save("Test memory", {"tag": "test"})
        
        # Verify request
        mock_post.assert_called_once_with(
            f"{self.base_url}/memory",
            headers=self.client.headers,
            json={"content": "Test memory", "metadata": {"tag": "test"}}
        )
        
        # Verify response
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["memory"]["content"], "Test memory")
    
    @patch('requests.post')
    def test_search_memories(self, mock_post):
        """Test searching for memories."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": "mem_1", "content": "First memory", "similarity_score": 0.9},
                {"id": "mem_2", "content": "Second memory", "similarity_score": 0.8}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test search
        results = self.client.search("test query", top_k=2)
        
        # Verify request
        mock_post.assert_called_once_with(
            f"{self.base_url}/memory/search",
            headers=self.client.headers,
            json={"query": "test query", "limit": 2}
        )
        
        # Verify response
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["content"], "First memory")
        self.assertEqual(results[1]["content"], "Second memory")
    
    @patch('requests.post')
    def test_context_method(self, mock_post):
        """Test getting context from memories."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": "mem_1", "content": "First relevant memory"},
                {"id": "mem_2", "content": "Second relevant memory"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test context
        context = self.client.context("test query")
        
        # Verify request
        mock_post.assert_called_once_with(
            f"{self.base_url}/memory/search",
            headers=self.client.headers,
            json={"query": "test query", "limit": 5}
        )
        
        # Verify response
        expected_context = "1. First relevant memory\n2. Second relevant memory"
        self.assertEqual(context, expected_context)
    
    @patch('requests.post')
    def test_context_empty_results(self, mock_post):
        """Test context method with no results."""
        # Mock empty response
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test context
        context = self.client.context("test query")
        
        # Verify empty context
        self.assertEqual(context, "")
    
    @patch('requests.get')
    def test_list_memories(self, mock_get):
        """Test listing memories."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "mem_1", "content": "Memory 1"},
            {"id": "mem_2", "content": "Memory 2"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test list
        memories = self.client.list_memories(limit=10, offset=5)
        
        # Verify request
        mock_get.assert_called_once_with(
            f"{self.base_url}/memory",
            headers=self.client.headers,
            params={"limit": 10, "offset": 5}
        )
        
        # Verify response
        self.assertEqual(len(memories), 2)
        self.assertEqual(memories[0]["content"], "Memory 1")
    
    @patch('requests.delete')
    def test_delete_memory(self, mock_delete):
        """Test deleting a memory."""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response
        
        # Test delete
        result = self.client.delete_memory("mem_123")
        
        # Verify request
        mock_delete.assert_called_once_with(
            f"{self.base_url}/memory/mem_123",
            headers=self.client.headers
        )
        
        # Verify response
        self.assertTrue(result)
    
    @patch('requests.get')
    def test_health_check(self, mock_get):
        """Test health check."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test health check
        health = self.client.health_check()
        
        # Verify request (should remove /v1 from URL)
        expected_url = self.base_url.replace('/v1', '') + '/health'
        mock_get.assert_called_once_with(expected_url)
        
        # Verify response
        self.assertEqual(health["status"], "ok")


if __name__ == "__main__":
    unittest.main()
