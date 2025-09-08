#!/usr/bin/env python3

import asyncio
import json
import logging

from fastmcp.client import Client

# Set up logging
logging.basicConfig(level=logging.INFO)


async def main():
    try:
        print("Connecting to MCP server at http://127.0.0.1:8888/mcp...")
        client = Client("http://127.0.0.1:8888/mcp", timeout=10)
        async with client:
            print("Connected! Listing available tools...")

            # List all available tools
            tools = await client.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")

            # Test each tool
            print("\n1. Testing get_tax_brackets...")
            result = await client.call_tool("get_tax_brackets", {})
            print(f"Result: {result[0].text[:200]}...")

            print("\n2. Testing get_cached_tax_info...")
            result = await client.call_tool("get_cached_tax_info", {"tax_topic": "tranches_impot"})
            data = json.loads(result[0].text)
            print(f"Status: {data['status']}")
            if "data" in data and "brackets" in data["data"]:
                print(f"Number of brackets: {len(data['data']['brackets'])}")
                print(f"First bracket: {data['data']['brackets'][0]}")

            print("\n3. Testing get_scheme_details...")
            result = await client.call_tool("get_scheme_details", {"scheme_name": "pinel"})
            print(f"Result: {result[0].text[:200]}...")

            print("\n4. Testing get_form_details...")
            result = await client.call_tool("get_form_details", {"form_number": "2042"})
            print(f"Result: {result[0].text[:200]}...")

            # Skip this test as it times out due to web scraping
            print("\n5. Skipping get_tax_info_from_web (takes too long)...")

            print("\n6. Testing generate_tax_report...")
            result = await client.call_tool(
                "generate_tax_report", {"tax_data": {"source": "test"}, "topic_name": "Test Report"}
            )
            print(f"Result: {result[0].text[:200]}...")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
