# PreciseMCP Server Refactoring Guide

This document explains how the original `mcp_precise.py` file has been reorganized into multiple modules for better maintainability and organization.

## File Structure

The functionality has been split into the following files:

### 1. `config.py` - Configuration Management
- **Purpose**: Centralized configuration and environment variables
- **Contains**:
  - All API URLs (RadFlow, Chatbot APIs)
  - Authentication credentials
  - Default server configuration
- **Dependencies**: None

### 2. `auth.py` - Authentication Utilities
- **Purpose**: JWT token management and caching
- **Contains**:
  - JWT token cache
  - `get_and_cache_jwt_token()` function for automatic token refresh
- **Dependencies**: `config.py`

### 3. `data_processing.py` - Data Transformation
- **Purpose**: Patient data processing and transformation
- **Contains**:
  - `process_patient_data()` function for transforming API responses
  - Patient data schema normalization
- **Dependencies**: None (only standard library)

### 4. `tools.py` - MCP Tools Definition
- **Purpose**: All MCP tool definitions and business logic
- **Contains**:
  - `register_tools()` function to register all tools with FastMCP
  - All API tool functions:
    - `fetch_patient_info()`
    - `fetch_patient_by_id()`
    - `fetch_patient_by_phone()`
    - `fetch_study_details()`
    - `get_case_update_details()`
    - `get_patient_report()`
    - `insert_case_update_log()`
    - `get_patient_todo_status()`
  - Resource definitions (greeting endpoint)
- **Dependencies**: `config.py`, `auth.py`, `data_processing.py`

### 5. `server.py` - Main Server Entry Point
- **Purpose**: Server initialization and startup
- **Contains**:
  - FastMCP server instance creation
  - Tool registration
  - ASGI app configuration
  - Main execution logic with startup messages
- **Dependencies**: `config.py`, `tools.py`

## Benefits of This Organization

### 1. **Separation of Concerns**
- Configuration is isolated in one place
- Authentication logic is separate from business logic
- Data processing is modular and reusable
- Server setup is clean and focused

### 2. **Better Maintainability**
- Each file has a single responsibility
- Easier to locate and modify specific functionality
- Reduced file size makes navigation easier

### 3. **Improved Testability**
- Individual modules can be unit tested in isolation
- Dependencies are clear and explicit
- Mocking external dependencies is easier

### 4. **Enhanced Reusability**
- Data processing functions can be reused across different tools
- Authentication utilities can be shared
- Configuration can be easily modified without touching business logic

## Migration Guide

To use the new structure instead of the original `mcp_precise.py`:

1. **Running the Server**:
   ```bash
   # Instead of: python mcp_precise.py
   python server.py
   ```

2. **Functionality Remains Identical**:
   - All API endpoints work exactly the same
   - All tools have the same signatures and behavior
   - Server startup and configuration are unchanged

3. **Environment Variables**:
   - All environment variables work the same way
   - Configuration is still read from the same sources

## File Dependencies Graph

```
server.py
├── config.py
└── tools.py
    ├── config.py
    ├── auth.py
    │   └── config.py
    └── data_processing.py
```

## Future Enhancements

This modular structure makes it easier to:

1. **Add New Tools**: Simply add them to `tools.py` or create tool-specific modules
2. **Modify Configuration**: Update `config.py` without touching business logic
3. **Enhance Authentication**: Improve JWT handling in `auth.py`
4. **Add Data Validation**: Extend `data_processing.py` with validation logic
5. **Create Tests**: Write focused unit tests for each module

## Backward Compatibility

The original `mcp_precise.py` file is preserved and remains functional. You can switch between the two approaches:

- **Monolithic**: `python mcp_precise.py`
- **Modular**: `python server.py`

Both provide identical functionality and API compatibility. 