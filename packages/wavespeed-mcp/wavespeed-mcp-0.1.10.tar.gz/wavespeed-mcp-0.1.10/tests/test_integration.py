"""Integration tests for WavespeedMCP.

These tests demonstrate how to use the WavespeedMCP service in a real-world scenario.
Note: These tests require a valid WaveSpeed API key to run.
"""

import os
import asyncio
import unittest
import json
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters


class TestWavespeedIntegration(unittest.TestCase):
    """Integration tests for WavespeedMCP."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        load_dotenv()
        cls.api_key = os.getenv("WAVESPEED_API_KEY")
        if not cls.api_key:
            raise unittest.SkipTest("WAVESPEED_API_KEY environment variable not set")

    async def _run_client(self, tool_name, params):
        """Run the client with the specified tool and parameters."""
        server_params = StdioServerParameters(
            command="wavespeed-mcp", args=["--api-key", self.api_key]
        )
        print(f"Running client with parameters: {server_params}")
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as client:
                await client.initialize()

                # Get available tools
                tools_result = await client.list_tools()
                tools = tools_result.tools

                # Verify tool is available
                tool_names = [tool.name for tool in tools]
                self.assertIn(tool_name, tool_names)

                # Call the tool
                result = await client.call_tool(tool_name, params)
                return result

    def test_generate_image(self):
        """Test generating an image."""
        params = {
            "prompt": "A beautiful mountain landscape with a lake",
            "size": "512*512",  # Smaller size for faster testing
            "num_images": 1,
        }

        print("Calling API with params:", params)
        result = asyncio.run(self._run_client("text_to_image", params))
        print("Received API response: ", result)

        # Verify result
        print("Verifying result...")
        self.assertIsNotNone(result)
        self.assertTrue(len(result.content) > 0)

        # 验证返回的内容
        content = result.content[0]
        self.assertEqual(content.type, "text")
        self.assertTrue(content.text)

        # 解析 JSON 字符串
        data = json.loads(content.text)
        self.assertEqual(data["status"], "success")
        self.assertIn("urls", data)
        self.assertIsInstance(data["urls"], list)
        self.assertGreater(len(data["urls"]), 0)
        url = data["urls"][0]
        self.assertTrue(url.startswith("http"))
        self.assertIsNone(data["error"])
        print(f"Generated image URL: {url}")

    def test_generate_video(self):
        """Test generating a video."""
        # For testing, we'll use a sample image URL
        # In a real test, you would use a valid image URL
        params = {
            "image": "https://d2p7pge43lyniu.cloudfront.net/output/b4d0ccc2-a2f4-4495-b4a8-fcbb60d3ab82-u2_0af704ff-9f76-4b06-8d94-97b1975ff604.jpeg",
            "prompt": "A peaceful mountain scene with gentle wind",
            "duration": 5,  # Short duration for faster testing
        }

        result = asyncio.run(self._run_client("generate_video", params))

        # Verify result
        self.assertIsNotNone(result)

        # Check if we got a text response with a video URL
        # Verify result
        print("Verifying result...:", result)
        self.assertIsNotNone(result)
        self.assertTrue(len(result.content) > 0)


if __name__ == "__main__":
    unittest.main()
