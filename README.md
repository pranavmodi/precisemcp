# MCP Server Example

This repository contains an example of an MCP (Model Context Protocol) server application. It demonstrates how to build and use MCP tools and resources with a streamable HTTP transport.

## 🏗️ Project Structure

```
precisemcp/
├── server.py                      # Main server entry point (NEW - modular)
├── config.py                      # Configuration management
├── auth.py                        # JWT authentication utilities
├── data_processing.py             # Patient data transformation
├── tools.py                       # MCP tools definitions
├── mcp_precise.py                 # Original monolithic server (still works)
├── mcp_utils.py                   # Utilities for the MCP server
├── test_client.py                 # Client for testing server tools
├── pyproject.toml                 # Dependencies
├── MCP_TOOLS_DOCUMENTATION.md     # Complete tool documentation
├── MCP_TOOLS_QUICK_REFERENCE.md   # Quick reference guide
├── REFACTORING_GUIDE.md           # Modular structure guide
└── README.md                      # This file
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

### **Option 1: Modular Server (Recommended)**

**Terminal 1 - Start the new modular server:**
```bash
# Run on default port 8000
uv run python3 server.py

# Run on a custom port (e.g., 8001)
PORT=8001 uv run python3 server.py
```

### **Option 2: Original Monolithic Server**

**Terminal 1 - Start the original server:**
```bash
# Run on default port 8000
uv run python3 mcp_precise.py

# Run on a custom port (e.g., 8001)
PORT=8001 uv run python3 mcp_precise.py
```

> **💡 Note**: Both servers provide identical functionality. The modular version (`server.py`) is recommended for better maintainability and development experience.

The server will print the exact URL it's running on.

### Running the Test Client

Once the server is running, you can use the test client to verify the functionality of the tools.

**Terminal 2 - Run Test Client:**
```bash
uv run python3 test_client.py
```

## 📋 Documentation

### 📖 Complete Tool Documentation
- **[MCP Tools Documentation](MCP_TOOLS_DOCUMENTATION.md)** - Comprehensive documentation for all MCP tools
- **[Quick Reference Guide](MCP_TOOLS_QUICK_REFERENCE.md)** - Quick lookup table for tools and parameters
- **[Refactoring Guide](REFACTORING_GUIDE.md)** - Details about the modular code organization

### 🔧 Available Tools (Summary)

The server exposes **8 MCP tools** organized into categories:

| Category | Tools | Purpose |
|----------|-------|---------|
| **Patient Info** | `fetch_patient_info`, `fetch_patient_by_id`, `fetch_patient_by_phone` | Patient data retrieval |
| **Studies** | `fetch_study_details` | Medical study information |
| **Case Management** | `get_case_update_details`, `insert_case_update_log` | Case tracking and updates |
| **Reporting** | `get_patient_report` | Patient reports |
| **Tasks** | `get_patient_todo_status` | Patient to-do items |

### 📚 Available Resources

| Resource | URI | Description |
|----------|-----|-------------|
| Greeting | `hello://greeting` | Server health check and greeting |

> 💡 **For detailed tool documentation including parameters, return values, and examples, see [MCP_TOOLS_DOCUMENTATION.md](MCP_TOOLS_DOCUMENTATION.md)**

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

1. ✅ **Real APIs**: Integrated with RadFlow and Chatbot APIs
2. ✅ **Authentication**: JWT and Basic auth implemented with caching
3. ✅ **Logging**: Enhanced logging and monitoring implemented
4. ✅ **Error Handling**: Robust error handling and recovery implemented
5. ✅ **Port Configuration**: Environment variable support for custom ports
6. ✅ **Modular Architecture**: Clean separation of concerns with multiple modules
7. **More Tools**: Add database, file system, or calculation tools
8. **WebSocket Support**: Add WebSocket transport option
9. **Load Balancing**: Configure multiple server instances
10. **Testing Suite**: Add comprehensive unit and integration tests
11. **Docker Support**: Add containerization for easy deployment
12. **API Rate Limiting**: Implement request rate limiting and throttling

## 📝 License

MIT License - Feel free to use this as a starting point for your own MCP projects!
