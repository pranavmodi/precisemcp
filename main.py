import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hello-mcp-server")

# Create FastMCP server instance
mcp = FastMCP("hello-mcp-server")

@mcp.resource("hello://greeting")
async def get_greeting() -> str:
    """A simple greeting resource."""
    return "Hello from your MCP server! 👋"

@mcp.tool()
async def say_hello(name: str) -> str:
    """Say hello to someone.
    
    Args:
        name: Name of the person to greet
    """
    return f"Hello, {name}! Nice to meet you! 🎉"

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
        "Bangalore": "mofo chilly asf"
    }
    
    weather = weather_data.get(city, f"Weather data not available for {city}")
    return f"Weather in {city}: {weather}"

if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run()
    print("MCP server started")
