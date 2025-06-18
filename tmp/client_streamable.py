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
    print("🚀 Starting RadFlow MCP Streamable HTTP Client...")
    print("=" * 50)
    
    # Connect to the independent MCP server via Streamable HTTP
    server_url = "http://localhost:8000/mcp"
    
    try:
        async with streamablehttp_client(server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                print("✅ Connected to RadFlow Streamable MCP Server!")
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
                
                # Test the fetch_patient_info tool
                print("🏥 Testing RadFlow Patient Info Tool:")
                print("-" * 40)
                
                # Test cases for patient info
                test_cases = [
                    {"patient_id": "12345", "conversation_id": "test-conv-001"},
                    {"patient_id": "67890", "conversation_id": "test-conv-002"},
                    {"patient_id": "DEMO001"},  # Test with default conversation_id
                ]
                
                for i, test_case in enumerate(test_cases, 1):
                    try:
                        print(f"📋 Test Case {i}: {test_case}")
                        result = await session.call_tool("fetch_patient_info", test_case)
                        
                        # Parse and format the JSON response
                        response_text = result.content[0].text
                        try:
                            response_data = json.loads(response_text)
                            print(f"✅ Response:")
                            print(f"   Success: {response_data.get('success', 'N/A')}")
                            print(f"   Patient ID: {response_data.get('patient_id', 'N/A')}")
                            print(f"   Conversation ID: {response_data.get('conversation_id', 'N/A')}")
                            print(f"   Message: {response_data.get('message', 'N/A')}")
                            
                            if response_data.get('error'):
                                print(f"   Error: {response_data['error']}")
                            elif response_data.get('data'):
                                print(f"   Data Available: Yes (contains {len(str(response_data['data']))} characters)")
                            
                        except json.JSONDecodeError:
                            print(f"✅ Raw Response: {response_text}")
                            
                    except Exception as e:
                        print(f"❌ Error with fetch_patient_info: {e}")
                    
                    print()  # Add spacing between test cases
                
                print("✨ Patient info tool testing complete!")
                print("🎉 RadFlow MCP Streamable HTTP Client demonstration complete!")
                
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        print(f"Make sure the server is running at {server_url}")
        print("💡 Start the server with: python server_streamable.py")

if __name__ == "__main__":
    asyncio.run(main()) 