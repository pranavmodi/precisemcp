#!/usr/bin/env python3
"""
MCP Streamable HTTP Client Application - Dynamic Version

This is an improved version of client_streamable.py that uses dynamic tool discovery
instead of hardcoding specific tool names.
"""

import asyncio
import json
import logging
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp_utils import MCPClientHelper, MCPParameterGenerator, format_tool_list

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-streamable-dynamic-client")

async def main():
    """Main client application with dynamic tool discovery."""
    print("🚀 Starting Dynamic MCP Streamable HTTP Client...")
    print("=" * 50)
    
    # Connect to the independent MCP server via Streamable HTTP
    server_url = "http://localhost:8000/mcp"
    
    try:
        async with streamablehttp_client(server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                print("✅ Connected to MCP Server!")
                print(f"🌐 Server URL: {server_url}")
                print("📡 Using Streamable HTTP transport")
                print()
                
                # Set up dynamic helper
                helper = MCPClientHelper(session)
                if not await helper.discover_all():
                    print("❌ Failed to discover server capabilities")
                    return
                
                print(f"🔍 Discovered {len(helper.tools)} tools and {len(helper.resources)} resources")
                print()
                
                # Display discovered capabilities
                await display_capabilities(helper)
                
                # Test resources dynamically
                await test_resources_dynamically(helper)
                
                # Test tools dynamically  
                await test_tools_dynamically(helper)
                
                print("🎉 Dynamic MCP Client demonstration complete!")
                
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        print(f"Make sure the server is running at {server_url}")
        print("💡 Start the server with: python server_streamable.py")

async def display_capabilities(helper: MCPClientHelper):
    """Display discovered tools and resources."""
    
    # Display resources
    print("📚 Available Resources:")
    if helper.resources:
        for resource in helper.resources:
            print(f"  - {resource.uri}: {resource.name}")
            if resource.description:
                print(f"    {resource.description}")
    else:
        print("  No resources available")
    print()
    
    # Display tools by category
    print("🔧 Available Tools (by category):")
    categories = helper.categorize_tools()
    
    for category, tools in categories.items():
        if tools:
            print(f"\n  📂 {category.title()} Tools:")
            for tool in tools:
                print(f"    - {tool.name}: {tool.description or 'No description'}")
    print()

async def test_resources_dynamically(helper: MCPClientHelper):
    """Test all available resources."""
    if not helper.resources:
        print("⚠️  No resources to test")
        return
    
    print("🌟 Testing All Resources:")
    print("-" * 40)
    
    for resource in helper.resources:
        print(f"📖 Testing resource: {resource.uri}")
        result = await helper.read_resource_safe(resource.uri)
        
        if result:
            # Display first content item
            if result.contents:
                content_text = result.contents[0].text if hasattr(result.contents[0], 'text') else str(result.contents[0])
                preview = content_text[:100] + "..." if len(content_text) > 100 else content_text
                print(f"   ✅ Content: {preview}")
            else:
                print(f"   ✅ Resource read successfully (no content)")
        else:
            print(f"   ❌ Failed to read resource")
    print()

async def test_tools_dynamically(helper: MCPClientHelper):
    """Test tools dynamically based on their categories and capabilities."""
    
    print("🧪 Testing Tools Dynamically:")
    print("-" * 40)
    
    # Test greeting/communication tools
    greeting_tools = helper.search_tools("hello") + helper.search_tools("greet")
    if greeting_tools:
        print("💬 Testing greeting tools:")
        for tool in greeting_tools[:2]:  # Limit to first 2
            result = await helper.test_tool_with_defaults(tool.name, {"name": "Dynamic Client User"})
            await display_tool_result(tool.name, result)
    
    # Test math tools
    math_tools = helper.search_tools("add") + helper.search_tools("calculate")
    if math_tools:
        print("\n🔢 Testing math tools:")
        for tool in math_tools[:2]:  # Limit to first 2
            custom_params = {}
            if "add" in tool.name.lower():
                custom_params = {"a": 25, "b": 17}
            elif "fibonacci" in tool.name.lower():
                custom_params = {"n": 7}
            
            result = await helper.test_tool_with_defaults(tool.name, custom_params)
            await display_tool_result(tool.name, result)
    
    # Test weather tools
    weather_tools = helper.search_tools("weather")
    if weather_tools:
        print("\n🌤️  Testing weather tools:")
        for tool in weather_tools:
            result = await helper.test_tool_with_defaults(tool.name, {"city": "Tokyo"})
            await display_tool_result(tool.name, result)
    
    # Test data/patient tools
    data_tools = helper.search_tools("fetch") + helper.search_tools("patient") + helper.search_tools("get")
    if data_tools:
        print("\n📊 Testing data/patient tools:")
        for tool in data_tools[:3]:  # Limit to first 3
            # Generate smart defaults for patient/medical tools
            custom_params = {}
            if "patient" in tool.name.lower():
                custom_params = {
                    "patient_id": "DYNAMIC_TEST_001", 
                    "conversation_id": "dynamic_session_001"
                }
            
            result = await helper.test_tool_with_defaults(tool.name, custom_params)
            await display_tool_result(tool.name, result)
    
    # Test any remaining tools (up to 5 more)
    tested_tools = set()
    for category_tools in [greeting_tools, math_tools, weather_tools, data_tools]:
        for tool in category_tools:
            tested_tools.add(tool.name)
    
    remaining_tools = [tool for tool in helper.tools if tool.name not in tested_tools]
    if remaining_tools:
        print(f"\n🔧 Testing additional tools ({min(5, len(remaining_tools))} of {len(remaining_tools)}):")
        for tool in remaining_tools[:5]:
            result = await helper.test_tool_with_defaults(tool.name)
            await display_tool_result(tool.name, result)

async def display_tool_result(tool_name: str, result):
    """Display the result of a tool call in a formatted way."""
    if result:
        print(f"   ✅ {tool_name} executed successfully")
        
        try:
            for content in result.content:
                if hasattr(content, 'text'):
                    text = content.text
                    
                    # Try to parse and format JSON
                    try:
                        parsed = json.loads(text)
                        if isinstance(parsed, dict):
                            # Show key information from JSON response
                            if parsed.get('success'):
                                print(f"      Success: {parsed.get('success')}")
                            if parsed.get('message'):
                                print(f"      Message: {parsed.get('message')}")
                            if parsed.get('error'):
                                print(f"      Error: {parsed.get('error')}")
                            elif parsed.get('data'):
                                print(f"      Data: Available (length: {len(str(parsed['data']))})")
                            else:
                                # Show first few key-value pairs
                                for key, value in list(parsed.items())[:3]:
                                    print(f"      {key}: {value}")
                        else:
                            print(f"      Result: {parsed}")
                    except (json.JSONDecodeError, TypeError):
                        # Not JSON, show text preview
                        preview = text[:80] + "..." if len(text) > 80 else text
                        print(f"      Result: {preview}")
                else:
                    print(f"      Result: {str(content)[:80]}...")
        except Exception as e:
            print(f"      Result available but couldn't display: {e}")
    else:
        print(f"   ❌ {tool_name} failed to execute")

if __name__ == "__main__":
    asyncio.run(main()) 