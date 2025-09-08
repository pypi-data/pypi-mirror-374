#!/usr/bin/env python3

import asyncio
import logging

from fastmcp.client import Client

# Set up logging
logging.basicConfig(level=logging.INFO)


async def main():
    try:
        print("Connecting to MCP server at http://127.0.0.1:8888/mcp...")
        client = Client("http://127.0.0.1:8888/mcp", timeout=10)
        async with client:
            print("Connected! Testing get_scheme_details tool...")

            # Call the get_scheme_details tool
            result = await client.call_tool("get_scheme_details", {"scheme_name": "pinel"})
            print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
