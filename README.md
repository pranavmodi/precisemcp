# MCP Server Example

This repository contains an example of an MCP (Model Context Protocol) server application. It demonstrates how to build and use MCP tools and resources with a streamable HTTP transport.

## 🏗️ Project Structure

```
precisemcp/
├── mcp_precise.py       # Independent MCP Server (Streamable HTTP transport)
├── mcp_utils.py         # Utilities for the MCP server
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

## 🖥️ Running the Application

**Terminal 1 - Start Streamable HTTP Server:**
```bash
# Run on default port 8000
uv run python3 mcp_precise.py

# Run on a custom port (e.g., 8001)
PORT=8001 uv run python3 mcp_precise.py
```
The server will print the exact URL it's running on.

## 🔧 Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `fetch_patient_info` | Fetch patient information from the RadFlow API using patient ID. | `patient_id: str` |
| `fetch_patient_by_id` | Fetch patient information by ID from the RadFlow API. | `patient_id: str` |
| `fetch_study_details` | Fetch study details for a patient by their ID. | `patient_id: str` |
| `fetch_patient_by_phone` | Fetch patient data from the API using phone number. | `phone: str` |

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

## 🌟 Benefits of an Independent Server

1. **Scalability**: Multiple clients can connect simultaneously
2. **Deployment Flexibility**: Server can run on different machines
3. **Production Ready**: Better suited for real-world applications
4. **Resource Efficiency**: No subprocess overhead
5. **Network Transparent**: Works across network boundaries
6. **Stateless Options**: Better for load balancing and cloud deployment

## 📦 Dependencies

- `mcp[cli]>=1.9.1` - MCP framework with CLI tools
- `uvicorn` - for running the server

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
