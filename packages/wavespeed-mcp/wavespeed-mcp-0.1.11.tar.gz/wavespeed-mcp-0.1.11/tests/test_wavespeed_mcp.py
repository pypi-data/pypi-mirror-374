"""Unit tests for WavespeedMCP."""

import os
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from wavespeed_mcp.utils import (
    build_output_path,
    build_output_file,
    validate_loras
)
from wavespeed_mcp.exceptions import WavespeedMcpError


class TestWavespeedUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_build_output_file(self):
        """Test build_output_file function."""
        tool = "test_tool"
        description = "test description"
        output_path = Path("/tmp")
        extension = "png"
        
        filename = build_output_file(tool, description, output_path, extension)
        
        self.assertTrue(filename.startswith(f"{tool}_test_description_"))
        self.assertTrue(filename.endswith(f".{extension}"))
    
    @patch('wavespeed_mcp.utils.is_file_writeable')
    def test_build_output_path_default(self, mock_is_writeable):
        """Test build_output_path with default values."""
        mock_is_writeable.return_value = True
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            path = build_output_path()
            
            self.assertEqual(path, Path.home() / "Desktop")
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    @patch('wavespeed_mcp.utils.is_file_writeable')
    def test_build_output_path_custom(self, mock_is_writeable):
        """Test build_output_path with custom directory."""
        mock_is_writeable.return_value = True
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            path = build_output_path("/custom/path")
            
            self.assertEqual(path, Path("/custom/path"))
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    @patch('wavespeed_mcp.utils.is_file_writeable')
    def test_build_output_path_not_writeable(self, mock_is_writeable):
        """Test build_output_path with non-writeable directory."""
        mock_is_writeable.return_value = False
        
        with self.assertRaises(WavespeedMcpError):
            build_output_path("/non/writeable/path")
    
    def test_validate_loras_valid(self):
        """Test validate_loras with valid loras."""
        loras = [
            {"path": "test/path", "scale": 1.0},
            {"path": "another/path"}
        ]
        
        result = validate_loras(loras)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["path"], "test/path")
        self.assertEqual(result[0]["scale"], 1.0)
        self.assertEqual(result[1]["path"], "another/path")
        self.assertEqual(result[1]["scale"], 1.0)  # Default scale added
    
    def test_validate_loras_invalid(self):
        """Test validate_loras with invalid loras."""
        # Missing path
        with self.assertRaises(WavespeedMcpError):
            validate_loras([{"scale": 1.0}])
        
        # Not a dict
        with self.assertRaises(WavespeedMcpError):
            validate_loras(["not a dict"])
    
    def test_validate_loras_empty(self):
        """Test validate_loras with empty loras."""
        self.assertEqual(validate_loras([]), [])
        self.assertEqual(validate_loras(None), [])


class TestWavespeedClient(unittest.TestCase):
    """Test API client."""
    
    @patch('wavespeed_mcp.client.requests.Session')
    def test_client_initialization(self, mock_session):
        """Test client initialization."""
        from wavespeed_mcp.client import WavespeedAPIClient
        
        api_key = "test_key"
        api_host = "https://test.host"
        
        client = WavespeedAPIClient(api_key, api_host)
        
        self.assertEqual(client.api_key, api_key)
        self.assertEqual(client.api_host, api_host)
        
        # Check headers
        headers = mock_session.return_value.headers.update.call_args[0][0]
        self.assertEqual(headers["Authorization"], f"Bearer {api_key}")
        self.assertEqual(headers["Content-Type"], "application/json")


if __name__ == "__main__":
    unittest.main()
