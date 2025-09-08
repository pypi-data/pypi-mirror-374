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
            print("Connected! Testing generate_tax_report tool...")

            # First get tax data
            tax_data = await client.call_tool(
                "get_cached_tax_info", {"tax_topic": "tranches_impot"}
            )
            tax_data_json = tax_data[0].text

            # Now generate a report
            result = await client.call_tool(
                "generate_tax_report",
                {
                    "tax_data": {"tax_brackets": tax_data_json},
                    "topic_name": "Tranches d'imposition 2025",
                    "format": "markdown",
                },
            )
            print(f"Report generated:\n{result}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
