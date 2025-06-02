#!/usr/bin/env python3
"""
MCP Streamable HTTP Client Application

This client connects to an independent MCP server via Streamable HTTP transport.
"""

import asyncio
import json
import logging
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-streamable-client")

async def main():
    """Main client application."""
    print("🚀 Starting MCP Streamable HTTP Client...")
    print("=" * 50)
    
    # Connect to the independent MCP server via Streamable HTTP
    server_url = "http://localhost:8000/mcp"
    
    try:
        async with streamablehttp_client(server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                print("✅ Connected to independent Streamable MCP Server!")
                print(f"🌐 Server URL: {server_url}")
                print("📡 Using Streamable HTTP transport")
                print()
                
                # List available resources
                print("📚 Available Resources:")
                resources = await session.list_resources()
                for resource in resources.resources:
                    print(f"  - {resource.uri}: {resource.name}")
                    if resource.description:
                        print(f"    {resource.description}")
                print()
                
                # List available tools
                print("🔧 Available Tools:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                print()
                
                # Test the greeting resource
                print("🌟 Testing Resources:")
                try:
                    greeting_response = await session.read_resource("hello://greeting")
                    print(f"📖 Greeting Resource: {greeting_response.contents[0].text}")
                except Exception as e:
                    print(f"❌ Error reading greeting resource: {e}")
                print()
                
                # Test all the tools
                print("🛠️  Testing Tools:")
                print("-" * 30)
                
                # Test say_hello tool
                try:
                    result = await session.call_tool("say_hello", {"name": "Bob"})
                    print(f"👋 say_hello('Bob'): {result.content[0].text}")
                except Exception as e:
                    print(f"❌ Error with say_hello: {e}")
                
                # Test add_numbers tool
                try:
                    result = await session.call_tool("add_numbers", {"a": 25.7, "b": 18.3})
                    print(f"➕ add_numbers(25.7, 18.3): {result.content[0].text}")
                except Exception as e:
                    print(f"❌ Error with add_numbers: {e}")
                
                # Test fibonacci tool
                try:
                    result = await session.call_tool("calculate_fibonacci", {"n": 10})
                    print(f"🔢 calculate_fibonacci(10): {result.content[0].text}")
                except Exception as e:
                    print(f"❌ Error with calculate_fibonacci: {e}")
                
                # Test get_weather tool with different cities
                cities = ["New York", "Sydney", "Bangalore", "Unknown City"]
                for city in cities:
                    try:
                        result = await session.call_tool("get_weather", {"city": city})
                        print(f"🌤️  get_weather('{city}'): {result.content[0].text}")
                    except Exception as e:
                        print(f"❌ Error with get_weather for {city}: {e}")
                
                print()
                print("✨ All tools tested successfully!")
                print("🎉 MCP Streamable HTTP Client demonstration complete!")
                
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        print(f"Make sure the server is running at {server_url}")

if __name__ == "__main__":
    asyncio.run(main()) 