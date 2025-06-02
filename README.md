# MCP Server & Client Example

This repository contains a complete example of an MCP (Model Context Protocol) server and client applications. It demonstrates how to build and use MCP tools and resources with **both stdio and independent HTTP transports**.

## 🏗️ Project Structure

```
precisemcp/
├── main.py              # Original MCP Server (stdio transport)
├── server.py            # Independent MCP Server (SSE transport)
├── server_streamable.py # Independent MCP Server (Streamable HTTP transport)
├── client.py            # Simple demonstration client (stdio)
├── client_http.py       # HTTP client for SSE transport
├── client_streamable.py # HTTP client for Streamable HTTP transport
├── interactive_client.py # Interactive client with menu (stdio)
├── test_transports.py   # Test script for all transport methods
├── pyproject.toml       # Dependencies
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+ (or 3.12+ should work)
- `uv` package manager

### Installation

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Add uv to your PATH permanently**:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Verify uv installation**:
   ```bash
   uv --version
   ```

4. **Install dependencies**:
   ```bash
   uv sync
   ```

## 🖥️ Running the Applications

### Option 1: Original stdio Setup (Server as subprocess)

#### 1. MCP Server Only

Start the MCP server to accept connections from other MCP clients:

```bash
uv run python3 main.py
```

#### 2. Demo Client

Run the simple demonstration client that tests all tools:

```bash
# In a new terminal window
uv run python3 client.py
```

#### 3. Interactive Client

Run the interactive client for hands-on exploration:

```bash
uv run python3 interactive_client.py
```

### Option 2: Independent HTTP Servers (Recommended)

#### SSE Transport Server

**Terminal 1 - Start SSE Server:**
```bash
uv run python3 server.py
# Server runs on http://localhost:8000/sse
```

**Terminal 2 - Run SSE Client:**
```bash
uv run python3 client_http.py
```

#### Streamable HTTP Transport Server (Preferred for Production)

**Terminal 1 - Start Streamable HTTP Server:**
```bash
uv run python3 server_streamable.py
# Server runs on http://localhost:8000/mcp
```

**Terminal 2 - Run Streamable HTTP Client:**
```bash
uv run python3 client_streamable.py
```

### Test All Transports

Run the comprehensive test suite to verify all transport methods:

```bash
uv run python3 test_transports.py
```

## 🌐 Transport Comparison

### stdio Transport (Original)
- ✅ Simple development setup
- ✅ Single process management
- ❌ Client spawns server as subprocess
- ❌ Not suitable for multi-client scenarios
- ❌ Limited scalability

### SSE Transport
- ✅ Independent server process (port 8000)
- ✅ Multiple clients can connect
- ✅ HTTP-based, firewall-friendly
- ✅ Real-time server-to-client events
- ⚠️ Being superseded by Streamable HTTP

### Streamable HTTP Transport (Recommended)
- ✅ Independent server process (port 8000)
- ✅ Multiple clients can connect
- ✅ Better scalability and performance
- ✅ Stateless operation option
- ✅ Production-ready
- ✅ Resumable sessions with event stores

## 🔧 Available Tools

All server variants provide these tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `say_hello` | Greet someone by name | `name: str` |
| `add_numbers` | Add two numbers together | `a: float, b: float` |
| `get_weather` | Get weather for a city (mock data) | `city: str` |
| `calculate_fibonacci` | Calculate fibonacci number | `n: int` (Streamable server only) |

## 📚 Available Resources

| Resource | URI | Description |
|----------|-----|-------------|
| Greeting | `hello://greeting` | A simple greeting message |

## 🛠️ Development

### Adding New Tools

To add a new tool to any server, use the `@mcp.tool()` decorator:

```python
@mcp.tool()
async def your_new_tool(param1: str, param2: int) -> str:
    """Description of what your tool does.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
    """
    # Your tool logic here
    return f"Result: {param1} {param2}"
```

### Adding New Resources

To add a new resource:

```python
@mcp.resource("your://resource/uri")
async def your_resource() -> str:
    """Description of your resource."""
    return "Your resource content"
```

## 🏃‍♂️ Example Usage

### Quick Test (stdio)
```bash
# Terminal 1: Start server
uv run python3 main.py

# Terminal 2: Run demo client
uv run python3 client.py
```

### Independent Server Test (HTTP)
```bash
# Terminal 1: Start independent server
uv run python3 server_streamable.py

# Terminal 2: Run HTTP client
uv run python3 client_streamable.py
```

### Interactive Session (stdio)
```bash
uv run python3 interactive_client.py
```

### Test All Transports
```bash
uv run python3 test_transports.py
```

## 🤝 Architecture Comparison

### stdio Architecture
```
┌─────────────────┐    stdio pipes    ┌─────────────────┐
│   MCP Client    │◄──────────────────►│   MCP Server    │
│                 │                    │   (subprocess)  │
│ - client.py     │                    │ - main.py       │
│ - interactive   │                    │ - Tools         │
│   _client.py    │                    │ - Resources     │
└─────────────────┘                    └─────────────────┘
```

### HTTP Architecture
```
┌─────────────────┐    HTTP/SSE      ┌─────────────────┐
│   MCP Client    │◄─────────────────►│   MCP Server    │
│                 │                   │  (independent)  │
│ - client_http   │     Port 8000     │ - server.py     │
│ - client_       │     Port 8000     │ - server_       │
│   streamable    │                   │   streamable.py │
└─────────────────┘                   └─────────────────┘
```

## 🌟 Benefits of Independent Servers

1. **Scalability**: Multiple clients can connect simultaneously
2. **Deployment Flexibility**: Server can run on different machines
3. **Production Ready**: Better suited for real-world applications
4. **Resource Efficiency**: No subprocess overhead
5. **Network Transparent**: Works across network boundaries
6. **Stateless Options**: Better for load balancing and cloud deployment

## 📦 Dependencies

- `mcp[cli]>=1.9.1` - MCP framework with CLI tools
- `httpx>=0.28.1` - HTTP client (for future web API tools)

## 🚀 Next Steps

1. **Add Real APIs**: Replace mock weather data with real API calls
2. **More Tools**: Add database, file system, or calculation tools
3. **Authentication**: Add secure authentication for production use
4. **Logging**: Enhanced logging and monitoring
5. **Error Handling**: More robust error handling and recovery
6. **WebSocket Support**: Add WebSocket transport option
7. **Load Balancing**: Configure multiple server instances
8. **Port Configuration**: Add environment variable support for custom ports

## 📝 License

MIT License - Feel free to use this as a starting point for your own MCP projects!
