#!/usr/bin/env python3

import asyncio
import json

from fastmcp.client import Client


async def main():
    print("Connecting to MCP server at http://127.0.0.1:8888/mcp...")
    client = Client("http://127.0.0.1:8888/mcp", timeout=10)

    async with client:
        print("Connected! Testing multiple queries...")

        # 1. Get tax brackets
        print("\n1. QUERYING TAX BRACKETS:")
        result = await client.call_tool("get_tax_brackets", {})
        response_json = json.loads(result[0].text)
        print(f"Status: {response_json['status']}")
        print(f"Year: {response_json['data']['year']}")
        print(f"Number of brackets: {len(response_json['data']['brackets'])}")
        print(f"First bracket: {response_json['data']['brackets'][0]}")

        # 2. Get LMNP scheme details
        print("\n2. QUERYING LMNP SCHEME DETAILS:")
        result = await client.call_tool("get_scheme_details", {"scheme_name": "lmnp"})
        response_json = json.loads(result[0].text)
        print(f"Status: {response_json['status']}")
        print(f"Scheme: {response_json['data']['scheme']}")
        print(f"Description: {response_json['data']['description'][:100]}...")
        print(f"Eligibility criteria: {len(response_json['data']['eligibility'])} items")
        print(f"Tax advantages: {len(response_json['data']['advantages'])} items")

        # 3. Get form details
        print("\n3. QUERYING FORM 2042 DETAILS:")
        result = await client.call_tool("get_form_details", {"form_number": "2042"})
        response_json = json.loads(result[0].text)
        print(f"Status: {response_json['status']}")
        print(f"Form: {response_json['data']['form']}")
        print(f"Title: {response_json['data']['title']}")
        print(f"Sections: {len(response_json['data']['sections'])} sections")
        print(f"Related forms: {len(response_json['data']['related_forms'])} forms")

        # 4. Generate a report
        print("\n4. GENERATING TAX REPORT:")
        tax_data = {"source": "test", "year": 2025, "topic": "LMNP"}
        result = await client.call_tool(
            "generate_tax_report",
            {"tax_data": tax_data, "topic_name": "Location Meublée Non Professionnelle"},
        )
        print(f"Report generated with {len(result[0].text)} characters")
        print(f"Report preview: {result[0].text[:150]}...")


if __name__ == "__main__":
    asyncio.run(main())
