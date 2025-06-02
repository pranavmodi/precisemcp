# MCP Server & Client Example

This repository contains a complete example of an MCP (Model Context Protocol) server and client applications. It demonstrates how to build and use MCP tools and resources.

## 🏗️ Project Structure

```
precisemcp/
├── main.py              # MCP Server with tools and resources
├── client.py            # Simple demonstration client
├── interactive_client.py # Interactive client with menu
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

### 1. MCP Server Only

Start the MCP server to accept connections from other MCP clients:

```bash
uv run python3 main.py
```

The server will start and output:
```
Starting MCP server...
MCP server started
```

### 2. Demo Client

Run the simple demonstration client that tests all tools:

```bash
# In a new terminal window
uv run python3 client.py
```

This will:
- Connect to the MCP server
- List all available tools and resources
- Test each tool with sample data
- Display the results

### 3. Interactive Client

Run the interactive client for hands-on exploration:

```bash
uv run python3 interactive_client.py
```

This provides a menu-driven interface where you can:
- View available tools and resources
- Test individual tools with your own input
- Run a complete demo

## 🔧 Available Tools

The MCP server provides these tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `say_hello` | Greet someone by name | `name: str` |
| `add_numbers` | Add two numbers together | `a: float, b: float` |
| `get_weather` | Get weather for a city (mock data) | `city: str` |

## 📚 Available Resources

| Resource | URI | Description |
|----------|-----|-------------|
| Greeting | `hello://greeting` | A simple greeting message |

## 🛠️ Development

### Adding New Tools

To add a new tool to the server, use the `@mcp.tool()` decorator:

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

### Client Integration

The clients demonstrate two approaches:

1. **Programmatic** (`client.py`): Direct tool calls for automation
2. **Interactive** (`interactive_client.py`): User-driven exploration

## 🏃‍♂️ Example Usage

### Quick Test
```bash
# Terminal 1: Start server
uv run python3 main.py

# Terminal 2: Run demo client
uv run python3 client.py
```

### Interactive Session
```bash
uv run python3 interactive_client.py
```

Then choose from the menu:
```
🚀 Interactive MCP Client
============================================================
Choose an option:
1. 📚 View available resources
2. 🔧 View available tools
3. 👋 Say hello to someone
4. ➕ Add two numbers
5. 🌤️  Get weather for a city
6. 📖 Read greeting resource
7. 🎯 Test all tools (demo mode)
0. 🚪 Exit
```

## 📦 Dependencies

- `mcp[cli]>=1.9.1` - MCP framework with CLI tools
- `httpx>=0.28.1` - HTTP client (for future web API tools)

## 🤝 Architecture

```
┌─────────────────┐    MCP Protocol    ┌─────────────────┐
│   MCP Client    │◄──────────────────►│   MCP Server    │
│                 │                    │                 │
│ - client.py     │                    │ - main.py       │
│ - interactive   │                    │ - Tools         │
│   _client.py    │                    │ - Resources     │
└─────────────────┘                    └─────────────────┘
```

## 🤔 Why Same Repository?

Having both server and client in the same repo is **recommended** for:

- ✅ **Development & Testing**: Easy to test server changes
- ✅ **Documentation**: Complete working examples
- ✅ **Shared Dependencies**: No duplication
- ✅ **Simple Deployment**: Everything in one place

Consider separating when:
- 🔄 **Production Use**: Different release cycles
- 📦 **Distribution**: Independent packaging needed
- 🎯 **Specialized Clients**: Very different requirements

## 🚀 Next Steps

1. **Add Real APIs**: Replace mock weather data with real API calls
2. **More Tools**: Add database, file system, or calculation tools
3. **Authentication**: Add secure authentication for production use
4. **Logging**: Enhanced logging and monitoring
5. **Error Handling**: More robust error handling and recovery

## 📝 License

MIT License - Feel free to use this as a starting point for your own MCP projects!
