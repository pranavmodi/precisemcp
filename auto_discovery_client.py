#!/usr/bin/env python3
"""
Auto-Discovery MCP Client

This client demonstrates how to programmatically discover and use MCP tools
without knowing in advance what tools will be available.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Tool, Resource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auto-discovery-client")

class AutoDiscoveryClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session: Optional[ClientSession] = None
        self.tools: List[Tool] = []
        self.resources: List[Resource] = []
    
    async def connect_and_discover(self):
        """Connect to server and discover capabilities."""
        try:
            async with streamablehttp_client(self.server_url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    self.session = session
                    await session.initialize()
                    
                    print(f"✅ Connected to MCP server: {self.server_url}")
                    
                    # Discover capabilities
                    await self._discover_tools()
                    await self._discover_resources()
                    
                    # Demonstrate dynamic usage
                    await self._demonstrate_dynamic_usage()
                    
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    
    async def _discover_tools(self):
        """Discover available tools."""
        try:
            tools_response = await self.session.list_tools()
            self.tools = tools_response.tools
            
            print(f"\n🔧 Discovered {len(self.tools)} tools:")
            for tool in self.tools:
                print(f"  - {tool.name}: {tool.description}")
                
        except Exception as e:
            print(f"❌ Error discovering tools: {e}")
    
    async def _discover_resources(self):
        """Discover available resources."""
        try:
            resources_response = await self.session.list_resources()
            self.resources = resources_response.resources
            
            print(f"\n📚 Discovered {len(self.resources)} resources:")
            for resource in self.resources:
                print(f"  - {resource.uri}: {resource.name}")
                
        except Exception as e:
            print(f"❌ Error discovering resources: {e}")
    
    def get_tool_by_name(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return next((tool for tool in self.tools if tool.name == name), None)
    
    def get_tools_by_keyword(self, keyword: str) -> List[Tool]:
        """Find tools that contain a keyword in name or description."""
        keyword_lower = keyword.lower()
        matching_tools = []
        
        for tool in self.tools:
            if (keyword_lower in tool.name.lower() or 
                (tool.description and keyword_lower in tool.description.lower())):
                matching_tools.append(tool)
        
        return matching_tools
    
    async def call_tool_with_defaults(self, tool_name: str, custom_params: Dict[str, Any] = None) -> Any:
        """
        Call a tool with intelligent parameter defaults.
        
        This demonstrates how to programmatically call tools when you don't know
        their exact parameter requirements in advance.
        """
        tool = self.get_tool_by_name(tool_name)
        if not tool:
            print(f"❌ Tool '{tool_name}' not found")
            return None
        
        # Build parameters with intelligent defaults
        parameters = {}
        if custom_params:
            parameters.update(custom_params)
        
        if tool.inputSchema and 'properties' in tool.inputSchema:
            properties = tool.inputSchema['properties']
            required = tool.inputSchema.get('required', [])
            
            for param_name, param_info in properties.items():
                if param_name in parameters:
                    continue  # Already provided
                    
                param_type = param_info.get('type', 'string')
                
                # Generate intelligent defaults based on parameter name and type
                if param_name in required:
                    if 'name' in param_name.lower():
                        parameters[param_name] = "Dynamic Client"
                    elif 'id' in param_name.lower():
                        parameters[param_name] = "AUTO_GENERATED_ID"
                    elif 'city' in param_name.lower():
                        parameters[param_name] = "San Francisco"
                    elif param_type == 'integer':
                        parameters[param_name] = 10
                    elif param_type == 'number':
                        parameters[param_name] = 5.0
                    elif param_type == 'boolean':
                        parameters[param_name] = True
                    else:
                        parameters[param_name] = f"auto_value_for_{param_name}"
        
        try:
            print(f"🔧 Calling {tool_name} with auto-generated parameters: {parameters}")
            result = await self.session.call_tool(tool_name, parameters)
            
            print(f"✅ Tool '{tool_name}' executed successfully!")
            return result
            
        except Exception as e:
            print(f"❌ Error calling tool '{tool_name}': {e}")
            return None
    
    async def test_all_available_tools(self):
        """Test all available tools with intelligent parameter generation."""
        print(f"\n🧪 Testing all {len(self.tools)} available tools...")
        print("=" * 60)
        
        results = {}
        for tool in self.tools:
            print(f"\n🔧 Testing tool: {tool.name}")
            result = await self.call_tool_with_defaults(tool.name)
            results[tool.name] = result is not None
            
            if result:
                # Display result preview
                try:
                    for content in result.content:
                        if hasattr(content, 'text'):
                            text = content.text
                            # Show first 100 chars
                            preview = text[:100] + "..." if len(text) > 100 else text
                            print(f"   Result preview: {preview}")
                except Exception as e:
                    print(f"   Result available but couldn't preview: {e}")
        
        # Summary
        successful = sum(results.values())
        total = len(results)
        print(f"\n📊 Tool Testing Summary: {successful}/{total} tools tested successfully")
        
        for tool_name, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {tool_name}")
    
    async def read_all_resources(self):
        """Read all available resources."""
        print(f"\n📖 Reading all {len(self.resources)} resources...")
        print("=" * 60)
        
        for resource in self.resources:
            try:
                print(f"\n📚 Reading resource: {resource.uri}")
                result = await self.session.read_resource(resource.uri)
                
                for content in result.contents:
                    if hasattr(content, 'text'):
                        text = content.text
                        preview = text[:200] + "..." if len(text) > 200 else text
                        print(f"   Content: {preview}")
                        
            except Exception as e:
                print(f"❌ Error reading resource '{resource.uri}': {e}")
    
    async def _demonstrate_dynamic_usage(self):
        """Demonstrate various ways to use tools dynamically."""
        print("\n" + "=" * 60)
        print("🎯 Dynamic Tool Usage Demonstration")
        print("=" * 60)
        
        # 1. Search for specific tool types
        print("\n1. Searching for greeting/hello tools:")
        greeting_tools = self.get_tools_by_keyword("hello")
        for tool in greeting_tools:
            await self.call_tool_with_defaults(tool.name, {"name": "Dynamic User"})
        
        # 2. Search for math/calculation tools
        print("\n2. Searching for math/calculation tools:")
        math_tools = self.get_tools_by_keyword("add") + self.get_tools_by_keyword("calculate")
        for tool in math_tools:
            if "add" in tool.name.lower():
                await self.call_tool_with_defaults(tool.name, {"a": 15, "b": 25})
            elif "fibonacci" in tool.name.lower():
                await self.call_tool_with_defaults(tool.name, {"n": 8})
        
        # 3. Search for weather tools
        print("\n3. Searching for weather tools:")
        weather_tools = self.get_tools_by_keyword("weather")
        for tool in weather_tools:
            await self.call_tool_with_defaults(tool.name, {"city": "New York"})
        
        # 4. Try to call any patient-related tools (for medical systems)
        print("\n4. Searching for patient/medical tools:")
        patient_tools = self.get_tools_by_keyword("patient")
        for tool in patient_tools:
            await self.call_tool_with_defaults(tool.name, {
                "patient_id": "DEMO_PATIENT_123",
                "conversation_id": "auto_discovery_session"
            })
        
        # 5. Read all available resources
        if self.resources:
            await self.read_all_resources()
        
        # 6. Test all tools (if not too many)
        if len(self.tools) <= 10:
            await self.test_all_available_tools()
        else:
            print(f"\n⏭️  Skipping full tool test ({len(self.tools)} tools available)")
            print("   To test all tools, run: await client.test_all_available_tools()")

async def main():
    """Main demonstration."""
    print("🚀 Auto-Discovery MCP Client Demo")
    print("=" * 50)
    print("This client demonstrates how to:")
    print("- Connect to any MCP server")
    print("- Dynamically discover available tools and resources")
    print("- Intelligently call tools without hardcoded parameters")
    print("- Handle unknown tool schemas gracefully")
    print()
    
    # You can change this URL to test with different servers
    server_url = "http://localhost:8000/mcp"
    
    client = AutoDiscoveryClient(server_url)
    await client.connect_and_discover()

if __name__ == "__main__":
    asyncio.run(main()) 