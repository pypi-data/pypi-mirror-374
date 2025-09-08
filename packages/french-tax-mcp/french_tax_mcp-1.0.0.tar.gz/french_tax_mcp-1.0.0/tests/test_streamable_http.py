#!/usr/bin/env python3

import asyncio
import logging

from fastmcp.client import Client

# Set up logging
logging.basicConfig(level=logging.INFO)


async def main():
    try:
        print("Connecting to MCP server at http://127.0.0.1:8888...")
        client = Client("http://127.0.0.1:8888", timeout=10)
        async with client:
            print("Connected! Listing available tools...")

            # List available tools
            tools = await client.list_tools()
            print(f"Available tools: {tools}")

            # Test get_tax_brackets tool
            print("\nTesting get_tax_brackets tool...")
            result = await client.call_tool("get_tax_brackets", {})
            print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
