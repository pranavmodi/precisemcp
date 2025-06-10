#!/usr/bin/env python3
"""
Dynamic MCP Client

This client dynamically discovers tools and resources from any MCP server
and provides an interactive interface to use them.
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
logger = logging.getLogger("dynamic-mcp-client")

class DynamicMCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session: Optional[ClientSession] = None
        self.tools: List[Tool] = []
        self.resources: List[Resource] = []
    
    async def connect(self):
        """Connect to the MCP server and discover available tools and resources."""
        try:
            self.transport = streamablehttp_client(self.server_url)
            self.read, self.write, _ = await self.transport.__aenter__()
            self.session = ClientSession(self.read, self.write)
            await self.session.__aenter__()
            await self.session.initialize()
            
            print(f"✅ Connected to MCP server at {self.server_url}")
            await self.discover_capabilities()
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if hasattr(self, 'transport'):
                await self.transport.__aexit__(None, None, None)
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def discover_capabilities(self):
        """Discover available tools and resources from the server."""
        try:
            # Discover tools
            tools_response = await self.session.list_tools()
            self.tools = tools_response.tools
            
            # Discover resources
            resources_response = await self.session.list_resources()
            self.resources = resources_response.resources
            
            print(f"🔍 Discovered {len(self.tools)} tools and {len(self.resources)} resources")
            
        except Exception as e:
            print(f"❌ Error discovering capabilities: {e}")
    
    def display_tools(self):
        """Display all available tools with their descriptions and parameters."""
        if not self.tools:
            print("❌ No tools available")
            return
        
        print("\n🔧 Available Tools:")
        print("=" * 50)
        
        for i, tool in enumerate(self.tools, 1):
            print(f"{i}. {tool.name}")
            print(f"   Description: {tool.description or 'No description'}")
            
            if tool.inputSchema and 'properties' in tool.inputSchema:
                print("   Parameters:")
                properties = tool.inputSchema['properties']
                required = tool.inputSchema.get('required', [])
                
                for param_name, param_info in properties.items():
                    param_type = param_info.get('type', 'unknown')
                    param_desc = param_info.get('description', 'No description')
                    required_str = " (required)" if param_name in required else " (optional)"
                    print(f"     - {param_name} ({param_type}){required_str}: {param_desc}")
            print()
    
    def display_resources(self):
        """Display all available resources."""
        if not self.resources:
            print("❌ No resources available")
            return
        
        print("\n📚 Available Resources:")
        print("=" * 50)
        
        for i, resource in enumerate(self.resources, 1):
            print(f"{i}. {resource.name}")
            print(f"   URI: {resource.uri}")
            if resource.description:
                print(f"   Description: {resource.description}")
            print()
    
    async def call_tool_interactive(self, tool_name: str):
        """Interactively call a tool by gathering parameters from user input."""
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            print(f"❌ Tool '{tool_name}' not found")
            return
        
        print(f"\n🔧 Calling tool: {tool.name}")
        print(f"Description: {tool.description or 'No description'}")
        
        # Gather parameters
        parameters = {}
        if tool.inputSchema and 'properties' in tool.inputSchema:
            properties = tool.inputSchema['properties']
            required = tool.inputSchema.get('required', [])
            
            print("\nPlease provide the following parameters:")
            for param_name, param_info in properties.items():
                param_type = param_info.get('type', 'string')
                param_desc = param_info.get('description', 'No description')
                required_str = " (required)" if param_name in required else " (optional)"
                
                while True:
                    user_input = input(f"{param_name} ({param_type}){required_str}: ").strip()
                    
                    # Handle optional parameters
                    if not user_input and param_name not in required:
                        break
                    
                    # Handle required parameters
                    if not user_input and param_name in required:
                        print("❌ This parameter is required. Please provide a value.")
                        continue
                    
                    # Type conversion
                    try:
                        if param_type == 'integer':
                            parameters[param_name] = int(user_input)
                        elif param_type == 'number':
                            parameters[param_name] = float(user_input)
                        elif param_type == 'boolean':
                            parameters[param_name] = user_input.lower() in ('true', '1', 'yes', 'y')
                        else:
                            parameters[param_name] = user_input
                        break
                    except ValueError:
                        print(f"❌ Invalid {param_type}. Please try again.")
        
        # Call the tool
        try:
            print(f"\n⏳ Calling {tool_name} with parameters: {parameters}")
            result = await self.session.call_tool(tool_name, parameters)
            
            print(f"\n✅ Tool '{tool_name}' executed successfully!")
            print("Response:")
            print("-" * 30)
            
            for content in result.content:
                if hasattr(content, 'text'):
                    # Try to pretty-print JSON if possible
                    try:
                        parsed = json.loads(content.text)
                        print(json.dumps(parsed, indent=2))
                    except (json.JSONDecodeError, TypeError):
                        print(content.text)
                else:
                    print(str(content))
            
        except Exception as e:
            print(f"❌ Error calling tool '{tool_name}': {e}")
    
    async def read_resource_interactive(self, resource_uri: str):
        """Read a resource and display its contents."""
        try:
            print(f"\n📖 Reading resource: {resource_uri}")
            result = await self.session.read_resource(resource_uri)
            
            print("✅ Resource read successfully!")
            print("Contents:")
            print("-" * 30)
            
            for content in result.contents:
                if hasattr(content, 'text'):
                    print(content.text)
                else:
                    print(str(content))
                    
        except Exception as e:
            print(f"❌ Error reading resource '{resource_uri}': {e}")
    
    async def interactive_menu(self):
        """Main interactive menu for the client."""
        while True:
            print("\n" + "=" * 60)
            print("🤖 Dynamic MCP Client - Main Menu")
            print("=" * 60)
            print("1. List available tools")
            print("2. List available resources")
            print("3. Call a tool")
            print("4. Read a resource")
            print("5. Refresh capabilities (re-discover)")
            print("6. Exit")
            print()
            
            choice = input("Select an option (1-6): ").strip()
            
            if choice == '1':
                self.display_tools()
                
            elif choice == '2':
                self.display_resources()
                
            elif choice == '3':
                if not self.tools:
                    print("❌ No tools available")
                    continue
                
                print("\nAvailable tools:")
                for i, tool in enumerate(self.tools, 1):
                    print(f"  {i}. {tool.name}")
                
                try:
                    tool_choice = input("\nEnter tool number or name: ").strip()
                    
                    # Handle numeric choice
                    if tool_choice.isdigit():
                        tool_index = int(tool_choice) - 1
                        if 0 <= tool_index < len(self.tools):
                            tool_name = self.tools[tool_index].name
                        else:
                            print("❌ Invalid tool number")
                            continue
                    else:
                        # Handle name choice
                        tool_name = tool_choice
                    
                    await self.call_tool_interactive(tool_name)
                    
                except (ValueError, KeyboardInterrupt):
                    print("❌ Invalid choice")
                    continue
                    
            elif choice == '4':
                if not self.resources:
                    print("❌ No resources available")
                    continue
                
                print("\nAvailable resources:")
                for i, resource in enumerate(self.resources, 1):
                    print(f"  {i}. {resource.uri} ({resource.name})")
                
                try:
                    resource_choice = input("\nEnter resource number or URI: ").strip()
                    
                    # Handle numeric choice
                    if resource_choice.isdigit():
                        resource_index = int(resource_choice) - 1
                        if 0 <= resource_index < len(self.resources):
                            resource_uri = self.resources[resource_index].uri
                        else:
                            print("❌ Invalid resource number")
                            continue
                    else:
                        # Handle URI choice
                        resource_uri = resource_choice
                    
                    await self.read_resource_interactive(resource_uri)
                    
                except (ValueError, KeyboardInterrupt):
                    print("❌ Invalid choice")
                    continue
                    
            elif choice == '5':
                print("🔄 Refreshing capabilities...")
                await self.discover_capabilities()
                print("✅ Capabilities refreshed!")
                
            elif choice == '6':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 1-6.")

async def main():
    """Main application entry point."""
    print("🚀 Dynamic MCP Client")
    print("=" * 50)
    print("This client can connect to any MCP server and dynamically")
    print("discover and use the available tools and resources.")
    print()
    
    # Get server URL from user or use default
    server_url = input("Enter MCP server URL (default: http://localhost:8000/mcp): ").strip()
    if not server_url:
        server_url = "http://localhost:8000/mcp"
    
    client = DynamicMCPClient(server_url)
    
    # Connect to server
    if not await client.connect():
        return
    
    try:
        # Start interactive menu
        await client.interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 