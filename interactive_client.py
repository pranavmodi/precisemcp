#!/usr/bin/env python3
"""
Interactive MCP Client Application

This client provides an interactive menu to use MCP server tools.
"""

import asyncio
import logging
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise for interactive use
logger = logging.getLogger("interactive-mcp-client")

class InteractiveMCPClient:
    def __init__(self):
        self.session = None
        self.tools = []
        self.resources = []
    
    async def connect(self):
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command="python3",
            args=["main.py"],
            env=None
        )
        
        self.stdio_client = stdio_client(server_params)
        read, write = await self.stdio_client.__aenter__()
        self.session = ClientSession(read, write)
        await self.session.__aenter__()
        await self.session.initialize()
        
        # Cache available tools and resources
        tools_response = await self.session.list_tools()
        self.tools = tools_response.tools
        
        resources_response = await self.session.list_resources()
        self.resources = resources_response.resources
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'stdio_client'):
            await self.stdio_client.__aexit__(None, None, None)
    
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "="*60)
        print("🚀 Interactive MCP Client")
        print("="*60)
        print("Choose an option:")
        print("1. 📚 View available resources")
        print("2. 🔧 View available tools")
        print("3. 👋 Say hello to someone")
        print("4. ➕ Add two numbers")
        print("5. 🌤️  Get weather for a city")
        print("6. 📖 Read greeting resource")
        print("7. 🎯 Test all tools (demo mode)")
        print("0. 🚪 Exit")
        print("-"*60)
    
    async def view_resources(self):
        """Display available resources."""
        print("\n📚 Available Resources:")
        print("-" * 30)
        for resource in self.resources:
            print(f"URI: {resource.uri}")
            print(f"Name: {resource.name}")
            if resource.description:
                print(f"Description: {resource.description}")
            print()
    
    async def view_tools(self):
        """Display available tools."""
        print("\n🔧 Available Tools:")
        print("-" * 30)
        for tool in self.tools:
            print(f"Name: {tool.name}")
            print(f"Description: {tool.description}")
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                print(f"Parameters: {tool.inputSchema.get('properties', {}).keys()}")
            print()
    
    async def say_hello_interactive(self):
        """Interactive say hello tool."""
        name = input("\n👋 Enter a name to greet: ").strip()
        if name:
            try:
                result = await self.session.call_tool("say_hello", {"name": name})
                print(f"🎉 {result.content[0].text}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ Name cannot be empty!")
    
    async def add_numbers_interactive(self):
        """Interactive add numbers tool."""
        try:
            a = float(input("\n➕ Enter first number: "))
            b = float(input("➕ Enter second number: "))
            
            result = await self.session.call_tool("add_numbers", {"a": a, "b": b})
            print(f"🧮 {result.content[0].text}")
        except ValueError:
            print("❌ Please enter valid numbers!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def get_weather_interactive(self):
        """Interactive weather tool."""
        city = input("\n🌤️  Enter city name: ").strip()
        if city:
            try:
                result = await self.session.call_tool("get_weather", {"city": city})
                print(f"🌡️ {result.content[0].text}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ City name cannot be empty!")
    
    async def read_greeting_resource(self):
        """Read the greeting resource."""
        try:
            result = await self.session.read_resource("hello://greeting")
            print(f"\n📖 Greeting Resource:")
            print(f"🎊 {result.contents[0].text}")
        except Exception as e:
            print(f"❌ Error reading resource: {e}")
    
    async def demo_mode(self):
        """Run all tools in demo mode."""
        print("\n🎯 Demo Mode - Testing all tools...")
        print("-" * 40)
        
        # Test greeting resource
        await self.read_greeting_resource()
        
        # Test say_hello
        result = await self.session.call_tool("say_hello", {"name": "Demo User"})
        print(f"\n👋 say_hello demo: {result.content[0].text}")
        
        # Test add_numbers
        result = await self.session.call_tool("add_numbers", {"a": 42, "b": 13})
        print(f"➕ add_numbers demo: {result.content[0].text}")
        
        # Test weather for multiple cities
        cities = ["New York", "Bangalore", "Unknown City"]
        for city in cities:
            result = await self.session.call_tool("get_weather", {"city": city})
            print(f"🌤️  {city}: {result.content[0].text}")
    
    async def run(self):
        """Main application loop."""
        try:
            await self.connect()
            print("✅ Connected to MCP Server!")
            
            while True:
                self.display_menu()
                choice = input("Enter your choice (0-7): ").strip()
                
                if choice == "0":
                    print("\n👋 Goodbye!")
                    break
                elif choice == "1":
                    await self.view_resources()
                elif choice == "2":
                    await self.view_tools()
                elif choice == "3":
                    await self.say_hello_interactive()
                elif choice == "4":
                    await self.add_numbers_interactive()
                elif choice == "5":
                    await self.get_weather_interactive()
                elif choice == "6":
                    await self.read_greeting_resource()
                elif choice == "7":
                    await self.demo_mode()
                else:
                    print("❌ Invalid choice! Please try again.")
                
                input("\nPress Enter to continue...")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await self.disconnect()

async def main():
    """Entry point."""
    client = InteractiveMCPClient()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main()) 