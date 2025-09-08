#!/usr/bin/env python3

import asyncio
import logging

import httpx
from fastmcp.client import Client

# Set up logging
logging.basicConfig(level=logging.DEBUG)


async def main():
    try:
        # First, let's check if the server is responding to any HTTP requests
        print("Testing basic HTTP connectivity...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://127.0.0.1:8888/")
                print(f"HTTP response: {response.status_code} {response.text}")
            except Exception as e:
                print(f"HTTP request failed: {e}")

        # Try different paths that might be used by the MCP server
        paths = [
            "/",
            "/mcp",
            "/api",
            "/api/v1",
            "/api/v1/mcp",
            "/api/mcp",
            "/mcp/api",
            "/mcp/v1",
            "/streamable-http",
            "/sse",
        ]

        print("\nTesting different MCP endpoint paths...")
        for path in paths:
            url = f"http://127.0.0.1:8888{path}"
            print(f"\nTrying MCP endpoint: {url}")
            try:
                client = Client(url, timeout=5)
                async with client:
                    print(f"  Connected to {url}!")
                    tools = await client.list_tools()
                    print(f"  Available tools: {tools}")
                    break
            except Exception as e:
                print(f"  Failed: {e}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
