#!/usr/bin/env python3

import asyncio
import json

from fastmcp.client import Client


async def main():
    print("Connecting to MCP server at http://127.0.0.1:8888/mcp...")
    client = Client("http://127.0.0.1:8888/mcp", timeout=15)

    async with client:
        print("Connected! Querying LMNP scheme details...")

        # Get LMNP scheme details
        result = await client.call_tool("get_scheme_details", {"scheme_name": "lmnp"})

        # Format the response for better readability
        response_text = result[0].text
        response_json = json.loads(response_text)
        formatted_response = json.dumps(response_json, indent=2)

        print("\nFormatted Response:")
        print(formatted_response)


if __name__ == "__main__":
    asyncio.run(main())
