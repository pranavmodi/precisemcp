#!/usr/bin/env python3
"""
MCP Client Application

This client connects to the MCP server and demonstrates using all available tools.
"""

import asyncio
import json
import logging
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-client")

async def main():
    """Main client application."""
    print("🚀 Starting MCP Client...")
    print("=" * 50)
    
    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="python3",
        args=["main.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            print("✅ Connected to MCP Server!")
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
                result = await session.call_tool("say_hello", {"name": "Alice"})
                print(f"👋 say_hello('Alice'): {result.content[0].text}")
            except Exception as e:
                print(f"❌ Error with say_hello: {e}")
            
            # Test add_numbers tool
            try:
                result = await session.call_tool("add_numbers", {"a": 15.5, "b": 24.3})
                print(f"➕ add_numbers(15.5, 24.3): {result.content[0].text}")
            except Exception as e:
                print(f"❌ Error with add_numbers: {e}")
            
            # Test get_weather tool with different cities
            cities = ["New York", "London", "Bangalore", "Mars"]
            for city in cities:
                try:
                    result = await session.call_tool("get_weather", {"city": city})
                    print(f"🌤️  get_weather('{city}'): {result.content[0].text}")
                except Exception as e:
                    print(f"❌ Error with get_weather for {city}: {e}")
            
            print()
            print("✨ All tools tested successfully!")
            print("🎉 MCP Client demonstration complete!")

if __name__ == "__main__":
    asyncio.run(main()) 