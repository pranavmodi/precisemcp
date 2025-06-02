#!/usr/bin/env python3
"""
Independent MCP Server with Streamable HTTP Transport

This server runs independently and can be accessed via HTTP.
"""

import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("streamable-mcp-server")

# Create FastMCP server instance with streamable HTTP support
mcp = FastMCP("streamable-mcp-server", stateless_http=True)

@mcp.resource("hello://greeting")
async def get_greeting() -> str:
    """A simple greeting resource."""
    return "Hello from your streamable MCP server! 🚀"

@mcp.tool()
async def say_hello(name: str) -> str:
    """Say hello to someone.
    
    Args:
        name: Name of the person to greet
    """
    return f"Hello, {name}! Nice to meet you from the streamable server! 🎉"

@mcp.tool()
async def add_numbers(a: float, b: float) -> str:
    """Add two numbers together.
    
    Args:
        a: First number
        b: Second number
    """
    result = a + b
    return f"The sum of {a} and {b} is {result}"

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather for a city using a mock API.
    
    Args:
        city: Name of the city
    """
    # Mock weather data - in a real implementation you'd call a weather API
    weather_data = {
        "New York": "Sunny, 72°F",
        "London": "Cloudy, 15°C", 
        "Tokyo": "Rainy, 18°C",
        "San Francisco": "Foggy, 16°C",
        "Bangalore": "mofo chilly asf",
        "Sydney": "Hot, 35°C"
    }
    
    weather = weather_data.get(city, f"Weather data not available for {city}")
    return f"Weather in {city}: {weather}"

@mcp.tool()
async def calculate_fibonacci(n: int) -> str:
    """Calculate fibonacci number at position n.
    
    Args:
        n: Position in fibonacci sequence (0-based)
    """
    if n < 0:
        return "Please provide a non-negative number"
    elif n <= 1:
        return f"Fibonacci({n}) = {n}"
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return f"Fibonacci({n}) = {b}"

if __name__ == "__main__":
    print("🚀 Starting Independent Streamable MCP Server...")
    print("=" * 60)
    print("Server will be available at:")
    print("  🌐 HTTP endpoint: http://localhost:8000/mcp")
    print("  📡 This server uses Streamable HTTP transport")
    print("  🔄 Stateless operation for better scalability")
    print("=" * 60)
    
    # Run with streamable HTTP transport (default port is 8000)
    mcp.run(transport="streamable-http") 