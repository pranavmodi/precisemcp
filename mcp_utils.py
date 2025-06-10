#!/usr/bin/env python3
"""
MCP Dynamic Discovery Utilities

A collection of utilities for dynamically discovering and using MCP tools
without prior knowledge of what tools will be available.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from mcp.client.session import ClientSession
from mcp.types import Tool, Resource

logger = logging.getLogger(__name__)

class MCPToolDiscovery:
    """Utility class for discovering and analyzing MCP tools dynamically."""
    
    @staticmethod
    def find_tools_by_pattern(tools: List[Tool], pattern: str, 
                            search_description: bool = True) -> List[Tool]:
        """
        Find tools that match a pattern in name or description.
        
        Args:
            tools: List of tools to search
            pattern: Pattern to search for (case-insensitive)
            search_description: Whether to search in descriptions too
            
        Returns:
            List of matching tools
        """
        pattern_lower = pattern.lower()
        matching_tools = []
        
        for tool in tools:
            if pattern_lower in tool.name.lower():
                matching_tools.append(tool)
            elif search_description and tool.description and pattern_lower in tool.description.lower():
                matching_tools.append(tool)
        
        return matching_tools
    
    @staticmethod
    def categorize_tools(tools: List[Tool]) -> Dict[str, List[Tool]]:
        """
        Categorize tools based on common patterns in names and descriptions.
        
        Returns:
            Dictionary mapping categories to lists of tools
        """
        categories = {
            "communication": [],
            "math": [],
            "data": [],
            "file": [],
            "web": [],
            "time": [],
            "system": [],
            "other": []
        }
        
        # Keywords for each category
        keyword_map = {
            "communication": ["hello", "greet", "message", "chat", "talk", "say"],
            "math": ["add", "subtract", "multiply", "divide", "calculate", "fibonacci", "math"],
            "data": ["fetch", "get", "retrieve", "query", "database", "patient", "user", "search"],
            "file": ["file", "read", "write", "open", "save", "document"],
            "web": ["http", "api", "request", "weather", "url", "web"],
            "time": ["time", "date", "schedule", "calendar", "clock"],
            "system": ["system", "process", "memory", "cpu", "status"]
        }
        
        for tool in tools:
            categorized = False
            tool_text = (tool.name + " " + (tool.description or "")).lower()
            
            for category, keywords in keyword_map.items():
                if any(keyword in tool_text for keyword in keywords):
                    categories[category].append(tool)
                    categorized = True
                    break
            
            if not categorized:
                categories["other"].append(tool)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

class MCPParameterGenerator:
    """Utility class for generating intelligent parameter defaults for MCP tools."""
    
    @staticmethod
    def generate_parameters(tool: Tool, custom_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate intelligent parameter defaults for a tool.
        
        Args:
            tool: The tool to generate parameters for
            custom_params: Custom parameters to override defaults
            
        Returns:
            Dictionary of parameters ready for tool calling
        """
        parameters = {}
        if custom_params:
            parameters.update(custom_params)
        
        if not tool.inputSchema or 'properties' not in tool.inputSchema:
            return parameters
        
        properties = tool.inputSchema['properties']
        required = tool.inputSchema.get('required', [])
        
        for param_name, param_info in properties.items():
            if param_name in parameters:
                continue  # Already provided
            
            param_type = param_info.get('type', 'string')
            param_default = MCPParameterGenerator._generate_default_value(
                param_name, param_type, param_info, param_name in required
            )
            
            if param_default is not None:
                parameters[param_name] = param_default
        
        return parameters
    
    @staticmethod
    def _generate_default_value(param_name: str, param_type: str, 
                              param_info: Dict[str, Any], is_required: bool) -> Any:
        """Generate a default value for a parameter."""
        param_name_lower = param_name.lower()
        
        # Skip optional parameters unless they have obvious defaults
        if not is_required and not any(keyword in param_name_lower 
                                     for keyword in ['name', 'id', 'city', 'query']):
            return None
        
        # Name-based defaults
        if 'name' in param_name_lower:
            return "AutoClient"
        elif 'id' in param_name_lower:
            if 'patient' in param_name_lower:
                return "DEMO_PATIENT_001"
            elif 'user' in param_name_lower:
                return "user_123"
            elif 'conversation' in param_name_lower:
                return "auto_session_001"
            else:
                return "AUTO_ID_001"
        elif 'city' in param_name_lower:
            return "San Francisco"
        elif 'weather' in param_name_lower:
            return "sunny"
        elif 'query' in param_name_lower:
            return "test query"
        elif 'message' in param_name_lower:
            return "Hello from auto client"
        elif 'phone' in param_name_lower:
            return "+1-555-0123"
        elif 'email' in param_name_lower:
            return "test@example.com"
        
        # Type-based defaults
        if param_type == 'integer':
            if 'count' in param_name_lower or 'num' in param_name_lower:
                return 5
            elif 'year' in param_name_lower:
                return 2024
            elif 'age' in param_name_lower:
                return 30
            else:
                return 10
        elif param_type == 'number':
            if any(word in param_name_lower for word in ['a', 'b', 'x', 'y']):
                return 5.0
            elif 'price' in param_name_lower or 'cost' in param_name_lower:
                return 99.99
            else:
                return 1.0
        elif param_type == 'boolean':
            return True
        elif param_type == 'array':
            return []
        elif param_type == 'object':
            return {}
        else:  # string
            if is_required:
                return f"auto_value_for_{param_name}"
            else:
                return None

class MCPClientHelper:
    """Helper class for common MCP client operations."""
    
    def __init__(self, session: ClientSession):
        self.session = session
        self.tools: List[Tool] = []
        self.resources: List[Resource] = []
    
    async def discover_all(self) -> bool:
        """Discover all tools and resources."""
        try:
            # Discover tools
            tools_response = await self.session.list_tools()
            self.tools = tools_response.tools
            
            # Discover resources
            resources_response = await self.session.list_resources()
            self.resources = resources_response.resources
            
            return True
        except Exception as e:
            logger.error(f"Error during discovery: {e}")
            return False
    
    async def call_tool_safe(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Any]:
        """Safely call a tool with error handling."""
        try:
            result = await self.session.call_tool(tool_name, parameters)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return None
    
    async def test_tool_with_defaults(self, tool_name: str, 
                                    custom_params: Dict[str, Any] = None) -> Optional[Any]:
        """Test a tool with auto-generated parameters."""
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            logger.error(f"Tool {tool_name} not found")
            return None
        
        parameters = MCPParameterGenerator.generate_parameters(tool, custom_params)
        return await self.call_tool_safe(tool_name, parameters)
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a tool."""
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return None
        
        info = {
            "name": tool.name,
            "description": tool.description,
            "parameters": {}
        }
        
        if tool.inputSchema and 'properties' in tool.inputSchema:
            properties = tool.inputSchema['properties']
            required = tool.inputSchema.get('required', [])
            
            for param_name, param_info in properties.items():
                info["parameters"][param_name] = {
                    "type": param_info.get('type', 'unknown'),
                    "description": param_info.get('description', 'No description'),
                    "required": param_name in required,
                    "default": param_info.get('default')
                }
        
        return info
    
    def search_tools(self, query: str) -> List[Tool]:
        """Search tools by query string."""
        return MCPToolDiscovery.find_tools_by_pattern(self.tools, query)
    
    def categorize_tools(self) -> Dict[str, List[Tool]]:
        """Categorize all discovered tools."""
        return MCPToolDiscovery.categorize_tools(self.tools)
    
    async def read_resource_safe(self, resource_uri: str) -> Optional[Any]:
        """Safely read a resource with error handling."""
        try:
            result = await self.session.read_resource(resource_uri)
            return result
        except Exception as e:
            logger.error(f"Error reading resource {resource_uri}: {e}")
            return None

# Convenience functions for quick usage
async def quick_tool_discovery(session: ClientSession) -> MCPClientHelper:
    """Quickly set up a helper with full discovery."""
    helper = MCPClientHelper(session)
    await helper.discover_all()
    return helper

def format_tool_list(tools: List[Tool]) -> str:
    """Format a list of tools for display."""
    if not tools:
        return "No tools available"
    
    lines = []
    for i, tool in enumerate(tools, 1):
        lines.append(f"{i}. {tool.name}")
        if tool.description:
            lines.append(f"   {tool.description}")
    
    return "\n".join(lines)

def format_tool_parameters(tool: Tool) -> str:
    """Format tool parameters for display."""
    if not tool.inputSchema or 'properties' not in tool.inputSchema:
        return "No parameters"
    
    properties = tool.inputSchema['properties']
    required = tool.inputSchema.get('required', [])
    
    lines = []
    for param_name, param_info in properties.items():
        param_type = param_info.get('type', 'unknown')
        param_desc = param_info.get('description', 'No description')
        required_str = " (required)" if param_name in required else " (optional)"
        lines.append(f"  - {param_name} ({param_type}){required_str}: {param_desc}")
    
    return "\n".join(lines) if lines else "No parameters" 