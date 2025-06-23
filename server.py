#!/usr/bin/env python3
"""
PreciseMCP Server with Streamable HTTP Transport

This server runs independently and can be accessed via HTTP.
"""

import asyncio
import logging
import os
import uvicorn
from mcp.server.fastmcp import FastMCP

from config import DEFAULT_PORT
from tools import register_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("precise-mcp-server")

# Create FastMCP server instance with streamable HTTP support
mcp = FastMCP("precise-mcp-server", stateless_http=True)

# Register all tools and resources
register_tools(mcp)

# Expose the ASGI app *after* all tools and resources are defined
app = mcp.streamable_http_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", DEFAULT_PORT))
    print("🚀 Starting PreciseMCP Server...")
    print("=" * 60)
    print("Server will be available at:")
    print(f"  🌐 HTTP endpoint: http://localhost:{port}")
    print("  📡 This server uses Streamable HTTP transport")
    print("  🔄 Stateless operation for better scalability")
    print("  🏥 RadFlow API integration enabled")
    print("  👤 Patient lookup by ID, phone number")
    print("  📋 Study details retrieval")
    print("=" * 60)
    
    # Run with uvicorn for better control over port
    uvicorn.run(app, host="0.0.0.0", port=port)